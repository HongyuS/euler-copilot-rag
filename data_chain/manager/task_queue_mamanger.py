
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
from sqlalchemy import select, delete, update, desc, asc, func, exists, or_, and_
import uuid
from typing import Dict, List, Optional, Tuple
from data_chain.logger.logger import logger as logging
from data_chain.stores.database.database import DataBase, TaskQueueEntity
from data_chain.entities.enum import TaskStatus


class TaskQueueManager():
    """任务队列管理类"""

    @staticmethod
    async def add_task(task: TaskQueueEntity):
        try:
            async with await DataBase.get_session() as session:
                session.add(task)
                await session.commit()
        except Exception as e:
            err = "添加任务到队列失败"
            logging.exception("[TaskQueueManager] %s", err)
            raise e

    @staticmethod
    async def delete_task_by_id(task_id: uuid.UUID):
        """根据任务ID删除任务"""
        try:
            async with await DataBase.get_session() as session:
                stmt = delete(TaskQueueEntity).where(TaskQueueEntity.id == task_id)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            err = "删除任务失败"
            logging.exception("[TaskQueueManager] %s", err)
            raise e

    @staticmethod
    async def get_oldest_tasks_by_status(status: TaskStatus) -> Optional[TaskQueueEntity]:
        """根据任务状态获取最早的任务"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    select(TaskQueueEntity)
                    .where(TaskQueueEntity.status == status.value)
                    .order_by(asc(TaskQueueEntity.created_time))
                    .limit(1)
                )
                return await session.scalars(stmt).first()
        except Exception as e:
            err = "获取最早的任务失败"
            logging.exception("[TaskQueueManager] %s", err)
            raise e

    @staticmethod
    async def get_task_by_id(task_id: uuid.UUID) -> Optional[TaskQueueEntity]:
        """根据任务ID获取任务"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TaskQueueEntity).where(TaskQueueEntity.id == task_id)
                return await session.scalars(stmt).first()
        except Exception as e:
            err = "获取任务失败"
            logging.exception("[TaskQueueManager] %s", err)
            raise e

    @staticmethod
    async def update_task_by_id(task_id: uuid.UUID, task: TaskQueueEntity):
        """根据任务ID更新任务"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    update(TaskQueueEntity)
                    .where(TaskQueueEntity.id == task_id)
                    .values(status=task.status)
                )
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            err = "更新任务失败"
            logging.exception("[TaskQueueManager] %s", err)
            raise e
