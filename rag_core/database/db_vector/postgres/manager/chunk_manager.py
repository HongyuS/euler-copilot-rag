from sqlalchemy import (
    Column,
    String,
    Text,
    BigInteger,
    DateTime,
    func,
    Index,
    update,
    delete,
    select,
)
from typing import Optional
import logging
from rag_core.ENUM.general import ExistedStatus
from rag_core.schema.request import ListChunkRequest, SearchChunkRequest
from rag_core.schema.knowledge_base import Chunk
from rag_core.database.db_vector.postgres.engine import (
    Postgres,
    DocumentEntity,
    ChunkEntity,
)

logger = logging.getLogger(__name__)


class ChunkManager:

    @staticmethod
    async def add_chunks(chunks: list[Chunk]) -> list[str]:
        """批量添加知识块"""
        chunk_entities = []
        for chunk in chunks:
            chunk_entity = await Postgres.convertor.chunk_to_chunk_entity(chunk)
            chunk_entities.append(chunk_entity)
        batch_size = 1024
        added_ids = []
        for i in range(0, len(chunk_entities), batch_size):
            batch = chunk_entities[i : i + batch_size]
            try:
                async with await Postgres.get_session() as session:
                    session.add_all(batch)
                    await session.commit()
                added_ids.extend([chunk.id for chunk in batch])
            except Exception as e:
                err = "批量添加知识块失败"
                logger.error(f"{err}: {e}")
        return added_ids

    @staticmethod
    async def delete_deleted_chunks() -> None:
        """删除存在状态为DELETED的知识块，一次删除1024条目录"""
        batch_size = 1024
        while True:
            try:
                async with await Postgres.get_session() as session:
                    stmt = (
                        delete(ChunkEntity)
                        .where(ChunkEntity.existed_status == ExistedStatus.DELETED)
                        .limit(batch_size)
                    )
                    result = await session.execute(stmt)
                    await session.commit()
                if result.rowcount == 0:
                    break
            except Exception as e:
                err = "删除存在状态为DELETED的知识块失败"
                logger.error(f"{err}: {e}")
                break

    @staticmethod
    async def delete_chunks_by_ids(chunk_ids: list[str]) -> list[str]:
        """根据知识块ID列表删除知识块"""
        if not chunk_ids:
            return []
        batch_size = 1024
        deleted_ids = []
        for i in range(0, len(chunk_ids), batch_size):
            batch_ids = chunk_ids[i : i + batch_size]
            try:
                async with await Postgres.get_session() as session:
                    stmt = delete(ChunkEntity).where(ChunkEntity.id.in_(batch_ids))
                    await session.execute(stmt)
                    await session.commit()
                deleted_ids.extend(batch_ids)
            except Exception as e:
                err = "根据知识块ID列表删除知识块失败"
                logger.error(f"{err}: {e}")
        return deleted_ids

    @staticmethod
    async def update_chunk_text_ts_vector_by_chunk_id(chunk_id: str) -> bool:
        """根据知识块ID更新知识块文本的ts_vector，默认使用zhparser分词器"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    update(ChunkEntity)
                    .where(ChunkEntity.id == chunk_id)
                    .values(
                        {
                            ChunkEntity.text_ts_vector: func.to_tsvector(
                                "zhparser", ChunkEntity.content
                            )
                        }
                    )
                )
                await session.execute(stmt)
                await session.commit()
            return True
        except Exception as e:
            err = "根据知识块ID更新知识块文本的ts_vector失败"
            logger.error(f"{err}: {e}")
            return False

    @staticmethod
    async def update_chunk_text_by_chunk_id(chunk_id: str, text: str) -> bool:
        """根据知识块ID更新知识块文本"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    update(ChunkEntity)
                    .where(ChunkEntity.id == chunk_id)
                    .values({"text": text})
                )
                await session.execute(stmt)
                await session.commit()
            return True
        except Exception as e:
            err = "根据知识块ID更新知识块文本失败"
            logger.error(f"{err}: {e}")
            return False

    @staticmethod
    async def update_chunks_text_ts_vector_by_chunk_ids(
        chunk_ids: list[str],
    ) -> int:
        """根据知识块ID更新知识块文本的ts_vector，默认使用zhparser分词器"""
        if not chunk_ids:
            return 0
        batch_size = 1024
        updated_count = 0
        for i in range(0, len(chunk_ids), batch_size):
            batch_ids = chunk_ids[i : i + batch_size]
            try:
                async with await Postgres.get_session() as session:
                    stmt = (
                        update(ChunkEntity)
                        .where(ChunkEntity.id.in_(batch_ids))
                        .values(
                            {
                                ChunkEntity.text_ts_vector: func.to_tsvector(
                                    "zhparser", ChunkEntity.content
                                )
                            }
                        )
                    )
                    await session.execute(stmt)
                    await session.commit()
                updated_count += len(batch_ids)
            except Exception as e:
                err = "根据知识块ID更新知识块文本的ts_vector失败"
                logger.error(f"{err}: {e}")
        return updated_count

    @staticmethod
    async def update_chunk_vector_by_chunk_id(
        chunk_id: str, vector: list[float]
    ) -> bool:
        """根据知识块ID更新知识块向量"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    update(ChunkEntity)
                    .where(ChunkEntity.id == chunk_id)
                    .values({"vector": vector})
                )
                await session.execute(stmt)
                await session.commit()
            return True
        except Exception as e:
            err = "根据知识块ID更新知识块向量失败"
            logger.error(f"{err}: {e}")
            return False

    @staticmethod
    async def switch_chunks_enabled_by_chunk_ids(
        chunk_ids: list[str], enabled: bool
    ) -> list[str]:
        """根据知识块ID列表禁用/启用知识块"""
        if not chunk_ids:
            return []
        batch_size = 1024
        switched_ids = []
        for i in range(0, len(chunk_ids), batch_size):
            batch_ids = chunk_ids[i : i + batch_size]
            try:
                async with await Postgres.get_session() as session:
                    stmt = (
                        update(ChunkEntity)
                        .where(ChunkEntity.id.in_(batch_ids))
                        .values({"enabled": enabled})
                    )
                    await session.execute(stmt)
                    await session.commit()
                switched_ids.extend(batch_ids)
            except Exception as e:
                err = "根据知识块ID列表禁用/启用知识块失败"
                logger.error(f"{err}: {e}")
        return switched_ids

    @staticmethod
    async def update_chunk_existed_status_by_chunk_id(
        chunk_id: str, existed_status: ExistedStatus
    ) -> bool:
        """根据知识块ID更新知识块存在状态"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    update(ChunkEntity)
                    .where(ChunkEntity.id == chunk_id)
                    .values({"existed_status": existed_status})
                )
                await session.execute(stmt)
                await session.commit()
            return True
        except Exception as e:
            err = "根据知识块ID更新知识块存在状态失败"
            logger.error(f"{err}: {e}")
            return False

    @staticmethod
    async def update_chunks_status_by_document_id(
        document_id: str, existed_status: ExistedStatus
    ) -> int:
        """根据文档ID更新知识块存在状态"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    update(ChunkEntity)
                    .where(ChunkEntity.document_id == document_id)
                    .values({"existed_status": existed_status})
                )
                result = await session.execute(stmt)
                await session.commit()
            return result.rowcount
        except Exception as e:
            err = "根据文档ID更新知识块存在状态失败"
            logger.error(f"{err}: {e}")
            return 0

    @staticmethod
    async def list_chunks_by_document_id(
        document_id: str, req: ListChunkRequest
    ) -> tuple[int, list[Chunk]]:
        """根据文档ID分页查询知识块列表"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    select(ChunkEntity)
                    .where(ChunkEntity.document_id == document_id)
                    .where(ChunkEntity.existed_status != ExistedStatus.DELETED)
                )
                if req.content:
                    stmt = stmt.where(ChunkEntity.content.ilike(f"%{req.content}%"))
                if req.chunk_type:
                    stmt = stmt.where(ChunkEntity.chunk_type == req.chunk_type)
                if req.enabled is not None:
                    stmt = stmt.where(ChunkEntity.enabled == req.enabled)
                if req.created_at_start:
                    stmt = stmt.where(ChunkEntity.created_at >= req.created_at_start)
                if req.created_at_end:
                    stmt = stmt.where(ChunkEntity.created_at <= req.created_at_end)
                total = await session.execute(
                    stmt.with_only_columns(func.count()).order_by(None)
                )
                total_count = total.scalar()
                stmt = (
                    stmt.order_by(
                        ChunkEntity.created_at.desc()
                        if req.created_at_desc
                        else ChunkEntity.created_at.asc()
                    )
                    .offset((req.page_num - 1) * req.page_size)
                    .limit(req.page_size)
                )
                result = await session.execute(stmt)
                chunk_entities = result.scalars().all()
                chunks = []
                for chunk_entity in chunk_entities:
                    chunk = await Postgres.convertor.chunk_entity_to_chunk(chunk_entity)
                    chunks.append(chunk)
            return total_count, chunks
        except Exception as e:
            err = "根据文档ID分页查询知识块列表失败"
            logger.error(f"{err}: {e}")
            return 0, []

    @staticmethod
    async def get_surrounding_chunks(
        doc_id: str, global_offset: int, limit: int
    ) -> list[Chunk]:
        """根据文档ID和全局偏移量获取前后知识块"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    select(ChunkEntity)
                    .where(ChunkEntity.document_id == doc_id)
                    .where(ChunkEntity.existed_status != ExistedStatus.DELETED)
                    .order_by(ChunkEntity.created_at.asc())
                    .offset(global_offset - limit)
                    .limit(limit * 2 + 1)
                )
                result = await session.execute(stmt)
                chunk_entities = result.scalars().all()
                chunks = []
                for chunk_entity in chunk_entities:
                    chunk = await Postgres.convertor.chunk_entity_to_chunk(chunk_entity)
                    chunks.append(chunk)
            return chunks
        except Exception as e:
            err = "根据文档ID和全局偏移量获取前后知识块失败"
            logger.error(f"{err}: {e}")
            return []

    @staticmethod
    async def search_chunks_by_keywords(
        kb_ids: list[str],
        query: str,
        top_k: int,
        doc_ids: Optional[list[str]] = None,
        banned_ids: Optional[list[str]] = None,
        is_tight: bool = True,
    ) -> list[Chunk]:
        """根据知识库ID列表和查询内容搜索知识块"""
        if not kb_ids:
            return []
        if doc_ids is not None and not doc_ids:
            return []
        chunk_entities = []
        async with await Postgres.get_session() as session:
            if is_tight:
                # 紧匹配：使用 plainto_tsquery 生成 tsquery，默认使用 zhparser 分词器
                tsquery = func.plainto_tsquery("zhparser", query)
            else:
                # 松匹配：使用 plainto_tsquery 生成 tsquery 后，将其中的 & 替换为 |，默认使用 zhparser 分词器
                tsquery = func.to_tsquery(
                    func.replace(
                        func.text(func.plainto_tsquery("zhparser", query)), "&", "|"
                    )
                )
            similarity_score = func.ts_rank_cd(
                ChunkEntity.text_ts_vector, tsquery
            ).label("similarity_score")
            stmt = (
                select(ChunkEntity, similarity_score)
                .join(DocumentEntity, DocumentEntity.id == ChunkEntity.doc_id)
                .where(ChunkEntity.text_ts_vector.op("@@")(tsquery))
                .where(similarity_score > 0)
                .where(DocumentEntity.enabled == True)
                .where(DocumentEntity.status != ExistedStatus.DELETED.value)
                .where(ChunkEntity.kb_id.in_(kb_ids))
                .where(ChunkEntity.enabled == True)
                .where(ChunkEntity.status != ExistedStatus.DELETED.value)
            )
            if doc_ids:
                stmt = stmt.where(DocumentEntity.id.in_(doc_ids))
            if banned_ids:
                stmt = stmt.where(ChunkEntity.id.notin_(banned_ids))
            stmt = stmt.order_by(similarity_score.desc())
            stmt = stmt.limit(top_k)
            result = await session.execute(stmt)
            chunk_entities = result.scalars().all()
        chunks = []
        for chunk_entity in chunk_entities:
            chunk = await Postgres.convertor.chunk_entity_to_chunk(chunk_entity)
            chunks.append(chunk)
        return chunks

    @staticmethod
    async def search_chunks_by_vector(
        kb_ids: list[str],
        vector: list[float],
        top_k: int,
        doc_ids: Optional[list[str]] = None,
        banned_ids: Optional[list[str]] = None,
    ):
        """根据知识库ID列表和查询向量搜索知识块"""
        if not kb_ids:
            return []
        if doc_ids is not None and not doc_ids:
            return []
        chunk_entities = []
        async with await Postgres.get_session() as session:
            vector_param = str(vector)
            similarity_score = func.cosine_similarity(
                ChunkEntity.text_vector, vector_param
            ).label("similarity_score")
            stmt = (
                select(ChunkEntity, similarity_score)
                .join(DocumentEntity, DocumentEntity.id == ChunkEntity.doc_id)
                .where(ChunkEntity.text_vector.isnot(None))
                .where(similarity_score > 0)
                .where(DocumentEntity.enabled == True)
                .where(DocumentEntity.status != ExistedStatus.DELETED.value)
                .where(ChunkEntity.kb_id.in_(kb_ids))
                .where(ChunkEntity.enabled == True)
                .where(ChunkEntity.status != ExistedStatus.DELETED.value)
            )
            if doc_ids:
                stmt = stmt.where(DocumentEntity.id.in_(doc_ids))
            if banned_ids:
                stmt = stmt.where(ChunkEntity.id.notin_(banned_ids))
            stmt = stmt.order_by(similarity_score.desc())
            stmt = stmt.limit(top_k)
            result = await session.execute(stmt)
            chunk_entities = result.scalars().all()
        chunks = []
        for chunk_entity in chunk_entities:
            chunk = await Postgres.convertor.chunk_entity_to_chunk(chunk_entity)
            chunks.append(chunk)
        return chunks
