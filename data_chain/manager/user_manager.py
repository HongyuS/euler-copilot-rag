# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
from sqlalchemy import select, delete, func, and_, update
from data_chain.logger.logger import logger as logging

from data_chain.entities.request_data import ListUserRequest
from data_chain.entities.enum import UserStatus, TeamUserStaus
from data_chain.stores.database.database import DataBase, UserEntity, TeamUserEntity


class UserManager:

    @staticmethod
    async def add_user(user_entity: UserEntity) -> bool:
        try:
            async with await DataBase.get_session() as session:
                current_user_entity = await UserManager.get_user_by_id(user_entity.id)
                if current_user_entity:
                    stmt = update(UserEntity).where(UserEntity.id == user_entity.id).values(
                        name=user_entity.name)
                    await session.execute(stmt)
                    await session.commit()
                    return True
                session.add(user_entity)
                await session.commit()
                await session.refresh(user_entity)
                return True
        except Exception as e:
            err = "用户添加失败"
            logging.warning("[UserManger] %s", err)
        return False

    @staticmethod
    async def list_user(user_sub: str, req: ListUserRequest) -> tuple[int, list[UserEntity]]:
        try:
            async with await DataBase.get_session() as session:
                stmt = select(UserEntity).where(
                    and_(UserEntity.status != UserStatus.DELETED.value,
                         UserEntity.id != user_sub))
                if req.user_sub:
                    stmt = stmt.where(UserEntity.id.ilike(f"%{req.user_sub}%"))
                if req.user_name:
                    stmt = stmt.where(
                        UserEntity.name.ilike(f"%{req.user_name}%"))
                if req.team_id is not None:
                    subquery = select(TeamUserEntity.user_id).where(
                        and_(
                            TeamUserEntity.team_id == req.team_id,
                            TeamUserEntity.status != TeamUserStaus.DELETED.value
                        )
                    ).subquery()
                    stmt = stmt.where(UserEntity.id.not_in(subquery))
                count_stmt = select(
                    func.count()).select_from(stmt.subquery())
                total = (await session.execute(count_stmt)).scalar()
                stmt = stmt.offset((req.page - 1) * req.page_size).limit(
                    req.page_size)
                stmt = stmt.order_by(UserEntity.created_time.desc())
                result = (await session.execute(stmt)).scalars().all()
                return total, result
        except Exception as e:
            err = "用户列表获取失败"
            logging.warning("[UserManger] %s", err)
            raise e
        return []

    @staticmethod
    async def get_user_by_id(user_id: str) -> UserEntity:
        """根据用户ID获取用户信息"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(UserEntity).where(and_(UserEntity.id == user_id,
                                                     UserEntity.status != UserStatus.DELETED.value))
                result = await session.execute(stmt)
                return result.scalars().first()
        except Exception as e:
            err = "获取用户信息失败"
            logging.warning("[UserManger] %s", err)
            return None

    @staticmethod
    async def update_user_name(user_id: str, user_name: str) -> bool:
        """更新用户名"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(UserEntity).where(UserEntity.id == user_id)
                result = await session.execute(stmt)
                user_entity = result.scalar_one_or_none()

                if user_entity:
                    user_entity.name = user_name
                    await session.commit()
                    return True
                return False
        except Exception as e:
            err = "用户名更新失败"
            logging.warning("[UserManger] %s", err)
            return False
