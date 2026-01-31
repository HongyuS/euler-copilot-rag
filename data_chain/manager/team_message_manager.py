# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
from sqlalchemy import select, update, delete, and_, func
from data_chain.logger.logger import logger as logging
from data_chain.entities.request_data import (
    ListTeamMsgRequest
)
from data_chain.entities.enum import (
    TeamMessageStatus
)
from data_chain.stores.database.database import DataBase, TeamMessageEntity


class TeamMessageManager:
    """团队消息管理器"""
    @staticmethod
    async def add_team_msg(team_msg_entity: TeamMessageEntity) -> TeamMessageEntity:
        """添加团队消息"""
        try:
            async with await DataBase.get_session() as session:
                session.add(team_msg_entity)
                await session.commit()
                await session.refresh(team_msg_entity)
        except Exception as e:
            err = "添加团队消息失败"
            logging.exception("[TeamMessageManager] %s", err)
            raise e
        return team_msg_entity

    @staticmethod
    async def list_team_msg_by_team_id(req: ListTeamMsgRequest) -> tuple[int, list[TeamMessageEntity]]:
        """列出团队消息"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(TeamMessageEntity).where(
                    and_(TeamMessageEntity.team_id == req.team_id,
                         TeamMessageEntity.status != TeamMessageStatus.DELETED.value)
                ).order_by(TeamMessageEntity.created_time.desc())
                if req.message_level:
                    stmt = stmt.where(
                        TeamMessageEntity.meggage_level == req.message_level.value)
                total_stmt = select(func.count()).select_from(stmt.subquery())
                total_result = await session.execute(total_stmt)
                total = total_result.scalar_one()
                stmt = stmt.order_by(TeamMessageEntity.created_time.desc())
                stmt = stmt.offset((req.page - 1) *
                                   req.page_size).limit(req.page_size)
                result = await session.execute(stmt)
                team_msg_entities = result.scalars().all()
                return total, team_msg_entities
        except Exception as e:
            err = "列出团队消息失败"
            logging.exception("[TeamMessageManager] %s", err)
            raise e
