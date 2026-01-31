# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
import asyncio
import uuid
from typing import Optional
from data_chain.entities.enum import TaskType, TaskStatus
from data_chain.apps.base.task.worker.base_worker import BaseWorker
# from data_chain.stores.mongodb.mongodb import MongoDB, Task
from data_chain.stores.database.database import TaskQueueEntity
from data_chain.manager.task_manager import TaskManager
from data_chain.manager.task_queue_mamanger import TaskQueueManager
from data_chain.logger.logger import logger as logging


class TaskQueueService:
    """任务队列"""

    @staticmethod
    async def init_task_queue():
        task_need_pending_ids = []
        task_need_delete_ids = []
        task_entities_need_add = []
        import time
        st = time.time()
        pending_task_entities = await TaskManager.list_task_by_task_status(TaskStatus.PENDING.value)
        en = time.time()
        pending_task_ids = [
            task_entity.id for task_entity in pending_task_entities]
        pending_task_entities_in_db = []
        batch_size = 1024
        for i in range(0, len(pending_task_ids), batch_size):
            st = time.time()
            batch_entities = await TaskQueueManager.get_tasks_by_ids(
                pending_task_ids[i:i+batch_size])
            en = time.time()
            pending_task_entities_in_db.extend(batch_entities)
        pending_task_ids_in_db = [
            task_entity.id for task_entity in pending_task_entities_in_db]
        pending_task_ids_not_in_db = list(
            set(pending_task_ids) - set(pending_task_ids_in_db))
        for task_id in pending_task_ids_not_in_db:
            task_entities_need_add.append(TaskQueueEntity(
                id=task_id, status=TaskStatus.PENDING.value))

        st = time.time()
        running_task_entities = await TaskManager.list_task_by_task_status(TaskStatus.RUNNING.value)
        en = time.time()
        for task_entity in running_task_entities:
            # 将所有任务取消
            try:
                st = time.time()
                flag = await BaseWorker.reinit(task_entity.id)
                en = time.time()
                if flag:
                    st = time.time()
                    task_need_pending_ids.append(task_entity.id)
                    en = time.time()
                else:
                    st = time.time()
                    task_need_delete_ids.append(task_entity.id)
                    en = time.time()
            except Exception as e:
                warning = f"[TaskQueueService] 初始化任务失败 {e}"
                logging.warning(warning)
        if len(task_need_pending_ids) > 0:
            st = time.time()
            for i in range(0, len(task_need_pending_ids), batch_size):
                await TaskQueueManager.update_task_by_ids(
                    task_need_pending_ids[i:i+batch_size], TaskStatus.PENDING)
            en = time.time()
        if len(task_need_delete_ids) > 0:
            st = time.time()
            for i in range(0, len(task_need_delete_ids), batch_size):
                await TaskQueueManager.delete_tasks_by_ids(
                    task_need_delete_ids[i:i+batch_size])
            en = time.time()
        if len(task_entities_need_add) > 0:
            st = time.time()
            for i in range(0, len(task_entities_need_add), batch_size):
                await TaskQueueManager.add_tasks(
                    task_entities_need_add[i:i+batch_size])
            en = time.time()

    @staticmethod
    async def init_task(task_type: str, op_id: uuid.UUID) -> uuid.UUID:
        """初始化任务"""
        try:
            task_id = await BaseWorker.init(task_type, op_id)
            if task_id:
                await TaskQueueManager.add_task(TaskQueueEntity(id=task_id, status=TaskStatus.PENDING.value))
            return task_id
        except Exception as e:
            err = f"[TaskQueueService] 初始化任务失败 {e}"
            logging.exception(err)

    @staticmethod
    async def stop_task(task_id: uuid.UUID):
        """停止任务"""
        try:
            flag = await BaseWorker.stop(task_id)
            if not flag:
                return None
            return task_id
        except Exception as e:
            err = f"[TaskQueueService] 停止任务失败 {e}"
            logging.exception(err)

    @staticmethod
    async def delete_task(task_id: uuid.UUID):
        """删除任务"""
        try:
            flag = await BaseWorker.stop(task_id)
            delete_flag = await BaseWorker.delete(task_id)
            if delete_flag:
                return task_id
            return None
        except Exception as e:
            err = f"[TaskQueueService] 删除任务失败 {e}"
            logging.exception(err)

    @staticmethod
    async def handle_successed_tasks():
        handle_successed_task_limit = 1024
        for i in range(handle_successed_task_limit):
            task = await TaskQueueManager.get_oldest_tasks_by_status(TaskStatus.SUCCESS)
            if task is None:
                break
            try:
                await BaseWorker.deinit(task.id)
            except Exception as e:
                err = f"[TaskQueueService] 处理成功任务失败 {e}"
                logging.error(err)
            await TaskQueueManager.delete_task_by_id(task.id)

    @staticmethod
    async def handle_failed_tasks():
        handle_failed_task_limit = 1024
        for i in range(handle_failed_task_limit):
            task = await TaskQueueManager.get_oldest_tasks_by_status(TaskStatus.FAILED)
            if task is None:
                break
            try:
                flag = await BaseWorker.reinit(task.id)
            except Exception as e:
                err = f"[TaskQueueService] 处理失败任务失败 {e}"
                logging.error(err)
                await TaskQueueManager.delete_task_by_id(task.id)
                continue
            if flag:
                await TaskQueueManager.update_task_by_id(task.id, TaskStatus.PENDING)
            else:
                await TaskQueueManager.delete_task_by_id(task.id)

    @staticmethod
    async def handle_pending_tasks():
        handle_pending_task_limit = 128
        for i in range(handle_pending_task_limit):
            task = await TaskQueueManager.get_oldest_tasks_by_status(TaskStatus.PENDING)
            if task is None:
                break
            try:
                flag = await BaseWorker.run(task.id)
            except Exception as e:
                err = f"[TaskQueueService] 处理待处理任务失败 {e}"
                logging.error(err)
                await TaskQueueManager.delete_task_by_id(task.id)
                continue
            if not flag:
                break
            await TaskQueueManager.delete_task_by_id(task.id)

    @staticmethod
    async def handle_tasks():
        await TaskQueueService.handle_successed_tasks()
        await TaskQueueService.handle_failed_tasks()
        await TaskQueueService.handle_pending_tasks()
