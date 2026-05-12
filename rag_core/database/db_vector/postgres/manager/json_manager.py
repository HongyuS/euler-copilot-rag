from datetime import datetime, timezone
from sqlalchemy import (
    func,
    delete,
    update,
    select,
    false,
)
from typing import Optional
import logging
from rag_core.ENUM.general import ExistedStatus
from rag_core.schema.json import LogicalExpression
from rag_core.schema.request import ListJsonRequest
from rag_core.schema.knowledge_base import Json
from rag_core.database.db_vector.postgres.engine import (
    Postgres,
    JsonEntity,
    JsonValueEntity,
)

logger = logging.getLogger(__name__)


class JsonManager:
    @staticmethod
    async def add_jsons(jsons: list[Json]) -> list[str]:
        """批量添加JSON"""
        json_entities = []
        for json in jsons:
            json_entity = await Postgres.convertor.json_to_json_entity(json)
            json_entities.append(json_entity)
        batch_size = 1024
        added_ids = []
        for i in range(0, len(json_entities), batch_size):
            batch = json_entities[i : i + batch_size]
            try:
                async with await Postgres.get_session() as session:
                    session.add_all(batch)
                    await session.commit()
                added_ids.extend([json.id for json in batch])
            except Exception as e:
                err = "批量添加JSON失败"
                logger.error(f"{err}: {e}")
        return added_ids

    @staticmethod
    async def add_json_values(
        json_id: str, key_path_and_value_list: list[tuple[list[str], str, list[float]]]
    ) -> bool:
        """批量添加JSON值"""
        json_value_entities = []
        for key_path, value, vector in key_path_and_value_list:
            json_value_entity = JsonValueEntity(
                json_id=json_id,
                key=key_path,
                value=value,
                value_vector=vector,
            )
            json_value_entities.append(json_value_entity)
        batch_size = 1024
        for i in range(0, len(json_value_entities), batch_size):
            batch = json_value_entities[i : i + batch_size]
            try:
                async with await Postgres.get_session() as session:
                    session.add_all(batch)
                    await session.commit()
            except Exception as e:
                err = "批量添加JSON值失败"
                logger.error(f"{err}: {e}")
                return False
        return True

    @staticmethod
    async def update_jsons_value_value_ts_vector_by_json_id(json_id: str) -> bool:
        """根据JSON ID更新JSON值的ts_vector，默认使用zhparser分词器"""
        try:
            async with await Postgres.get_session() as session:
                stmt = (
                    update(JsonValueEntity)
                    .where(JsonValueEntity.json_id == json_id)
                    .values(
                        {
                            JsonValueEntity.value_ts_vector: func.to_tsvector(
                                "zhparser", JsonValueEntity.value
                            )
                        }
                    )
                )
                await session.execute(stmt)
                await session.commit()
                return True
        except Exception as e:
            err = "根据JSON ID更新JSON值的ts_vector失败"
            logger.error(f"{err}: {e}")
            return False

    @staticmethod
    async def delete_jsons_by_json_ids(json_ids: list[str]) -> list[str]:
        """根据JSON ID批量删除JSON"""
        batch_size = 1024
        deleted_ids = []
        for i in range(0, len(json_ids), batch_size):
            batch = json_ids[i : i + batch_size]
            try:
                async with await Postgres.get_session() as session:
                    stmt = delete(JsonEntity).where(JsonEntity.id.in_(batch))
                    await session.execute(stmt)
                    await session.commit()
                    deleted_ids.extend(batch)
            except Exception as e:
                err = "批量删除JSON失败"
                logger.error(f"{err}: {e}")
        return deleted_ids

    @staticmethod
    async def list_jsons(kb_id: str, request: ListJsonRequest) -> list[Json]:
        """列举JSON"""
        try:
            async with await Postgres.get_session() as session:
                stmt = select(JsonEntity).where(JsonEntity.kb_id == kb_id)
                if request.name:
                    stmt = stmt.where(JsonEntity.name.ilike(f"%{request.name}%"))
                if request.created_at_start:
                    created_at_start = datetime.strptime(
                        request.created_at_start, "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc)
                    stmt = stmt.where(JsonEntity.created_at >= created_at_start)
                if request.created_at_end:
                    created_at_end = datetime.strptime(
                        request.created_at_end, "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc)
                    stmt = stmt.where(JsonEntity.created_at <= created_at_end)
                if request.created_at_desc:
                    stmt = stmt.order_by(JsonEntity.created_at.desc())
                else:
                    stmt = stmt.order_by(JsonEntity.created_at.asc())
                stmt = stmt.offset((request.page_num - 1) * request.page_size).limit(
                    request.page_size
                )
                result = await session.execute(stmt)
                json_entities = result.scalars().all()
                jsons = []
                for json_entity in json_entities:
                    json = await Postgres.convertor.json_entity_to_json(json_entity)
                    jsons.append(json)
                return jsons
        except Exception as e:
            err = "列举JSON失败"
            logger.error(f"{err}: {e}")
            return []

    @staticmethod
    async def search_jsons_by_logical_expression(
        kb_ids: list[str],
        logical_expression: LogicalExpression,
        top_k: int,
        banned_json_ids: Optional[list[str]],
    ) -> list[Json]:
        """根据逻辑表达式搜索JSON"""
        if not kb_ids:
            return []
        if top_k <= 0:
            return []
        stmt = select(JsonEntity).where(JsonEntity.kb_id.in_(kb_ids))
        logical_expression_filter = (
            await (
                Postgres.change_logical_expression_to_sqlalchemy_filter(
                    logical_expression
                )
            )
        )
        stmt = stmt.where(logical_expression_filter)
        if banned_json_ids:
            stmt = stmt.where(JsonEntity.id.notin_(banned_json_ids))
        stmt = stmt.order_by(JsonEntity.created_at.desc())
        stmt = stmt.limit(top_k)
        async with await Postgres.get_session() as session:
            result = await session.execute(stmt)
            json_entities = result.scalars().all()
        jsons = []
        for json_entity in json_entities:
            json = await Postgres.convertor.json_entity_to_json(json_entity)
            jsons.append(json)
        return jsons

    @staticmethod
    async def search_jsons_by_keyword(
        kb_ids: list[str],
        top_k: int,
        banned_json_ids: Optional[list[str]],
        logical_expression: Optional[LogicalExpression],
        query: Optional[str],
        semantic_keys: Optional[list[list[str]]],
    ) -> list[Json]:
        """根据关键词搜索JSON"""
        if not kb_ids:
            return []
        if top_k <= 0:
            return []
        if semantic_keys is not None and not semantic_keys:
            return []
        ts_query = func.plainto_tsquery("zhparser", query)
        similarity_score = func.ts_rank_cd(
            JsonValueEntity.value_ts_vector, ts_query
        ).label("similarity_score")
        stmt = (
            select(JsonEntity, similarity_score)
            .join(JsonValueEntity, JsonValueEntity.json_id == JsonEntity.id)
            .where(JsonEntity.kb_id.in_(kb_ids))
            .where(JsonEntity.enabled == True)
            .where(JsonEntity.status != ExistedStatus.DELETED.value)
            .where(JsonValueEntity.value_ts_vector.op("@@")(ts_query))
            .where(similarity_score > 0)
        )
        if logical_expression:
            logical_expression_filter = (
                await (
                    Postgres.change_logical_expression_to_sqlalchemy_filter(
                        logical_expression
                    )
                )
            )
            stmt = stmt.where(logical_expression_filter)
        if banned_json_ids:
            stmt = stmt.where(JsonEntity.id.notin_(banned_json_ids))
        if semantic_keys:
            # 构造语义检索条件，JsonValueEntity.key与semantic_keys中的任一列表匹配即可
            semantic_filter = false()
            for key_list in semantic_keys:
                semantic_filter = semantic_filter | JsonValueEntity.key.op("&&")(
                    key_list
                )
            stmt = stmt.where(semantic_filter)
        stmt = stmt.order_by(similarity_score.desc())
        stmt = stmt.limit(top_k)
        async with await Postgres.get_session() as session:
            result = await session.execute(stmt)
            json_entities = result.scalars().all()
        jsons = []
        for json_entity in json_entities:
            json = await Postgres.convertor.json_entity_to_json(json_entity)
            jsons.append(json)
        return jsons

    @staticmethod
    async def search_jsons_by_vector(
        kb_ids: list[str],
        vector: list[float],
        top_k: int,
        logical_expression: Optional[LogicalExpression] = None,
        banned_json_ids: Optional[list[str]] = None,
        semantic_keys: Optional[list[list[str]]] = None,
    ) -> list[Json]:
        """根据知识库ID列表和查询向量搜索JSON"""
        if not kb_ids:
            return []
        if top_k <= 0:
            return []
        if semantic_keys is not None and not semantic_keys:
            return []
        vector_param = str(vector)
        similarity_score = func.cosine_similarity(
            JsonValueEntity.value_vector, vector_param
        ).label("similarity_score")
        stmt = (
            select(JsonEntity, similarity_score)
            .join(JsonValueEntity, JsonValueEntity.json_id == JsonEntity.id)
            .where(JsonValueEntity.value_vector.isnot(None))
            .where(similarity_score > 0)
            .where(JsonEntity.kb_id.in_(kb_ids))
            .where(JsonEntity.enabled == True)
            .where(JsonEntity.status != ExistedStatus.DELETED.value)
        )
        if logical_expression:
            logical_expression_filter = (
                await (
                    Postgres.change_logical_expression_to_sqlalchemy_filter(
                        logical_expression
                    )
                )
            )
            stmt = stmt.where(logical_expression_filter)
        if banned_json_ids:
            stmt = stmt.where(JsonEntity.id.notin_(banned_json_ids))
        if semantic_keys:
            # 构造语义检索条件，JsonValueEntity.key与semantic_keys中的任一列表匹配即可
            semantic_filter = false()
            for key_list in semantic_keys:
                semantic_filter = semantic_filter | JsonValueEntity.key.op("&&")(
                    key_list
                )
            stmt = stmt.where(semantic_filter)
        stmt = stmt.order_by(similarity_score.desc())
        stmt = stmt.limit(top_k)
        async with await Postgres.get_session() as session:
            result = await session.execute(stmt)
            json_entities = result.scalars().all()
        jsons = []
        for json_entity in json_entities:
            json = await Postgres.convertor.json_entity_to_json(json_entity)
            jsons.append(json)
        return jsons
