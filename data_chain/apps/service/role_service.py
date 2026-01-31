# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
import copy
import uuid
from typing import Union
from data_chain.logger.logger import logger as logging
from data_chain.entities.request_data import (
    ListRoleRequest,
    CreateRoleRequest,
    UpdateRoleRequest
)
from data_chain.entities.response_data import (
    Action,
    TypeAction,
    ListActionMsg,
    GetUserRoleMsg,
    Role,
    ListRoleMsg
)
from data_chain.entities.enum import (
    ActionType,
    RoleActionStatus,
    DeafaultRole,
    LanguageType
)
from data_chain.entities.common import actions
from data_chain.stores.database.database import RoleEntity, RoleActionEntity
from data_chain.apps.base.convertor import Convertor
from data_chain.manager.team_manager import TeamManager
from data_chain.manager.role_manager import RoleManager


class RoleService:
    """团队服务"""
    @staticmethod
    async def validate_user_action_to_role(
            user_sub: str, role_id: uuid.UUID, action: str) -> bool:
        """验证用户对角色的操作权限"""
        try:
            role_entity = await RoleManager.get_role_by_id(role_id)
            if not role_entity:
                raise Exception('角色不存在')

            action_entity = await RoleManager.get_action_by_team_id_user_sub_and_action(
                user_sub, role_entity.team_id, action)
            if action_entity is None:
                return False
            return True
        except Exception as e:
            err = "验证用户对角色的操作权限失败"
            logging.exception("[RoleService] %s", err)
            raise e

    @staticmethod
    async def get_all_actions() -> list[str]:
        """获取所有操作列表"""
        tmp_actions = []
        for action in actions:
            tmp_actions.append(action['action'])
        return tmp_actions

    @staticmethod
    async def get_type_actions(language: LanguageType) -> list[TypeAction]:
        """获取所有操作列表"""
        action_dict = {}
        for action in actions:
            if action['type'][language] not in action_dict:
                action_dict[action['type'][language]] = []
            action_dict[action['type'][language]].append(
                Action(
                    actionName=action['name'][language],
                    action=action['action'])
            )
        logging.debug(f"action_dict: {action_dict}")
        action_strings = [member.value for member in ActionType]
        type_actions = []
        for action_string in action_strings:
            if action_string in action_dict:
                type_actions.append(
                    TypeAction(actionType=ActionType(action_string),
                               actions=action_dict[action_string])
                )
        return type_actions

    @staticmethod
    async def list_actions(language: LanguageType) -> ListActionMsg:
        """获取所有操作列表"""
        try:
            type_actions = await RoleService.get_type_actions(language)
            return ListActionMsg(TypeActions=type_actions)
        except Exception as e:
            err = "获取所有操作列表失败"
            logging.exception("[RoleService] %s", err)
            raise e

    @staticmethod
    async def get_user_role_in_team(user_sub: str, team_id: uuid.UUID) -> GetUserRoleMsg:
        """获取用户在团队中的角色"""
        try:
            team_user_entity = await TeamManager.get_team_user_by_user_sub_and_team_id(
                user_sub, team_id)
            if not team_user_entity:
                raise Exception('用户不在该团队中')
            user_role_entity = await RoleManager.get_user_role_by_user_sub_and_team_id(
                user_sub, team_id)
            role_entity = await RoleManager.get_role_by_id(user_role_entity.role_id)
            return GetUserRoleMsg(
                userSub=user_sub,
                roleId=role_entity.id,
                roleName=role_entity.name,
                isOwner=role_entity.name == DeafaultRole.OWENER.value
            )
        except Exception as e:
            err = "获取用户在团队中的角色失败"
            logging.exception("[RoleService] %s", err)
            raise e

    @staticmethod
    async def list_roles(req: ListRoleRequest) -> ListRoleMsg:
        """根据团队标识获取角色列表"""
        try:
            team_entity = await TeamManager.get_team_by_id(req.team_id)
            if not team_entity:
                raise Exception('团队不存在')
            total, role_entities = await RoleManager.list_roles(req)
            roles = []
            type_actions = await RoleService.get_type_actions(req.language)
            role_action_entities = await RoleManager.list_role_actions_by_role_ids(
                [role_entity.id for role_entity in role_entities])
            role_action_dict = {}
            for role_action_entity in role_action_entities:
                if role_action_entity.role_id not in role_action_dict:
                    role_action_dict[role_action_entity.role_id] = set()
                role_action_dict[role_action_entity.role_id].add(
                    role_action_entity.action)
            for role_entity in role_entities:
                if role_entity.name == DeafaultRole.OWENER.value:
                    continue
                role = await Convertor.convert_role_entity_to_role(role_entity)
                if req.is_editable:
                    type_actions_cp = copy.deepcopy(type_actions)
                    for type_action in type_actions_cp:
                        for action in type_action.actions:
                            if (role_entity.id in role_action_dict and
                                    action.action in role_action_dict[role_entity.id]):
                                action.is_used = True
                    role.type_actions = type_actions_cp
                roles.append(role)
            return ListRoleMsg(total=total, roles=roles)
        except Exception as e:
            err = "根据团队标识获取角色列表失败"
            logging.exception("[RoleService] %s", err)
            raise e

    @staticmethod
    async def create_role(team_id: uuid.UUID, req: CreateRoleRequest) -> uuid.UUID:
        """创建角色"""
        try:
            existing_role_entity = await RoleManager.get_role_by_role_name_and_team_id(
                req.role_name, team_id)
            if existing_role_entity:
                req.role_name = f"{req.role_name}_{str(uuid.uuid4())[:16]}"
            role_entity = RoleEntity(
                team_id=team_id,
                name=req.role_name,
            )
            role_entity = await RoleManager.add_role(role_entity)
            role_id = role_entity.id
            role_action_entities = []
            actions = await RoleService.get_all_actions()
            actions_set = set(actions)
            for action in req.actions:
                if action not in actions_set:
                    continue
                role_action_entities.append(
                    RoleActionEntity(role_id=role_id, action=action)
                )
            await RoleManager.add_role_actions(role_action_entities)
            return role_id
        except Exception as e:
            err = "创建角色失败"
            logging.exception("[RoleService] %s", err)
            raise e

    async def update_role(role_id: uuid.UUID, req: UpdateRoleRequest) -> uuid.UUID:
        role_entity = await RoleManager.get_role_by_id(role_id)
        logging.error(req)
        if req.role_name is not None:
            existing_role_entity = await RoleManager.get_role_by_role_name_and_team_id(
                req.role_name, role_entity.team_id)
            if existing_role_entity and existing_role_entity.id != role_id:
                raise Exception('角色名称已存在')
            await RoleManager.update_role_by_id(role_id, {'name': req.role_name})
        if req.actions is not None:
            await RoleManager.update_role_actions_by_role_id(
                role_id, {'status': RoleActionStatus.DELETED.value})
            role_action_entities = []
            actions = await RoleService.get_all_actions()
            actions_set = set(actions)
            for action in req.actions:
                if action not in actions_set:
                    continue
                role_action_entities.append(
                    RoleActionEntity(role_id=role_id, action=action)
                )
            await RoleManager.add_role_actions(role_action_entities)
            return role_id

    async def delete_role(role_id: uuid.UUID) -> uuid.UUID:
        try:
            await RoleManager.update_role_by_id(role_id, {'status': RoleActionStatus.DELETED.value})
            await RoleManager.update_role_actions_by_role_id(
                role_id, {'status': RoleActionStatus.DELETED.value})
            return role_id
        except Exception as e:
            err = "删除角色失败"
            logging.exception("[RoleService] %s", err)
            raise e
