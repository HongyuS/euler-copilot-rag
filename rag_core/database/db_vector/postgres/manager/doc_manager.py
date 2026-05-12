from datetime import datetime, timezone
from sqlalchemy import (
    func,
    update,
    delete,
    select,
)
from typing import Optional
import logging
from rag_core.ENUM.general import ExistedStatus
from rag_core.schema.request import ListDocRequest
from rag_core.schema.knowledge_base import Document
from rag_core.database.db_vector.postgres.engine import (
    Postgres,
    DocumentEntity,
)

logger = logging.getLogger(__name__)


class DocManager:
    @staticmethod
    async def add_docs(docs: list[Document]) -> list[str]:
        """批量添加文档，返回添加的文档ID列表"""
        doc_entities = []
        for doc in docs:
            doc_entity = await Postgres.convertor.document_to_document_entity(doc)
            doc_entities.append(doc_entity)
        batch_size = 1024
        added_ids = []
        for i in range(0, len(doc_entities), batch_size):
            batch = doc_entities[i : i + batch_size]
            try:
                async with await Postgres.get_session() as session:
                    session.add_all(batch)
                    await session.commit()
                added_ids.extend([doc.id for doc in batch])
            except Exception as e:
                logger.error(f"批量添加文档失败，错误信息：{e}")
        return added_ids

    @staticmethod
    async def delete_docs_deleted() -> None:
        """删除存在状态为DELETED的文档，一次删除1024条目录"""
        batch_size = 1024
        while True:
            try:
                async with await Postgres.get_session() as session:
                    stmt = (
                        select(DocumentEntity.id)
                        .where(DocumentEntity.status == ExistedStatus.DELETED.value)
                        .limit(batch_size)
                    )
                    result = await session.execute(stmt)
                    deleted_ids = [row[0] for row in result.fetchall()]
                    if not deleted_ids:
                        break
                    delete_stmt = delete(DocumentEntity).where(
                        DocumentEntity.id.in_(deleted_ids)
                    )
                    await session.execute(delete_stmt)
                    await session.commit()
            except Exception as e:
                logger.error(f"批量删除文档失败，错误信息：{e}")
                break

    @staticmethod
    async def update_doc_abstract_ts_vector_by_doc_id(doc_id) -> bool:
        """根据文档ID更新文档摘要的ts_vector字段"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    update(DocumentEntity)
                    .where(DocumentEntity.id == doc_id)
                    .values(
                        {
                            DocumentEntity.abstract_ts_vector: func.to_tsvector(
                                "zhparser", DocumentEntity.abstract
                            )
                        }
                    )
                )
                await session.execute(stmt)
                await session.commit()
            return True
        except Exception as e:
            err = "根据文档ID更新文档摘要的ts_vector失败"
            logger.error(f"{err}: {e}")
            return False

    @staticmethod
    async def update_doc(doc_id: str, doc_info_dict: dict) -> bool:
        """根据文档ID更新文档信息"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    update(DocumentEntity)
                    .where(DocumentEntity.id == doc_id)
                    .values(doc_info_dict)
                )
                await session.execute(stmt)
                await session.commit()
            return True
        except Exception as e:
            err = "根据文档ID更新文档信息失败"
            logger.error(f"{err}: {e}")
            return False

    @staticmethod
    async def switch_doc_enabled_by_doc_ids(
        doc_ids: list[str], enabled: bool
    ) -> list[str]:
        """根据文档ID列表禁用/启用文档"""
        batch_size = 1024
        switched_ids = []
        for i in range(0, len(doc_ids), batch_size):
            batch = doc_ids[i : i + batch_size]
            try:
                async with await Postgres.get_session() as session:
                    stmt = (
                        update(DocumentEntity)
                        .where(DocumentEntity.id.in_(batch))
                        .values({"enabled": enabled})
                    )
                    await session.execute(stmt)
                    await session.commit()
                switched_ids.extend(batch)
            except Exception as e:
                logger.error(f"批量禁用/启用文档失败，错误信息：{e}")
        return switched_ids

    @staticmethod
    async def update_doc_existed_status_by_doc_id(
        doc_id: str, existed_status: ExistedStatus
    ) -> bool:
        """根据文档ID更新文档存在状态"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    update(DocumentEntity)
                    .where(DocumentEntity.id == doc_id)
                    .values({"status": existed_status.value})
                )
                await session.execute(stmt)
                await session.commit()
            return True
        except Exception as e:
            err = "根据文档ID更新文档存在状态失败"
            logger.error(f"{err}: {e}")
            return False

    @staticmethod
    async def list_docs(kb_id: str, req: ListDocRequest) -> tuple[int, list[Document]]:
        """根据知识库ID分页查询文档列表"""
        try:
            async with await Postgres.get_session() as session:
                stmt = select(DocumentEntity).where(DocumentEntity.kb_id == kb_id)
                if req.name:
                    stmt = stmt.where(DocumentEntity.name.ilike(f"%{req.name}%"))
                if req.owner_id:
                    stmt = stmt.where(DocumentEntity.owner_id == req.owner_id)
                if req.owner_name:
                    stmt = stmt.where(
                        DocumentEntity.owner_name.ilike(f"%{req.owner_name}%")
                    )
                if req.enabled is not None:
                    stmt = stmt.where(DocumentEntity.enabled == req.enabled)
                if req.created_at_start:
                    stmt = stmt.where(
                        DocumentEntity.created_at
                        >= datetime.strptime(
                            req.created_at_start, "%Y-%m-%d %H:%M"
                        ).replace(tzinfo=timezone.utc)
                    )
                if req.created_at_end:
                    stmt = stmt.where(
                        DocumentEntity.created_at
                        <= datetime.strptime(
                            req.created_at_end, "%Y-%m-%d %H:%M"
                        ).replace(tzinfo=timezone.utc)
                    )
                if req.created_at_desc:
                    stmt = stmt.order_by(DocumentEntity.created_at.desc())
                total_result = await session.execute(
                    stmt.with_only_columns(func.count()).order_by(None)
                )
                total = total_result.scalar()
                stmt = stmt.offset((req.page_num - 1) * req.page_size).limit(
                    req.page_size
                )
                result = await session.execute(stmt)
                docs = result.scalars().all()
                doc_list = [
                    await Postgres.convertor.document_entity_to_document(doc) for doc in docs
                ]
            return total, doc_list
        except Exception as e:
            logger.error(f"根据知识库ID分页查询文档列表失败，错误信息：{e}")
            return 0, []

    @staticmethod
    async def get_doc_by_id(doc_id: str) -> Optional[Document]:
        """根据文档ID查询文档信息"""
        try:
            async with await Postgres.get_session() as session:
                stmt = select(DocumentEntity).where(DocumentEntity.id == doc_id)
                result = await session.execute(stmt)
                doc_entity = result.scalar_one_or_none()
                if doc_entity:
                    return await Postgres.convertor.document_entity_to_document(doc_entity)
                else:
                    return None
        except Exception as e:
            logger.error(f"根据文档ID查询文档信息失败，错误信息：{e}")

    @staticmethod
    async def get_docs_cnt_and_size_by_kb_id(kb_id: str) -> tuple[int, int]:
        """根据知识库ID查询文档数量和文档总大小"""
        try:
            async with await Postgres.get_session() as session:
                stmt = select(
                    func.count(), func.coalesce(func.sum(DocumentEntity.size), 0)
                ).where(DocumentEntity.kb_id == kb_id)
                result = await session.execute(stmt)
                doc_cnt, total_size = result.fetchone()
            return doc_cnt, total_size
        except Exception as e:
            logger.error(f"根据知识库ID查询文档数量和文档总大小失败，错误信息：{e}")
            return 0, 0

    @staticmethod
    async def search_docs_by_keywords(
        kb_ids: list[str],
        query: str,
        top_k: int,
        doc_ids: Optional[list[str]] = None,
        banned_doc_ids: Optional[list[str]] = None,
        is_tight: bool = True,
    ) -> list[Document]:
        """根据关键词搜索文档，返回匹配的文档列表"""
        if not kb_ids:
            return []
        if doc_ids is not None and not doc_ids:
            return []
        doc_entities = []
        async with await Postgres.get_session() as session:
            if is_tight:
                tsquery = func.plainto_tsquery("zhparser", query)
            else:
                tsquery = func.to_tsquery(
                    func.replace(
                        func.text(func.plainto_tsquery("zhparser", query)), "&", "|"
                    )
                )
            similarity_score = func.ts_rank_cd(
                DocumentEntity.abstract_ts_vector, tsquery
            ).label("similarity_score")
            stmt = (
                select(DocumentEntity, similarity_score)
                .where(DocumentEntity.abstract_ts_vector.op("@@")(tsquery))
                .where(similarity_score > 0)
                .where(DocumentEntity.enabled == True)
                .where(DocumentEntity.status != ExistedStatus.DELETED.value)
                .where(DocumentEntity.kb_id.in_(kb_ids))
            )
            if doc_ids:
                stmt = stmt.where(DocumentEntity.id.in_(doc_ids))
            if banned_doc_ids:
                stmt = stmt.where(DocumentEntity.id.notin_(banned_doc_ids))
            stmt = stmt.order_by(similarity_score.desc())
            stmt = stmt.limit(top_k)
            result = await session.execute(stmt)
            doc_entities = result.scalars().all()
        docs = []
        for doc_entity in doc_entities:
            doc = await Postgres.convertor.document_entity_to_document(doc_entity)
            docs.append(doc)
        return docs

    @staticmethod
    async def search_docs_by_vector(
        kb_ids: list[str],
        vector: list[float],
        top_k: int,
        doc_ids: Optional[list[str]] = None,
        banned_doc_ids: Optional[list[str]] = None,
    ) -> list[Document]:
        """根据查询向量搜索文档，返回匹配的文档列表"""
        if not kb_ids:
            return []
        if doc_ids is not None and not doc_ids:
            return []
        doc_entities = []
        async with await Postgres.get_session() as session:
            vector_param = str(vector)
            similarity_score = func.cosine_similarity(
                DocumentEntity.abstract_vector, vector_param
            ).label("similarity_score")
            stmt = (
                select(DocumentEntity, similarity_score)
                .where(DocumentEntity.abstract_vector.isnot(None))
                .where(similarity_score > 0)
                .where(DocumentEntity.enabled == True)
                .where(DocumentEntity.kb_id.in_(kb_ids))
                .where(DocumentEntity.status != ExistedStatus.DELETED.value)
            )
            if doc_ids:
                stmt = stmt.where(DocumentEntity.id.in_(doc_ids))
            if banned_doc_ids:
                stmt = stmt.where(DocumentEntity.id.notin_(banned_doc_ids))
            stmt = stmt.order_by(similarity_score.desc())
            stmt = stmt.limit(top_k)
            result = await session.execute(stmt)
            doc_entities = result.scalars().all()
        docs = []
        for doc_entity in doc_entities:
            doc = await Postgres.convertor.document_entity_to_document(doc_entity)
            docs.append(doc)
        return docs
