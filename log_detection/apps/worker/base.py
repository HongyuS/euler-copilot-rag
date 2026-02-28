import uuid
import logging
from apps.enum.task import TaskStatusEnum, TaskTypeEnum
from apps.service.process import ProcessHandler
from apps.sqlite.manager.task import TaskManager


class BaseWorker:
    """
    BaseWorker
    """
    name = TaskTypeEnum.BASE

    @staticmethod
    def find_worker_class(worker_name):
        subclasses = BaseWorker.__subclasses__()
        for subclass in subclasses:
            if subclass.name == worker_name:
                return subclass
        return None

    @staticmethod
    async def get_worker_name(task_id: uuid.UUID) -> str:
        '''获取worker_name'''
        task_entity = await TaskManager.get_task_by_id(str(task_id))
        if task_entity is None:
            err = f"获取任务失败, 任务ID: {task_id}"
            logging.error("[BaseWorker] %s", err)
            raise ValueError(err)
        return task_entity.task_type

    @staticmethod
    async def run(task_id: uuid.UUID) -> bool:
        '''运行任务'''
        worker_name = await BaseWorker.get_worker_name(task_id)
        flag = ProcessHandler.add_task(
            task_id, BaseWorker.find_worker_class(worker_name).run, task_id)
        await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.RUNNNING.value})
        return flag

    @staticmethod
    async def stop(task_id: uuid.UUID) -> bool:
        '''停止任务'''
        worker_name = await BaseWorker.get_worker_name(task_id)
        task_entity = await TaskManager.get_task_by_id(str(task_id))
        if task_entity.status == TaskStatusEnum.RUNNNING.value:
            ProcessHandler.remove_task(task_id)
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.CANCLED.value})
        elif task_entity.status == TaskStatusEnum.PENDING.value:
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.CANCLED.value})
        else:
            return False
        task_id = await (BaseWorker.find_worker_class(worker_name).stop(task_id))
        return (task_id is not None)
