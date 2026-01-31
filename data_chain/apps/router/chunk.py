# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
from data_chain.apps.service.session_service import get_user_sub, verify_user
from fastapi import APIRouter, Depends, Query, Body
from typing import Annotated
from uuid import UUID
from data_chain.entities.request_data import (
    ListChunkRequest,
    UpdateChunkRequest,
    SearchChunkRequest,
)

from data_chain.entities.response_data import (
    ListChunkMsg,
    ListChunkResponse,
    SearchChunkResponse,
    UpdateChunkResponse,
    UpdateChunkEnabledResponse
)
from data_chain.entities.enum import IdType, MessageLevel
from data_chain.apps.service.router_service import get_route_info
from data_chain.apps.exceptions import (
    ChunkPermissionDeniedException,
    DocumentPermissionDeniedException
)
from data_chain.apps.service.team_service import TeamService
from data_chain.apps.service.document_service import DocumentService
from data_chain.apps.service.chunk_service import ChunkService
router = APIRouter(prefix='/chunk', tags=['Chunk'])


@router.post('/list', response_model=ListChunkResponse, dependencies=[Depends(verify_user)])
async def list_chunks_by_document_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        req: Annotated[ListChunkRequest, Body()],
):
    if not (await DocumentService.validate_user_action_to_document(user_sub, req.doc_id, action)):
        raise ChunkPermissionDeniedException("访问该文档的分片", str(req.doc_id))
    list_chunk_msg = await ChunkService.list_chunks_by_document_id(req)
    await TeamService.add_team_msg(user_sub, req.doc_id, IdType.DOCUMENT, MessageLevel.INFO, '查看了知识库{kbName}的文档《{documentName}》的分片列表', 'knowledge base {kbName} Document {documentName} chunk list viewed')
    return ListChunkResponse(result=list_chunk_msg)


@router.post('/search', response_model=SearchChunkResponse, dependencies=[Depends(verify_user)])
async def search_chunks(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        req: Annotated[SearchChunkRequest, Body()],
):
    search_chunk_msg = await ChunkService.search_chunks(user_sub, action, req)
    return SearchChunkResponse(result=search_chunk_msg)


@router.put('', response_model=UpdateChunkResponse, dependencies=[Depends(verify_user)])
async def update_chunk_by_id(user_sub: Annotated[str, Depends(get_user_sub)],
                             action: Annotated[str, Depends(get_route_info)],
                             chunk_id: Annotated[UUID, Query(alias="chunkId")],
                             req: Annotated[UpdateChunkRequest, Body()]):
    if not (await ChunkService.validate_user_action_to_chunk(user_sub, chunk_id, action)):
        raise ChunkPermissionDeniedException("更新分片", str(chunk_id))
    chunk_id = await ChunkService.update_chunk_by_id(chunk_id, req)
    await TeamService.add_team_msg(user_sub, chunk_id, IdType.CHUNK, MessageLevel.INFO, '更新了知识库{kbName}的文档《{documentName}》的分片', 'knowledge base {kbName} Document {documentName} chunk updated')
    return UpdateChunkResponse(result=chunk_id)


@router.put('/switch', response_model=UpdateChunkEnabledResponse, dependencies=[Depends(verify_user)])
async def update_chunk_enabled_by_id(user_sub: Annotated[str, Depends(get_user_sub)],
                                     action: Annotated[str, Depends(get_route_info)],
                                     chunk_ids: Annotated[list[UUID], Body(alias="chunkId")],
                                     enabled: Annotated[bool, Query()]):
    for chunk_id in chunk_ids:
        if not (await ChunkService.validate_user_action_to_chunk(user_sub, chunk_id, action)):
            raise ChunkPermissionDeniedException("访问分片", str(chunk_id))
    chunk_ids = await ChunkService.update_chunks_enabled_by_id(chunk_ids, enabled)
    for chunk_id in chunk_ids:
        await TeamService.add_team_msg(user_sub, chunk_id, IdType.CHUNK, MessageLevel.INFO, '更新了知识库{kbName}的文档《{documentName}》的分片启用状态', 'knowledge base {kbName} Document {documentName} chunk enabled status updated')
    return UpdateChunkEnabledResponse(result=chunk_ids)
