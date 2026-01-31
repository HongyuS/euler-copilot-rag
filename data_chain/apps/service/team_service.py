# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
import uuid
from typing import Union, Any
from data_chain.logger.logger import logger as logging
from data_chain.apps.exceptions import (
    TeamPermissionDeniedException,
    PermissionDeniedException
)
from data_chain.entities.request_data import (
    ListTeamUserRequest,
    ListTeamMsgRequest,
    ListTeamRequest,
    CreateTeamRequest,
    InviteTeamUserRequest
)
from data_chain.entities.response_data import (
    TeamUser,
    ListTeamMsg,
    ListTeamMsgMsg,
    ListTeamUserMsg
)
from data_chain.entities.enum import (
    TeamType,
    TeamStatus,
    TeamUserStaus,
    UserRoleStatus,
    UserMessageStatus,
    UserMessageType,
    DeafaultRole,
    IdType,
    MessageLevel,
    TaskType
)
from data_chain.entities.enum import IdType
from data_chain.entities.common import default_roles
from data_chain.stores.database.database import TeamEntity
from data_chain.apps.base.convertor import Convertor
from data_chain.manager.team_manager import TeamManager
from data_chain.manager.team_message_manager import TeamMessageManager
from data_chain.manager.user_manager import UserManager
from data_chain.manager.user_message_manager import UserMessageManager
from data_chain.manager.role_manager import RoleManager
from data_chain.manager.knowledge_manager import KnowledgeBaseManager
from data_chain.manager.document_manager import DocumentManager
from data_chain.manager.role_manager import RoleManager
from data_chain.manager.chunk_manager import ChunkManager
from data_chain.manager.dataset_manager import DatasetManager
from data_chain.manager.testing_manager import TestingManager
from data_chain.manager.testcase_manager import TestCaseManager
from data_chain.manager.task_manager import TaskManager
from data_chain.apps.service.knwoledge_base_service import KnowledgeBaseService


class TeamService:
    """团队服务"""
    @staticmethod
    async def validate_user_action_in_team(
            user_sub: str, team_id: uuid.UUID, action: str) -> bool:
        """验证用户在团队中的操作权限"""
        try:
            action_entity = await RoleManager.get_action_by_team_id_user_sub_and_action(user_sub, team_id, action)
            if action_entity is None:
                return False
            return True
        except Exception as e:
            err = "验证用户在团队中的操作权限失败"
            logging.exception("[TeamService] %s", err)
            raise e

    @staticmethod
    async def list_teams(user_sub: str, req: ListTeamRequest) -> ListTeamMsg:
        """列出团队"""
        if req.team_type == TeamType.MYCREATED:
            total, team_entities = await TeamManager.list_team_mycreated_by_user_sub(user_sub, req)
        elif req.team_type == TeamType.MYJOINED:
            total, team_entities = await TeamManager.list_team_myjoined_by_user_sub(user_sub, req)
        elif req.team_type == TeamType.PUBLIC:
            total, team_entities = await TeamManager.list_public_team(user_sub, req)
        else:
            total_mycreated, team_entities_mycreated = await TeamManager.list_team_mycreated_by_user_sub(user_sub, req)
            total_myjoined, team_entities_myjoined = await TeamManager.list_team_myjoined_by_user_sub(user_sub, req)
            total = total_mycreated + total_myjoined
            team_entities = team_entities_mycreated + team_entities_myjoined
            team_entities.sort(key=lambda x: x.created_time, reverse=True)
        teams = []
        team_ids = [team_entity.id for team_entity in team_entities]
        team_entites_myjoined = await TeamManager.list_team_myjoined_by_user_sub_and_team_ids(user_sub, team_ids)
        team_ids_myjoined = [
            team_entity.id for team_entity in team_entites_myjoined]
        team_entities_mycreated = await TeamManager.list_team_mycreated_by_user_sub_and_team_ids(user_sub, team_ids)
        team_ids_mycreated = [
            team_entity.id for team_entity in team_entities_mycreated]
        for team_entity in team_entities:
            team = await Convertor.convert_team_entity_to_team(team_entity)
            if team_entity.id in team_ids_mycreated:
                team.is_my_created = True
            elif team_entity.id in team_ids_myjoined:
                team.is_my_joined = True
            teams.append(team)
        return ListTeamMsg(total=total, teams=teams)

    @staticmethod
    async def list_team_users(req: ListTeamUserRequest) -> ListTeamUserMsg:
        """列出团队成员"""
        total, user_entities = await TeamManager.list_team_user_by_team_id(req)
        user_subs = [
            user_entity.id for user_entity in user_entities]
        user_role_entities = await RoleManager.list_user_roles_by_team_id_and_user_subs(
            req.team_id, user_subs)
        role_ids = list(
            set([user_role_entity.role_id for user_role_entity in user_role_entities]))
        role_entities = await RoleManager.list_roles_by_role_ids(role_ids)
        user_role_dict = {
            user_role_entity.user_id: user_role_entity for user_role_entity in user_role_entities}
        role_dict = {
            role_entity.id: role_entity for role_entity in role_entities}
        team_users = []
        # 先加入创建者
        for user_entity in user_entities:
            user_role = user_role_dict.get(user_entity.id)
            role = role_dict.get(user_role.role_id) if user_role else None
            logging.error(role.name)
            if role and role.name == DeafaultRole.OWENER.value:
                team_user = await Convertor.convert_user_entity_and_role_entity_to_team_user(user_entity, role)
                team_user.is_editable = False
                team_users.append(team_user)
                break
        # 再加入管理员
        admin_team_users = []
        for user_entity in user_entities:
            user_role = user_role_dict.get(user_entity.id)
            role = role_dict.get(user_role.role_id) if user_role else None
            if role and role.name == DeafaultRole.ADMINISTRATOR.value:
                team_user = await Convertor.convert_user_entity_and_role_entity_to_team_user(user_entity, role)
                admin_team_users.append((team_user, user_role.created_time))
        admin_team_users.sort(key=lambda x: x[1], reverse=False)
        team_users.extend([item[0] for item in admin_team_users])
        # 最后加入普通成员
        normal_team_users = []
        for user_entity in user_entities:
            user_role = user_role_dict.get(user_entity.id)
            role = role_dict.get(user_role.role_id) if user_role else None
            if role and role.name != DeafaultRole.OWENER.value and role.name != DeafaultRole.ADMINISTRATOR.value:
                team_user = await Convertor.convert_user_entity_and_role_entity_to_team_user(user_entity, role)
                normal_team_users.append((team_user, user_role.created_time))
        normal_team_users.sort(key=lambda x: x[1], reverse=False)
        team_users.extend([item[0] for item in normal_team_users])
        return ListTeamUserMsg(total=total, teamUsers=team_users)

    @staticmethod
    async def add_team_msg(user_sub: str, id: uuid.UUID, id_type: IdType, message_level: MessageLevel, zh_message: str, en_message: str, ** kwargs: dict[str, Any]) -> uuid.UUID:
        """添加团队消息"""
        try:
            if id_type == IdType.TEAM:
                team_entity = await TeamManager.get_team_by_id(id)
                if team_entity is None:
                    err = f"团队不存在，团队ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                team_id = team_entity.id
            elif id_type == IdType.ROLE:
                role_entity = await RoleManager.get_role_by_id(id)
                if role_entity is None:
                    err = f"角色不存在，角色ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                team_entity = await TeamManager.get_team_by_id(role_entity.team_id)
                team_id = team_entity.id
                zh_message = zh_message.format(roleName=role_entity.name)
                en_message = en_message.format(roleName=role_entity.name)
            elif id_type == IdType.USER:
                team_entity = await TeamManager.get_team_by_id(id)
                if team_entity is None:
                    err = f"团队不存在，团队ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                team_id = team_entity.id
                if 'targetUserName' in kwargs:
                    zh_message = zh_message.format(
                        targetUserName=kwargs['targetUserName'])
                    en_message = en_message.format(
                        targetUserName=kwargs['targetUserName'])
            elif id_type == IdType.MSG:
                team_msg_entity = await UserMessageManager.get_user_message_by_msg_id(id)
                if team_msg_entity is None:
                    err = f"消息不存在，消息ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                team_entity = await TeamManager.get_team_by_id(team_msg_entity.team_id)
                team_id = team_entity.id
                zh_message = zh_message.format(
                    targetUserName=team_msg_entity.receiver_id)
                en_message = en_message.format(
                    targetUserName=team_msg_entity.receiver_id)
            elif id_type == IdType.KNOWLEDGE_BASE:
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(id)
                if kb_entity is None:
                    err = f"知识库不存在，知识库ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                team_id = kb_entity.team_id
                zh_message = zh_message.format(kbName=kb_entity.name)
                en_message = en_message.format(kbName=kb_entity.name)
            elif id_type == IdType.DOCUMENT:
                doc_entity = await DocumentManager.get_document_by_doc_id(id)
                if doc_entity is None:
                    err = f"文档不存在，文档ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(doc_entity.kb_id)
                team_id = kb_entity.team_id
                zh_message = zh_message.format(
                    kbName=kb_entity.name, documentName=doc_entity.name)
                en_message = en_message.format(
                    kbName=kb_entity.name, documentName=doc_entity.name)
            elif id_type == IdType.CHUNK:
                chunk_entity = await ChunkManager.get_chunk_by_chunk_id(id)
                if chunk_entity is None:
                    err = f"分片不存在，分片ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                doc_entity = await DocumentManager.get_document_by_doc_id(chunk_entity.doc_id)
                if doc_entity is None:
                    err = f"文档不存在，文档ID: {chunk_entity.doc_id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(doc_entity.kb_id)
                if kb_entity is None:
                    err = f"知识库不存在，知识库ID: {doc_entity.kb_id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                team_id = kb_entity.team_id
                zh_message = zh_message.format(
                    kbName=kb_entity.name, documentName=doc_entity.name)
                en_message = en_message.format(
                    kbName=kb_entity.name, documentName=doc_entity.name)
            elif id_type == IdType.DATASET:
                dataset_entity = await DatasetManager.get_dataset_by_dataset_id(id)
                if dataset_entity is None:
                    err = f"数据集不存在，数据集ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(dataset_entity.kb_id)
                team_id = kb_entity.team_id
                zh_message = zh_message.format(
                    kbName=kb_entity.name, datasetName=dataset_entity.name)
                en_message = en_message.format(
                    kbName=kb_entity.name, datasetName=dataset_entity.name)
            elif id_type == IdType.DATASET_DATA:
                dataset_entity = await DatasetManager.get_dataset_by_data_id(id)
                if dataset_entity is None:
                    err = f"数据集不存在，数据集ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(dataset_entity.kb_id)
                team_id = kb_entity.team_id
                zh_message = zh_message.format(
                    kbName=kb_entity.name, datasetName=dataset_entity.name)
                en_message = en_message.format(
                    kbName=kb_entity.name, datasetName=dataset_entity.name)
            elif id_type == IdType.TESTING:
                testing_entity = await TestingManager.get_testing_by_testing_id(id)
                if testing_entity is None:
                    err = f"测试不存在，测试ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(testing_entity.kb_id)
                team_id = kb_entity.team_id
                zh_message = zh_message.format(
                    kbName=kb_entity.name, testingName=testing_entity.name)
                en_message = en_message.format(
                    kbName=kb_entity.name, testingName=testing_entity.name)
            elif id_type == IdType.TEST_CASE:
                testcase_entity = await TestCaseManager.get_test_case_by_id(id)
                if testcase_entity is None:
                    err = f"测试用例不存在，测试用例ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                testing_entity = await TestingManager.get_testing_by_testing_id(testcase_entity.testing_id)
                if testing_entity is None:
                    err = f"测试不存在，测试ID: {testcase_entity.testing_id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(testing_entity.kb_id)
                team_id = kb_entity.team_id
                zh_message = zh_message.format(
                    kbName=kb_entity.name, testingName=testing_entity.name)
                en_message = en_message.format(
                    kbName=kb_entity.name, testingName=testing_entity.name)
            elif id_type == IdType.TASK:
                task_entity = await TaskManager.get_task_by_task_id(id)
                if task_entity is None:
                    err = f"任务不存在，任务ID: {id}"
                    logging.warning("[TeamService] %s", err)
                    return None
                team_id = task_entity.team_id
                # 根据任务类型处理不同的消息格式
                if task_entity.type in [TaskType.DATASET_EXPORT.value, TaskType.DATASET_IMPORT.value, TaskType.DATASET_GENERATE.value]:
                    # 数据集相关任务，需要获取数据集信息
                    dataset_entity = await DatasetManager.get_dataset_by_dataset_id(task_entity.op_id)
                    if dataset_entity is None:
                        err = f"数据集不存在，数据集ID: {task_entity.op_id}"
                        logging.warning("[TeamService] %s", err)
                        return None
                    kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(dataset_entity.kb_id)
                    zh_message = zh_message.format(
                        kbName=kb_entity.name, datasetName=dataset_entity.name)
                    en_message = en_message.format(
                        kbName=kb_entity.name, datasetName=dataset_entity.name)
                else:
                    # 其他类型任务，只使用任务名称
                    zh_message = zh_message.format(
                        taskName=task_entity.op_name or str(task_entity.id))
                    en_message = en_message.format(
                        taskName=task_entity.op_name or str(task_entity.id))
            team_msg_entity = await Convertor.convert_user_sub_team_id_and_message_to_team_message_entity(
                user_sub, team_id, message_level, zh_message, en_message)
            team_msg_entity = await TeamMessageManager.add_team_msg(team_msg_entity)
            return team_msg_entity.id
        except Exception as e:
            err = "添加团队消息失败"
            logging.exception("[TeamService] %s", err)
            raise e

    @staticmethod
    async def list_team_msg_by_team_id(req: ListTeamMsgRequest) -> ListTeamMsgMsg:
        """列出团队消息"""
        total, team_msg_entities = await TeamMessageManager.list_team_msg_by_team_id(req)
        team_msgs = []
        for team_msg_entity in team_msg_entities:
            team_msg = await Convertor.convert_team_message_entity_to_team_message(req.language, team_msg_entity)
            team_msgs.append(team_msg)
        return ListTeamMsgMsg(total=total, teamMsgs=team_msgs)

    @staticmethod
    async def create_team(user_sub: str, req: CreateTeamRequest) -> uuid.UUID:
        """创建团队"""
        try:
            user_entity = await UserManager.get_user_by_id(user_sub)
            team_entity = await Convertor.convert_create_team_request_to_team_entity(user_sub, user_entity.name, req)
            team_entity = await TeamManager.add_team(team_entity)
            team_user_entity = await Convertor.convert_user_sub_and_team_id_to_team_user_entity(user_sub, team_entity.id)
            await TeamManager.add_team_user(team_user_entity)
            creator_role_id = ''
            for role_dict in default_roles:
                role_entity = await Convertor.convert_default_role_dict_to_role_entity(team_entity.id, role_dict)
                role_entity = await RoleManager.add_role(role_entity)
                if role_entity.name == DeafaultRole.OWENER.value:
                    creator_role_id = role_entity.id
                role_action_entities = await Convertor.convert_default_role_action_dicts_to_role_action_entities(role_entity.id, role_dict['actions'])
                await RoleManager.add_role_actions(role_action_entities)
            user_role_entity = await Convertor.convert_user_sub_role_id_and_team_id_to_user_role_entity(
                user_sub, creator_role_id, team_entity.id)
            await RoleManager.add_user_role(user_role_entity)
            return team_entity.id
        except Exception as e:
            err = "创建团队失败"
            logging.exception("[TeamService] %s", err)
            raise e

    @staticmethod
    async def invite_team_users(user_sub: str, team_id: uuid.UUID, req: InviteTeamUserRequest) -> list[str]:
        """邀请团队成员"""
        """增加多条用户邀请的信息"""
        team_entity = await TeamManager.get_team_by_id(team_id)
        if team_entity is None:
            err = "邀请团队成员失败, 团队不存在"
            logging.exception("[TeamService] %s", err)
            raise Exception("邀请团队成员失败, 团队不存在")
        user_subs_invite = []
        for invite_user in req.invite_users:
            user_subs_invite.append(invite_user.user_sub)
        team_user_entities = await TeamManager.get_team_user_by_subs_and_team_id(user_subs_invite, team_id)
        exist_user_subs = []
        for team_user in team_user_entities:
            exist_user_subs.append(team_user.user_id)
        user_subs_invite = list(set(user_subs_invite) - set(exist_user_subs))
        if not user_subs_invite:
            return []
        user_role = []
        for invite_user in req.invite_users:
            if invite_user.user_sub in user_subs_invite:
                user_role.append((invite_user.user_sub, invite_user.role_id))
        try:
            user_message_entities = []
            for user_sub_invite, role_id in user_role:
                user_message_entity = await Convertor.convert_user_sub_team_id_role_id_and_receiver_sub_to_user_message_entity(
                    user_sub, team_id, team_entity.name, role_id, user_sub_invite, False, "", UserMessageType.INVITATION.value)
                user_message_entities.append(user_message_entity)
            index = 0
            while index < len(user_message_entities):
                await UserMessageManager.add_user_messages(user_message_entities[index:index+1024])
                index += 1024
            return user_subs_invite
        except Exception as e:
            err = "邀请团队成员失败"
            logging.exception("[TeamService] %s", err)
            raise e

    @staticmethod
    async def apply_to_join_team(user_sub: str, team_id: uuid.UUID) -> str:
        """用户申请加入团队"""
        team_entity = await TeamManager.get_team_by_id(team_id)
        if team_entity is None or not team_entity.is_public:
            err = "用户申请加入团队失败, 团队不存在或不是公开团队"
            logging.exception("[TeamService] %s", err)
            raise Exception("用户申请加入团队失败, 团队不存在或不是公开团队")
        try:
            member_role_entity = await RoleManager.get_role_by_role_name_and_team_id(
                DeafaultRole.MEMBER.value, team_id)
            if member_role_entity is None:
                err = "用户申请加入团队失败, 角色不存在"
                logging.exception("[TeamService] %s", err)
                raise Exception("用户申请加入团队失败, 角色不存在")
            user_message_entity = await Convertor.convert_user_sub_team_id_role_id_and_receiver_sub_to_user_message_entity(
                user_sub, team_id, team_entity.name, member_role_entity.id, "", True, "", UserMessageType.APPLICATION.value)
            user_message_entity = await UserMessageManager.add_user_message(user_message_entity)
            if not user_message_entity:
                err = "用户申请加入团队失败"
                logging.exception("[TeamService] %s", err)
                raise Exception("用户申请加入团队失败")
            return user_sub
        except Exception as e:
            err = "用户申请加入团队失败"
            logging.exception("[TeamService] %s", err)
            raise e

    @staticmethod
    async def add_team_user(team_id: uuid.UUID, role_id: uuid.UUID, user_sub_invite: str) -> Union[None, uuid.UUID]:
        # 判断用户是否已经是团队成员
        team_user_entity = await TeamManager.get_team_user_by_user_sub_and_team_id(user_sub_invite, team_id)
        if team_user_entity:
            return None
        try:
            team_user_entity = await Convertor.convert_user_sub_and_team_id_to_team_user_entity(user_sub_invite, team_id)
            team_user_entity = await TeamManager.add_team_user(team_user_entity)
            role_entity = await RoleManager.get_role_by_id(role_id)
            if role_entity is None or role_entity.team_id != team_id or role_entity.is_unique:
                member_role_entity = await RoleManager.get_role_by_role_name_and_team_id(
                    DeafaultRole.MEMBER.value, team_id)
                if member_role_entity is None:
                    err = "邀请团队成员失败, 角色不存在"
                    logging.exception("[TeamService] %s", err)
                    raise Exception("邀请团队成员失败, 角色不存在")
                role_id = member_role_entity.id
            user_role_entity = await Convertor.convert_user_sub_role_id_and_team_id_to_user_role_entity(
                user_sub_invite, role_id, team_id)
            user_role_entity = await RoleManager.add_user_role(user_role_entity)
            await TeamManager.update_team_user_cnt_by_team_id(team_id)
            return user_sub_invite
        except Exception as e:
            err = "邀请团队成员失败"
            logging.exception("[TeamService] %s", err)
            raise e

    @staticmethod
    async def update_team_by_team_id(team_id: uuid.UUID, req: CreateTeamRequest) -> bool:
        """更新团队"""
        try:
            team_dict = await Convertor.convert_update_team_request_to_dict(req)
            team_entity = await TeamManager.update_team_by_id(team_id, team_dict)
            if team_entity is None:
                err = "更新团队失败"
                logging.exception("[TeamService] %s", err)
                raise Exception("更新团队失败, 团队不存在")
            return team_entity.id
        except Exception as e:
            err = "更新团队失败"
            logging.exception("[TeamService] %s", err)
            raise e

    @staticmethod
    async def update_team_user_role_by_team_id_and_user_sub(
            user_sub: uuid.UUID, team_id: uuid.UUID, target_user_sub: str, role_id: uuid.UUID) -> uuid.UUID:
        """更新团队成员角色"""
        if user_sub == target_user_sub:
            err = "更新团队成员角色失败, 不能修改自己的角色"
            logging.exception("[TeamService] %s", err)
            raise TeamPermissionDeniedException("修改自己的角色", str(team_id))
        team_entity = await TeamManager.get_team_by_id(team_id)
        if team_entity is None:
            err = "更新团队成员角色失败, 团队不存在"
            logging.exception("[TeamService] %s", err)
            raise Exception("更新团队成员角色失败, 团队不存在")
        team_user_entity = await TeamManager.get_team_user_by_user_sub_and_team_id(target_user_sub, team_id)
        if team_user_entity is None:
            err = "更新团队成员角色失败, 团队成员不存在"
            logging.exception("[TeamService] %s", err)
            raise Exception("更新团队成员角色失败, 团队成员不存在")
        current_user_role_entity = await RoleManager.get_user_role_by_user_sub_and_team_id(target_user_sub, team_id)
        current_role_entity = await RoleManager.get_role_by_id(current_user_role_entity.role_id)
        if current_role_entity.name == DeafaultRole.OWENER.value:
            err = "更新团队成员角色失败, 不能修改创建者的角色"
            logging.exception("[TeamService] %s", err)
            raise TeamPermissionDeniedException("修改创建者的角色", str(team_id))
        role_entity = await RoleManager.get_role_by_id(role_id)
        if role_entity is None or role_entity.team_id != team_id:
            err = "更新团队成员角色失败, 角色不存在"
            logging.exception("[TeamService] %s", err)
            raise Exception("更新团队成员角色失败, 角色不存在")
        if role_entity.is_unique:
            err = "更新团队成员角色失败, 该角色为唯一角色"
            logging.exception("[TeamService] %s", err)
            raise Exception("更新团队成员角色失败, 该角色为唯一角色")
        try:
            user_role_entity = await RoleManager.get_user_role_by_user_sub_and_team_id(target_user_sub, team_id)
            if user_role_entity is None:
                err = "更新团队成员角色失败, 团队成员角色不存在"
                logging.exception("[TeamService] %s", err)
                raise Exception("更新团队成员角色失败, 团队成员角色不存在")
            user_role_entity = await RoleManager.update_user_role_by_id(
                user_role_entity.id, {"role_id": role_id})
            if user_role_entity is None:
                err = "更新团队成员角色失败"
                logging.exception("[TeamService] %s", err)
                raise Exception("更新团队成员角色失败")
        except Exception as e:
            err = "更新团队成员角色失败"
            logging.exception("[TeamService] %s", err)
            raise e
        return target_user_sub

    @staticmethod
    async def update_team_author_by_team_id(user_sub: str, team_id: uuid.UUID, target_user_sub: str) -> uuid.UUID:
        """转让团队"""
        team_entity = await TeamManager.get_team_by_id(team_id)
        if team_entity is None:
            err = "转让团队失败, 团队不存在"
            logging.exception("[TeamService] %s", err)
            raise Exception("转让团队失败, 团队不存在")
        creator_role_entity = await RoleManager.get_role_by_role_name_and_team_id(
            DeafaultRole.OWENER.value, team_id)
        if creator_role_entity is None:
            err = "转让团队失败, 创建者角色不存在"
            logging.exception("[TeamService] %s", err)
            raise Exception("转让团队失败, 创建者角色不存在")
        admin_role_entity = await RoleManager.get_role_by_role_name_and_team_id(
            DeafaultRole.ADMINISTRATOR.value, team_id)
        if admin_role_entity is None:
            err = "转让团队失败, 管理员角色不存在"
            logging.exception("[TeamService] %s", err)
            raise Exception("转让团队失败, 管理员角色不存在")
        team_user_entity = await TeamManager.get_team_user_by_user_sub_and_team_id(target_user_sub, team_id)
        if team_user_entity is None:
            err = "转让团队失败, 团队成员不存在"
            logging.exception("[TeamService] %s", err)
            raise Exception("转让团队失败, 团队成员不存在")
        try:
            # 将当前创建者角色转为管理员角色
            current_creator_user_role_entity = await RoleManager.get_user_role_by_user_sub_and_team_id(user_sub, team_id)
            if current_creator_user_role_entity is None:
                err = "转让团队失败, 当前创建者角色不存在"
                logging.exception("[TeamService] %s", err)
                raise Exception("转让团队失败, 当前创建者角色不存在")
            # 将目标成员角色转为创建者角色
            target_user_role_entity = await RoleManager.get_user_role_by_user_sub_and_team_id(target_user_sub, team_id)
            if target_user_role_entity is None:
                err = "转让团队失败, 目标成员角色不存在"
                logging.exception("[TeamService] %s", err)
                raise Exception("转让团队失败, 目标成员角色不存在")
            await RoleManager.update_user_role_by_id(
                current_creator_user_role_entity.id, {"role_id": admin_role_entity.id})
            await RoleManager.update_user_role_by_id(
                target_user_role_entity.id, {"role_id": creator_role_entity.id})
            # 更新团队的创建者
            from data_chain.manager.user_manager import UserManager
            target_user_entity = await UserManager.get_user_by_id(target_user_sub)
            target_author_name = target_user_entity.name if target_user_entity and target_user_entity.name else target_user_sub
            team_entity = await TeamManager.update_team_by_id(team_id, {"author_id": target_user_sub, "author_name": target_author_name})
            return team_entity.id
        except Exception as e:
            err = "转让团队失败"
            logging.exception("[TeamService] %s", err)
            raise e

    @staticmethod
    async def soft_delete_team_by_team_id(
            team_id: uuid.UUID) -> bool:
        """软删除团队"""
        try:
            knowlede_base_entities = await KnowledgeBaseManager.list_knowledge_base_by_team_ids([team_id])
            kb_ids = [kb_entity.id for kb_entity in knowlede_base_entities]
            await KnowledgeBaseService.delete_kb_by_kb_ids(kb_ids)
            team_entity = await TeamManager.update_team_by_id(
                team_id, {"status": TeamStatus.DELETED.value})
            if team_entity is None:
                err = "软删除团队失败"
                logging.exception("[TeamService] %s", err)
                raise Exception("软删除团队失败, 团队不存在")
            return team_entity.id
        except Exception as e:
            err = "软删除团队失败"
            logging.exception("[TeamService] %s", err)
            raise e

    @staticmethod
    async def delete_team_user_by_team_id_and_user_subs(
            team_id: uuid.UUID, user_subs: list[str]) -> list[uuid.UUID]:
        """删除团队成员"""
        team_entity = await TeamManager.get_team_by_id(team_id)
        if team_entity is None:
            err = "删除团队成员失败, 团队不存在"
            logging.exception("[TeamService] %s", err)
            raise Exception("删除团队成员失败, 团队不存在")
        team_user_entities = await TeamManager.list_team_user_by_team_id_and_user_subs(team_id, user_subs)
        user_subs = [team_user.user_id for team_user in team_user_entities]
        try:
            user_role_entities = await RoleManager.list_user_roles_by_team_id_and_user_subs(
                team_id, user_subs)
            unique_role_ids = set(
                [user_role.role_id for user_role in user_role_entities])
            role_entities = await RoleManager.list_roles_by_role_ids(
                list(unique_role_ids))
            usr_role_dict = {
                user_role.user_id: user_role for user_role in user_role_entities}
            role_dict = {
                role_entity.id: role_entity for role_entity in role_entities}
            user_subs_deleted = []
            for user_sub in user_subs:
                user_role = usr_role_dict.get(user_sub)
                role = role_dict.get(user_role.role_id) if user_role else None
                if role and role.name == DeafaultRole.OWENER.value:
                    warning = f"删除团队成员失败, 不能删除创建者 {user_sub}"
                    logging.warning("[TeamService] %s", warning)
                    continue
                user_subs_deleted.append(user_sub)
            await TeamManager.update_team_users_by_team_id_and_user_subs(
                team_id, user_subs, {"status": TeamUserStaus.DELETED.value})
            await RoleManager.update_user_roles_by_team_id_and_user_subs(
                team_id, user_subs, {"status": UserRoleStatus.DELETED.value})
            await TeamManager.update_team_user_cnt_by_team_id(team_id)
            return user_subs_deleted
        except Exception as e:
            err = "删除团队成员失败"
            logging.exception("[TeamService] %s", err)
            raise e
