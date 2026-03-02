# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import os
import signal
import uuid
import asyncio
import multiprocessing
import logging
from apps.sqlite.manager.task import TaskManager
from apps.enum.task import TaskStatusEnum
logger = logging.getLogger(__name__)

multiprocessing = multiprocessing.get_context('spawn')


class ProcessHandler:
    ''' 进程处理器类'''
    lock = asyncio.Lock()
    time_out = 10

    @staticmethod
    def subprocess_target(target, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(target(*args, **kwargs))
        finally:
            loop.close()

    @staticmethod
    async def add_task(task_id: uuid.UUID, target, *args, **kwargs):
        """添加任务到进程池"""
        acquired = ProcessHandler.lock.acquire(timeout=ProcessHandler.time_out)
        if not acquired:
            warning = f"获取锁失败，可能是进程池已满或其他原因。请稍后再试。"
            logger.warning(f"[ProcessHandler] %s", warning)
            return False
        # 当本机每个cpu使用率>=85%时，认为进程池已满，拒绝添加新任务
        # 计算cpu使用率
        cpu_usage = os.getloadavg()[2] / os.cpu_count() * 100
        if cpu_usage >= 85:
            warning = f"CPU使用率过高({cpu_usage:.2f}%)，拒绝添加新任务。"
            logger.warning(f"[ProcessHandler] %s", warning)
            ProcessHandler.lock.release()
            return False
        task_model = await TaskManager.get_task_by_id(task_id)
        if task_model and task_model.status == TaskStatusEnum.PENDING.value:
            try:
                process = multiprocessing.Process(target=ProcessHandler.subprocess_target,
                                                  args=(target,) + args, kwargs=kwargs)
                process.start()
                ProcessHandler.lock.release()
                await TaskManager.update_task_by_id(task_id, {"pid": process.pid})
                return True
            except Exception as e:
                error = f"添加任务 {task_id} 失败: {e}"
                logger.error(f"[ProcessHandler] %s", error)
                ProcessHandler.lock.release()
                return False
        else:
            info = f"任务ID {task_id} 已存在，无法添加。"
            logger.info(f"[ProcessHandler] %s", info)
            ProcessHandler.lock.release()
            return False

    @staticmethod
    async def remove_task(task_id: uuid.UUID):
        """从进程池中移除任务"""
        acquired = ProcessHandler.lock.acquire(timeout=ProcessHandler.time_out)
        if not acquired:
            warning = f"获取锁失败，可能是进程池已满或其他原因。请稍后再试。"
            logger.warning(f"[ProcessHandler] %s", warning)
            return
        task_model = await TaskManager.get_task_by_id(task_id)
        if task_model and task_model.pid:
            try:
                pid = task_model.pid
                os.kill(pid, signal.SIGKILL)
                info = f"进程 {task_id} ({pid}) 被杀死。"
                logger.info(f"[ProcessHandler] %s", info)
            except Exception as e:
                warning = f"杀死进程 {task_id} 失败: {e}"
                logger.warning(f"[ProcessHandler] %s", warning)
        ProcessHandler.lock.release()
