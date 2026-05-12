from datetime import datetime, timezone
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
from rag_core.schema.knowledge_base import Json
from rag_core.database.db_vector.postgres.engine import (
    Postgres,
    DocumentEntity,
    ChunkEntity,
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
