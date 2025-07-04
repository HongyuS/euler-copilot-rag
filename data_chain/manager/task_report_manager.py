# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
from sqlalchemy import select, delete, update, desc, asc, func, exists, or_, and_
from sqlalchemy.orm import aliased
import uuid
from typing import Dict, List, Optional, Tuple
from data_chain.logger.logger import logger as logging
from data_chain.stores.database.database import DataBase, TaskReportEntity
from data_chain.entities.enum import TaskStatus


class TaskReportManager():
    @staticmethod
    async def add_task_report(task_report_entity: TaskReportEntity) -> TaskReportEntity:
        """添加任务报告"""
        try:
            async with await DataBase.get_session() as session:
                session.add(task_report_entity)
                await session.commit()
                await session.refresh(task_report_entity)
            return task_report_entity
        except Exception as e:
            err = "添加任务报告失败"
            logging.exception("[TaskReportManager] %s", err)

    @staticmethod
    async def list_current_task_report_by_task_ids(task_ids: List[uuid.UUID]) -> List[TaskReportEntity]:
        """根据任务ID列表查询当前任务报告"""
        try:
            async with await DataBase.get_session() as session:
                # 创建一个别名用于子查询
                report_alias = aliased(TaskReportEntity)

                # 构建子查询，为每个task_id分配行号，并过滤无效状态
                subquery = (
                    select(
                        report_alias.id,  # 只选择ID列，用于后续连接
                        func.row_number().over(
                            partition_by=report_alias.task_id,
                            order_by=desc(report_alias.created_time)
                        ).label('rn')
                    )
                    .where(
                        report_alias.task_id.in_(task_ids)
                    )
                    .subquery()
                )

                # 主查询通过ID连接子查询，获取完整的TaskReportEntity对象
                stmt = (
                    select(TaskReportEntity)
                    .join(
                        subquery,
                        TaskReportEntity.id == subquery.c.id  # 通过ID连接确保获取完整实体
                    )
                    .where(subquery.c.rn == 1)  # 只取每个task_id的最新记录
                )

                result = await session.execute(stmt)
                task_report_entities = result.scalars().all()  # 直接获取实体对象列表
                return task_report_entities
        except Exception as e:
            err = "查询当前任务报告失败"
            logging.exception("[TaskReportManager] %s", err)
            raise e

    @staticmethod
    async def list_all_task_report_by_task_id(task_id: uuid.UUID) -> List[TaskReportEntity]:
        """根据任务ID查询所有任务报告"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TaskReportEntity).where(TaskReportEntity.task_id == task_id)
                stmt = stmt.order_by(TaskReportEntity.created_time.desc())
                stmt = stmt.order_by(TaskReportEntity.id.asc())
                result = await session.execute(stmt)
                task_report_entities = result.scalars().all()
                return task_report_entities
        except Exception as e:
            err = "查询所有任务报告失败"
            logging.exception("[TaskReportManager] %s", err)
            raise e
