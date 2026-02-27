import json
from apps.parser.parser import LogParser
from apps.sqlite.manager.task import TaskManager
from apps.schemas.task import TaskModel
from apps.enum.task import TaskTypeEnum, TaskStatusEnum
from apps.schemas.log import LogModel, LogTemplateModel


class LogDetectionBasedOnClusteringWorker:
    name = TaskTypeEnum.LOG_DETECTION_BASE_ON_CLUSTERING

    @staticmethod
    async def stop(task_id: str) -> None:
        """停止日志检测服务"""
        # 这里实现停止日志检测的具体逻辑
        pass

    @staticmethod
    async def run(task_id: str) -> None:
        """日志检测服务"""
        task_entity = await TaskManager.get_task_by_id(task_id)
        if task_entity is None:
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.FAILED.value})
            raise ValueError(f"任务 {task_id} 不存在")
        task_related_params = json.loads(task_entity.task_related_params)
        query = task_related_params.get("query", "")
        file_path_list = task_related_params.get("file_path_list", [])
        max_anomaly_log_count = task_related_params.get(
            "max_anomaly_log_count", 100)
        anomaly_keywords = task_related_params.get("anomaly_keywords", [])
        time_start = task_related_params.get("time_start", None)
        time_end = task_related_params.get("time_end", None)
        for file_path in file_path_list:
            log_models = await LogParser.parse_log_file(file_path=file_path, need_embedding=True, need_split_by_regex=True, time_start=time_start, time_end=time_end)
            