# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import os
import signal
import uuid
import asyncio
import multiprocessing
import logging

from apps.config.config import Config
logger = logging.getLogger(__name__)

multiprocessing = multiprocessing.get_context('spawn')


class ProcessHandler:
    ''' 进程处理器类'''
    tasks = {}  # 存储进程的字典
    lock = asyncio.Lock()
    if Config().get_config().log_pare_use_cpu_limit is None:
        max_processes = max((os.cpu_count() or 1) // 2, 1)
    else:
        max_processes = Config().get_config().log_pare_use_cpu_limit
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
    def add_task(task_id: uuid.UUID, target, *args, **kwargs):
        """添加任务到进程池"""
        acquired = ProcessHandler.lock.acquire(timeout=ProcessHandler.time_out)
        if not acquired:
            warning = f"获取锁失败，可能是进程池已满或其他原因。请稍后再试。"
            logger.warning(f"[ProcessHandler] %s", warning)
            return False

        if len(ProcessHandler.tasks) >= ProcessHandler.max_processes:
            warning = f"任务数量已达上限({ProcessHandler.max_processes})，请稍后再试。"
            logger.warning(f"[ProcessHandler] %s", warning)
            ProcessHandler.lock.release()
            return False

        if task_id not in ProcessHandler.tasks:
            try:
                process = multiprocessing.Process(target=ProcessHandler.subprocess_target,
                                                  args=(target,) + args, kwargs=kwargs)
                ProcessHandler.tasks[task_id] = process
                process.start()
                ProcessHandler.lock.release()
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
    def remove_task(task_id: uuid.UUID):
        acquired = ProcessHandler.lock.acquire(timeout=ProcessHandler.time_out)
        if not acquired:
            warning = f"获取锁失败，可能是进程池已满或其他原因。请稍后再试。"
            logger.warning(f"[ProcessHandler] %s", warning)
            return
        if task_id in ProcessHandler.tasks.keys():
            process = ProcessHandler.tasks[task_id]
            del ProcessHandler.tasks[task_id]
            try:
                if process.is_alive():
                    pid = process.pid
                    os.kill(pid, signal.SIGKILL)
                    info = f"进程 {task_id} ({pid}) 被杀死。"
                    logger.info(f"[ProcessHandler] %s", info)
            except Exception as e:
                warning = f"杀死进程 {task_id} 失败: {e}"
                logger.warning(f"[ProcessHandler] %s", warning)
            info = f"任务ID {task_id} 被删除。"
            logger.info(f"[ProcessHandler] %s", info)
        else:
            waring = f"任务ID {task_id} 不存在，无法删除。"
            logger.warning(f"[ProcessHandler] %s", waring)
        ProcessHandler.lock.release()
