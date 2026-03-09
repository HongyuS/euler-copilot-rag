"""
RAG 工具返回结果的 Schema 定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Generic, TypeVar, Dict, Any

# 泛型类型变量，用于 BaseResponse
T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """通用响应结构"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息，描述操作结果或错误信息")
    data: Optional[T] = Field(default=None, description="响应数据，具体结构根据操作类型而定")


# ==================== 知识库相关 Schema ====================

class KnowledgeBaseInfo(BaseModel):
    """知识库信息（用于列表返回）"""
    id: str = Field(..., description="知识库唯一标识符（UUID格式）")
    name: str = Field(..., description="知识库名称，必须唯一")
    chunk_size: int = Field(..., description="文档分块大小（token数）")
    embedding_model: Optional[str] = Field(None, description="向量化模型名称，如果未配置则为None")
    created_at: Optional[str] = Field(None, description="创建时间（ISO格式字符串）")


class CreateKnowledgeBaseData(BaseModel):
    """创建知识库的响应数据"""
    kb_id: str = Field(..., description="新创建的知识库ID（UUID格式）")
    kb_name: str = Field(..., description="知识库名称")
    chunk_size: int = Field(..., description="设置的chunk大小（token数）")


class DeleteKnowledgeBaseData(BaseModel):
    """删除知识库的响应数据"""
    requested_count: int = Field(..., description="请求删除的知识库数量")
    deleted_count: int = Field(..., description="实际成功删除的知识库数量（软删除）")
    not_found: List[str] = Field(default_factory=list, description="未找到的知识库名称列表")


class ListKnowledgeBasesData(BaseModel):
    """列出知识库的响应数据"""
    knowledge_bases: List[KnowledgeBaseInfo] = Field(default_factory=list, description="知识库信息列表")
    count: int = Field(..., description="知识库数量")
    keyword: Optional[str] = Field(None, description="使用的关键词（如果进行了关键词过滤）")


# ==================== 文档相关 Schema ====================

class DocumentInfo(BaseModel):
    """文档信息（用于列表返回）"""
    id: str = Field(..., description="文档唯一标识符（UUID格式）")
    name: str = Field(..., description="文档名称")
    file_path: Optional[str] = Field(None, description="文档文件路径（绝对路径）")
    file_type: Optional[str] = Field(None, description="文件类型（如：txt, docx, pdf等）")
    chunk_size: Optional[int] = Field(None, description="文档的chunk大小（token数）")
    created_at: Optional[str] = Field(None, description="创建时间（ISO格式字符串）")
    updated_at: Optional[str] = Field(None, description="更新时间（ISO格式字符串）")


class ImportFileSuccess(BaseModel):
    """成功导入的文件信息"""
    file_path: str = Field(..., description="文件路径（绝对路径）")
    doc_name: str = Field(..., description="导入后的文档名称")
    chunk_count: int = Field(..., description="生成的chunk数量")


class ImportFileFailed(BaseModel):
    """失败导入的文件信息"""
    file_path: str = Field(..., description="文件路径（绝对路径）")
    error: str = Field(..., description="错误信息")


class ImportDocumentData(BaseModel):
    """导入文档的响应数据"""
    total: int = Field(..., description="总文件数")
    success_count: int = Field(..., description="成功导入的文件数")
    failed_count: int = Field(..., description="失败的文件数")
    success_files: List[ImportFileSuccess] = Field(default_factory=list, description="成功导入的文件列表")
    failed_files: List[ImportFileFailed] = Field(default_factory=list, description="失败的文件列表")


class ListDocumentsData(BaseModel):
    """列出文档的响应数据"""
    documents: List[DocumentInfo] = Field(default_factory=list, description="文档信息列表")
    count: int = Field(..., description="文档数量")
    keyword: Optional[str] = Field(None, description="使用的关键词（如果进行了关键词过滤）")


class DeleteDocumentData(BaseModel):
    """删除文档的响应数据"""
    requested_count: int = Field(..., description="请求删除的文档数量")
    deleted_count: int = Field(..., description="实际成功删除的文档数量（软删除）")
    kb_name: str = Field(..., description="文档所在的知识库名称")


# ==================== 搜索相关 Schema ====================

class SearchChunk(BaseModel):
    """搜索返回的chunk信息"""
    id: str = Field(..., description="chunk唯一标识符（UUID格式）")
    doc_id: str = Field(..., description="所属文档ID（UUID格式）")
    content: str = Field(..., description="chunk文本内容")
    tokens: Optional[int] = Field(None, description="chunk的token数量")
    chunk_index: Optional[int] = Field(None, description="chunk在文档中的索引位置")
    doc_name: str = Field(..., description="所属文档名称")
    score: float = Field(..., description="搜索分数（加权后的综合分数，数值越大表示相关性越高）")
    jaccard_score: Optional[float] = Field(None, description="Jaccard相似度分数（rerank后添加，用于重排序）")


class GitHubIssue(BaseModel):
    """GitHub Issue检索结果"""
    repo: str = Field(..., description="仓库名称")
    title: str = Field(..., description="Issue标题")
    content: str = Field(..., description="Issue的完整内容（标题 + 正文等）")
    similarity: float = Field(..., description="相似度分数（0-1之间，越高越相似）")


class GitHubCommit(BaseModel):
    """GitHub Commit检索结果"""
    summary: str = Field(..., description="Commit摘要")
    content: str = Field(..., description="Commit的完整内容（提交信息等）")
    similarity: float = Field(..., description="相似度分数（0-1之间，越高越相似）")


class GitHubSearchResult(BaseModel):
    """GitHub检索结果"""
    issues: List[GitHubIssue] = Field(default_factory=list, description="Issue列表")
    commits: List[GitHubCommit] = Field(default_factory=list, description="Commit列表")
    success: bool = Field(default=True, description="GitHub检索是否成功")
    error_message: Optional[str] = Field(None, description="如果失败，错误信息")


class SearchData(BaseModel):
    """搜索的响应数据"""
    chunks: List[SearchChunk] = Field(default_factory=list, description="搜索到的chunk列表，按相关性排序")
    count: int = Field(..., description="返回的chunk数量")
    github_results: Optional[GitHubSearchResult] = Field(None, description="GitHub线上检索结果（仅当online=true时返回）")


# ==================== 文档解析结果相关 Schema ====================

class DocumentChunkInfo(BaseModel):
    """文档chunk信息（用于展示文档解析结果）"""
    id: str = Field(..., description="chunk唯一标识符（UUID格式）")
    doc_id: str = Field(..., description="所属文档ID（UUID格式）")
    content: str = Field(..., description="chunk文本内容")
    tokens: Optional[int] = Field(None, description="chunk的token数量")
    chunk_index: Optional[int] = Field(None, description="chunk在文档中的索引位置（从0开始）")
    created_at: Optional[str] = Field(None, description="创建时间（ISO格式字符串）")


class GetDocumentChunksData(BaseModel):
    """获取文档解析结果的响应数据"""
    doc_id: str = Field(..., description="文档ID（UUID格式）")
    doc_name: str = Field(..., description="文档名称")
    kb_name: str = Field(..., description="文档所在的知识库名称")
    chunks: List[DocumentChunkInfo] = Field(default_factory=list, description="文档的所有chunk列表，按chunk_index排序")
    count: int = Field(..., description="chunk数量")


# 知识库相关响应类型
CreateKnowledgeBaseResponse = BaseResponse[CreateKnowledgeBaseData]
DeleteKnowledgeBaseResponse = BaseResponse[DeleteKnowledgeBaseData]
ListKnowledgeBasesResponse = BaseResponse[ListKnowledgeBasesData]

# 文档相关响应类型
ImportDocumentResponse = BaseResponse[ImportDocumentData]
ListDocumentsResponse = BaseResponse[ListDocumentsData]
DeleteDocumentResponse = BaseResponse[DeleteDocumentData]

# 搜索相关响应类型
SearchResponse = BaseResponse[SearchData]

# 文档解析结果相关响应类型
GetDocumentChunksResponse = BaseResponse[GetDocumentChunksData]

