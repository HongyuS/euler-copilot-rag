# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.

from fastapi import APIRouter, Depends, Query, Body
from typing import Annotated
from uuid import UUID
from data_chain.entities.request_data import (
    ListTeamRequest,
    ListTeamMsgRequest,
    ListTeamUserRequest,
    CreateTeamRequest,
    InviteTeamUserRequest,
    UpdateTeamRequest,
    DetleteTeamUserRequest
)
from data_chain.entities.enum import IdType, MessageLevel
from data_chain.entities.response_data import (
    ListTeamMsg,
    ListTeamResponse,
    ListTeamMsgResponse,
    ListTeamUserResponse,
    CreateTeamResponse,
    UpdateTeamResponse,
    DeleteTeamResponse,
    UpdateTeamUserRoleResponse,
    UpdateTeamAuthorResponse,
    DeleteTeamUserResponse,
    JoinTeamResponse,
    InviteTeamUserResponse
)
from data_chain.apps.service.session_service import get_user_sub, verify_user
from data_chain.apps.service.team_service import TeamService
from data_chain.apps.service.router_service import get_route_info
from data_chain.apps.exceptions import TeamPermissionDeniedException
router = APIRouter(prefix='/team', tags=['Team'])


@router.post('/list', response_model=ListTeamResponse, dependencies=[Depends(verify_user)])
async def list_teams(
    user_sub: Annotated[str, Depends(get_user_sub)],
    action: Annotated[str, Depends(get_route_info)],
    req: Annotated[ListTeamRequest, Body()]
):
    list_team_msg = await TeamService.list_teams(user_sub, req)
    return ListTeamResponse(message='团队列表获取成功', result=list_team_msg)


@router.post('/usr', response_model=ListTeamUserResponse, dependencies=[Depends(verify_user)])
async def list_team_user_by_team_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        req: Annotated[ListTeamUserRequest, Body()]):
    if not (await TeamService.validate_user_action_in_team(user_sub, req.team_id, action)):
        raise TeamPermissionDeniedException('查看该团队成员', str(req.team_id))
    list_team_user_msg = await TeamService.list_team_users(req)
    return ListTeamUserResponse(message='团队成员列表获取成功', result=list_team_user_msg)


@router.post('/msg', response_model=ListTeamMsgResponse, dependencies=[Depends(verify_user)])
async def list_team_msg_by_team_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        req: Annotated[ListTeamMsgRequest, Body()]):
    if not (await TeamService.validate_user_action_in_team(user_sub, req.team_id, action)):
        raise TeamPermissionDeniedException('查看该团队消息', str(req.team_id))
    list_team_msg = await TeamService.list_team_msg_by_team_id(req)
    return ListTeamMsgResponse(message='团队消息列表获取成功', result=list_team_msg)


@router.post('', response_model=CreateTeamResponse, dependencies=[Depends(verify_user)])
async def create_team(user_sub: Annotated[str, Depends(get_user_sub)],
                      action: Annotated[str, Depends(get_route_info)],
                      req: Annotated[CreateTeamRequest, Body()]):
    team_id = await TeamService.create_team(user_sub, req)
    return CreateTeamResponse(message='团队创建成功', result=team_id)


@router.post('/invitation', response_model=InviteTeamUserResponse, dependencies=[Depends(verify_user)])
async def invite_team_user_by_user_sub(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        team_id: Annotated[UUID, Query(alias="teamId")],
        req: Annotated[InviteTeamUserRequest, Body()]):
    if not (await TeamService.validate_user_action_in_team(user_sub, team_id, action)):
        raise TeamPermissionDeniedException('邀请该团队成员', str(team_id))
    user_subs_invite = await TeamService.invite_team_users(user_sub, team_id, req)
    return InviteTeamUserResponse(message='团队成员邀请成功', result=user_subs_invite)


@router.post('/application', response_model=JoinTeamResponse, dependencies=[Depends(verify_user)])
async def apply_to_join_team(
        user_sub: Annotated[str, Depends(get_user_sub)],
        team_id: Annotated[UUID, Query(alias="teamId")]):
    user_sub = await TeamService.apply_to_join_team(user_sub, team_id)
    return JoinTeamResponse(message='团队加入申请发送成功', result=user_sub)


@router.put('', response_model=UpdateTeamResponse, dependencies=[Depends(verify_user)])
async def update_team_by_team_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        team_id: Annotated[UUID, Query(alias="teamId")],
        req: Annotated[UpdateTeamRequest, Body()]):
    if not (await TeamService.validate_user_action_in_team(user_sub, team_id, action)):
        raise TeamPermissionDeniedException('修改该团队', str(team_id))
    team_id = await TeamService.update_team_by_team_id(team_id, req)
    await TeamService.add_team_msg(user_sub, team_id, IdType.TEAM, MessageLevel.INFO, '更新了团队信息', 'team info updated')
    return UpdateTeamResponse(message='团队更新成功', result=team_id)


@router.put('/usr', response_model=UpdateTeamUserRoleResponse, dependencies=[Depends(verify_user)])
async def update_usr_role_by_team_id_and_user_sub(
    user_sub: Annotated[str, Depends(get_user_sub)],
    action: Annotated[str, Depends(get_route_info)],
    team_id: Annotated[UUID, Query(alias="teamId")],
    target_user_sub: Annotated[str, Query(alias="targetUserSub")],
    role_id: Annotated[UUID, Query(alias="roleId")],
):
    if not (await TeamService.validate_user_action_in_team(user_sub, team_id, action)):
        raise TeamPermissionDeniedException('修改该团队成员角色', str(team_id))
    target_user_sub = await TeamService.update_team_user_role_by_team_id_and_user_sub(user_sub, team_id, target_user_sub, role_id)
    await TeamService.add_team_msg(user_sub, team_id, IdType.USER, MessageLevel.INFO, '更新了成员{targetUserName}的角色', 'user {targetUserName} role updated', targetUserName=target_user_sub)
    return UpdateTeamUserRoleResponse(message='团队成员角色更新成功', result=target_user_sub)


@router.put('/author', response_model=UpdateTeamAuthorResponse, dependencies=[Depends(verify_user)])
async def update_team_author_by_team_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        target_user_sub: Annotated[str, Query(alias="targetUserSub")],
        team_id: Annotated[UUID, Query(alias="teamId")]):
    if not (await TeamService.validate_user_action_in_team(user_sub, team_id, action)):
        raise TeamPermissionDeniedException('转让该团队', str(team_id))
    team_id = await TeamService.update_team_author_by_team_id(user_sub, team_id, target_user_sub)
    await TeamService.add_team_msg(user_sub, team_id, IdType.USER, MessageLevel.INFO, '将团队转让给了{targetUserName}', 'team transferred to {targetUserName}', targetUserName=target_user_sub)
    return UpdateTeamAuthorResponse(message='团队转让成功', result=team_id)


@router.delete('', response_model=DeleteTeamResponse, dependencies=[Depends(verify_user)])
async def delete_team_by_team_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        team_id: Annotated[UUID, Query(alias="teamId")]):
    if not (await TeamService.validate_user_action_in_team(user_sub, team_id, action)):
        raise TeamPermissionDeniedException('删除该团队', str(team_id))
    team_id = await TeamService.soft_delete_team_by_team_id(team_id)
    return DeleteTeamResponse(message='团队删除成功', result=team_id)


@router.delete('/usr', response_model=DeleteTeamUserResponse, dependencies=[Depends(verify_user)])
async def delete_team_user_by_team_id_and_user_subs(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        req: Annotated[DetleteTeamUserRequest, Body()]):
    flag = await TeamService.validate_user_action_in_team(user_sub, req.team_id, action)
    if len(req.user_subs) == 1 and req.user_subs[0] == user_sub:
        flag = True
    if not flag:
        raise TeamPermissionDeniedException('删除该团队成员', str(req.team_id))
    user_subs = await TeamService.delete_team_user_by_team_id_and_user_subs(req.team_id, req.user_subs)
    if len(req.user_subs) == 1 and req.user_subs[0] == user_sub:
        await TeamService.add_team_msg(user_sub, req.team_id,IdType.TEAM, MessageLevel.INFO, '退出了团队', 'left the team')
    else:
        for target_user_sub in req.user_subs:
            await TeamService.add_team_msg(user_sub, req.team_id, IdType.USER, MessageLevel.INFO, '将成员{targetUserName}移出了团队', 'user {targetUserName} removed from team', targetUserName=target_user_sub)
    return DeleteTeamUserResponse(message='团队成员删除成功', result=user_subs)
