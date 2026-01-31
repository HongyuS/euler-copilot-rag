# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.

from fastapi import APIRouter, Depends, Query, Body
from typing import Annotated
from uuid import UUID
from data_chain.entities.enum import LanguageType, IdType, MessageLevel
from data_chain.entities.request_data import (
    ListRoleRequest,
    CreateRoleRequest,
    UpdateRoleRequest
)

from data_chain.entities.response_data import (
    ListActionResponse,
    GetUserRoleResponse,
    ListRoleResponse,
    CreateRoleResponse,
    UpdateRoleResponse,
    DeleteRoleResponse
)
from data_chain.apps.service.role_service import RoleService
from data_chain.apps.service.team_service import TeamService
from data_chain.apps.service.session_service import get_user_sub, verify_user
from data_chain.apps.service.router_service import get_route_info
from data_chain.apps.exceptions import (
    RolePermissionDeniedException,
    TeamPermissionDeniedException
)
router = APIRouter(prefix='/role', tags=['Role'])


@router.get('/action', response_model=ListActionResponse, dependencies=[Depends(verify_user)])
async def list_actions(
    user_sub: Annotated[str, Depends(get_user_sub)],
    language: Annotated[LanguageType | None,
                        Query(alias="language")] = LanguageType.CHINESE
):
    list_action_msg = await RoleService.list_actions(language)
    return ListActionResponse(message='操作列表获取成功', result=list_action_msg)


@router.get('', response_model=GetUserRoleResponse, dependencies=[Depends(verify_user)])
async def get_user_role(
    user_sub: Annotated[str, Depends(get_user_sub)],
    team_id: Annotated[UUID, Query(alias="teamId")]
):
    user_role_msg = await RoleService.get_user_role_in_team(user_sub, team_id)
    return GetUserRoleResponse(message='用户角色获取成功', result=user_role_msg)


@router.post('/list', response_model=ListRoleResponse, dependencies=[Depends(verify_user)])
async def list_roles(
    user_sub: Annotated[str, Depends(get_user_sub)],
    action: Annotated[str, Depends(get_route_info)],
    req: Annotated[ListRoleRequest, Body()],
):
    if not (await TeamService.validate_user_action_in_team(user_sub, req.team_id, action)):
        raise RolePermissionDeniedException("查看该团队角色", str(req.team_id))
    list_role_msg = await RoleService.list_roles(req)
    await TeamService.add_team_msg(user_sub, req.team_id, IdType.TEAM, MessageLevel.INFO, '查看了角色列表', 'role list viewed')
    return ListRoleResponse(message='角色列表获取成功', result=list_role_msg)


@router.post('', response_model=CreateRoleResponse, dependencies=[Depends(verify_user)])
async def create_role(user_sub: Annotated[str, Depends(get_user_sub)],
                      action: Annotated[str, Depends(get_route_info)],
                      team_id: Annotated[UUID, Query(alias="teamId")],
                      req: Annotated[CreateRoleRequest, Body()]):
    if not (await TeamService.validate_user_action_in_team(user_sub, team_id, action)):
        raise RolePermissionDeniedException("创建该团队角色", str(team_id))
    role_id = await RoleService.create_role(team_id, req)
    await TeamService.add_team_msg(user_sub, role_id, IdType.ROLE, MessageLevel.INFO, '创建了角色{roleName}', 'created role {roleName}')
    return CreateRoleResponse(message='角色创建成功', result=role_id)


@router.put('', response_model=UpdateRoleResponse, dependencies=[Depends(verify_user)])
async def update_role_by_role_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        role_id: Annotated[UUID, Query(alias="roleId")],
        req: Annotated[UpdateRoleRequest, Body()]):
    if not (await RoleService.validate_user_action_to_role(user_sub, role_id, action)):
        raise RolePermissionDeniedException("修改该团队角色", str(role_id))
    role_id = await RoleService.update_role(role_id, req)
    await TeamService.add_team_msg(user_sub, role_id, IdType.ROLE, MessageLevel.INFO, '更新了角色{roleName}', 'updated role {roleName}')
    return UpdateRoleResponse(message='角色更新成功', result=role_id)


@router.delete('', response_model=DeleteRoleResponse, dependencies=[Depends(verify_user)])
async def delete_role_by_role_ids(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        role_id: Annotated[UUID, Query(alias="roleId")]):
    if not (await RoleService.validate_user_action_to_role(user_sub, role_id, action)):
        raise RolePermissionDeniedException("删除该团队角色", str(role_id))
    role_id = await RoleService.delete_role(role_id)
    await TeamService.add_team_msg(user_sub, role_id, IdType.ROLE, MessageLevel.INFO, '删除了角色{roleName}', 'deleted role {roleName}')
    return DeleteRoleResponse(message='角色删除成功', result=role_id)
