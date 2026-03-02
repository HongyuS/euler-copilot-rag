from datetime import datetime
import json
import uuid
from apps.sqlite.manager.task import TaskManager
from apps.schemas.task import TaskModel, TaskRelatedParamsModel
from apps.schemas.log import LogModel, LogParseResultModel
from apps.worker.base import BaseWorker
from apps.enum.task import TaskTypeEnum, TaskStatusEnum
from apps.enum.log import LogLevelEnum, LogTypeEnum
from apps.sqlite.manager.log_parse_result import LogParseResultManager
from apps.config.config import Config


class LogTaskHandleService:
    @staticmethod
    async def create_log_parse_task(task_type: TaskTypeEnum | None, query: str, file_path_list: list[str], max_anomaly_log_count: int, anomaly_keywords: list[str], time_start: str, time_end: str) -> str:
        """创建日志解析任务"""
        if task_type is None:
            task_type = Config().get_config().log_parse_method
        task_model = TaskModel(
            task_name=f"{task_type.value} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            task_type=task_type.value,
            compltetion_precent=0.0,
            status=TaskStatusEnum.PENDING.value,
            task_related_params=json.dumps({
                "query": query,
                "file_path_list": file_path_list,
                "max_anomaly_log_count": max_anomaly_log_count,
                "anomaly_keywords": anomaly_keywords,
                "time_start": time_start,
                "time_end": time_end
            })
        )
        task_id = await TaskManager.create_task(task_model)
        return task_id

    @staticmethod
    async def stop_task(task_id: uuid.UUID) -> bool:
        """停止日志解析任务"""
        flag = await BaseWorker.stop(task_id)
        return flag

    @staticmethod
    async def get_task_message(task_id: uuid.UUID) -> TaskModel:
        """获取任务信息"""
        task_model = await TaskManager.get_task_by_id(str(task_id))
        return task_model

    @staticmethod
    async def get_task_result(task_id: uuid.UUID, limit: int | None = None, offset: int | None = None, is_anomalous: bool | None = None) -> tuple[int, list[LogParseResultModel]]:
        """获取任务结果"""
        total, log_parse_result_models = await LogParseResultManager.get_log_parse_results_by_task_id(str(task_id), limit, offset, is_anomalous)
        return total, log_parse_result_models
