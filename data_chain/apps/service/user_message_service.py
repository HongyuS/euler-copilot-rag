# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
import uuid
from typing import Union
from data_chain.logger.logger import logger as logging
from data_chain.apps.exceptions import MessagePermissionDeniedException
from data_chain.entities.request_data import (
    ListUserMessageRequest
)
from data_chain.entities.response_data import (
    ListUserMessageMsg
)
from data_chain.entities.enum import (
    IdType,
    TeamType,
    TeamStatus,
    TeamUserStaus,
    UserRoleStatus,
    UserMessageStatus,
    UserMessageType,
    DeafaultRole,
    MessageLevel
)
from data_chain.entities.common import default_roles
from data_chain.stores.database.database import TeamEntity
from data_chain.apps.base.convertor import Convertor
from data_chain.apps.service.team_service import TeamService
from data_chain.manager.team_manager import TeamManager
from data_chain.manager.team_message_manager import TeamMessageManager
from data_chain.manager.user_message_manager import UserMessageManager
from data_chain.manager.role_manager import RoleManager
from data_chain.manager.knowledge_manager import KnowledgeBaseManager
from data_chain.apps.service.knwoledge_base_service import KnowledgeBaseService


class UserMessageService:
    """用户消息服务"""
    @staticmethod
    async def is_user_message_exist(user_sub: str, team_id: uuid, msg_type: UserMessageType) -> bool:
        """检查用户是否存在某类型的消息"""
        try:
            is_exist = await UserMessageManager.is_user_message_exist(user_sub, team_id, msg_type)
            return is_exist
        except Exception as e:
            err = "检查用户是否存在某类型的消息失败"
            logging.exception("[UserMessageService] %s", err)
            raise e

    @staticmethod
    async def list_user_messages(
            user_sub: str, req: ListUserMessageRequest) -> ListUserMessageMsg:
        """根据用户标识和消息类型获取用户消息列表"""
        try:
            total, user_message_entities = await UserMessageManager.list_user_messages(
                user_sub, req)
            user_messages = []
            for user_message_entity in user_message_entities:
                user_message = await Convertor.convert_user_sub_and_user_message_entity_to_user_message(user_sub, user_message_entity)
                user_messages.append(user_message)
            return ListUserMessageMsg(total=total, userMessages=user_messages)
        except Exception as e:
            err = "根据用户标识和消息类型获取用户消息列表失败"
            logging.exception("[UserMessageService] %s", err)
            raise e

    @staticmethod
    async def update_user_message(
            user_sub: str, msg_id: uuid.UUID, msg_status: UserMessageStatus) -> Union[None, str]:
        """根据消息标识和消息状态更新用户消息"""
        user_message_entity = await UserMessageManager.get_user_message_by_msg_id(msg_id)
        if not user_message_entity:
            raise Exception('用户消息不存在')
        if user_message_entity.status_to_receiver != UserMessageStatus.UNREAD.value:
            raise Exception('用户消息状态只能从未读更新为已读')
        if msg_status == UserMessageStatus.UNREAD:
            raise Exception('用户消息状态只能从未读更新为已读')
        if user_sub == user_message_entity.sender_id:
            raise Exception('用户不能修改自己发送的消息')
        can_access = False
        if user_sub == user_message_entity.receiver_id:
            can_access = True
        if user_sub != user_message_entity.sender_id and user_message_entity.is_to_all:
            action_entity = await RoleManager.get_action_by_team_id_user_sub_and_action(
                user_sub, user_message_entity.team_id, 'PUT /usr_msg')
            if action_entity:
                can_access = True
        if not can_access:
            raise MessagePermissionDeniedException("修改该消息", str(msg_id))
        await UserMessageManager.update_user_message_by_msg_id(
            msg_id, {'status_to_receiver': msg_status.value})
        if user_message_entity.type == UserMessageType.INVITATION:
            if msg_status == UserMessageStatus.REJECTED:
                await TeamService.add_team_msg(user_message_entity.receiver_id, user_message_entity.team_id, IdType.USER, MessageLevel.INFO, '拒绝了你的邀请', 'reject your invitation')
                return None
            elif msg_status == UserMessageStatus.ACCEPTED:
                await TeamService.add_team_user(user_message_entity.team_id, user_message_entity.role_id, user_message_entity.receiver_id)
                await TeamService.add_team_msg(user_message_entity.receiver_id, user_message_entity.team_id, IdType.USER, MessageLevel.INFO, '加入了团队', 'join_team')
                return msg_id
        elif user_message_entity.type == UserMessageType.APPLICATION:
            if msg_status == UserMessageStatus.REJECTED:
                await TeamService.add_team_msg(user_sub, user_message_entity.team_id, IdType.USER, MessageLevel.INFO, '拒绝了你的申请', 'reject your application')
                return None
            elif msg_status == UserMessageStatus.ACCEPTED:
                await TeamService.add_team_user(user_message_entity.team_id, user_message_entity.role_id, user_message_entity.sender_id)
                await TeamService.add_team_msg(user_message_entity.sender_id, user_message_entity.team_id, IdType.USER, MessageLevel.INFO, '加入了团队', 'join_team')
                return msg_id
        return None

    @staticmethod
    async def delete_user_messages(
            user_sub: str, msg_id: uuid.UUID) -> Union[None, str]:
        """根据消息标识删除用户消息"""
        try:
            user_message_entity = await UserMessageManager.get_user_message_by_msg_id(msg_id)
            if not user_message_entity:
                raise Exception('用户消息不存在')
            msg_dict = {}
            if user_sub == user_message_entity.sender_id:
                msg_dict['status_to_sender'] = UserMessageStatus.DELETED.value
            if user_sub == user_message_entity.receiver_id:
                msg_dict['status_to_receiver'] = UserMessageStatus.DELETED.value
            if user_sub != user_message_entity.sender_id and user_message_entity.is_to_all:
                action_entity = await RoleManager.get_action_by_team_id_user_sub_and_action(
                    user_sub, user_message_entity.team_id, 'PUT /usr_msg')
                if action_entity:
                    msg_dict['status_to_receiver'] = UserMessageStatus.DELETED.value
            if not msg_dict:
                raise MessagePermissionDeniedException("删除该消息", str(msg_id))
            await UserMessageManager.update_user_message_by_msg_id(
                msg_id, msg_dict)
            return msg_id
        except Exception as e:
            err = "根据消息标识删除用户消息失败"
            logging.exception("[UserMessageService] %s", err)
            raise e
