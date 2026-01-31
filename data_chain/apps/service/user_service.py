# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
import uuid
from typing import Union
from data_chain.logger.logger import logger as logging
from data_chain.entities.request_data import (
    ListUserRequest
)
from data_chain.entities.response_data import (
    User,
    ListUserMsg
)
from data_chain.entities.enum import (
    IdType,
    TeamType,
    TeamStatus,
    TeamUserStaus,
    UserRoleStatus,
    UserMessageStatus,
    UserMessageType,
    DeafaultRole
)
from data_chain.entities.common import default_roles
from data_chain.apps.base.convertor import Convertor
from data_chain.manager.user_manager import UserManager


class UserService:
    @staticmethod
    async def list_users(user_sub: str, req: ListUserRequest) -> ListUserMsg:
        try:
            total, user_entities = await UserManager.list_user(user_sub, req)
            user_list = []
            for user_entity in user_entities:
                user = await Convertor.convert_user_entity_to_user(user_entity)
                user_list.append(user)
            return ListUserMsg(total=total, users=user_list)
        except Exception as e:
            err = "用户列表获取失败"
            logging.warning("[UserService] %s", err)
            raise e
