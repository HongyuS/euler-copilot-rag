# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
from sqlalchemy import (
    select,
    update,
    func,
    text,
    or_,
    and_,
    bindparam,
    literal_column,
    Float,
)
from typing import List, Tuple, Dict, Optional
import uuid
from datetime import datetime
from data_chain.entities.enum import DocumentStatus, ChunkStatus, Tokenizer
from data_chain.entities.request_data import ListChunkRequest
from data_chain.config.config import config
from data_chain.stores.database.database import DocumentEntity, ChunkEntity, DataBase
from data_chain.manager.knowledge_manager import KnowledgeBaseManager
from data_chain.logger.logger import logger as logging
from data_chain.parser.tools.token_tool import TokenTool
import logging


class ChunkManager:
    @staticmethod
    async def add_chunk(chunk: ChunkEntity) -> ChunkEntity:
        """添加文档"""
        try:
            async with await DataBase.get_session() as session:
                session.add(chunk)
                await session.commit()
                return chunk
        except Exception as e:
            err = "添加文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)

    @staticmethod
    async def add_chunks(chunks: List[ChunkEntity]) -> List[ChunkEntity]:
        """批量添加文档"""
        try:
            async with await DataBase.get_session() as session:
                session.add_all(chunks)
                await session.commit()
                return chunks
        except Exception as e:
            err = "批量添加文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)

    @staticmethod
    async def get_chunk_by_chunk_id(chunk_id: uuid.UUID) -> Optional[ChunkEntity]:
        """根据文档ID查询文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(ChunkEntity).where(ChunkEntity.id == chunk_id)
                result = await session.execute(stmt)
                return result.scalars().first()
        except Exception as e:
            err = "根据文档ID查询文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)
            raise e

    @staticmethod
    async def get_chunk_cnt_by_doc_ids(doc_ids: List[uuid.UUID]) -> int:
        """根据文档ID查询文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    select(func.count())
                    .where(ChunkEntity.doc_id.in_(doc_ids))
                    .where(ChunkEntity.status != ChunkStatus.DELETED.value)
                )
                result = await session.execute(stmt)
                return result.scalar()
        except Exception as e:
            err = "根据文档ID查询文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)
            raise e

    async def get_chunk_cnt_by_kb_id(kb_id) -> int:
        """根据文档ID查询文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    select(func.count())
                    .where(ChunkEntity.kb_id == kb_id)
                    .where(ChunkEntity.status != ChunkStatus.DELETED.value)
                )
                result = await session.execute(stmt)
                return result.scalar()
        except Exception as e:
            err = "根据文档ID查询文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)
            raise e

    @staticmethod
    async def get_chunk_tokens_by_doc_ids(doc_ids: List[uuid.UUID]) -> int:
        """根据文档ID查询文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    select(func.sum(ChunkEntity.tokens))
                    .where(ChunkEntity.doc_id.in_(doc_ids))
                    .where(ChunkEntity.status != ChunkStatus.DELETED.value)
                )
                result = await session.execute(stmt)
                return result.scalar()
        except Exception as e:
            err = "根据文档ID查询文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)
            raise e

    @staticmethod
    async def get_chunk_tokens_by_kb_id(kb_id) -> int:
        """根据文档ID查询文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    select(func.sum(ChunkEntity.tokens))
                    .where(ChunkEntity.kb_id == kb_id)
                    .where(ChunkEntity.status != ChunkStatus.DELETED.value)
                )
                result = await session.execute(stmt)
                return result.scalar()
        except Exception as e:
            err = "根据文档ID查询文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)
            raise e

    async def list_chunk(
        req: ListChunkRequest,
    ) -> Tuple[int, List[ChunkEntity]]:
        """根据文档ID查询文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(ChunkEntity).where(
                    ChunkEntity.status != ChunkStatus.DELETED.value
                )
                if req.doc_id is not None:
                    stmt = stmt.where(ChunkEntity.doc_id == req.doc_id)
                if req.text is not None:
                    stmt = stmt.where(ChunkEntity.text.ilike(f"%{req.text}%"))
                if req.types is not None:
                    stmt = stmt.where(
                        ChunkEntity.type.in_([t.value for t in req.types])
                    )
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total = (await session.execute(count_stmt)).scalar()
                stmt = stmt.offset((req.page - 1) * req.page_size).limit(req.page_size)
                stmt = stmt.order_by(ChunkEntity.global_offset)
                result = await session.execute(stmt)
                chunk_entities = result.scalars().all()
                return total, chunk_entities
        except Exception as e:
            err = "根据文档ID查询文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)
            raise e

    @staticmethod
    async def list_all_chunk_by_doc_id(doc_id: uuid.UUID) -> List[ChunkEntity]:
        """根据文档ID查询文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    select(ChunkEntity)
                    .where(
                        and_(
                            ChunkEntity.doc_id == doc_id,
                            ChunkEntity.status != ChunkStatus.DELETED.value,
                        )
                    )
                    .order_by(ChunkEntity.global_offset)
                )
                result = await session.execute(stmt)
                return result.scalars().all()
        except Exception as e:
            err = "根据文档ID查询文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)
            raise e

    @staticmethod
    async def get_top_k_chunk_by_kb_id_vector(
        kb_id: uuid.UUID,
        vector: List[float],
        top_k: int,
        doc_ids: list[uuid.UUID] = None,
        banned_ids: list[uuid.UUID] = [],
        chunk_to_type: str = None,
        pre_ids: list[uuid.UUID] = None,
    ) -> List[ChunkEntity]:
        """根据知识库ID和向量查询文档解析结果（适配OpenGauss强制索引）"""
        try:
            if top_k <= 0:
                return []
            st = datetime.now()
            async with await DataBase.get_session() as session:
                # --------------------------
                # 原有逻辑：构建WHERE条件和params（完全保留）
                # --------------------------
                where_conditions = [
                    "document.enabled = true",
                    "document.status != 'deleted'",
                    "chunk.kb_id = :kb_id",
                    "chunk.enabled = true",
                    "chunk.status != 'deleted'",
                    "chunk.text_vector IS NOT NULL",
                ]

                # 处理向量格式兼容性：PostgreSQL需要字符串格式，OpenGauss可以直接使用列表
                if config["DATABASE_TYPE"].lower() == "opengauss":
                    vector_param = vector
                else:
                    # PostgreSQL需要将向量转换为字符串格式
                    vector_param = str(vector)

                params = {"vector": vector_param, "kb_id": kb_id, "limit": top_k}

                if banned_ids:
                    banned_placeholders = []
                    for i, banned_id in enumerate(banned_ids):
                        param_name = f"banned_id_{i}"
                        banned_placeholders.append(f":{param_name}")
                        params[param_name] = banned_id
                    where_conditions.append(
                        f"chunk.id NOT IN ({','.join(banned_placeholders)})"
                    )

                if doc_ids is not None:
                    doc_placeholders = []
                    for i, doc_id in enumerate(doc_ids):
                        param_name = f"doc_id_{i}"
                        doc_placeholders.append(f":{param_name}")
                        params[param_name] = doc_id
                    where_conditions.append(
                        f"document.id IN ({','.join(doc_placeholders)})"
                    )

                if chunk_to_type is not None:
                    where_conditions.append(
                        "chunk.parse_topology_type = :chunk_to_type"
                    )
                    params["chunk_to_type"] = chunk_to_type

                if pre_ids is not None:
                    if not pre_ids:
                        return []
                    pre_placeholders = []
                    for i, pre_id in enumerate(pre_ids):
                        param_name = f"pre_id_{i}"
                        pre_placeholders.append(f":{param_name}")
                        params[param_name] = pre_id
                    where_conditions.append(
                        f"chunk.pre_id_in_parse_topology IN ({','.join(pre_placeholders)})"
                    )

                where_clause = " AND ".join(where_conditions)

                # --------------------------
                # 核心修复：替换为OpenGauss支持的索引提示（二选一，推荐方案1）
                # --------------------------
                # 方案1：临时关闭全表扫描（优先推荐，简单有效，会话级生效，不影响其他查询）
                # 执行SET命令：关闭全表扫描后，数据库会优先选择可用索引（text_vector_index）
                await session.execute(text("SET enable_seqscan = off;"))
                await session.execute(text("SET enable_indexscan = on;"))
                # 增加searcher数量，提升向量检索性能（可选）
                await session.execute(text("SET hnsw.ef_search = 1000;"))
                # 方案2（备选）：使用OpenGauss查询计划hints（需确保数据库开启hints支持）
                # 在SELECT后添加 /*+ IndexScan(chunk text_vector_index) */ 强制索引扫描
                # 若用方案2，需将下面SELECT行改为：SELECT /*+ IndexScan(chunk text_vector_index) */

                # 构建查询SQL（移除USE INDEX，保留其他原有逻辑）
                base_sql = f"""
                    SELECT
                        chunk.id, chunk.team_id, chunk.kb_id, chunk.doc_id, chunk.doc_name,
                        chunk.text, chunk.text_vector, chunk.tokens, chunk.type,
                        chunk.pre_id_in_parse_topology, chunk.parse_topology_type,
                        chunk.global_offset, chunk.local_offset, chunk.enabled,
                        chunk.status, chunk.created_time, chunk.updated_time,
                        chunk.text_vector <=> :vector AS similarity_score
                    FROM chunk
                    JOIN document ON document.id = chunk.doc_id
                    WHERE {where_clause}
                    AND (chunk.text_vector <=> :vector) IS NOT NULL
                    ORDER BY similarity_score ASC NULLS LAST
                    LIMIT :limit
                """
                # --------------------------
                # 原有逻辑：执行查询与结果处理（完全保留）
                # --------------------------
                result = await session.execute(text(base_sql), params)
                rows = result.fetchall()

                chunk_entities = []
                for row in rows:
                    chunk_entity = ChunkEntity(
                        id=row.id,
                        team_id=row.team_id,
                        kb_id=row.kb_id,
                        doc_id=row.doc_id,
                        doc_name=row.doc_name,
                        text=row.text,
                        text_vector=row.text_vector,
                        tokens=row.tokens,
                        type=row.type,
                        pre_id_in_parse_topology=row.pre_id_in_parse_topology,
                        parse_topology_type=row.parse_topology_type,
                        global_offset=row.global_offset,
                        local_offset=row.local_offset,
                        enabled=row.enabled,
                        status=row.status,
                        created_time=row.created_time,
                        updated_time=row.updated_time,
                    )
                    chunk_entities.append(chunk_entity)

                # 可选：查询结束后恢复enable_seqscan（避免影响后续查询，会话结束也会自动恢复）

                logging.info(f"向量查询耗时：{datetime.now()-st}")
                return chunk_entities

        except Exception as e:
            err = f"根据知识库ID和向量查询文档解析结果失败: {str(e)}"
            logging.exception("[ChunkManager] %s", err)
            return []

    @staticmethod
    async def get_top_k_chunk_by_kb_id_keyword(
        kb_id: uuid.UUID,
        query: str,
        top_k: int,
        doc_ids: list[uuid.UUID] = None,
        banned_ids: list[uuid.UUID] = [],
        chunk_to_type: str = None,
        pre_ids: list[uuid.UUID] = None,
        is_tight: bool = True,
    ) -> List[ChunkEntity]:
        """根据知识库ID和向量查询文档解析结果"""
        try:
            st = datetime.now()
            async with await DataBase.get_session() as session:
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(
                    kb_id
                )
                if kb_entity.tokenizer == Tokenizer.ZH.value:
                    if config["DATABASE_TYPE"].lower() == "opengauss":
                        tokenizer = "chparser"
                    else:
                        tokenizer = "zhparser"
                elif kb_entity.tokenizer == Tokenizer.EN.value:
                    tokenizer = "english"
                else:
                    if config["DATABASE_TYPE"].lower() == "opengauss":
                        tokenizer = "chparser"
                    else:
                        tokenizer = "zhparser"

                # -------------------------- 新增：提前生成 tsquery（复用逻辑，避免重复计算） --------------------------
                if is_tight:
                    # 与原similarity_score中的tsquery逻辑完全一致
                    tsquery = func.plainto_tsquery(tokenizer, query)
                else:
                    # 与原similarity_score中的tsquery逻辑完全一致
                    tsquery = func.to_tsquery(
                        func.replace(
                            func.text(func.plainto_tsquery(tokenizer, query)), "&", "|"
                        )
                    )
                # ---------------------------------------------------------------------------------------------------

                # 计算相似度分数并选择它（逻辑不变，复用上面生成的tsquery）
                similarity_score = func.ts_rank_cd(
                    ChunkEntity.text_ts_vector,
                    tsquery,  # 替换原重复的tsquery生成逻辑，直接用提前生成的
                ).label("similarity_score")

                stmt = (
                    select(ChunkEntity, similarity_score)
                    .join(DocumentEntity, DocumentEntity.id == ChunkEntity.doc_id)
                    # -------------------------- 核心新增：通过 @@ 条件强制触发 GIN 索引 --------------------------
                    .where(ChunkEntity.text_ts_vector.op("@@")(tsquery))
                    # ---------------------------------------------------------------------------------------------------
                    .where(similarity_score > 0)  # 原条件保留，顺序不变
                    .where(DocumentEntity.enabled == True)
                    .where(DocumentEntity.status != DocumentStatus.DELETED.value)
                    .where(ChunkEntity.kb_id == kb_id)
                    .where(ChunkEntity.enabled == True)
                    .where(ChunkEntity.status != ChunkStatus.DELETED.value)
                )
                if banned_ids:
                    stmt = stmt.where(ChunkEntity.id.notin_(banned_ids))
                if doc_ids is not None:
                    stmt = stmt.where(DocumentEntity.id.in_(doc_ids))
                if chunk_to_type is not None:
                    stmt = stmt.where(ChunkEntity.parse_topology_type == chunk_to_type)
                if pre_ids is not None:
                    if not pre_ids:
                        return []
                    stmt = stmt.where(ChunkEntity.pre_id_in_parse_topology.in_(pre_ids))
                # 按相似度分数排序（逻辑不变）
                stmt = stmt.order_by(similarity_score.desc())
                stmt = stmt.limit(top_k)
                result = await session.execute(stmt)
                chunk_entities = result.scalars().all()
                logging.info(
                    f"[ChunkManager] get_top_k_chunk_by_kb_id_keyword cost: {(datetime.now()-st).total_seconds()}s"
                )
                return chunk_entities
        except Exception as e:
            err = f"根据知识库ID和向量查询文档解析结果失败: {str(e)}"
            logging.exception("[ChunkManager] %s", err)
            return []

    @staticmethod
    async def get_top_k_chunk_by_kb_id_bm25(
        kb_id: uuid.UUID,
        query: str,  # 关键词列表改为单查询文本
        top_k: int,
        doc_ids: list[uuid.UUID] = None,
        banned_ids: list[uuid.UUID] = [],
        chunk_to_type: str = None,
        pre_ids: list[uuid.UUID] = None,
    ) -> List[ChunkEntity]:
        """根据知识库ID和查询文本查询文档解析结果（使用BM25直接打分）"""
        try:
            st = datetime.now()
            async with await DataBase.get_session() as session:
                # 1. 构建查询文本参数（单文本，无需CTE列表）
                params = {"query": query}

                # 2. 初始化查询（直接使用查询文本计算BM25分数）
                # 使用bindparam定义参数，避免混合使用占位符和美元符号引用
                query_param = bindparam("query")
                stmt = (
                    select(
                        ChunkEntity,
                        # 计算查询文本与chunk的BM25分数
                        ChunkEntity.text.op("<&>")(query_param).label(
                            "similarity_score"
                        ),
                    )
                    # 关联文档表
                    .join(DocumentEntity, DocumentEntity.id == ChunkEntity.doc_id)
                    # 基础过滤条件
                    .where(DocumentEntity.enabled == True)
                    .where(DocumentEntity.status != DocumentStatus.DELETED.value)
                    .where(ChunkEntity.kb_id == kb_id)
                    .where(ChunkEntity.enabled == True)
                    .where(ChunkEntity.status != ChunkStatus.DELETED.value)
                    # 过滤BM25分数大于0的结果（确保有相关性）
                    .where(ChunkEntity.text.op("<&>")(query_param) > 0)
                )

                # 3. 动态条件：禁用ID
                if banned_ids:
                    stmt = stmt.where(ChunkEntity.id.notin_(banned_ids))

                # 4. 其他动态条件
                if doc_ids is not None:
                    stmt = stmt.where(DocumentEntity.id.in_(doc_ids))
                if chunk_to_type is not None:
                    stmt = stmt.where(ChunkEntity.parse_topology_type == chunk_to_type)
                if pre_ids is not None:
                    stmt = stmt.where(ChunkEntity.pre_id_in_parse_topology.in_(pre_ids))

                # 5. 排序、限制（直接使用BM25分数排序）
                stmt = stmt.order_by(
                    ChunkEntity.text.op("<&>")(query_param).desc()
                ).limit(top_k)

                # 6. 执行查询与结果处理
                await session.execute(text("SET enable_seqscan = off;"))
                await session.execute(text("SET enable_indexscan = on;"))
                result = await session.execute(stmt, params=params)
                chunk_entities = result.scalars().all()

                # 7. 日志输出
                cost = (datetime.now() - st).total_seconds()
                logging.info(
                    f"[ChunkManager] BM25查询耗时: {cost}s "
                    f"| kb_id: {kb_id} | query: {query[:50]}... | 匹配数量: {len(chunk_entities)}"
                )
                return chunk_entities

        except Exception as e:
            err = f"BM25查询失败: kb_id={kb_id}, query={query[:50]}..., error={str(e)[:150]}"
            logging.exception("[ChunkManager] %s", err)
            return []

    @staticmethod
    async def get_top_k_chunk_by_kb_id_jieba(
        kb_id: uuid.UUID,
        query: str,  # 关键词列表改为单查询文本
        top_k: int,
        doc_ids: list[uuid.UUID] = None,
        banned_ids: list[uuid.UUID] = [],
        chunk_to_type: str = None,
        pre_ids: list[uuid.UUID] = None,
    ) -> List[ChunkEntity]:
        """根据知识库ID和关键词权重查询文档解析结果（修复NoneType报错+强制索引）"""
        try:
            keywords, weights = TokenTool.get_top_k_keywords_and_weights(query)
            if len(keywords) == 0:
                return []
            if len(keywords) != len(weights):
                return []
            if len(keywords) > 50:
                keywords = keywords[:50]
                weights = weights[:50]
            st = datetime.now()
            async with await DataBase.get_session() as session:
                # 1. 分词器选择（保留原逻辑）
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(
                    kb_id
                )
                if kb_entity.tokenizer == Tokenizer.ZH.value:
                    tokenizer = (
                        "chparser"
                        if config["DATABASE_TYPE"].lower() == "opengauss"
                        else "zhparser"
                    )
                elif kb_entity.tokenizer == Tokenizer.EN.value:
                    tokenizer = "english"
                else:
                    tokenizer = (
                        "chparser"
                        if config["DATABASE_TYPE"].lower() == "opengauss"
                        else "zhparser"
                    )

                # 2. 构建加权关键词CTE（保留原逻辑）
                params = {}
                values_clause = []
                for idx, (term, weight) in enumerate(zip(keywords, weights)):
                    params[f"term_{idx}"] = term
                    params[f"weight_{idx}"] = weight
                    values_clause.append(
                        f"(CAST(:term_{idx} AS TEXT), CAST(:weight_{idx} AS FLOAT8))"
                    )
                values_text = f"(VALUES {', '.join(values_clause)}) AS t(term, weight)"
                weighted_terms = (
                    select(
                        literal_column("t.term").label("term"),
                        literal_column("t.weight").cast(Float).label("weight"),
                    )
                    .select_from(text(values_text))
                    .cte("weighted_terms")
                )

                # 3. 初始化查询（确保stmt始终是Select对象，不直接赋值None）
                stmt = (
                    select(
                        ChunkEntity,
                        func.sum(
                            func.ts_rank_cd(
                                ChunkEntity.text_ts_vector,
                                func.to_tsquery(tokenizer, weighted_terms.c.term),
                            )
                            * weighted_terms.c.weight
                        ).label("similarity_score"),
                    )
                    # 关联文档表
                    .join(DocumentEntity, DocumentEntity.id == ChunkEntity.doc_id)
                    .join(  # 关联CTE+强制触发GIN索引（核心优化）
                        weighted_terms,
                        ChunkEntity.text_ts_vector.op("@@")(
                            func.to_tsquery(tokenizer, weighted_terms.c.term)
                        ),
                        isouter=False,
                    )
                    # 基础过滤条件
                    .where(DocumentEntity.enabled == True)
                    .where(DocumentEntity.status != DocumentStatus.DELETED.value)
                    .where(ChunkEntity.kb_id == kb_id)
                    .where(ChunkEntity.enabled == True)
                    .where(ChunkEntity.status != ChunkStatus.DELETED.value)
                )

                # 4. 动态条件：禁用ID（修复关键：用if-else确保stmt不被赋值为None）
                if banned_ids:
                    stmt = stmt.where(ChunkEntity.id.notin_(banned_ids))

                # 5. 其他动态条件（同样用if-else确保链式调用不中断）
                if doc_ids is not None:
                    stmt = stmt.where(DocumentEntity.id.in_(doc_ids))
                if chunk_to_type is not None:
                    stmt = stmt.where(ChunkEntity.parse_topology_type == chunk_to_type)
                if pre_ids is not None:
                    stmt = stmt.where(ChunkEntity.pre_id_in_parse_topology.in_(pre_ids))

                # 6. 分组、过滤分数、排序、限制行数（链式调用安全）
                stmt = (
                    stmt.group_by(ChunkEntity.id)  # 按chunk分组计算总权重
                    .order_by(  # 按总分数降序
                        func.sum(
                            func.ts_rank_cd(
                                ChunkEntity.text_ts_vector,
                                func.to_tsquery(tokenizer, weighted_terms.c.term),
                            )
                            * weighted_terms.c.weight
                        ).desc()
                    )
                    .limit(top_k)  # 限制返回数量
                )

                # 7. 执行查询与结果处理（保留原逻辑）
                result = await session.execute(stmt, params=params)
                chunk_entities = result.scalars().all()

                # 8. 日志输出
                cost = (datetime.now() - st).total_seconds()
                logging.warning(
                    f"[ChunkManager] get_top_k_chunk_by_kb_id_dynamic_weighted_keyword cost: {cost}s "
                    f"| kb_id: {kb_id} | keywords: {keywords[:2]}... | match_count: {len(chunk_entities)}"
                )
                return chunk_entities

        except Exception as e:
            # 异常日志补充关键上下文
            err = f"根据知识库ID和关键词权重查询失败: kb_id={kb_id}, keywords={keywords[:2]}..., error={str(e)[:150]}"
            logging.exception("[ChunkManager] %s", err)
            return []

    @staticmethod
    async def get_top_k_chunk_by_kb_id_dynamic_weighted_keyword(
        kb_id: uuid.UUID,
        query: str,
        top_k: int,
        doc_ids: list[uuid.UUID] = None,
        banned_ids: list[uuid.UUID] = [],
        chunk_to_type: str = None,
        pre_ids: list[uuid.UUID] = None,
    ) -> List[ChunkEntity]:
        """根据知识库ID和关键词权重查询文档解析结果（动态加权关键词）"""
        if config["DATABASE_TYPE"].lower() == "postgres":
            return await ChunkManager.get_top_k_chunk_by_kb_id_jieba(
                kb_id, query, top_k, doc_ids, banned_ids, chunk_to_type, pre_ids
            )
        else:
            return await ChunkManager.get_top_k_chunk_by_kb_id_bm25(
                kb_id, query, top_k, doc_ids, banned_ids, chunk_to_type, pre_ids
            )

    @staticmethod
    async def fetch_surrounding_chunk_by_doc_id_and_global_offset(
        doc_id: uuid.UUID,
        global_offset: int,
        top_k: int = 50,
        banned_ids: list[uuid.UUID] = [],
    ) -> List[ChunkEntity]:
        """根据文档ID和全局偏移量查询文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    select(ChunkEntity)
                    .where(
                        and_(
                            ChunkEntity.doc_id == doc_id,
                            ChunkEntity.status != ChunkStatus.DELETED.value,
                        )
                    )
                    .where(
                        and_(
                            ChunkEntity.global_offset >= global_offset - top_k,
                            ChunkEntity.global_offset <= global_offset + top_k,
                        )
                    )
                    .where(ChunkEntity.id.notin_(banned_ids))
                    .order_by(ChunkEntity.global_offset)
                )
                result = await session.execute(stmt)
                chunk_entities = result.scalars().all()
                return chunk_entities
        except Exception as e:
            err = "根据文档ID和全局偏移量查询文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)
            raise e

    @staticmethod
    async def update_chunk_text_ts_vector_by_chunk_ids(
        chunk_ids: List[uuid.UUID],
    ) -> None:
        """根据文档ID更新文档解析结果"""
        if not chunk_ids:
            return
        try:
            kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(
                (await ChunkManager.get_chunk_by_chunk_id(chunk_ids[0])).kb_id
            )
            if kb_entity.tokenizer == Tokenizer.ZH.value:
                if config["DATABASE_TYPE"].lower() == "opengauss":
                    tokenizer = "chparser"
                else:
                    tokenizer = "zhparser"
            elif kb_entity.tokenizer == Tokenizer.EN.value:
                tokenizer = "english"
            else:
                if config["DATABASE_TYPE"].lower() == "opengauss":
                    tokenizer = "chparser"
                else:
                    tokenizer = "zhparser"
            async with await DataBase.get_session() as session:
                stmt = (
                    update(ChunkEntity)
                    .where(ChunkEntity.id.in_(chunk_ids))
                    .values(
                        {
                            ChunkEntity.text_ts_vector: func.to_tsvector(
                                tokenizer, ChunkEntity.text
                            )
                        }
                    )
                )
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = "根据文档ID更新文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)

    @staticmethod
    async def update_chunk_by_doc_id(
        doc_id: uuid.UUID, chunk_dict: Dict[str, str]
    ) -> bool:
        """根据文档ID更新文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    update(ChunkEntity)
                    .where(ChunkEntity.doc_id == doc_id)
                    .values(**chunk_dict)
                )
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = "根据文档ID更新文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)

    @staticmethod
    async def update_chunk_by_chunk_id(
        chunk_id: uuid.UUID, chunk_dict: Dict[str, str]
    ) -> ChunkEntity:
        """根据文档ID更新文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    update(ChunkEntity)
                    .where(ChunkEntity.id == chunk_id)
                    .values(**chunk_dict)
                )
                await session.execute(stmt)
                await session.commit()
                stmt = select(ChunkEntity).where(ChunkEntity.id == chunk_id)
                result = await session.execute(stmt)
                chunk_entity = result.scalars().first()
                return chunk_entity
        except Exception as e:
            err = "根据文档ID更新文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)

    @staticmethod
    async def update_chunk_by_chunk_ids(
        chunk_ids: List[uuid.UUID], chunk_dict: Dict[str, str]
    ) -> list[ChunkEntity]:
        """根据文档ID更新文档解析结果"""
        try:
            async with await DataBase.get_session() as session:
                stmt = (
                    update(ChunkEntity)
                    .where(ChunkEntity.id.in_(chunk_ids))
                    .values(**chunk_dict)
                )
                await session.execute(stmt)
                await session.commit()
                stmt = select(ChunkEntity).where(ChunkEntity.id.in_(chunk_ids))
                result = await session.execute(stmt)
                chunk_entities = result.scalars().all()
                return chunk_entities
        except Exception as e:
            err = "根据文档ID更新文档解析结果失败"
            logging.exception("[ChunkManager] %s", err)
