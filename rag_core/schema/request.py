from pydantic import BaseModel, Field
from typing import Optional
from rag_core.schema.config import ModelConfig
from rag_core.ENUM.parse import Language, ParseMode, MetaDataType, ChunkType
from rag_core.ENUM.task import TaskStatus


class CreateAccessKeyRequest(BaseModel):
    name: str = Field("", description="访问密钥名称")
    description: str = Field("", description="访问密钥描述")
    owner_id: str = Field(..., description="访问密钥所属用户ID")
    owner_name: str = Field(..., description="访问密钥所属用户名")


class UpdateAccessKeyRequest(BaseModel):
    name: Optional[str] = Field(None, description="访问密钥名称")
    description: Optional[str] = Field(None, description="访问密钥描述")


class ListAccessKeyRequest(BaseModel):
    name: Optional[str] = Field(None, description="访问密钥名称")
    description: Optional[str] = Field(None, description="访问密钥描述")
    owner_id: Optional[str] = Field(None, description="访问密钥所属用户ID")
    owner_name: Optional[str] = Field(None, description="访问密钥所属用户名")
    page_size: int = Field(10, description="每页记录数")
    page_num: int = Field(1, description="页码")
    created_at_start: Optional[str] = Field(
        None, description="访问密钥创建时间范围开始，格式为YYYY-MM-DD HH:MM:SS"
    )
    created_at_end: Optional[str] = Field(
        None, description="访问密钥创建时间范围结束，格式为YYYY-MM-DD HH:MM:SS"
    )
    created_at_desc: bool = Field(
        False, description="访问密钥创建时间排序，True表示降序，False表示升序"
    )


class CreateKnowledgeBaseRequest(BaseModel):
    name: str = Field(..., description="知识库名称")
    owner_id: str = Field("", description="知识库所属用户ID")
    owner_name: str = Field("", description="知识库作者名称")
    description: str = Field("", description="知识库描述")
    meta_data_type: MetaDataType = Field(
        MetaDataType.DOCUMENT, description="知识库元数据类型，默认为文档"
    )
    upload_count_limit: int = Field(128, description="单次更新数量限制")
    upload_size_limit: int = Field(512, description="单次更新大小限制，单位为MB")


class CreateDocKnowledgeBaseRequest(CreateKnowledgeBaseRequest):
    language: Language = Field(Language.ZH, description="知识库语言")
    special_characters: Optional[str] = Field(
        None, description="知识库分块特殊字符（如换行符、逗号等）"
    )
    default_chunk_size: int = Field(1024, description="知识库默认分块大小")
    default_parse_mode: ParseMode = Field(
        ParseMode.GENERAL, description="知识库默认解析模式"
    )
    embedding_model_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的文本嵌入模型配置"
    )
    rerank_model_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的重排序模型配置"
    )
    chat_model_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的聊天模型配置"
    )
    multimodal_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的多模态模型配置"
    )


class CreateJsonKnowledgeBaseRequest(BaseModel):
    embedding_model_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的文本嵌入模型配置"
    )
    rerank_model_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的重排序模型配置"
    )


class UpdateKnowledgeBaseRequest(BaseModel):
    name: Optional[str] = Field(None, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    upload_count_limit: Optional[int] = Field(None, description="单次更新数量限制")
    upload_size_limit: Optional[int] = Field(
        None, description="单次更新大小限制，单位为MB"
    )


class UpdateDocKnowledgeBaseRequest(UpdateKnowledgeBaseRequest):
    language: Optional[Language] = Field(None, description="知识库语言")
    special_characters: Optional[str] = Field(
        None, description="知识库分块特殊字符（如换行符、逗号等）"
    )
    default_chunk_size: Optional[int] = Field(None, description="知识库默认分块大小")
    default_parse_mode: Optional[ParseMode] = Field(
        None, description="知识库默认解析模式"
    )
    embedding_model_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的文本嵌入模型配置"
    )
    rerank_model_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的重排序模型配置"
    )
    chat_model_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的聊天模型配置"
    )
    multimodal_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的多模态模型配置"
    )


class UpdateJsonKnowledgeBaseRequest(UpdateKnowledgeBaseRequest):
    embedding_model_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的文本嵌入模型配置"
    )
    rerank_model_config: Optional[ModelConfig] = Field(
        None, description="知识库使用的重排序模型配置"
    )


class ListKnowledgeBaseRequest(BaseModel):
    name: Optional[str] = Field(None, description="知识库名称")
    owner_id: Optional[str] = Field(None, description="知识库所属用户ID")
    owner_name: Optional[str] = Field(None, description="知识库作者名称")
    meta_data_type: Optional[MetaDataType] = Field(None, description="知识库元数据类型")
    page_size: int = Field(10, description="每页记录数")
    page_num: int = Field(1, description="页码")
    created_at_start: Optional[str] = Field(
        None, description="知识库创建时间范围开始，格式为YYYY-MM-DD HH:MM:SS"
    )
    created_at_end: Optional[str] = Field(
        None, description="知识库创建时间范围结束，格式为YYYY-MM-DD HH:MM:SS"
    )
    created_at_desc: bool = Field(
        False, description="知识库创建时间排序，True表示降序，False表示升序"
    )


class UpdateDocRequest(BaseModel):
    name: Optional[str] = Field(None, description="文档名称")
    parse_mode: Optional[ParseMode] = Field(None, description="文档解析模式")
    chunk_size: Optional[int] = Field(None, description="文档分块大小")


class SwitchDocEnabledRequest(BaseModel):
    doc_ids: list[str] = Field(..., description="要启用的文档ID列表")
    enabled: bool = Field(..., description="文档是否启用")


class ListDocRequest(BaseModel):
    name: Optional[str] = Field(None, description="文档名称")
    owner_id: Optional[str] = Field(None, description="文档所属用户ID")
    owner_name: Optional[str] = Field(None, description="文档作者名称")
    parse_mode: Optional[ParseMode] = Field(None, description="文档解析模式")
    enabled: Optional[bool] = Field(None, description="文档是否启用")
    parse_status: Optional[TaskStatus] = Field(None, description="文档解析状态")
    page_size: int = Field(10, description="每页记录数")
    page_num: int = Field(1, description="页码")
    created_at_start: Optional[str] = Field(
        None, description="文档创建时间范围开始，格式为YYYY-MM-DD HH:MM:SS"
    )
    created_at_end: Optional[str] = Field(
        None, description="文档创建时间范围结束，格式为YYYY-MM-DD HH:MM:SS"
    )
    created_at_desc: bool = Field(
        False, description="文档创建时间排序，True表示降序，False表示升序"
    )


class ListJsonRequest(BaseModel):
    name: Optional[str] = Field(None, description="JSON名称")
    owner_id: Optional[str] = Field(None, description="JSON所属用户ID")
    owner_name: Optional[str] = Field(None, description="JSON作者名称")
    page_size: int = Field(10, description="每页记录数")
    page_num: int = Field(1, description="页码")
    created_at_start: Optional[str] = Field(
        None, description="JSON创建时间范围开始，格式为YYYY-MM-DD HH:MM:SS"
    )
    created_at_end: Optional[str] = Field(
        None, description="JSON创建时间范围结束，格式为YYYY-MM-DD HH:MM:SS"
    )
    created_at_desc: bool = Field(
        False, description="JSON创建时间排序，True表示降序，False表示升序"
    )


class SwitchChunkEnabledRequest(BaseModel):
    chunk_ids: list[str] = Field(..., description="要启用的分块ID列表")
    enabled: bool = Field(..., description="分块是否启用")


class ListChunkRequest(BaseModel):
    doc_id: str = Field(..., description="所属文档ID")
    content: Optional[str] = Field(None, description="分块内容")
    chunk_type: Optional[ChunkType] = Field(None, description="分块类型")
    enabled: Optional[bool] = Field(None, description="分块是否启用")
    page_size: int = Field(10, description="每页记录数")
    page_num: int = Field(1, description="页码")
    created_at_start: Optional[str] = Field(
        None, description="分块创建时间范围开始，格式为YYYY-MM-DD HH:MM:SS"
    )
    created_at_end: Optional[str] = Field(
        None, description="分块创建时间范围结束，格式为YYYY-MM-DD HH:MM:SS"
    )
    created_at_desc: bool = Field(
        False, description="分块创建时间排序，True表示降序，False表示升序"
    )


class SearchChunkRequest(BaseModel):
    kb_ids: list[str] = Field(..., description="所属知识库ID列表")
    query: str = Field(default="", description="查询内容")
    top_k: int = Field(default=5, description="返回的结果数量")
    doc_ids: list[str] = Field(default=[], description="所属文档ID列表")
    banned_doc_ids: list[str] = Field(default=[], description="被禁止的文档ID列表")
    is_related_surrounding: bool = Field(default=True, description="是否关联上下文")
    is_classify_by_doc: bool = Field(default=False, description="是否按文档分类")
    is_rerank: bool = Field(default=False, description="是否重新排序")
    is_compress: bool = Field(default=False, description="是否压缩")
    tokens_limit: int = Field(default=8192, description="token限制")


class ListTraceDetailsRequest(BaseModel):
    func_name: Optional[str] = Field(None, description="函数名称")
    page_size: int = Field(10, description="每页记录数")
    page_num: int = Field(1, description="页码")
    time_start: Optional[str] = Field(
        None, description="函数执行时间范围开始，格式为YYYY-MM-DD HH:MM:SS"
    )
    time_end: Optional[str] = Field(
        None, description="函数执行时间范围结束，格式为YYYY-MM-DD HH:MM:SS"
    )
    time_desc: bool = Field(
        False, description="函数执行时间排序，True表示降序，False表示升序"
    )
    cost_time_start: Optional[float] = Field(
        None, description="函数执行耗时范围开始，单位为秒"
    )
    cost_time_end: Optional[float] = Field(
        None, description="函数执行耗时范围结束，单位为秒"
    )
    cost_time_desc: bool = Field(
        False, description="函数执行耗时排序，True表示降序，False表示升序"
    )
