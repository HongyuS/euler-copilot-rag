# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.

from fastapi import APIRouter, Depends, Query, Body
from typing import Annotated
from uuid import UUID
from data_chain.entities.enum import UserMessageType, UserStatus, UserMessageStatus
from data_chain.entities.request_data import (
    ListUserMessageRequest
)
from data_chain.entities.response_data import (
    IsUserMessageExistResponse,
    ListUserMessageResponse,
    UpdateUserMessageResponse,
    DeleteUserMessageResponse
)
from data_chain.apps.service.user_message_service import UserMessageService
from data_chain.apps.service.session_service import get_user_sub, verify_user
from data_chain.apps.service.router_service import get_route_info
router = APIRouter(prefix='/usr_msg', tags=['User Message'])


@router.get('/exist', response_model=IsUserMessageExistResponse, dependencies=[Depends(verify_user)])
async def is_user_message_exist(
    user_sub: Annotated[str, Depends(get_user_sub)],
    team_id: Annotated[UUID, Query(alias="teamId")],
    msg_type: Annotated[UserMessageType, Query(alias="msgType")],
):
    is_exist = await UserMessageService.is_user_message_exist(user_sub, team_id, msg_type)
    return IsUserMessageExistResponse(message='用户消息存在性检查成功', result=is_exist)


@router.post('/list', response_model=ListUserMessageResponse, dependencies=[Depends(verify_user)])
async def list_user_msgs_by_user_sub(
    user_sub: Annotated[str, Depends(get_user_sub)],
    req: Annotated[ListUserMessageRequest, Body()]
):
    list_user_message = await UserMessageService.list_user_messages(user_sub, req)
    return ListUserMessageResponse(message='用户消息列表获取成功', result=list_user_message)


@router.put('', response_model=UpdateUserMessageResponse, dependencies=[Depends(verify_user)])
async def update_user_msg_by_msg_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        msg_id: Annotated[UUID, Query(alias="msgId")],
        msg_status: Annotated[UserMessageStatus, Query(alias="msgStatus")]):
    msg_id = await UserMessageService.update_user_message(user_sub, msg_id, msg_status)
    return UpdateUserMessageResponse(message='用户消息更新成功', result=msg_id)


@router.delete('', response_model=DeleteUserMessageResponse, dependencies=[Depends(verify_user)])
async def delete_user_msg_by_msg_ids(
        user_sub: Annotated[str, Depends(get_user_sub)],
        msg_id: Annotated[UUID, Query(alias="msgId")]):
    msg_id = await UserMessageService.delete_user_messages(user_sub, msg_id)
    return DeleteUserMessageResponse(message='用户消息删除成功', result=msg_id)
