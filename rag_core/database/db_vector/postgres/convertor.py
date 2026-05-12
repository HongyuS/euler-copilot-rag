from rag_core.database.db_vector.postgres.engine import (
    DocumentEntity,
    ChunkEntity,
    JsonEntity,
)
from rag_core.schema.knowledge_base import Document, Chunk, Json
from rag_core.ENUM.parse import ParseMode, Topology, ChunkParseTopology, ChunkType
from rag_core.ENUM.general import ExistedStatus


class Convertor:
    @staticmethod
    async def document_to_document_entity(document: Document) -> DocumentEntity:
        return DocumentEntity(
            id=document.id,
            kb_id=document.kb_id,
            name=document.name,
            owner_id=document.owner_id,
            owner_name=document.owner_name,
            extension=document.extension,
            size=document.size,
            parse_mode=document.parse_mode.value,
            chunk_size=document.chunk_size,
            topology=document.topology.value,
            enabled=document.enabled,
            abstract=document.abstract,
            abstract_vector=document.abstract_vector,
            content=document.content,
            hit_count=document.hit_count,
        )

    @staticmethod
    async def document_entity_to_document(entity: DocumentEntity) -> Document:
        return Document(
            id=entity.id,
            kb_id=entity.kb_id,
            name=entity.name,
            owner_id=entity.owner_id,
            owner_name=entity.owner_name,
            extension=entity.extension,
            size=entity.size,
            parse_mode=ParseMode(entity.parse_mode),
            chunk_size=entity.chunk_size,
            topology=Topology(entity.topology),
            enabled=entity.enabled,
            abstract=entity.abstract,
            abstract_vector=entity.abstract_vector,
            content=entity.content,
            hit_count=entity.hit_count,
            created_at=entity.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=entity.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    @staticmethod
    async def chunk_to_chunk_entity(chunk: Chunk) -> ChunkEntity:
        return ChunkEntity(
            id=chunk.id,
            kb_id=chunk.kb_id,
            doc_id=chunk.doc_id,
            content=chunk.content,
            tokens=chunk.tokens,
            type=chunk.type.value,
            text=chunk.text,
            vector=chunk.vector,
            global_offset=chunk.global_offset,
            local_offset=chunk.local_offset,
            enabled=chunk.enabled,
            hit_count=chunk.hit_count,
        )

    @staticmethod
    async def chunk_entity_to_chunk(entity: ChunkEntity) -> Chunk:
        return Chunk(
            id=entity.id,
            kb_id=entity.kb_id,
            doc_id=entity.doc_id,
            content=entity.content,
            tokens=entity.tokens,
            type=ChunkType(entity.type),
            text=entity.text,
            vector=entity.vector,
            global_offset=entity.global_offset,
            local_offset=entity.local_offset,
            enabled=entity.enabled,
            hit_count=entity.hit_count,
            created_at=entity.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=entity.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    @staticmethod
    async def json_to_json_entity(json: Json) -> JsonEntity:
        return JsonEntity(
            id=json.id,
            kb_id=json.kb_id,
            name=json.name,
            content=json.content,
            hit_count=json.hit_count,
        )

    @staticmethod
    async def json_entity_to_json(entity: JsonEntity) -> Json:
        return Json(
            id=entity.id,
            kb_id=entity.kb_id,
            name=entity.name,
            content=entity.content,
            hit_count=entity.hit_count,
            created_at=entity.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=entity.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
