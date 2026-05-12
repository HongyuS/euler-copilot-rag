from pydantic import BaseModel, Field
from typing import Optional, Any
from rag_core.schema.access_key import AccessKey
from rag_core.schema.config import ModelConfig
from rag_core.schema.knowledge_base import (
    DocKnowledgeBase,
    JsonKnowledgeBase,
    Document,
    Json,
    Chunk,
)
from rag_core.schema.task import Task
from rag_core.schema.trace import Trace, TraceDetail
from rag_core.ENUM.parse import Language, ParseMode, MetaDataType, ChunkType
from rag_core.ENUM.task import TaskStatus


class ResponseBase(BaseModel):
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(..., description="响应消息")
    result: Any = Field(..., description="响应结果")


class CreateAccessKeyMsg(BaseModel):
    key: str = Field(..., description="访问密钥")


class CreateAccessKeyResponse(ResponseBase):
    result: CreateAccessKeyMsg = Field(..., description="创建访问密钥响应结果")


class DeleteAccessMsg(BaseModel):
    success: bool = Field(..., description="删除是否成功")


class UpdateAccessKeyMsg(BaseModel):
    success: bool = Field(..., description="更新是否成功")


class UpdateAccessKeyResponse(ResponseBase):
    result: UpdateAccessKeyMsg = Field(..., description="更新访问密钥响应结果")


class ListAccessKeyMsg(BaseModel):
    total: int = Field(..., description="访问密钥总数")
    access_keys: list[AccessKey] = Field(..., description="访问密钥列表")


class ListAccessKeyResponse(ResponseBase):
    result: ListAccessKeyMsg = Field(..., description="访问密钥列表响应结果")


class GetAccessKeyMsg(BaseModel):
    access_key: AccessKey = Field(..., description="访问密钥信息")


class GetAccessKeyResponse(ResponseBase):
    result: GetAccessKeyMsg = Field(..., description="获取访问密钥响应结果")


class CreateKnowledgeBaseMsg(BaseModel):
    kb_id: str = Field(..., description="知识库ID")


class CreateKnowledgeBaseResponse(ResponseBase):
    result: CreateKnowledgeBaseMsg = Field(..., description="创建知识库响应结果")


class UpdateKnowledgeBaseMsg(BaseModel):
    success: bool = Field(..., description="更新是否成功")


class UpdateKnowledgeBaseResponse(ResponseBase):
    result: UpdateKnowledgeBaseMsg = Field(..., description="更新知识库响应结果")


class ListKnowledgeBaseMsg(BaseModel):
    total: int = Field(..., description="知识库总数")
    knowledge_bases: list[DocKnowledgeBase | JsonKnowledgeBase] = Field(
        ..., description="知识库列表"
    )


class ListKnowledgeBaseResponse(ResponseBase):
    result: ListKnowledgeBaseMsg = Field(..., description="知识库列表响应结果")


class GetKnowledgeBaseMsg(BaseModel):
    knowledge_base: DocKnowledgeBase | JsonKnowledgeBase = Field(
        ..., description="知识库信息"
    )


class GetKnowledgeBaseResponse(ResponseBase):
    result: GetKnowledgeBaseMsg = Field(..., description="获取知识库响应结果")


class CreateKnowledgeBaseExportTaskMsg(BaseModel):
    task_id: str = Field(..., description="导出任务ID")


class CreateKnowledgeBaseExportTaskResponse(ResponseBase):
    result: CreateKnowledgeBaseExportTaskMsg = Field(
        ..., description="创建知识库导出任务响应结果"
    )


class CreateKnowledgeBaseImportTaskMsg(BaseModel):
    task_id: str = Field(..., description="导入任务ID")


class CreateKnowledgeBaseImportTaskResponse(ResponseBase):
    result: CreateKnowledgeBaseImportTaskMsg = Field(
        ..., description="创建知识库导入任务响应结果"
    )


class UploadDocumentMsg(BaseModel):
    doc_ids: list[str] = Field(..., description="上传文档ID列表")


class UploadDocumentResponse(ResponseBase):
    result: UploadDocumentMsg = Field(..., description="上传文档响应结果")


class DeleteDocumentMsg(BaseModel):
    success: bool = Field(..., description="删除是否成功")


class DeleteDocumentResponse(ResponseBase):
    result: DeleteDocumentMsg = Field(..., description="删除文档响应结果")


class UpdateDocumentMsg(BaseModel):
    success: bool = Field(..., description="更新是否成功")


class UpdateDocumentResponse(ResponseBase):
    result: UpdateDocumentMsg = Field(..., description="更新文档响应结果")


class SwitchDocumentEnabledMsg(BaseModel):
    doc_ids: list[str] = Field(..., description="禁用/启用成功的文档ID列表")


class SwitchDocumentEnabledResponse(ResponseBase):
    result: SwitchDocumentEnabledMsg = Field(..., description="禁用/启用文档响应结果")


class listDocumentMsg(BaseModel):
    total: int = Field(..., description="文档总数")
    documents: list[Document] = Field(..., description="文档列表")


class ListDocumentResponse(ResponseBase):
    result: listDocumentMsg = Field(..., description="文档列表响应结果")


class GetDocumentMsg(BaseModel):
    document: Document = Field(..., description="文档信息")


class GetDocumentResponse(ResponseBase):
    result: GetDocumentMsg = Field(..., description="获取文档响应结果")


class CreateJsonMsg(BaseModel):
    json_id: str = Field(..., description="JSON ID")


class CreateJsonResponse(ResponseBase):
    result: CreateJsonMsg = Field(..., description="创建JSON响应结果")


class DeleteJsonMsg(BaseModel):
    success: bool = Field(..., description="删除是否成功")


class DeleteJsonResponse(ResponseBase):
    result: DeleteJsonMsg = Field(..., description="删除JSON响应结果")


class ListJsonMsg(BaseModel):
    total: int = Field(..., description="JSON总数")
    jsons: list[Json] = Field(..., description="JSON列表")


class ListJsonResponse(ResponseBase):
    result: ListJsonMsg = Field(..., description="JSON列表响应结果")


class GetJsonMsg(BaseModel):
    json: Json = Field(..., description="JSON信息")


class GetJsonResponse(ResponseBase):
    result: GetJsonMsg = Field(..., description="获取JSON响应结果")


class JsonAndScore(BaseModel):
    json: Json = Field(..., description="JSON信息")
    score: float = Field(..., description="相关度分数")


class SearchJsonMsg(BaseModel):
    json_and_scores: list[JsonAndScore] = Field(..., description="JSON搜索结果列表")


class SearchJsonResponse(ResponseBase):
    result: SearchJsonMsg = Field(..., description="搜索JSON响应结果")


class DeleteChunkMsg(BaseModel):
    success: bool = Field(..., description="删除是否成功")


class DeleteChunkResponse(ResponseBase):
    result: DeleteChunkMsg = Field(..., description="删除分块响应结果")


class UpdateChunkMsg(BaseModel):
    success: bool = Field(..., description="更新是否成功")


class UpdateChunkResponse(ResponseBase):
    result: UpdateChunkMsg = Field(..., description="更新分块响应结果")


class SwitchChunkEnabledMsg(BaseModel):
    chunk_ids: list[str] = Field(..., description="禁用/启用成功的分块ID列表")


class SwitchChunkEnabledResponse(ResponseBase):
    result: SwitchChunkEnabledMsg = Field(..., description="禁用/启用分块响应结果")


class ListChunkMsg(BaseModel):
    total: int = Field(..., description="分块总数")
    chunks: list[Chunk] = Field(..., description="分块列表")


class ListChunkResponse(ResponseBase):
    result: ListChunkMsg = Field(..., description="分块列表响应结果")


class ChunkAndScore(BaseModel):
    chunk: Chunk = Field(..., description="分块信息")
    score: float = Field(..., description="相关度分数")


class SearchChunkMsg(BaseModel):
    chunk_and_scores: list[ChunkAndScore] = Field(..., description="分块搜索结果列表")


class SearchChunkResponse(ResponseBase):
    result: SearchChunkMsg = Field(..., description="搜索分块响应结果")


class ListTraceMsg(BaseModel):
    total: int = Field(..., description="跟踪总数")
    traces: list[Trace] = Field(..., description="跟踪列表")


class ListTraceResponse(ResponseBase):
    result: ListTraceMsg = Field(..., description="跟踪列表响应结果")


class ListTraceDetailMsg(BaseModel):
    total: int = Field(..., description="跟踪详情总数")
    traces: list[Trace] = Field(..., description="跟踪详情列表")


class ListTraceDetailResponse(ResponseBase):
    result: ListTraceDetailMsg = Field(..., description="跟踪详情列表响应结果")


class DeleteTraceMsg(BaseModel):
    success: bool = Field(..., description="删除是否成功")


class DeleteTraceResponse(ResponseBase):
    result: DeleteTraceMsg = Field(..., description="删除跟踪响应结果")


class StopOrRunTaskMsg(BaseModel):
    success: bool = Field(..., description="停止/运行任务是否成功")


class StopOrRunTaskResponse(ResponseBase):
    result: StopOrRunTaskMsg = Field(..., description="停止/运行任务响应结果")


class ListTaskMsg(BaseModel):
    total: int = Field(..., description="任务总数")
    tasks: list[Task] = Field(..., description="任务列表")


class ListTaskResponse(ResponseBase):
    result: ListTaskMsg = Field(..., description="任务列表响应结果")


class GetTaskMsg(BaseModel):
    task: Task = Field(..., description="任务信息")


class GetTaskResponse(ResponseBase):
    result: GetTaskMsg = Field(..., description="获取任务响应结果")
