from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import uuid4
from ENUM.parse import (
    ParseResultTopology,
    ChunkType,
    ParseMode,
    Language,
)
from ENUM.general import ExistedStatus


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
    source_data: str = Field("", description="知识块来源数据")
    vector: Optional[list[float]] = Field(default=None, description="知识块向量")
    global_offset: int = Field(0, description="知识块在原始数据中的全局偏移位置")
    local_offset: int = Field(0, description="知识块在所属页面中的局部偏移位置")
    enabled: bool = Field(default=True, description="知识块是否启用")
    status: ExistedStatus = Field(ExistedStatus.EXISTED, description="知识块存在状态")
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
    author_name: str = Field(..., description="文档作者名称")
    extension: str = Field(..., description="文档扩展名")
    size: int = Field(..., description="文档大小，单位为字节")
    parse_mode: ParseMode = Field(..., description="文档解析模式")
    topology: ParseResultTopology = Field(..., description="文档解析结果拓扑")
    enabled: bool = Field(default=True, description="文档是否启用")
    status: ExistedStatus = Field(ExistedStatus.EXISTED, description="文档存在状态")
    abstract: str = Field("", description="文档摘要")
    abstract_vector: Optional[list[float]] = Field(
        default=None, description="文档摘要向量"
    )
    content: str = Field("", description="文档内容")
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="文档创建时间",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="文档更新时间",
    )


class DocKnowledgeBase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    name: str = Field(..., description="知识库名称")
    author_name: str = Field(..., description="知识库作者名称")
    access_key: str = Field(..., description="知识库访问密钥")
    language: Language = Field(Language.ZH, description="知识库语言")
    description: str = Field("", description="知识库描述")
    special_characters: str = Field(
        "", description="知识库分块特殊字符（如换行符、逗号等）"
    )
    default_chunk_size: int = Field(1024, description="知识库默认分块大小")
    default_parse_mode: ParseMode = Field(
        ParseMode.GENERAL, description="知识库默认解析模式"
    )
    doc_count: int = Field(0, description="知识库中文档数量")
    doc_size: int = Field(0, description="知识库中文档总大小，单位为字节")
    embedding_model_id: Optional[str] = Field(
        None, description="知识库使用的文本嵌入模型ID"
    )
    rerank_model_id: Optional[str] = Field(None, description="知识库使用的重排序模型ID")
    chat_model_id: Optional[str] = Field(None, description="知识库使用的聊天模型ID")
    upload_count_limit: int = Field(128, description="单次更新文档数量限制")
    upload_size_limit: int = Field(512, description="单次更新文档大小限制，单位为MB")
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="知识库创建时间",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="知识库更新时间",
    )


class Json(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    kb_id: str = Field(..., description="所属知识库ID")
    name: str = Field(..., description="JSON名称")
    content: Any = Field(..., description="JSON内容")
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="创建时间",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="更新时间",
    )


class JsonKnowledgeBase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    name: str = Field(..., description="知识库名称")
    author_name: str = Field(..., description="知识库作者名称")
    access_key: str = Field(..., description="知识库访问密钥")
    embedding_model_id: Optional[str] = Field(
        None, description="知识库使用的文本嵌入模型ID"
    )
    rerank_model_id: Optional[str] = Field(None, description="知识库使用的重排序模型ID")
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="知识库创建时间",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="知识库更新时间",
    )
