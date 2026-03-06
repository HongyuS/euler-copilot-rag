import asyncio
import json
from faiss import IndexFlatL2
import numpy as np
import jieba
import re
from datetime import datetime
from src.worker.base import BaseWorker
from src.service.embedding import Embedding
from src.service.cluster import ClusterService
from src.service.convert import ConvertService
from src.parser.parser import LogParser
from src.parser.log_feature import log_feature_class_mapping
from src.sqlite.manager.task import TaskManager
from src.sqlite.manager.log_parse_result import LogParseResultManager
from src.schemas.task import TaskRelatedParamsModel
from src.schemas.cluster import ClusterModel
from src.enum.log import LogTypeEnum
from src.enum.task import TaskTypeEnum, TaskStatusEnum
from src.schemas.log import LogModel


class LogDetectionBasedOnKeywordsWorker(BaseWorker):
    """
    基于关键词的日志检测Worker
    """
    name = TaskTypeEnum.LOG_DETECTION_BASE_ON_KEYWORDS.value

    @staticmethod
    async def cal_keyword_similarity(str1: str, keywords: list[str]) -> float:
        """计算jaccard相似度"""
        words = list(jieba.cut(str1))
        new_keywords = []
        for keyword in keywords:
            new_keywords.extend(jieba.cut(keyword)) 
        keywords = set(new_keywords)
        words_set = set(words)
        intersection = words_set & keywords
        return (len(intersection) / len(keywords) if len(keywords) > 0 else 0.0)*100

    @staticmethod
    async def cal_sentiment_score(log_type: LogTypeEnum, log_content: str) -> float:
        log_class = log_feature_class_mapping.get(log_type, None)
        if log_class is None:
            return 0.0
        sum = 0.0
        score = 0.0
        for anomalous_keywords, _ in log_class.keywords_regex_and_scores["anomalous"].items():
            sum += _
            if re.search(anomalous_keywords, log_content):
                score += _
        return score/sum * 100 if sum > 0 else 0.0

    @staticmethod
    async def handle_single_log_file(file_path: str, max_anomaly_log_count: int, anomaly_keywords: list[str], time_start: str, time_end: str) -> list[LogModel]:
        """处理单个日志文件的逻辑"""
        # 这里实现处理单个日志文件的具体逻辑
        log_models: list[LogModel] = await LogParser.parse_log_file(file_path=file_path, need_split_by_regex=True, time_start=time_start, time_end=time_end)
        for log_model in log_models:
            log_type = log_model.log_type
            log_content = log_model.content
            sentiment_score = await LogDetectionBasedOnKeywordsWorker.cal_sentiment_score(log_type, log_content)
            keyword_similarity = await LogDetectionBasedOnKeywordsWorker.cal_keyword_similarity(log_content, anomaly_keywords)
            final_score = 0.2*sentiment_score + 0.8*keyword_similarity
            log_model.anomaly_score = final_score
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
            file_path_list = await BaseWorker.get_files_from_file_path_list(file_path_list)
            for i in range(0, len(file_path_list), batch_size):
                batch_file_path_list = file_path_list[i:i + batch_size]
                handle_tasks = []
                for file_path in batch_file_path_list:
                    handle_tasks.append(LogDetectionBasedOnKeywordsWorker.handle_single_log_file(
                        file_path, max_anomaly_log_count, anomaly_keywords, time_start, time_end))
                batch_results = await asyncio.gather(*handle_tasks)
                for log_model_list, candidate_unnormal_log_model_list in batch_results:
                    log_models.extend(log_model_list)
                    candidate_unnormal_log_models.extend(
                        candidate_unnormal_log_model_list)
            candidate_unnormal_log_models.sort(
                key=lambda x: x.anomaly_score, reverse=True)
            candidate_unnormal_log_models = candidate_unnormal_log_models[:max_anomaly_log_count]
            await LogDetectionBasedOnKeywordsWorker.add_log_parse_results(candidate_unnormal_log_models, log_models, task_id)
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.SUCCESSFUL_PENDING_REMOVE.value})
        except Exception as e:
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.FAILED_PENDING_REMOVE.value})
            raise e
