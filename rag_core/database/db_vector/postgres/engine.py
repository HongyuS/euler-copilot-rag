# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import Index
from sqlalchemy import Boolean, Column, ForeignKey, BigInteger, Float, Text, func
from sqlalchemy.types import TIMESTAMP, UUID
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import (
    declarative_base,
    DeclarativeBase,
    MappedAsDataclass,
    Mapped,
    mapped_column,
)
from pgvector.sqlalchemy import Vector
from datetime import datetime
import logging
import uuid
from uuid import uuid4
import urllib.parse
from rag_core.config.config import Config
from rag_core.database.db_vector.base.engine import BaseVectorDataBase
from rag_core.ENUM.parse import ParseResultTopology, ChunkType, ParseMode, MetaDataType
from rag_core.ENUM.general import ExistedStatus

logger = logging.getLogger(__name__)
Base = declarative_base()


class Chunk(BaseModel):
    """
    知识块
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    knowledge_base_id: str = Field(..., description="所属知识库ID")
    document_id: str = Field(..., description="所属文档ID")
    content: str = Field(..., description="知识块内容")
    tokens: int = Field(..., description="知识块的token数量")
    type: ChunkType = Field(..., description="知识块类型")
    text: str = Field(default="", description="知识块文本")
    vector: Optional[list[float]] = Field(default=None, description="知识块向量")
    global_offset: int = Field(0, description="知识块在原始数据中的全局偏移位置")
    local_offset: int = Field(0, description="知识块在所属页面中的局部偏移位置")
    enabled: bool = Field(default=True, description="知识块是否启用")
    status: ExistedStatus = Field(ExistedStatus.EXISTED, description="知识块存在状态")
    hit_count: int = Field(0, description="知识块被检索命中的次数")
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="知识块创建时间",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="知识块更新时间",
    )


class Document(BaseModel):
    """
    文档
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    kb_id: str = Field(..., description="所属知识库ID")
    name: str = Field(..., description="文档名称")
    owner_id: str = Field("", description="文档所属用户ID")
    owner_name: str = Field("", description="文档作者名称")
    extension: str = Field(..., description="文档扩展名")
    size: int = Field(..., description="文档大小，单位为字节")
    parse_mode: ParseMode = Field(..., description="文档解析模式")
    chunk_size: int = Field(..., description="文档分块大小")
    topology: ParseResultTopology = Field(..., description="文档解析结果拓扑")
    enabled: bool = Field(default=True, description="文档是否启用")
    status: ExistedStatus = Field(ExistedStatus.EXISTED, description="文档存在状态")
    abstract: str = Field("", description="文档摘要")
    abstract_vector: Optional[list[float]] = Field(
        default=None, description="文档摘要向量"
    )
    content: str = Field("", description="文档内容")
    hit_count: int = Field(0, description="文档被检索命中的次数")
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="文档创建时间",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="文档更新时间",
    )


class DocumentEntity(Base):
    __tablename__ = "document"

    id = Column(Text, default=lambda: str(uuid4()), primary_key=True)  # 文档id
    kb_id = Column(Text)  # 知识库id
    name = Column(Text)  # 文档名称
    owner_id = Column(Text)  # 文档所属用户id
    owner_name = Column(Text)  # 文档作者名称
    extension = Column(Text)  # 文档扩展名
    size = Column(BigInteger)  # 文档大小，单位为字节
    parse_mode = Column(Text)  # 文档解析模式
    chunk_size = Column(BigInteger)  # 文档分块大小
    topology = Column(Text)  # 文档解析结果拓扑
    enabled = Column(Boolean)  # 文档是否启用
    status = Column(Text, default=ExistedStatus.EXISTED.value)  # 文档状态
    abstract = Column(Text)  # 文档摘要
    abstract_ts_vector = Column(TSVECTOR)  # 文档摘要词向量
    abstract_vector = Column(Vector(1024))  # 文档摘要向量
    content = Column(Text)  # 文档内容
    hit_count = Column(BigInteger)  # 文档被检索命中的次数
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    __table_args__ = (
        Index("doc_kb_id_index", kb_id),
        Index("abstract_ts_vector_index", abstract_ts_vector, postgresql_using="gin"),
        Index(
            "abstract_vector_index",
            abstract_vector,
            postgresql_using="hnsw",
            postgresql_with={"m": 32, "ef_construction": 200},
            postgresql_ops={"abstract_vector": "vector_cosine_ops"},
        ),
    )


class ChunkEntity(Base):
    __tablename__ = "chunk"

    id = Column(Text, default=lambda: str(uuid4()), primary_key=True)  # 知识块id
    knowledge_base_id = Column(Text)  # 所属知识库id
    document_id = Column(Text)  # 所属文档id
    content = Column(Text)  # 知识块内容
    tokens = Column(BigInteger)  # 知识块的token数量
    type = Column(Text)  # 知识块类型
    text = Column(Text)  # 知识块文本
    text_ts_vector = Column(TSVECTOR)  # 知识块文本词向量
    vector = Column(Vector(1024))  # 知识块向量
    global_offset = Column(BigInteger)  # 知识块在原始数据中的全局偏移位置
    local_offset = Column(BigInteger)  # 知识块在所属页面中的局部偏移位置
    enabled = Column(Boolean)  # 知识块是否启用
    status = Column(Text, default=ExistedStatus.EXISTED.value)  # 知识块状态
    hit_count = Column(BigInteger)  # 知识块被检索命中的次数
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    __table_args__ = (
        Index("chunk_kb_id_index", knowledge_base_id),
        Index("chunk_doc_id_index", document_id),
        Index("chunk_text_ts_vector_index", text_ts_vector, postgresql_using="gin"),
        Index(
            "chunk_vector_index",
            vector,
            postgresql_using="hnsw",
            postgresql_with={"m": 32, "ef_construction": 200},
            postgresql_ops={"vector": "vector_cosine_ops"},
        ),
    )


class JsonEntity(Base):
    __tablename__ = "json"

    id = Column(Text, default=lambda: str(uuid4()), primary_key=True)  # JSON id
    kb_id = Column(Text)  # 所属知识库id
    name = Column(Text)  # JSON名称
    content = Column(Text)  # JSON内容，存储为字符串格式
    hit_count = Column(BigInteger)  # JSON被检索命中的次数
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class JsonValue(Base):
    id = Column(Text, default=lambda: str(uuid4()), primary_key=True)  # JSON值id
    json_id = Column(Text)  # 所属JSON id
    key = Column(Text)  # JSON键
    value_ts_vector = Column(TSVECTOR)  # JSON值词向量
    value_vector = Column(Vector(1024))  # JSON值向量
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    __table_args__ = (
        Index("json_value_json_id_index", json_id),
        Index(
            "json_value_value_ts_vector_index", value_ts_vector, postgresql_using="gin"
        ),
        Index(
            "json_value_value_vector_index",
            value_vector,
            postgresql_using="hnsw",
            postgresql_with={"m": 32, "ef_construction": 200},
            postgresql_ops={"value_vector": "vector_cosine_ops"},
        ),
    )


class Postgres(BaseVectorDataBase):

    # 对密码进行 URL 编码
    password = Config().get_config().database_password
    encoded_password = urllib.parse.quote_plus(password)
    database_url = f"postgresql+asyncpg://{Config().get_config().database_user}:{encoded_password}@{Config().get_config().database_host}:{Config().get_config().database_port}/{Config().get_config().database_db}"
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_recycle=300,
        pool_pre_ping=True,
        pool_size=Config().get_config().database_pool_size,
    )

    @classmethod
    async def init_database_specifics(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def get_session(cls):
        connection = async_sessionmaker(cls.engine, expire_on_commit=False)()
        return cls._ConnectionManager(connection)
