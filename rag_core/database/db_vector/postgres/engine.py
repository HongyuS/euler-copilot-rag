# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import Index
from sqlalchemy import (
    Boolean,
    Column,
    BigInteger,
    Text,
    func,
    JSON,
    ARRAY,
)
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
import logging
from uuid import uuid4
import urllib.parse
from rag_core.config.config import Config
from rag_core.database.db_vector.base.engine import BaseVectorDataBase
from rag_core.database.db_vector.postgres.manager.chunk_manager import ChunkManager
from rag_core.database.db_vector.postgres.manager.doc_manager import DocManager
from rag_core.database.db_vector.postgres.manager.json_manager import JsonManager
from rag_core.database.db_vector.postgres.convertor import Convertor
from rag_core.schema.json import LogicalExpression, Condition
from rag_core.ENUM.general import ExistedStatus
from rag_core.ENUM.json import LogicOperatorType, OperationType

logger = logging.getLogger(__name__)
Base = declarative_base()


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
    kb_id = Column(Text)  # 所属知识库id
    doc_id = Column(Text)  # 所属文档id
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
        Index("chunk_kb_id_index", kb_id),
        Index("chunk_doc_id_index", doc_id),
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
    content = Column(JSON)  # JSON内容
    enabled = Column(Boolean)  # JSON是否启用
    status = Column(Text, default=ExistedStatus.EXISTED.value)  # JSON状态
    hit_count = Column(BigInteger)  # JSON被检索命中的次数
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class JsonValueEntity(Base):
    __tablename__ = "json_value"
    id = Column(Text, default=lambda: str(uuid4()), primary_key=True)  # JSON值id
    json_id = Column(Text)  # 所属JSON id
    key = Column(ARRAY(Text))  # JSON值对应的JSON字段路径，支持多级路径
    value = Column(Text)  # JSON值文本
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
    doc_manager = DocManager
    chunk_manager = ChunkManager
    json_manager = JsonManager
    convertor = Convertor
    # 对密码进行 URL 编码
    password = Config().get_config().database_password
    encoded_password = urllib.parse.quote_plus(password)
    db_config = Config().get_config()
    database_url = (
        f"postgresql+asyncpg://{db_config.database_user}:{encoded_password}"
        f"@{db_config.database_host}:{db_config.database_port}/{db_config.database_db}"
    )
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

    @staticmethod
    async def change_logical_expression_to_sqlalchemy_filter(
        logical_expression: LogicalExpression,
    ) -> any:
        if isinstance(logical_expression, Condition):
            field_path = logical_expression.field
            operator = logical_expression.operator
            value = logical_expression.value

            # 解析多级JSON路径：支持 str / list[str]
            def get_json_path(expr, path):
                if isinstance(path, str):
                    path = [path]
                for key in path:
                    expr = expr[key]
                return expr

            json_field = get_json_path(JsonEntity.content, field_path)
            json_text = json_field.astext

            if operator == OperationType.EQ:
                return json_text == str(value)
            elif operator == OperationType.NE:
                return json_text != str(value)
            elif operator == OperationType.GT:
                return json_text > str(value)
            elif operator == OperationType.GTE:
                return json_text >= str(value)
            elif operator == OperationType.LT:
                return json_text < str(value)
            elif operator == OperationType.LTE:
                return json_text <= str(value)
            elif operator == OperationType.LIKE:
                return json_text.ilike(f"%{value}%")
            elif operator == OperationType.LIKE_LEFT:
                return json_text.ilike(f"%{value}")
            elif operator == OperationType.LIKE_RIGHT:
                return json_text.ilike(f"{value}%")
            elif operator == OperationType.IN:
                if not isinstance(value, list):
                    raise ValueError("IN 操作的值必须是列表")
                return json_text.in_([str(v) for v in value])
            elif operator == OperationType.NOT_IN:
                if not isinstance(value, list):
                    raise ValueError("NOT IN 操作的值必须是列表")
                return ~json_text.in_([str(v) for v in value])
            elif operator == OperationType.IS_NULL:
                return json_field.is_(None)
            elif operator == OperationType.IS_NOT_NULL:
                return json_field.isnot(None)
            elif operator == OperationType.BETWEEN:
                if not (
                    isinstance(value, list) and len(value) == 2 and None not in value
                ):
                    raise ValueError("BETWEEN 必须是两个非空值的列表")
                return func.and_(json_text >= str(value[0]), json_text <= str(value[1]))
            elif operator == OperationType.LENGTH_EQ:
                return func.length(json_text) == int(value)
            elif operator == OperationType.LENGTH_GT:
                return func.length(json_text) > int(value)
            elif operator == OperationType.LENGTH_GTE:
                return func.length(json_text) >= int(value)
            elif operator == OperationType.LENGTH_LT:
                return func.length(json_text) < int(value)
            elif operator == OperationType.LENGTH_LTE:
                return func.length(json_text) <= int(value)
            else:
                raise ValueError(f"不支持的操作符: {operator}")
        else:
            operator = logical_expression.operator
            conditions = logical_expression.conditions
            filters = [
                await Postgres.change_logical_expression_to_sqlalchemy_filter(cond)
                for cond in conditions
            ]

            if operator == LogicOperatorType.AND:
                return func.and_(*filters)
            elif operator == LogicOperatorType.OR:
                return func.or_(*filters)
            elif operator == LogicOperatorType.AND_NOT:
                return ~func.and_(*filters)
            elif operator == LogicOperatorType.OR_NOT:
                return ~func.or_(*filters)
            else:
                raise ValueError(f"不支持的逻辑运算符: {operator}")
