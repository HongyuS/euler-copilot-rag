# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
from sqlalchemy import select, delete, update, func, between, asc, desc, and_, Float, literal_column, text, bindparam
from datetime import datetime, timezone
import uuid
from typing import Dict, List, Tuple

from data_chain.config.config import config
from data_chain.entities.enum import TaskStatus, OrderType
from data_chain.stores.database.database import DataBase, KnowledgeBaseEntity, DocumentTypeEntity, DocumentEntity, TaskEntity
from data_chain.entities.enum import KnowledgeBaseStatus, DocumentStatus
from data_chain.manager.knowledge_manager import KnowledgeBaseManager
from data_chain.entities.enum import Tokenizer, ChunkStatus
from data_chain.entities.request_data import ListDocumentRequest
from data_chain.parser.tools.token_tool import TokenTool
from data_chain.logger.logger import logger as logging


class DocumentManager():
    """文档管理类"""

    @staticmethod
    async def add_document(document_entity: DocumentEntity) -> DocumentEntity:
        """添加文档"""
        try:
            async with await DataBase.get_session() as session:
                session.add(document_entity)
                await session.commit()
                return document_entity
        except Exception as e:
            err = "添加文档失败"
            logging.exception("[DocumentManager] %s", err)

    @staticmethod
    async def add_documents(document_entities: List[DocumentEntity]) -> List[DocumentEntity]:
        """批量添加文档"""
        try:
            async with await DataBase.get_session() as session:
                session.add_all(document_entities)
                await session.commit()
                for document_entity in document_entities:
                    await session.refresh(document_entity)
                return document_entities
        except Exception as e:
            err = "批量添加文档失败"
            logging.exception("[DocumentManager] %s", err)

    @staticmethod
    async def get_top_k_document_by_kb_id_vector(
            kb_id: uuid.UUID, vector: list[float],
            top_k: int = 5, doc_ids: list[uuid.UUID] = None, banned_ids: list[uuid.UUID] = []) -> List[DocumentEntity]:
        """根据知识库ID和向量获取前K个文档"""
        try:
            if top_k <= 0:
                return []
            # 构建基础WHERE条件
            where_conditions = [
                "document.kb_id = :kb_id",
                "document.status != :deleted_status",
                "document.enabled = TRUE",
                "document.abstract_vector IS NOT NULL"
            ]

            # 处理向量格式兼容性：PostgreSQL需要字符串格式，OpenGauss可以直接使用列表
            if config['DATABASE_TYPE'].lower() == 'opengauss':
                vector_param = vector
            else:
                # PostgreSQL需要将向量转换为字符串格式
                vector_param = str(vector)

            # 构建参数字典
            params = {
                "vector": vector_param,
                "kb_id": kb_id,
                "deleted_status": DocumentStatus.DELETED.value
            }

            # 添加banned_ids条件
            if banned_ids:
                banned_placeholders = []
                for i, banned_id in enumerate(banned_ids):
                    param_name = f"banned_id_{i}"
                    banned_placeholders.append(f":{param_name}")
                    params[param_name] = banned_id
                where_conditions.append(
                    f"document.id NOT IN ({','.join(banned_placeholders)})")

            # 添加doc_ids条件
            if doc_ids is not None:
                doc_placeholders = []
                for i, doc_id in enumerate(doc_ids):
                    param_name = f"doc_id_{i}"
                    doc_placeholders.append(f":{param_name}")
                    params[param_name] = doc_id
                where_conditions.append(
                    f"document.id IN ({','.join(doc_placeholders)})")

            # 组合WHERE条件
            where_clause = " AND ".join(where_conditions)

            # 构建查询SQL - 添加分数有效性检查
            base_sql = f"""
                SELECT 
                    document.id, document.team_id, document.kb_id, document.author_id, 
                    document.author_name, document.name, document.extension, 
                    document.size, document.parse_method, document.parse_relut_topology, 
                    document.chunk_size, document.type_id, document.enabled, 
                    document.status, document.full_text, document.abstract, 
                    document.abstract_vector, document.created_time, document.updated_time,
                    document.abstract_vector <=> :vector AS similarity_score
                FROM document 
                WHERE {where_clause}
                AND (document.abstract_vector <=> :vector) IS NOT NULL
                AND (document.abstract_vector <=> :vector) = (document.abstract_vector <=> :vector)
                ORDER BY similarity_score ASC NULLS LAST
                LIMIT :limit
            """
            # 增加searcher数量，提升向量检索性能（可选）
            async with await DataBase.get_session() as session:
                await session.execute(text("SET enable_seqscan = off;"))
                await session.execute(text("SET enable_indexscan = on;"))
                await session.execute(text("SET hnsw.ef_search = 1000;"))
                params["limit"] = top_k
                result = await session.execute(text(base_sql), params)
                rows = result.fetchall()
                document_entities = []
                for row in rows:
                    doc_entity = DocumentEntity(
                        id=row.id,
                        team_id=row.team_id,
                        kb_id=row.kb_id,
                        author_id=row.author_id,
                        author_name=row.author_name,
                        name=row.name,
                        extension=row.extension,
                        size=row.size,
                        parse_method=row.parse_method,
                        parse_relut_topology=row.parse_relut_topology,
                        chunk_size=row.chunk_size,
                        type_id=row.type_id,
                        enabled=row.enabled,
                        status=row.status,
                        full_text=row.full_text,
                        abstract=row.abstract,
                        abstract_vector=row.abstract_vector,
                        created_time=row.created_time,
                        updated_time=row.updated_time
                    )
                    document_entities.append(doc_entity)
                return document_entities
        except Exception as e:
            err = "获取前K个文档失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def get_top_k_document_by_kb_id_keyword(
            kb_id: uuid.UUID, query: str, top_k: int = 5, doc_ids: list[uuid.UUID] = None, banned_ids: list[uuid.UUID] = []) -> List[DocumentEntity]:
        """根据知识库ID和关键词获取前K个文档"""
        try:
            async with await DataBase.get_session() as session:
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(kb_id)
                # 设置分词器，增加默认值处理
                if kb_entity.tokenizer == Tokenizer.ZH.value:
                    if config['DATABASE_TYPE'].lower() == 'opengauss':
                        tokenizer = 'chparser'
                    else:
                        tokenizer = 'zhparser'
                elif kb_entity.tokenizer == Tokenizer.EN.value:
                    tokenizer = 'english'
                else:
                    # 增加默认分词器处理，与第一个方法保持一致
                    if config['DATABASE_TYPE'].lower() == 'opengauss':
                        tokenizer = 'chparser'
                    else:
                        tokenizer = 'zhparser'

                # 提前生成tsquery，复用逻辑
                tsquery = func.to_tsquery(
                    func.replace(
                        func.text(func.plainto_tsquery(tokenizer, query)),
                        '&', '|'
                    )
                )

                # 计算相似度分数，使用提前生成的tsquery
                similarity_score = func.ts_rank_cd(
                    DocumentEntity.abstract_ts_vector,
                    tsquery
                ).label("similarity_score")

                stmt = (
                    select(DocumentEntity, similarity_score)
                    .where(DocumentEntity.kb_id == kb_id)
                    .where(DocumentEntity.id.notin_(banned_ids))
                    .where(DocumentEntity.status != DocumentStatus.DELETED.value)
                    .where(DocumentEntity.enabled == True)
                    # 新增：通过@@条件强制触发GIN索引
                    .where(DocumentEntity.abstract_ts_vector.op('@@')(tsquery))
                    # 新增：过滤相似度大于0的结果
                    .where(similarity_score > 0)
                )
                if doc_ids:
                    stmt = stmt.where(DocumentEntity.id.in_(doc_ids))

                stmt = stmt.order_by(
                    similarity_score.desc()
                )
                stmt = stmt.limit(top_k)
                result = await session.execute(stmt)
                document_entities = result.scalars().all()
                return document_entities
        except Exception as e:
            err = "获取前K个文档失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def get_top_k_document_by_kb_id_bm25(
            kb_id: uuid.UUID, query: str,  # 关键词列表改为单查询文本，移除weights参数
            top_k: int, doc_ids: list[uuid.UUID] = None, banned_ids: list[uuid.UUID] = []) -> List[DocumentEntity]:
        """根据知识库ID和查询文本查询文档（BM25检索版，匹配abstract_bm25_index索引）"""
        try:
            st = datetime.now()
            async with await DataBase.get_session() as session:
                # 1. 构建查询文本参数（单文本，无需CTE列表）
                params = {"query": query}

                # 2. 初始化查询（直接使用查询文本计算BM25分数）
                query_param = bindparam("query")
                stmt = (
                    select(
                        DocumentEntity,
                        # 计算查询文本与文档abstract的BM25分数
                        DocumentEntity.abstract.op('<&>')(
                            query_param).label("similarity_score")
                    )
                    # 基础过滤条件
                    .where(DocumentEntity.enabled == True)
                    .where(DocumentEntity.status != DocumentStatus.DELETED.value)
                    .where(DocumentEntity.kb_id == kb_id)
                    # 过滤BM25分数大于0的结果（确保有相关性）
                    .where(DocumentEntity.abstract.op('<&>')(query_param) > 0)
                )

                # 3. 动态条件：禁用ID
                if banned_ids:
                    stmt = stmt.where(DocumentEntity.id.notin_(banned_ids))

                # 4. 其他动态条件：指定文档ID过滤
                if doc_ids is not None:
                    stmt = stmt.where(DocumentEntity.id.in_(doc_ids))

                # 5. 排序、限制（直接使用BM25分数排序）
                stmt = (stmt
                        .order_by(
                            DocumentEntity.abstract.op(
                                '<&>')(query_param).desc()
                        )
                        .limit(top_k)
                        )

                # 6. 执行查询与结果处理
                await session.execute(text("SET enable_seqscan = off;"))
                await session.execute(text("SET enable_indexscan = on;"))
                result = await session.execute(stmt, params=params)
                doc_entities = result.scalars().all()

                # 7. 日志输出
                cost = (datetime.now() - st).total_seconds()
                logging.warning(
                    f"[DocumentManager] BM25检索文档耗时: {cost}s "
                    f"| kb_id: {kb_id} | query: {query[:50]}... | 匹配数量: {len(doc_entities)}"
                )
                return doc_entities

        except Exception as e:
            err = f"BM25检索文档失败: kb_id={kb_id}, query={query[:50]}..., error={str(e)[:150]}"
            logging.exception("[DocumentManager] %s", err)
            return []

    @staticmethod
    async def get_top_k_document_by_kb_id_jieba(
            kb_id: uuid.UUID, query: str,  # 关键词列表改为单查询文本，移除weights参数
            top_k: int, doc_ids: list[uuid.UUID] = None, banned_ids: list[uuid.UUID] = []) -> List[DocumentEntity]:
        try:
            keywords, weights = TokenTool.get_top_k_keywords_and_weights(query)
            if len(keywords) == 0:
                return []
            if len(keywords) != len(weights):
                return []
            if len(keywords) > 50:
                keywords = keywords[:50]
                weights = weights[:50]
            st = datetime.now()  # 新增计时日志
            async with await DataBase.get_session() as session:
                # 1. 分词器选择（与第一个方法保持一致）
                kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(kb_id)
                if kb_entity.tokenizer == Tokenizer.ZH.value:
                    tokenizer = 'chparser' if config['DATABASE_TYPE'].lower(
                    ) == 'opengauss' else 'zhparser'
                elif kb_entity.tokenizer == Tokenizer.EN.value:
                    tokenizer = 'english'
                else:
                    tokenizer = 'chparser' if config['DATABASE_TYPE'].lower(
                    ) == 'opengauss' else 'zhparser'

                # 2. 构建加权关键词CTE（保留原逻辑）
                params = {}
                values_clause = []
                for idx, (term, weight) in enumerate(zip(keywords, weights)):
                    params[f"term_{idx}"] = term
                    params[f"weight_{idx}"] = weight
                    values_clause.append(
                        f"(CAST(:term_{idx} AS TEXT), CAST(:weight_{idx} AS FLOAT8))")
                values_text = f"(VALUES {', '.join(values_clause)}) AS t(term, weight)"
                weighted_terms = (
                    select(
                        literal_column("t.term").label("term"),
                        literal_column("t.weight").cast(Float).label("weight")
                    )
                    .select_from(text(values_text))
                    .cte("weighted_terms")
                )

                # 3. 初始化查询（确保stmt始终是Select对象）
                stmt = (
                    select(
                        DocumentEntity,
                        func.sum(
                            func.ts_rank_cd(DocumentEntity.abstract_ts_vector, func.to_tsquery(
                                tokenizer, weighted_terms.c.term))
                            * weighted_terms.c.weight
                        ).label("similarity_score")
                    )
                    # 关联CTE+强制触发GIN索引（核心优化）
                    .join(
                        weighted_terms,
                        DocumentEntity.abstract_ts_vector.op(
                            '@@')(func.to_tsquery(tokenizer, weighted_terms.c.term)),
                        isouter=False
                    )
                    # 基础过滤条件
                    .where(DocumentEntity.enabled == True)
                    .where(DocumentEntity.status != DocumentStatus.DELETED.value)
                    .where(DocumentEntity.kb_id == kb_id)
                )

                # 4. 动态条件：禁用ID（确保stmt链式调用不中断）
                if banned_ids:
                    stmt = stmt.where(DocumentEntity.id.notin_(banned_ids))

                # 5. 其他动态条件
                if doc_ids is not None:
                    stmt = stmt.where(DocumentEntity.id.in_(doc_ids))

                # 6. 分组、过滤分数、排序、限制行数（链式调用安全）
                stmt = (stmt
                        .group_by(DocumentEntity.id)  # 按文档ID分组计算总权重
                        .order_by(  # 按总分数降序
                            func.sum(
                                func.ts_rank_cd(DocumentEntity.abstract_ts_vector, func.to_tsquery(
                                    tokenizer, weighted_terms.c.term))
                                * weighted_terms.c.weight
                            ).desc()
                        )
                        .limit(top_k)  # 限制返回数量
                        )

                # 7. 执行查询与结果处理
                result = await session.execute(stmt, params=params)
                doc_entities = result.scalars().all()

                # 8. 新增执行时间日志
                cost = (datetime.now() - st).total_seconds()
                logging.warning(
                    f"[DocumentManager] get_top_k_document_by_kb_id_dynamic_weighted_keyword cost: {cost}s "
                    f"| kb_id: {kb_id} | keywords: {keywords[:2]}... | match_count: {len(doc_entities)}"
                )
                return doc_entities

        except Exception as e:
            # 异常日志补充关键上下文
            err = f"根据知识库ID和关键词权重查询文档失败: kb_id={kb_id}, keywords={keywords[:2]}..., error={str(e)[:150]}"
            logging.exception("[DocumentManager] %s", err)
            return []

    @staticmethod
    async def get_top_k_document_by_kb_id_dynamic_weighted_keyword(
            kb_id: uuid.UUID, query: str,  # 关键词列表改为单查询文本，移除weights参数
            top_k: int, doc_ids: list[uuid.UUID] = None, banned_ids: list[uuid.UUID] = []) -> List[DocumentEntity]:
        """根据知识库ID和查询文本查询文档（动态加权关键词版）"""
        if config['DATABASE_TYPE'].lower() == 'postgres':
            return await DocumentManager.get_top_k_document_by_kb_id_jieba(
                kb_id, query, top_k, doc_ids, banned_ids)
        else:
            return await DocumentManager.get_top_k_document_by_kb_id_bm25(
                kb_id, query, top_k, doc_ids, banned_ids)

    @staticmethod
    async def get_doc_cnt_by_kb_id(kb_id: uuid.UUID) -> int:
        """根据知识库ID获取文档数量"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(func.count()).select_from(DocumentEntity).where(
                    and_(DocumentEntity.kb_id == kb_id,
                         DocumentEntity.status != DocumentStatus.DELETED.value))
                result = await session.execute(stmt)
                return result.scalar()
        except Exception as e:
            err = "获取文档数量失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def list_document(req: ListDocumentRequest) -> tuple[int, List[DocumentEntity]]:
        """
        列出文档
        :param req: 请求参数
        :return: 文档列表
        """
        try:
            async with await DataBase.get_session() as session:
                subq = (select(TaskEntity.op_id, TaskEntity.status, func.row_number().over(
                    partition_by=TaskEntity.op_id, order_by=desc(TaskEntity.created_time)).label('rn')).subquery())

                stmt = (
                    select(DocumentEntity)
                    .outerjoin(subq, and_(DocumentEntity.id == subq.c.op_id, subq.c.rn == 1))
                )
                stmt = stmt.where(DocumentEntity.status !=
                                  DocumentStatus.DELETED.value)
                if req.kb_id is not None:
                    stmt = stmt.where(DocumentEntity.kb_id == req.kb_id)
                if req.doc_id is not None:
                    stmt = stmt.where(DocumentEntity.id == req.doc_id)
                if req.doc_name is not None:
                    stmt = stmt.where(
                        DocumentEntity.name.ilike(f"%{req.doc_name}%"))
                if req.doc_type_ids is not None:
                    stmt = stmt.where(
                        DocumentEntity.type_id.in_(req.doc_type_ids))
                if req.parse_status is not None:
                    stmt = stmt.where(subq.c.status.in_(
                        [status.value for status in req.parse_status]))
                if req.parse_methods is not None:
                    stmt = stmt.where(DocumentEntity.parse_method.in_(
                        [parse_method.value for parse_method in req.parse_methods]))
                if req.author_name is not None:
                    stmt = stmt.where(
                        DocumentEntity.author_name.ilike(f"%{req.author_name}%"))
                if req.enabled is not None:
                    stmt = stmt.where(DocumentEntity.enabled == req.enabled)
                if req.created_time_start and req.created_time_end:
                    stmt = stmt.where(
                        between(DocumentEntity.created_time,
                                datetime.strptime(req.created_time_start,
                                                  '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc),
                                datetime.strptime(req.created_time_end, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc))
                    )
                count_stmt = select(func.count()).select_from(stmt.subquery())
                if req.created_time_order == OrderType.DESC:
                    stmt = stmt.order_by(DocumentEntity.created_time.desc())
                else:
                    stmt = stmt.order_by(DocumentEntity.created_time.asc())
                total = (await session.execute(count_stmt)).scalar()
                stmt = stmt.offset(
                    (req.page - 1) * req.page_size).limit(req.page_size)
                stmt = stmt.order_by(DocumentEntity.id.desc())
                result = await session.execute(stmt)
                document_entities = result.scalars().all()
                return (total, document_entities)
        except Exception as e:
            err = "获取文档列表失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def list_all_document_by_kb_id(kb_id: uuid.UUID) -> List[DocumentEntity]:
        """根据知识库ID获取文档列表"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(DocumentEntity).where(
                    and_(DocumentEntity.kb_id == kb_id,
                         DocumentEntity.status != DocumentStatus.DELETED.value))
                result = await session.execute(stmt)
                document_entities = result.scalars().all()
                return document_entities
        except Exception as e:
            err = "获取所有文档列表失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def list_document_by_doc_ids(doc_ids: list[uuid.UUID]) -> List[DocumentEntity]:
        """根据文档ID获取文档列表"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(DocumentEntity).where(
                    and_(DocumentEntity.id.in_(doc_ids),
                         DocumentEntity.status != DocumentStatus.DELETED.value))
                result = await session.execute(stmt)
                document_entities = result.scalars().all()
                return document_entities
        except Exception as e:
            err = "获取文档列表失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def get_document_by_doc_id(doc_id: uuid.UUID) -> DocumentEntity:
        """根据文档ID获取文档"""
        try:
            async with await DataBase.get_session() as session:
                stmt = select(DocumentEntity).where(
                    and_(DocumentEntity.id == doc_id,
                         DocumentEntity.status != DocumentStatus.DELETED.value))
                result = await session.execute(stmt)
                document_entity = result.scalars().first()
                return document_entity
        except Exception as e:
            err = "获取文档失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def update_document_abstract_ts_vector_by_doc_ids(doc_ids: list[uuid.UUID]) -> None:
        """根据文档ID批量更新文档摘要词向量"""
        try:
            kb_entity = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(
                (await DocumentManager.get_document_by_doc_id(doc_ids[0])).kb_id)
            if kb_entity.tokenizer == Tokenizer.ZH.value:
                if config['DATABASE_TYPE'].lower() == 'opengauss':
                    tokenizer = 'chparser'
                else:
                    tokenizer = 'zhparser'
            elif kb_entity.tokenizer == Tokenizer.EN.value:
                tokenizer = 'english'
            else:
                if config['DATABASE_TYPE'].lower() == 'opengauss':
                    tokenizer = 'chparser'
                else:
                    tokenizer = 'zhparser'
            async with await DataBase.get_session() as session:
                stmt = update(DocumentEntity).where(
                    and_(DocumentEntity.id.in_(doc_ids),
                         DocumentEntity.status != DocumentStatus.DELETED.value)
                ).values(abstract_ts_vector=func.to_tsvector(tokenizer, DocumentEntity.abstract))
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            err = "批量更新文档摘要词向量失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def update_doc_type_by_kb_id(
            kb_id: uuid.UUID, old_doc_type_ids: list[uuid.UUID],
            new_doc_type_id: uuid.UUID) -> None:
        """根据知识库ID更新文档类型"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(DocumentEntity).where(
                    and_(DocumentEntity.kb_id == kb_id,
                         DocumentEntity.status != DocumentStatus.DELETED.value,
                         DocumentEntity.type_id.in_(old_doc_type_ids))
                ).values(type_id=new_doc_type_id)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            err = "更新文档类型失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def update_document_by_doc_id(doc_id: uuid.UUID, doc_dict: Dict[str, str]) -> DocumentEntity:
        """根据文档ID更新文档"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(DocumentEntity).where(
                    and_(DocumentEntity.id == doc_id,
                         DocumentEntity.status != DocumentStatus.DELETED.value)
                ).values(**doc_dict)
                await session.execute(stmt)
                await session.commit()
                return await DocumentManager.get_document_by_doc_id(doc_id)
        except Exception as e:
            err = "更新文档失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def update_document_by_doc_ids(doc_ids: list[uuid.UUID], doc_dict: Dict[str, str]) -> list[DocumentEntity]:
        """根据文档ID批量更新文档"""
        try:
            async with await DataBase.get_session() as session:
                stmt = update(DocumentEntity).where(
                    and_(DocumentEntity.id.in_(doc_ids),
                         DocumentEntity.status != DocumentStatus.DELETED.value)
                ).values(**doc_dict)
                await session.execute(stmt)
                await session.commit()
                stmt = select(DocumentEntity).where(
                    DocumentEntity.id.in_(doc_ids)
                )
                result = await session.execute(stmt)
                document_entities = result.scalars().all()
                return document_entities
        except Exception as e:
            err = "批量更新文档失败"
            logging.exception("[DocumentManager] %s", err)
            raise e

    @staticmethod
    async def delte_document_by_doc_id(doc_id: uuid.UUID) -> None:
        """根据文档ID删除文档"""
        pass

    @staticmethod
    async def delete_document_by_kb_id(kb_id: uuid.UUID) -> None:
        """根据知识库ID删除文档"""
        pass

    @staticmethod
    async def delete_document_by_doc_id(doc_id: uuid.UUID) -> None:
        """根据文档ID删除文档"""
        pass

    @staticmethod
    async def delete_document_by_doc_ids(doc_ids: list[uuid.UUID]) -> None:
        """根据文档ID批量删除文档"""
        pass
