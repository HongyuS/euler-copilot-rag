# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
from sqlalchemy import select, update, delete, and_, or_, func
from typing import Dict
import uuid

from data_chain.logger.logger import logger as logging
from data_chain.entities.request_data import (
    ListUserMessageRequest
)
from data_chain.entities.enum import (
    TeamStatus,
    UserRoleStatus,
    RoleStatus,
    UserMessageStatus,
    UserMessageType
)
from data_chain.manager.team_manager import TeamManager
from data_chain.stores.database.database import (
    DataBase,
    TeamEntity,
    UserRoleEntity,
    RoleActionEntity,
    UserMessageEntity
)


class UserMessageManager:
    """用户消息管理器"""

    @staticmethod
    async def add_user_message(user_message_entity: UserMessageEntity) -> bool:
        try:
            async with await DataBase.get_session() as session:
                session.add(user_message_entity)
                await session.commit()
                await session.refresh(user_message_entity)
                return True
        except Exception as e:
            err = f"用户消息添加失败 {e}"
            logging.warning("[UserMessageManager] %s", err)
        return False

    @staticmethod
    async def add_user_messages(user_message_entities: list[UserMessageEntity]) -> bool:
        try:
            async with await DataBase.get_session() as session:
                session.add_all(user_message_entities)
                await session.commit()
                for entity in user_message_entities:
                    await session.refresh(entity)
                return True
        except Exception as e:
            err = "用户消息批量添加失败"
            logging.warning("[UserMessageManager] %s", err)
        return False

    @staticmethod
    async def is_user_message_exist(user_sub: str, team_id: uuid.UUID, msg_type: UserMessageType) -> bool:
        """检查用户是否存在某类型的消息"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(func.count()).select_from(UserMessageEntity).where(
                    and_(
                        UserMessageEntity.sender_id == user_sub,
                        UserMessageEntity.team_id == team_id,
                        UserMessageEntity.type == msg_type.value,
                        UserMessageEntity.status_to_sender == UserMessageStatus.UNREAD.value
                    )
                )
                count = (await session.execute(stmt)).scalar()
                return count > 0
        except Exception as e:
            err = f"检查用户是否存在某类型的消息失败 {e}"
            logging.warning("[UserMessageManager] %s", err)
        return False

    @staticmethod
    async def list_user_messages(
            user_sub: str, req: ListUserMessageRequest) -> tuple[int, list[UserMessageEntity]]:
        """根据用户标识和消息类型列出用户消息"""
        try:
            async with await DataBase.get_session() as session:
                # 查询用户加入或者创建的团队，加入的团队要求用户的角色有 POST /usr_msg/list 权限
                stmt = select(TeamEntity.id).where(
                    TeamEntity.author_id == user_sub,
                    TeamEntity.status == TeamStatus.EXISTED.value
                )
                team_ids_created = [team_id for team_id, in await session.execute(stmt)]
                stmt = select(TeamEntity.id).join(
                    UserRoleEntity, TeamEntity.id == UserRoleEntity.team_id
                ).join(
                    RoleActionEntity, UserRoleEntity.role_id == RoleActionEntity.role_id
                ).where(
                    and_(
                        TeamEntity.author_id != user_sub,
                        UserRoleEntity.user_id == user_sub,
                        TeamEntity.status == TeamStatus.EXISTED.value,
                        UserRoleEntity.status == UserRoleStatus.EXISTED.value,
                        RoleActionEntity.action == 'POST /usr_msg/list'
                    )
                ).distinct()
                team_ids_joined = [team_id for team_id, in await session.execute(stmt)]
                team_ids = team_ids_created + team_ids_joined

                # 创建基础查询条件
                base_conditions = or_(
                    and_(
                        UserMessageEntity.sender_id == user_sub,
                        UserMessageEntity.status_to_sender != UserMessageStatus.DELETED.value
                    ),
                    and_(
                        UserMessageEntity.receiver_id == user_sub,
                        UserMessageEntity.status_to_receiver != UserMessageStatus.DELETED.value
                    ),
                    and_(
                        UserMessageEntity.sender_id != user_sub,
                        UserMessageEntity.receiver_id != user_sub,
                        UserMessageEntity.team_id.in_(team_ids),
                        UserMessageEntity.is_to_all == True,
                        UserMessageEntity.status_to_receiver != UserMessageStatus.DELETED.value
                    )
                )

                # 单独构建计数查询
                count_stmt = select(func.count()).select_from(
                    UserMessageEntity).where(base_conditions)
                if req.msg_type:
                    count_stmt = count_stmt.where(
                        UserMessageEntity.type == req.msg_type.value)
                total = (await session.execute(count_stmt)).scalar()

                # 构建数据查询
                data_stmt = select(UserMessageEntity).where(base_conditions)
                if req.msg_type:
                    data_stmt = data_stmt.where(
                        UserMessageEntity.type == req.msg_type.value)

                # 添加排序和分页
                data_stmt = data_stmt.order_by(UserMessageEntity.created_time.desc())\
                    .offset((req.page - 1) * req.page_size)\
                    .limit(req.page_size)

                result = await session.execute(data_stmt)
                user_message_entities = result.scalars().all()

                return total, user_message_entities
        except Exception as e:
            err = f"根据用户标识和消息类型列出用户消息失败 {e}"
            logging.warning("[UserMessageManager] %s", err)
            return 0, []

    @staticmethod
    async def get_user_message_by_msg_id(msg_id: uuid.UUID) -> UserMessageEntity:
        """通过消息ID获取用户消息"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(UserMessageEntity).where(
                    UserMessageEntity.id == msg_id,
                    or_(
                        UserMessageEntity.status_to_sender != UserMessageStatus.DELETED.value,
                        UserMessageEntity.status_to_receiver != UserMessageStatus.DELETED.value
                    )
                )
                result = await session.execute(stmt)
                user_message_entity = result.scalars().first()
                return user_message_entity
        except Exception as e:
            err = f"通过消息ID获取用户消息失败 {e}"
            logging.warning("[UserMessageManager] %s", err)
        return None

    @staticmethod
    async def update_user_message_by_msg_id(msg_id: uuid.UUID, msg_dict: Dict[str, str]) -> bool:
        """通过消息ID更新用户消息"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(UserMessageEntity).where(
                    UserMessageEntity.id == msg_id
                ).values(**msg_dict)
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = "通过消息ID更新用户消息失败"
            logging.warning("[UserMessageManager] %s", err)
        return False
