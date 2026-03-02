import asyncio
import json
from faiss import IndexFlatL2
import numpy as np
import jieba
import re
from datetime import datetime
from apps.prompt.log_detection import DETECT_LOG_PROMPT
from apps.worker.base import BaseWorker
from apps.service.embedding import Embedding
from apps.service.llm import LLMService
from apps.parser.parser import LogParser
from apps.sqlite.manager.task import TaskManager
from apps.schemas.task import TaskRelatedParamsModel
from apps.enum.task import TaskTypeEnum, TaskStatusEnum
from apps.schemas.log import LogModel
from apps.config.config import Config


class LogDetectionBasedOnLLMWorker(BaseWorker):
    """
    基于LLM的日志检测Worker
    """
    name = TaskTypeEnum.LOG_DETECTION_BASE_ON_LLM.value

    @staticmethod
    async def handle_single_log_model(query: str, log_model: LogModel, llm: LLMService) -> LogModel:
        """处理单个日志模型的逻辑"""
        log_content = log_model.content
        prompt = DETECT_LOG_PROMPT.format(query=query, log_content=log_content)
        llm_response = await llm.nostream([], prompt, "请直接返回JSON格式的字符串，包含anomaly_score（异常分数，0-100）和anomaly_reason（异常原因）两个字段", st_str="{", en_str="}")
        try:
            response_dict = json.loads(llm_response)
            log_model.anomaly_score = response_dict.get("anomaly_score", 0.0)
            log_model.anomaly_reason = response_dict.get("anomaly_reason", "")
        except json.JSONDecodeError:
            log_model.anomaly_score = 0.0
            log_model.anomaly_reason = "LLM返回的结果无法解析"

    @staticmethod
    async def handle_single_log_file(file_path: str, max_anomaly_log_count: int, query: str, llm: LLMService, time_start: str, time_end: str) -> list[LogModel]:
        """处理单个日志文件的逻辑"""
        # 这里实现处理单个日志文件的具体逻辑
        log_models: list[LogModel] = await LogParser.parse_log_file(file_path=file_path, time_start=time_start, time_end=time_end, chunk_size=min(8192, llm.max_tokens//3*2))
        for i in range(0, len(log_models), llm.batch_size):
            batch_log_models = log_models[i:i + llm.batch_size]
            handle_tasks = []
            for log_model in batch_log_models:
                handle_tasks.append(
                    LogDetectionBasedOnLLMWorker.handle_single_log_model(query, log_model, llm))
            await asyncio.gather(*handle_tasks)
        candidate_unnormal_log_models = sorted(
            log_models, key=lambda x: x.anomaly_score, reverse=True)[:max_anomaly_log_count]
        return log_models, candidate_unnormal_log_models

    @staticmethod
    async def run(task_id: str) -> None:
        """日志检测服务"""
        try:
            task_entity = await TaskManager.get_task_by_id(task_id)
            if task_entity is None:
                await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.FAILED.value})
                raise ValueError(f"任务 {task_id} 不存在")
            task_related_params_js = json.loads(
                task_entity.task_related_params)
            if "time_start" in task_related_params_js:
                task_related_params_js["timestart"] = datetime.strptime(task_related_params_js["time_start"],
                                                                        '%Y-%m-%d %H:%M')
            if "time_end" in task_related_params_js:
                task_related_params_js["time_end"] = datetime.strptime(task_related_params_js["time_end"],
                                                                       '%Y-%m-%d %H:%M')
            task_related_params_model = TaskRelatedParamsModel(
                **task_related_params_js)
            query = task_related_params_model.query
            query_embedding = await Embedding.get_embedding(query)
            file_path_list = task_related_params_model.file_path_list
            max_anomaly_log_count = task_related_params_model.max_anomaly_log_count
            anomaly_keywords: list[str] = task_related_params_model.anomaly_keywords
            time_start = task_related_params_model.time_start
            time_end = task_related_params_model.time_end
            # 异常日志候选列表
            log_models = []
            candidate_unnormal_log_models: list[LogModel] = []
            batch_size = 8
            llm = LLMService(openai_api_key=Config().get_config().llm_model.api_key, openai_api_base=Config().get_config().llm_model.end_point, model_name=Config(
            ).get_config().llm_model.model_name, max_tokens=Config().get_config().llm_model.max_tokens, batch_size=Config().get_config().llm_model.batch_size)
            file_path_list = await BaseWorker.get_files_from_file_path_list(file_path_list)
            for i in range(0, len(file_path_list), batch_size):
                batch_file_path_list = file_path_list[i:i + batch_size]
                handle_tasks = []
                for file_path in batch_file_path_list:
                    handle_tasks.append(LogDetectionBasedOnLLMWorker.handle_single_log_file(
                        file_path, max_anomaly_log_count, query, llm, time_start, time_end))
                batch_results = await asyncio.gather(*handle_tasks)
                for log_model_list, candidate_unnormal_log_model_list in batch_results:
                    log_models.extend(log_model_list)
                    candidate_unnormal_log_models.extend(
                        candidate_unnormal_log_model_list)
            candidate_unnormal_log_models.sort(
                key=lambda x: x.anomaly_score, reverse=True)
            candidate_unnormal_log_models = candidate_unnormal_log_models[:max_anomaly_log_count]
            await LogDetectionBasedOnLLMWorker.add_log_parse_results(candidate_unnormal_log_models, log_models, task_id)
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.SUCCESSFUL_PENDING_REMOVE.value})
        except Exception as e:
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.FAILED_PENDING_REMOVE.value})
            raise e
