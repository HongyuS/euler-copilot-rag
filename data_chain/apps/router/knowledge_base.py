# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.

from fastapi import APIRouter, Depends, Query, Body, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, Response
from typing import Annotated, Optional
import urllib
from uuid import UUID
from httpx import AsyncClient
from data_chain.entities.request_data import (
    ListKnowledgeBaseRequest,
    CreateKnowledgeBaseRequest,
    UpdateKnowledgeBaseRequest,
)
from data_chain.entities.enum import IdType, MessageLevel
from data_chain.entities.response_data import (
    ListAllKnowledgeBaseMsg,
    ListAllKnowledgeBaseResponse,
    ListKnowledgeBaseResponse,
    ListDocumentTypesResponse,
    CreateKnowledgeBaseResponse,
    ImportKnowledgeBaseResponse,
    ExportKnowledgeBaseResponse,
    UpdateKnowledgeBaseResponse,
    DeleteKnowledgeBaseResponse,
)
from data_chain.apps.service.team_service import TeamService
from data_chain.apps.service.knwoledge_base_service import KnowledgeBaseService
from data_chain.apps.service.task_service import TaskService
from data_chain.apps.service.session_service import get_user_sub, verify_user
from data_chain.apps.service.router_service import get_route_info
from data_chain.apps.exceptions import (
    TeamPermissionDeniedException,
    KnowledgeBasePermissionDeniedException,
    TaskPermissionDeniedException
)
router = APIRouter(prefix='/kb', tags=['Knowledge Base'])


@router.get('', response_model=ListAllKnowledgeBaseResponse, dependencies=[Depends(verify_user)])
async def list_kb_by_user_sub(
    user_sub: Annotated[str, Depends(get_user_sub)],
    action: Annotated[str, Depends(get_route_info)],
    kb_id: Optional[UUID] = Query(default=None, alias="kbId"),
    kb_name:  Optional[str] = Query(default=None, alias="kbName")
):
    list_all_kb_msg = await KnowledgeBaseService.list_kb_by_user_sub(user_sub, kb_id=kb_id, kb_name=kb_name)
    return ListAllKnowledgeBaseResponse(result=list_all_kb_msg)


@router.post('/team', response_model=ListKnowledgeBaseResponse, dependencies=[Depends(verify_user)])
async def list_kb_by_team_id(
    user_sub: Annotated[str, Depends(get_user_sub)],
    action: Annotated[str, Depends(get_route_info)],
    req: Annotated[ListKnowledgeBaseRequest, Body()]
):
    if not await TeamService.validate_user_action_in_team(user_sub, req.team_id, action):
        raise KnowledgeBasePermissionDeniedException("访问该团队的知识库", str(req.team_id))
    list_kb_msg = await KnowledgeBaseService.list_kb_by_team_id(req)
    await TeamService.add_team_msg(user_sub, req.team_id, IdType.TEAM, MessageLevel.INFO, '查看了知识库列表', 'knowledge base list viewed')
    return ListKnowledgeBaseResponse(result=list_kb_msg)


@router.get('/doc_type', response_model=ListDocumentTypesResponse, dependencies=[Depends(verify_user)])
async def list_doc_types_by_kb_id(
    user_sub: Annotated[str, Depends(get_user_sub)],
    action: Annotated[str, Depends(get_route_info)],
    kb_id: Annotated[UUID, Query(alias="kbId")],
):
    if not await KnowledgeBaseService.validate_user_action_to_knowledge_base(user_sub, kb_id, action):
        raise KnowledgeBasePermissionDeniedException("访问该知识库的文档类型", str(kb_id))
    doc_types = await KnowledgeBaseService.list_doc_types_by_kb_id(kb_id)
    await TeamService.add_team_msg(user_sub, kb_id, IdType.KNOWLEDGE_BASE, MessageLevel.INFO, '查看了知识库{kbName}的文档类型', 'knowledge base {kbName} Document types viewed')
    return ListDocumentTypesResponse(result=doc_types)


@router.get('/download', dependencies=[Depends(verify_user)])
async def download_kb_by_task_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        task_id: Annotated[UUID, Query(alias="taskId")]):
    if not await TaskService.validate_user_action_to_task(user_sub, task_id, action):
        raise TaskPermissionDeniedException("访问该知识库的任务", str(task_id))
    zip_download_url = await KnowledgeBaseService.generate_knowledge_base_download_link(task_id)
    if not zip_download_url:
        raise Exception("知识库下载连接生成失败")
    async with AsyncClient() as async_client:
        response = await async_client.get(zip_download_url)
        if response.status_code == 200:
            zip_name = f"{task_id}.zip"
            content_disposition = f"attachment; filename={urllib.parse.quote(zip_name.encode('utf-8'))}"
            content_length = response.headers.get('content-length')

            # 定义一个协程函数来生成数据流
            async def stream_generator():
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    yield chunk

            return StreamingResponse(
                stream_generator(),
                headers={
                    "Content-Disposition": content_disposition,
                    "Content-Length": str(content_length) if content_length else None
                },
                media_type="application/zip"
            )
        else:
            raise Exception(f"下载知识库 zip 失败，状态码: {response.status_code}")


@router.post('', response_model=CreateKnowledgeBaseResponse, dependencies=[Depends(verify_user)])
async def create_kb(user_sub: Annotated[str, Depends(get_user_sub)],
                    action: Annotated[str, Depends(get_route_info)],
                    team_id: Annotated[UUID, Query(alias="teamId")],
                    req: Annotated[CreateKnowledgeBaseRequest, Body()]):
    if not await TeamService.validate_user_action_in_team(user_sub, team_id, action):
        raise KnowledgeBasePermissionDeniedException("在该团队创建知识库", str(team_id))
    kb_id = await KnowledgeBaseService.create_kb(user_sub, team_id, req)
    await TeamService.add_team_msg(user_sub, kb_id, IdType.KNOWLEDGE_BASE, MessageLevel.INFO, '创建了知识库{kbName}', 'knowledge base {kbName} created')
    return CreateKnowledgeBaseResponse(result=kb_id)


@router.post('/import', response_model=ImportKnowledgeBaseResponse, dependencies=[Depends(verify_user)])
async def import_kbs(user_sub: Annotated[str, Depends(get_user_sub)],
                     action: Annotated[str, Depends(get_route_info)],
                     team_id: Annotated[UUID, Query(alias="teamId")],
                     kb_packages: list[UploadFile] = File(...)):
    if not await TeamService.validate_user_action_in_team(user_sub, team_id, action):
        raise KnowledgeBasePermissionDeniedException("在该团队导入知识库", str(team_id))
    kb_import_task_ids = await KnowledgeBaseService.import_kbs(user_sub, team_id, kb_packages)
    await TeamService.add_team_msg(user_sub, team_id, IdType.TEAM, MessageLevel.INFO, '导入了知识库', 'knowledge base imported')
    return ImportKnowledgeBaseResponse(result=kb_import_task_ids)


@router.post('/export', response_model=ExportKnowledgeBaseResponse, dependencies=[Depends(verify_user)])
async def export_kb_by_kb_ids(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        kb_ids: Annotated[list[UUID], Query(alias="kbIds")]):
    for kb_id in kb_ids:
        if not await KnowledgeBaseService.validate_user_action_to_knowledge_base(user_sub, kb_id, action):
            raise KnowledgeBasePermissionDeniedException("导出该知识库", str(kb_id))
    kb_export_task_ids = await KnowledgeBaseService.export_kb_by_kb_ids(kb_ids)
    for kb_id in kb_ids:
        await TeamService.add_team_msg(user_sub, kb_id, IdType.KNOWLEDGE_BASE, MessageLevel.INFO, '导出了知识库{kbName}', 'knowledge base {kbName} exported')
    return ExportKnowledgeBaseResponse(result=kb_export_task_ids)


@router.put('', response_model=UpdateKnowledgeBaseResponse, dependencies=[Depends(verify_user)])
async def update_kb_by_kb_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        kb_id: Annotated[UUID, Query(alias="kbId")],
        req: Annotated[UpdateKnowledgeBaseRequest, Body()]):
    if not await KnowledgeBaseService.validate_user_action_to_knowledge_base(user_sub, kb_id, action):
        raise KnowledgeBasePermissionDeniedException("更新该知识库", str(kb_id))
    kb_id = await KnowledgeBaseService.update_kb_by_kb_id(kb_id, req)
    await TeamService.add_team_msg(user_sub, kb_id, IdType.KNOWLEDGE_BASE, MessageLevel.INFO, '更新了知识库{kbName}', 'knowledge base {kbName} updated')
    return UpdateKnowledgeBaseResponse(result=kb_id)


@router.delete('', response_model=DeleteKnowledgeBaseResponse, dependencies=[Depends(verify_user)])
async def delete_kb_by_kb_ids(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        kb_ids: Annotated[list[UUID], Body(alias="kbIds")]):
    for kb_id in kb_ids:
        if not await KnowledgeBaseService.validate_user_action_to_knowledge_base(user_sub, kb_id, action):
            raise KnowledgeBasePermissionDeniedException("删除该知识库", str(kb_id))
    for kb_id in kb_ids:
        await TeamService.add_team_msg(user_sub, kb_id, IdType.KNOWLEDGE_BASE, MessageLevel.WARNING, '删除了知识库{kbName}', 'knowledge base {kbName} deleted')
    kb_ids_deleted = await KnowledgeBaseService.delete_kb_by_kb_ids(kb_ids)
    return DeleteKnowledgeBaseResponse(result=kb_ids_deleted)
