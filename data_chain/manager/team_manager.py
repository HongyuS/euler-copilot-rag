# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
from sqlalchemy import select, update, delete, and_, or_, func, distinct, exists
from typing import Dict
import uuid

from data_chain.logger.logger import logger as logging
from data_chain.entities.request_data import (
    ListTeamUserRequest,
    ListTeamRequest
)
from data_chain.entities.enum import (
    TeamStatus,
    UserStatus,
    TeamUserStaus
)
from data_chain.stores.database.database import DataBase, TeamEntity, UserEntity, TeamUserEntity


class TeamManager:

    @staticmethod
    async def add_team(team_entity: TeamEntity) -> TeamEntity:
        """添加团队"""
        try:
            async with await DataBase.get_session() as session:
                session.add(team_entity)
                await session.commit()
                await session.refresh(team_entity)
        except Exception as e:
            err = "添加团队失败"
            logging.exception("[TeamManger] %s", err)
            raise e
        return team_entity

    @staticmethod
    async def add_team_user(team_user_entity: TeamUserEntity) -> TeamUserEntity:
        """添加团队成员"""
        try:
            async with await DataBase.get_session() as session:
                session.add(team_user_entity)
                await session.commit()
                await session.refresh(team_user_entity)
        except Exception as e:
            err = "添加团队成员失败"
            logging.exception("[TeamManger] %s", err)
        return team_user_entity

    @staticmethod
    async def list_team_myjoined_by_user_sub(user_sub: str, req: ListTeamRequest) -> list[TeamEntity]:
        """列出我加入的团队,以及总数"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TeamEntity).join(TeamUserEntity, TeamEntity.id == TeamUserEntity.team_id).where(
                    and_(TeamUserEntity.user_id == user_sub,
                         TeamEntity.author_id != user_sub,
                         TeamEntity.status != TeamStatus.DELETED.value,
                         TeamUserEntity.status != TeamUserStaus.DELETED.value
                         ))
                if req.team_id:
                    stmt = stmt.where(TeamEntity.id == req.team_id)
                if req.team_name:
                    stmt = stmt.where(
                        TeamEntity.name.ilike(f"%{req.team_name}%"))
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total = (await session.execute(count_stmt)).scalar()
                stmt = stmt.limit(req.page_size).offset(
                    (req.page - 1) * req.page_size)
                stmt = stmt.order_by(TeamEntity.created_time.desc())
                result = await session.execute(stmt)
                team_entities = result.scalars().all()
                return (total, team_entities)
        except Exception as e:
            err = "列出我加入的团队失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def list_team_mycreated_by_user_sub(user_sub: str, req: ListTeamRequest) -> list[TeamEntity]:
        """列出我创建的团队"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TeamEntity).where(and_(
                    TeamEntity.author_id == user_sub, TeamEntity.status != TeamStatus.DELETED.value))
                if req.team_id:
                    stmt = stmt.where(TeamEntity.id == req.team_id)
                if req.team_name:
                    stmt = stmt.where(
                        TeamEntity.name.ilike(f"%{req.team_name}%"))
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total = (await session.execute(count_stmt)).scalar()
                stmt = stmt.limit(req.page_size).offset(
                    (req.page - 1) * req.page_size)
                stmt = stmt.order_by(TeamEntity.created_time.desc())
                result = await session.execute(stmt)
                team_entities = result.scalars().all()
                return (total, team_entities)
        except Exception as e:
            err = "列出我创建的团队失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def list_all_team_user_created_or_joined(user_sub: str) -> list[TeamEntity]:
        """列出我创建或加入的团队"""
        try:
            async with await DataBase.get_session() as session:
                # 合并查询：创建者 或 成员（排除自己创建的情况）
                stmt = select(TeamEntity).where(
                    TeamEntity.status != TeamStatus.DELETED.value,
                    or_(
                        TeamEntity.author_id == user_sub,
                        exists(
                            select(TeamUserEntity.team_id)
                            .where(
                                TeamUserEntity.team_id == TeamEntity.id,
                                TeamUserEntity.user_id == user_sub,
                                TeamEntity.author_id != user_sub
                            )
                        )
                    )
                ).order_by(TeamEntity.created_time.desc())
                
                result = await session.execute(stmt)
                team_entities = result.scalars().all()
                return team_entities
        except Exception as e:
            err = "列出我创建或加入的团队失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def list_team_mycreated_by_user_sub_and_team_ids(user_sub: str, team_ids: list[uuid.UUID]) -> list[TeamEntity]:
        """列出我创建的团队通过团队ID列表"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TeamEntity).where(and_(
                    TeamEntity.author_id == user_sub,
                    TeamEntity.status != TeamStatus.DELETED.value,
                    TeamEntity.id.in_(team_ids)))
                result = await session.execute(stmt)
                team_entities = result.scalars().all()
                return team_entities
        except Exception as e:
            err = "列出我创建的团队通过团队ID列表失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def list_team_myjoined_by_user_sub_and_team_ids(user_sub: str, team_ids: list[uuid.UUID]) -> list[TeamEntity]:
        """列出我加入的团队通过团队ID列表"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TeamEntity).join(TeamUserEntity, TeamEntity.id == TeamUserEntity.team_id).where(
                    and_(TeamUserEntity.user_id == user_sub,
                         TeamEntity.author_id != user_sub,
                         TeamEntity.status != TeamStatus.DELETED.value,
                         TeamUserEntity.status != TeamUserStaus.DELETED.value,
                         TeamEntity.id.in_(team_ids)))
                result = await session.execute(stmt)
                team_entities = result.scalars().all()
                return team_entities
        except Exception as e:
            err = "列出我加入的团队通过团队ID列表失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def list_public_team(user_sub: str, req: ListTeamRequest) -> tuple[int, list[TeamEntity]]:
        """列出公开的团队（同时满足去重和按时间排序）"""
        try:
            async with await DataBase.get_session() as session:
                # 1. 构建所有筛选条件（复用逻辑）
                base_condition = TeamEntity.status != TeamStatus.DELETED.value

                core_condition = or_(
                    TeamEntity.is_public == True,
                    TeamEntity.author_id == user_sub,
                    exists(
                        select(TeamUserEntity.id)
                        .where(
                            TeamUserEntity.team_id == TeamEntity.id,
                            TeamUserEntity.user_id == user_sub,
                            TeamEntity.status != TeamStatus.DELETED.value,
                            TeamUserEntity.status != TeamUserStaus.DELETED.value)
                    )
                )

                filter_conditions = []
                if req.team_id:
                    filter_conditions.append(TeamEntity.id == req.team_id)
                if req.team_name:
                    filter_conditions.append(
                        TeamEntity.name.ilike(f"%{req.team_name}%"))

                all_conditions = [base_condition,
                                  core_condition] + filter_conditions

                # 2. 子查询：先筛选并去重，仅获取不重复的团队ID
                # 作用：解决团队因多成员导致的重复问题
                distinct_team_ids = (
                    select(TeamEntity.id)
                    .where(*all_conditions)
                    .distinct()  # 去重核心：确保每个团队ID只出现一次
                    .subquery()  # 转为子查询，供主查询使用
                )

                # 3. 主查询：基于去重后的ID查询完整团队信息，并按时间排序
                # 优势：排序不受DISTINCT ON限制，可直接按created_time排序
                data_stmt = (
                    select(TeamEntity)
                    .where(TeamEntity.id.in_(distinct_team_ids))  # 只查去重后的团队
                    .order_by(TeamEntity.created_time.desc())  # 按创建时间倒序（最新的在前）
                )

                # 4. 分页：在排序之后执行，确保分页基于正确的时间顺序
                data_stmt = data_stmt.limit(req.page_size).offset(
                    (req.page - 1) * req.page_size)

                # 5. 计数查询：复用筛选条件，统计去重后的总数量
                count_stmt = select(func.count(
                    distinct(TeamEntity.id))).where(*all_conditions)
                total = (await session.execute(count_stmt)).scalar() or 0

                # 6. 执行查询并返回结果
                result = await session.execute(data_stmt)
                team_entities = result.scalars().all()

                return (total, team_entities)
        except Exception as e:
            err = "列出公开的团队失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def list_team_user_by_team_id(req: ListTeamUserRequest) -> tuple[int, list[UserEntity]]:
        """列出团队成员"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(UserEntity).join(TeamUserEntity, UserEntity.id == TeamUserEntity.user_id).where(
                    and_(TeamUserEntity.team_id == req.team_id, UserEntity.status != UserStatus.DELETED.value, TeamUserEntity.status != TeamUserStaus.DELETED.value))
                if req.user_sub:
                    stmt = stmt.where(UserEntity.id.ilike(f"%{req.user_sub}%"))
                if req.user_name:
                    stmt = stmt.where(
                        UserEntity.name.ilike(f"%{req.user_name}%"))
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total = (await session.execute(count_stmt)).scalar()
                stmt = stmt.limit(req.page_size).offset(
                    (req.page - 1) * req.page_size)
                stmt = stmt.order_by(UserEntity.created_time.desc())
                result = await session.execute(stmt)
                team_user_entities = result.scalars().all()
                return (total, team_user_entities)
        except Exception as e:
            err = "列出团队成员失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def list_team_user_by_team_id_and_user_subs(team_id: uuid.UUID, user_subs: list[str]) -> list[TeamUserEntity]:
        """列出团队成员通过用户ID列表"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TeamUserEntity).where(and_(
                    TeamUserEntity.team_id == team_id,
                    TeamUserEntity.user_id.in_(user_subs),
                    TeamUserEntity.status != TeamUserStaus.DELETED.value
                ))
                result = await session.execute(stmt)
                team_user_entities = result.scalars().all()
                return team_user_entities
        except Exception as e:
            err = "列出团队成员通过用户ID列表失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def get_team_user_by_user_sub_and_team_id(user_sub: str, team_id: uuid.UUID) -> TeamUserEntity:
        """根据用户ID和团队ID获取团队成员"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TeamUserEntity).where(and_(
                    TeamUserEntity.user_id == user_sub,
                    TeamUserEntity.team_id == team_id,
                    TeamUserEntity.status != TeamUserStaus.DELETED.value
                ))
                result = await session.execute(stmt)
                team_user_entity = result.scalars().first()
                return team_user_entity
        except Exception as e:
            err = "根据用户ID和团队ID获取团队成员失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def get_team_user_by_subs_and_team_id(user_subs: list[str], team_id: uuid.UUID) -> list[TeamUserEntity]:
        """根据用户ID列表和团队ID获取团队成员用户ID列表"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TeamUserEntity).where(and_(
                    TeamUserEntity.user_id.in_(user_subs),
                    TeamUserEntity.team_id == team_id,
                    TeamUserEntity.status != TeamUserStaus.DELETED.value
                ))
                result = await session.execute(stmt)
                team_user_subs = result.scalars().all()
                return team_user_subs
        except Exception as e:
            err = "根据用户ID列表和团队ID获取团队成员用户ID列表失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def get_team_by_id(team_id: uuid.UUID) -> TeamEntity:
        """根据团队ID获取团队"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TeamEntity).where(
                    and_(
                        TeamEntity.id == team_id,
                        TeamEntity.status != TeamStatus.DELETED.value
                    )
                )
                result = await session.execute(stmt)
                team_entity = result.scalars().first()
                return team_entity
        except Exception as e:
            err = "根据团队ID获取团队失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def delete_team_by_id(team_id: uuid.UUID) -> uuid.UUID:
        """删除团队"""
        try:
            async with await DataBase.get_session() as session:
                stmt = delete(TeamEntity).where(TeamEntity.id == team_id)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            err = "删除团队失败"
            logging.exception("[TeamManager] %s", err)
            raise e
        return team_id

    @staticmethod
    async def delete_teams_deleted() -> None:
        """删除团队"""
        try:
            async with await DataBase.get_session() as session:
                stmt = delete(TeamEntity).where(
                    TeamEntity.status == TeamStatus.DELETED.value)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            err = "删除团队失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def update_team_by_id(team_id: uuid.UUID, team_dict: Dict[str, str]) -> TeamEntity:
        """更新团队"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(TeamEntity).where(
                    TeamEntity.id == team_id).values(**team_dict)
                await session.execute(stmt)
                await session.commit()
                stmt = select(TeamEntity).where(TeamEntity.id == team_id)
                result = await session.execute(stmt)
                team_entity = result.scalars().first()
                return team_entity
        except Exception as e:
            err = "更新团队失败"
            logging.exception("[TeamManager] %s", err)
            raise e

    @staticmethod
    async def update_team_users_by_team_id_and_user_subs(
            team_id: uuid.UUID, user_subs: list[str], user_role_dict: Dict[str, str]) -> bool:
        """通过团队ID和用户ID列表更新团队成员"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(TeamUserEntity).where(
                    and_(
                        TeamUserEntity.team_id == team_id,
                        TeamUserEntity.user_id.in_(user_subs)
                    )
                ).values(**user_role_dict)
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = "通过团队ID和用户ID列表更新团队成员失败"
            logging.exception("[TeamManager] %s", err)
        return False

    @staticmethod
    async def update_team_user_cnt_by_team_id(team_id: uuid.UUID) -> bool:
        """更新团队成员数量"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(func.count()).select_from(TeamUserEntity).where(and_(
                    TeamUserEntity.team_id == team_id,
                    TeamUserEntity.status != TeamUserStaus.DELETED.value
                ))
                total = (await session.execute(stmt)).scalar()
                stmt = update(TeamEntity).where(TeamEntity.id ==
                                                team_id).values(member_cnt=total)
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = "更新团队成员数量失败"
            logging.exception("[TeamManager] %s", err)
        return False
