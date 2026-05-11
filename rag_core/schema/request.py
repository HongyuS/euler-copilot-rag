from pydantic import BaseModel, Field
from typing import Optional
from rag_core.schema.config import ModelConfig
from rag_core.ENUM.parse import Language, ParseMode


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


class GetAccessKeyRequest(BaseModel):
    key: str = Field(..., description="访问密钥")


class CreateDocKnowledgeBaseRequest(BaseModel):
    name: str = Field(..., description="知识库名称")
    owner_id: str = Field("", description="知识库所属用户ID")
    owner_name: str = Field("", description="知识库作者名称")
    language: Language = Field(Language.ZH, description="知识库语言")
    description: str = Field("", description="知识库描述")
    upload_count_limit: int = Field(128, description="单次更新文档数量限制")
    upload_size_limit: int = Field(512, description="单次更新文档大小限制，单位为MB")
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


