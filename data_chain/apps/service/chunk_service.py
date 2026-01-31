# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import time
import asyncio
from fastapi import APIRouter, Depends, Query, Body, File, UploadFile
import uuid
import traceback
import os
from data_chain.entities.request_data import (
    ListChunkRequest,
    UpdateChunkRequest,
    SearchChunkRequest,
)
from data_chain.entities.response_data import (
    Task,
    Document,
    Chunk,
    DocChunk,
    ListChunkMsg,
    SearchChunkMsg
)
from data_chain.apps.base.convertor import Convertor
from data_chain.apps.service.task_queue_service import TaskQueueService
from data_chain.apps.service.knwoledge_base_service import KnowledgeBaseService
from data_chain.apps.service.document_service import DocumentService
from data_chain.manager.knowledge_manager import KnowledgeBaseManager
from data_chain.manager.document_type_manager import DocumentTypeManager
from data_chain.manager.document_manager import DocumentManager
from data_chain.manager.chunk_manager import ChunkManager
from data_chain.manager.role_manager import RoleManager
from data_chain.manager.task_manager import TaskManager
from data_chain.manager.task_report_manager import TaskReportManager
from data_chain.stores.database.database import ChunkEntity
from data_chain.stores.minio.minio import MinIO
from data_chain.entities.enum import ParseMethod, DataSetStatus, DocumentStatus, TaskType
from data_chain.entities.common import DOC_PATH_IN_OS, DOC_PATH_IN_MINIO, DEFAULT_KNOWLEDGE_BASE_ID, DEFAULT_DOC_TYPE_ID
from data_chain.logger.logger import logger as logging
from data_chain.rag.base_searcher import BaseSearcher
from data_chain.parser.tools.token_tool import TokenTool
from data_chain.embedding.embedding import Embedding


class ChunkService:

    """Chunk Service"""
    @staticmethod
    async def validate_user_action_to_chunk(user_sub: str, chunk_id: uuid.UUID, action: str) -> bool:
        """验证用户对分片的操作权限"""
        try:
            chunk_entity = await ChunkManager.get_chunk_by_chunk_id(chunk_id)
            if chunk_entity is None:
                err = f"分片不存在，分片ID: {chunk_id}"
                logging.error("[ChunkService] %s", err)
                return False
            action_entity = await RoleManager.get_action_by_team_id_user_sub_and_action(
                user_sub, chunk_entity.team_id, action)
            if action_entity is None:
                return False
            return True
        except Exception as e:
            err = "验证用户对分片的操作权限失败"
            logging.exception("[ChunkService] %s", err)
            raise e

    @staticmethod
    async def list_chunks_by_document_id(req: ListChunkRequest) -> ListChunkMsg:
        """根据文档ID列出分片"""
        try:
            doc_entity = await DocumentManager.get_document_by_doc_id(req.doc_id)
            if doc_entity.status != DocumentStatus.IDLE.value:
                return ListChunkMsg(total=0, chunks=[])
            total, chunk_entities = await ChunkManager.list_chunk(req)
            chunks = []
            for chunk_entity in chunk_entities:
                chunk = await Convertor.convert_chunk_entity_to_chunk(chunk_entity)
                chunks.append(chunk)
            return ListChunkMsg(total=total, chunks=chunks)
        except Exception as e:
            err = "根据文档ID列出分片失败"
            logging.exception("[ChunkService] %s", err)
            raise e

    @staticmethod
    async def search_chunks_from_kb(user_sub: str, action: str, search_method: str, kb_id: uuid.UUID, query: str, top_k: int, doc_ids: list[uuid.UUID] = None, banned_ids: list[uuid.UUID] = [], is_rerank: bool = False) -> list[ChunkEntity]:
        """从知识库搜索分片"""
        top_k_search = top_k
        if is_rerank:
            top_k_search = top_k * 3
        try:
            chunk_entities = await BaseSearcher.search(search_method, kb_id, query, top_k_search, doc_ids, banned_ids)
        except Exception as e:
            err = f"搜索分片失败，error: {e}"
            logging.exception("[ChunkService] %s", err)
            return []
        return chunk_entities

    @staticmethod
    async def rerank_chunks(chunk_entities: list[ChunkEntity], rerank_method: str, query: str, top_k: int) -> list[ChunkEntity]:
        """对分片进行重排序"""
        chunk_entities = await BaseSearcher.rerank(chunk_entities, rerank_method, query)
        chunk_entities = chunk_entities[:top_k]
        return chunk_entities
    # 关联上下文

    @staticmethod
    async def relate_surrounding_chunks(chunk_entities: list[ChunkEntity], tokens_limit: int) -> list[ChunkEntity]:
        """关联上下文到搜索分片结果中"""
        chunk_ids = [chunk_entity.id for chunk_entity in chunk_entities]
        tokens_limit_every_chunk = tokens_limit // len(
            chunk_entities) if len(chunk_entities) > 0 else tokens_limit
        leave_tokens = 0
        related_chunk_entities = []
        token_sum = 0
        for chunk_entity in chunk_entities:
            token_sum += chunk_entity.tokens
        for chunk_entity in chunk_entities:
            leave_tokens = tokens_limit_every_chunk+leave_tokens
            try:
                sub_related_chunk_entities = await BaseSearcher.related_surround_chunk(chunk_entity, leave_tokens-chunk_entity.tokens, chunk_ids)
            except Exception as e:
                leave_tokens += tokens_limit_every_chunk
                err = f"[ChunkService] 关联上下文失败，error: {e}"
                logging.exception(err)
                continue
            for related_chunk_entity in sub_related_chunk_entities:
                token_sum += related_chunk_entity.tokens
                leave_tokens -= related_chunk_entity.tokens
            if leave_tokens < 0:
                leave_tokens = 0
            chunk_ids += [chunk_entity.id for chunk_entity in sub_related_chunk_entities]
            related_chunk_entities += sub_related_chunk_entities
            if token_sum >= tokens_limit:
                break
        return related_chunk_entities
    # 补全文档信息

    @staticmethod
    async def enrich_doc_info_to_search_chunks(search_chunk_msg: SearchChunkMsg) -> None:
        """补全文档信息到搜索分片结果中"""
        doc_entities = await DocumentManager.list_document_by_doc_ids(
            [doc_chunk.doc_id for doc_chunk in search_chunk_msg.doc_chunks])
        doc_map = {doc_entity.id: doc_entity for doc_entity in doc_entities}
        for doc_chunk in search_chunk_msg.doc_chunks:
            doc_entity = doc_map.get(doc_chunk.doc_id)
            doc_chunk.doc_author = doc_entity.author_name if doc_entity else ""
            doc_chunk.doc_created_at = doc_entity.created_time.strftime(
                '%Y-%m-%d %H:%M') if doc_entity else ""
            doc_chunk.doc_abstract = doc_entity.abstract if doc_entity else ""
            doc_chunk.doc_extension = doc_entity.extension if doc_entity else ""
            doc_chunk.doc_size = doc_entity.size if doc_entity else 0

    @staticmethod
    async def search_chunks(user_sub: str, action: str, req: SearchChunkRequest) -> SearchChunkMsg:
        """根据查询条件搜索分片"""
        search_chunk_msg = SearchChunkMsg(docChunks=[])
        kb_ids_after_validate = []
        for kb_id in req.kb_ids:
            if kb_id == DEFAULT_KNOWLEDGE_BASE_ID or await KnowledgeBaseService.validate_user_action_to_knowledge_base(user_sub, kb_id, action):
                kb_ids_after_validate.append(kb_id)
            else:
                logging.error(
                    "[ChunkService] 用户没有权限访问该知识库，知识库ID: %s", str(kb_id))
        req.kb_ids = kb_ids_after_validate
        logging.error("[ChunkService] 搜索分片，查询条件: %s", req)
        chunk_entities = []
        search_tasks = []
        st = time.time()
        for kb_id in req.kb_ids:
            search_task = ChunkService.search_chunks_from_kb(
                user_sub, action, req.search_method, kb_id, req.query, req.top_k, req.doc_ids, req.banned_ids, req.is_rerank)
            search_tasks.append(search_task)
        search_results = await asyncio.gather(*search_tasks)
        en = time.time()
        if req.is_testing_scene:
            search_chunk_msg.t_used_in_search = round(en - st, 3)
        if req.is_rerank:
            st = time.time()
            for i in range(len(req.kb_ids)):
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(req.kb_ids[i])
                search_results[i] = await ChunkService.rerank_chunks(
                    search_results[i], kb_entity.rerank_method, req.query, req.top_k)
                chunk_entities += search_results[i]
            en = time.time()
            if req.is_testing_scene:
                search_chunk_msg.t_used_in_rerank = round(en - st, 3)
        else:
            for result in search_results:
                chunk_entities += result
        if len(chunk_entities) == 0:
            return SearchChunkMsg(docChunks=[])
        if req.is_rerank:
            st = time.time()
            chunk_entities = await BaseSearcher.rerank(chunk_entities, None, req.query)
            en = time.time()
            if req.is_testing_scene:
                search_chunk_msg.t_used_in_rerank = round(
                    (search_chunk_msg.t_used_in_rerank or 0) + (en - st), 3)
        chunk_entities = chunk_entities[:req.top_k]
        logging.error("[ChunkService] 搜索分片，查询结果数量: %s", len(chunk_entities))
        if req.is_related_surrounding:
            # 关联上下文
            st = time.time()
            chunk_entities_related = await ChunkService.relate_surrounding_chunks(
                chunk_entities, req.tokens_limit)
            chunk_entities += chunk_entities_related
            en = time.time()
            if req.is_testing_scene:
                search_chunk_msg.t_used_in_surrounding_text_relation = round(
                    en - st, 3)
        if req.is_classify_by_doc:
            doc_chunks = await BaseSearcher.classify_by_doc_id(chunk_entities)
            search_chunk_msg.doc_chunks = doc_chunks
        else:
            for chunk_entity in chunk_entities:
                chunk = await Convertor.convert_chunk_entity_to_chunk(chunk_entity)
                dc = DocChunk(docId=chunk_entity.doc_id,
                              docName=chunk_entity.doc_name, chunks=[chunk])
                search_chunk_msg.doc_chunks.append(dc)
        if req.is_compress:
            st = time.time()
            for doc_chunk in search_chunk_msg.doc_chunks:
                for chunk in doc_chunk.chunks:
                    chunk.text = await TokenTool.compress_tokens(chunk.text)
            en = time.time()
            if req.is_testing_scene:
                search_chunk_msg.t_used_in_text_compression = round(
                    en - st, 3)
        if req.is_testing_scene:
            for doc_chunk in search_chunk_msg.doc_chunks:
                for chunk in doc_chunk.chunks:
                    chunk.score = await TokenTool.cal_jac(req.query, chunk.text)
        await ChunkService.enrich_doc_info_to_search_chunks(search_chunk_msg)
        logging.error("f{search_chunk_msg}")
        return search_chunk_msg

    async def update_chunk_by_id(chunk_id: uuid.UUID, req: UpdateChunkRequest) -> uuid.UUID:
        try:
            chunk_dict = await Convertor.convert_update_chunk_request_to_dict(req)
            if req.text:
                vector = await Embedding.vectorize_embedding(req.text)
                chunk_dict["text_vector"] = vector
                await ChunkManager.update_chunk_text_ts_vector_by_chunk_ids([chunk_id])
            chunk_entity = await ChunkManager.update_chunk_by_chunk_id(chunk_id, chunk_dict)
            return chunk_entity.id
        except Exception as e:
            err = "更新分片失败"
            logging.exception("[ChunkService] %s", err)
            raise Exception(err)

    async def update_chunks_enabled_by_id(chunk_ids: list[uuid.UUID], enabled: bool) -> list[uuid.UUID]:
        try:
            chunk_dict = {"enabled": enabled}
            chunk_entities = await ChunkManager.update_chunk_by_chunk_ids(chunk_ids, chunk_dict)
            chunk_ids = [chunk_entity.id for chunk_entity in chunk_entities]
            return chunk_ids
        except Exception as e:
            err = "更新分片失败"
            logging.exception("[ChunkService] %s", err)
            raise Exception(err)
