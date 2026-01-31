# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
from sqlalchemy import select, delete, update, and_, func
from typing import Dict
import uuid

from data_chain.logger.logger import logger as logging
from data_chain.entities.request_data import (
    ListRoleRequest
)
from data_chain.entities.enum import (
    TeamStatus,
    RoleActionStatus,
    UserRoleStatus,
    RoleStatus
)
from data_chain.stores.database.database import DataBase, RoleEntity, ActionEntity, RoleActionEntity, UserRoleEntity


class RoleManager:
    @staticmethod
    async def add_role(role_entity: RoleEntity) -> RoleEntity:
        """添加角色"""
        try:
            async with await DataBase.get_session() as session:
                session.add(role_entity)
                await session.commit()
                await session.refresh(role_entity)
        except Exception as e:
            err = "添加角色失败"
            logging.exception("[RoleManager] %s", err)
            raise e
        return role_entity

    @staticmethod
    async def add_user_role(user_role_entity: UserRoleEntity) -> UserRoleEntity:
        """添加用户角色"""
        try:
            async with await DataBase.get_session() as session:
                session.add(user_role_entity)
                await session.commit()
                await session.refresh(user_role_entity)
        except Exception as e:
            err = "添加用户角色失败"
            logging.exception("[RoleManager] %s", err)
            raise e
        return user_role_entity

    @staticmethod
    async def add_action(action_entity: ActionEntity) -> ActionEntity:
        """添加操作"""
        try:
            async with await DataBase.get_session() as session:
                session.add(action_entity)
                await session.commit()
                await session.refresh(action_entity)
            return True
        except Exception as e:
            err = "添加操作失败"
            logging.warning("[RoleManager] %s", err)
            return False

    @staticmethod
    async def add_role_actions(role_action_entities: list[RoleActionEntity]) -> bool:
        """添加角色操作"""
        try:
            async with await DataBase.get_session() as session:
                for role_action_entity in role_action_entities:
                    session.add(role_action_entity)
                await session.commit()
                for role_action_entity in role_action_entities:
                    await session.refresh(role_action_entity)
        except Exception as e:
            err = "添加角色操作失败"
            logging.exception("[RoleManager] %s", err)
            raise e

    @staticmethod
    async def get_role_by_id(role_id: uuid.UUID) -> RoleEntity:
        """根据角色ID获取角色"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(RoleEntity).where(
                    and_(
                        RoleEntity.id == role_id,
                        RoleEntity.status != RoleStatus.DELETED.value
                    )
                )
                result = await session.execute(stmt)
                role_entity = result.scalars().first()
                return role_entity
        except Exception as e:
            err = "根据角色ID获取角色失败"
            logging.exception("[RoleManager] %s", err)
            raise e

    @staticmethod
    async def get_action_by_action(action: str) -> ActionEntity:
        """根据action获取操作"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(ActionEntity).where(ActionEntity.action == action)
                result = await session.execute(stmt)
                action_entity = result.scalars().first()
                return action_entity
        except Exception as e:
            err = "根据action获取操作失败"
            logging.warning("[RoleManager] %s: %s", err, e)
            return None

    @staticmethod
    async def get_user_role_by_user_sub_and_team_id(
            user_sub: str, team_id: uuid.UUID) -> UserRoleEntity:
        """根据用户ID和团队ID获取用户角色"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(UserRoleEntity).where(
                    and_(
                        UserRoleEntity.user_id == user_sub,
                        UserRoleEntity.team_id == team_id,
                        UserRoleEntity.status != UserRoleStatus.DELETED.value
                    )
                )
                result = await session.execute(stmt)
                user_role_entity = result.scalars().first()
                return user_role_entity
        except Exception as e:
            err = "根据用户ID和团队ID获取用户角色失败"
            logging.exception("[RoleManager] %s", err)
            raise e

    @staticmethod
    async def get_role_by_role_name_and_team_id(
            role_name: str, team_id: uuid.UUID) -> RoleEntity:
        """根据角色名称和团队ID获取角色"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(RoleEntity).where(
                    and_(
                        RoleEntity.name == role_name,
                        RoleEntity.team_id == team_id,
                        RoleEntity.status != RoleStatus.DELETED.value
                    )
                )
                result = await session.execute(stmt)
                role_entity = result.scalars().first()
                return role_entity
        except Exception as e:
            err = "根据角色名称和团队ID获取角色失败"
            logging.exception("[RoleManager] %s", err)
            raise e

    @staticmethod
    async def get_action_by_team_id_user_sub_and_action(
            user_sub: str, team_id: uuid.UUID, action: str) -> ActionEntity:
        """根据团队ID、用户ID和操作获取操作"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(ActionEntity).join(
                    RoleActionEntity, ActionEntity.action == RoleActionEntity.action).join(
                    UserRoleEntity, RoleActionEntity.role_id == UserRoleEntity.role_id).where(
                    and_(
                        UserRoleEntity.user_id == user_sub,
                        UserRoleEntity.team_id == team_id,
                        ActionEntity.action == action,
                        RoleActionEntity.status != RoleActionStatus.DELETED.value,
                        UserRoleEntity.status != UserRoleStatus.DELETED.value,
                    )
                )
                result = await session.execute(stmt)
                action_entity = result.scalars().first()
                return action_entity
        except Exception as e:
            err = "根据团队ID、用户ID和操作获取操作失败"
            logging.exception("[RoleManager] %s", err)
            raise e

    @staticmethod
    async def list_roles(req: ListRoleRequest) -> tuple[int, list[RoleEntity]]:
        """根据团队ID获取角色列表"""
        logging.error(req)
        try:
            async with await DataBase.get_session() as session:
                stmt = select(RoleEntity).where(
                    and_(
                        RoleEntity.team_id == req.team_id,
                        RoleEntity.status != RoleStatus.DELETED.value
                    )
                )
                if req.role_id is not None:
                    stmt = stmt.where(RoleEntity.id == req.role_id)
                if req.role_name is not None:
                    stmt = stmt.where(
                        RoleEntity.role_name.iike(f"%{req.role_name}%"))
                count_stmt = select(
                    func.count()).select_from(stmt.subquery())
                result = await session.execute(count_stmt)
                total = result.scalar()
                stmt = stmt.order_by(RoleEntity.created_time.asc())
                stmt = stmt.offset((req.page - 1) *
                                   req.page_size).limit(req.page_size)
                result = await session.execute(stmt)
                role_entities = result.scalars().all()
                return total, role_entities
        except Exception as e:
            err = "根据团队ID获取角色列表失败"
            logging.exception("[RoleManager] %s", err)
            raise e

    @staticmethod
    async def list_user_roles_by_team_id_and_user_subs(
            team_id: uuid.UUID, user_subs: list[str]) -> list[UserRoleEntity]:
        """根据团队ID和用户ID列表列出用户角色"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(UserRoleEntity).where(
                    and_(
                        UserRoleEntity.team_id == team_id,
                        UserRoleEntity.user_id.in_(user_subs),
                        UserRoleEntity.status != UserRoleStatus.DELETED.value
                    )
                )
                result = await session.execute(stmt)
                user_role_entities = result.scalars().all()
                return user_role_entities
        except Exception as e:
            err = "根据团队ID和用户ID列表列出用户角色失败"
            logging.exception("[RoleManager] %s", err)
            raise e

    @staticmethod
    async def list_roles_by_role_ids(role_ids: list[uuid.UUID]) -> list[RoleEntity]:
        """根据角色ID列表列出角色"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(RoleEntity).where(
                    and_(
                        RoleEntity.id.in_(role_ids),
                        RoleEntity.status != RoleStatus.DELETED.value
                    )
                )
                result = await session.execute(stmt)
                role_entities = result.scalars().all()
                return role_entities
        except Exception as e:
            err = "根据角色ID列表列出角色失败"
            logging.exception("[RoleManager] %s", err)
            raise e

    @staticmethod
    async def list_role_actions_by_role_ids(role_ids: list[uuid.UUID]) -> list[RoleActionEntity]:
        """根据角色ID列表列出角色操作"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(RoleActionEntity).where(
                    and_(
                        RoleActionEntity.role_id.in_(role_ids),
                        RoleActionEntity.status != RoleActionStatus.DELETED.value
                    )
                )
                result = await session.execute(stmt)
                role_action_entities = result.scalars().all()
                return role_action_entities
        except Exception as e:
            err = "根据角色ID列表列出角色操作失败"
            logging.exception("[RoleManager] %s", err)
            raise e

    @staticmethod
    async def update_role_by_id(role_id: uuid.UUID, role_dict: Dict[str, str]) -> bool:
        """通过角色ID更新角色"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(RoleEntity).where(
                    RoleEntity.id == role_id
                ).values(**role_dict)
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = f"通过角色ID更新角色失败 {e}"
            logging.warning("[RoleManager] %s", err)
        return False

    @staticmethod
    async def update_role_actions_by_role_id(
            role_id: uuid.UUID, role_action_dict: Dict[str, str]) -> bool:
        """通过角色ID更新角色操作"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(RoleActionEntity).where(
                    RoleActionEntity.role_id == role_id
                ).values(**role_action_dict)
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = "通过角色ID更新角色操作失败"
            logging.warning("[RoleManager] %s", err)

    @staticmethod
    async def update_user_role_by_id(user_role_id: uuid.UUID, user_role_dict: Dict[str, str]) -> bool:
        """通过用户角色ID更新用户角色"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(UserRoleEntity).where(
                    UserRoleEntity.id == user_role_id
                ).values(**user_role_dict)
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = "通过用户角色ID更新用户角色失败"
            logging.warning("[RoleManager] %s", err)
        return False

    @staticmethod
    async def update_user_role_by_role_id(
            role_id: uuid.UUID, user_role_dict: Dict[str, str]) -> bool:
        """通过角色ID更新用户角色"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(UserRoleEntity).where(
                    UserRoleEntity.role_id == role_id
                ).values(**user_role_dict)
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = "通过角色ID更新用户角色失败"
            logging.warning("[RoleManager] %s", err)
        return False

    @staticmethod
    async def update_user_roles_by_team_id_and_user_subs(
            team_id: uuid.UUID, user_subs: list[str], user_role_dict: Dict[str, str]) -> bool:
        """通过团队ID和用户ID列表更新用户角色"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(UserRoleEntity).where(
                    and_(
                        UserRoleEntity.team_id == team_id,
                        UserRoleEntity.user_id.in_(user_subs)
                    )
                ).values(**user_role_dict)
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = "通过团队ID和用户ID列表更新用户角色失败"
            logging.warning("[RoleManager] %s", err)
        return False
