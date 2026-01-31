import asyncio
import json
import logging
from apps.worker.base import BaseWorker
from apps.service.process import ProcessHandler
from apps.enum.task import TaskStatusEnum
from apps.sqlite.manager.task import TaskManager


logger = logging.getLogger(__name__)


class TaskService:
    """任务服务类"""
    @staticmethod
    async def process_successful_or_failed_tasks():
        """处理所有成功或失败的任务"""
        tasks = await TaskManager.get_tasks_by_status([TaskStatusEnum.SUCCESSFUL, TaskStatusEnum.FAILED])
        for task in tasks:
            try:
                await ProcessHandler.remove_task(task.task_id)
                logger.info(f"任务 {task.task_id} 处理完成并移除")
            except Exception as e:
                logger.error(f"处理任务 {task.task_id} 时出错: {e}")
            return []

    @staticmethod
    async def process_pending_tasks():
        """处理所有待处理任务"""
        tasks = await TaskManager.get_tasks_by_status([TaskStatusEnum.PENDING])
        for task in tasks:
            try:
                result = BaseWorker.run(task.task_id)
                if not result:
                    break
            except Exception as e:
                logger.error(f"处理任务 {task.task_id} 时出错: {e}")

    async def listen_and_process_tasks(self):
        """监听并处理任务的主循环"""
        while 1:
            try:
                await self.process_successful_or_failed_tasks()
                await self.process_pending_tasks()
            except Exception as e:
                logger.error(f"任务处理主循环出错: {e}")
            await asyncio.sleep(2)  # 每隔2秒检查一次任务
