import uuid
import logging
import os
from src.sqlite.manager.log_parse_result import LogParseResultManager
from src.schemas.log import LogModel, LogParseResultModel
from src.enum.task import TaskStatusEnum, TaskTypeEnum
from src.service.convert import ConvertService
from src.service.process import ProcessHandler
from src.sqlite.manager.task import TaskManager


logger = logging.getLogger(__name__)


class BaseWorker:
    """
    BaseWorker
    """
    name = TaskTypeEnum.BASE.value

    @staticmethod
    def find_worker_class(worker_name):
        subclasses = BaseWorker.__subclasses__()
        for subclass in subclasses:
            if subclass.name == worker_name:
                return subclass
        return None

    @staticmethod
    async def get_worker_name(task_id: str) -> str:
        '''获取worker_name'''
        task_entity = await TaskManager.get_task_by_id(task_id)
        if task_entity is None:
            err = f"获取任务失败, 任务ID: {task_id}"
            logging.error("[BaseWorker] %s", err)
            raise ValueError(err)
        return task_entity.task_type

    @staticmethod
    async def add_log_parse_results(anomaly_log_models: list[LogModel], log_models: list[LogModel], task_id: str) -> None:
        """将异常日志模型列表添加到日志解析结果表中"""
        anomaly_log_models_id_set = set(
            [log_model.id for log_model in anomaly_log_models])
        for log_model in log_models:
            if log_model.id in anomaly_log_models_id_set and log_model.anomaly_score > 0:
                log_model.is_anomalous = True
            else:
                log_model.is_anomalous = False
        log_parse_result_models = await ConvertService.log_models_to_log_parse_result_models(
            log_models, task_id)
        await LogParseResultManager.add_log_parse_results(log_parse_result_models)

    @staticmethod
    async def get_files_from_file_path_list(file_path_list: list[str]) -> list[str]:
        """从文件路径列表中获取所有的文件路径"""
        file_path_list = list(set(file_path_list))
        all_file_paths = []
        for file_path in file_path_list:
            if os.path.isfile(file_path):
                all_file_paths.append(file_path)
            elif os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        all_file_paths.append(os.path.join(root, file))
        return all_file_paths

    @staticmethod
    async def run(task_id: str) -> bool:
        '''运行任务'''
        logger.info(f"[BaseWorker] 开始运行任务: {task_id}")
        worker_name = await BaseWorker.get_worker_name(task_id)
        logger.info(f"[BaseWorker] Worker类型: {worker_name}")
        
        worker_class = BaseWorker.find_worker_class(worker_name)
        if not worker_class:
            logger.error(f"[BaseWorker] 找不到Worker类: {worker_name}")
            return False
            
        logger.info(f"[BaseWorker] 准备添加任务到进程: {task_id}")
        flag = await ProcessHandler.add_task(
            task_id, worker_class.run, task_id)
        
        logger.info(f"[BaseWorker] ProcessHandler.add_task 返回: {flag}")
        
        if flag:
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.RUNNING.value})
            logger.info(f"[BaseWorker] 任务状态已更新为 RUNNING: {task_id}")
        else:
            logger.warning(f"[BaseWorker] 任务添加失败: {task_id}")
        
        return flag

    @staticmethod
    async def stop(task_id: str) -> bool:
        '''停止任务'''
        task_entity = await TaskManager.get_task_by_id(task_id)
        if task_entity.status == TaskStatusEnum.RUNNING.value:
            await ProcessHandler.remove_task(task_id)
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.CANCLED.value})
            return True
        elif task_entity.status == TaskStatusEnum.PENDING.value:
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.CANCLED.value})
            return True
        return False
