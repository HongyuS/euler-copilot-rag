import os
import sys
import uuid
import logging
import asyncio
import json
from typing import Optional, Dict, Any, List

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from manager.database_manager import Database, get_kb_id_by_name, get_kb_ids_by_names
from manager.document_manager import DocumentManager
from common.config import get_default_top_k, get_github_enabled, get_github_default_online_top_k
from sqlite.kb_sqlite import KnowledgeBase, Document, Chunk
from search.weighted_keyword_and_vector_search import weighted_keyword_and_vector_search
from search.online_search import search_github_online
from schema import (
    BaseResponse,
    CreateKnowledgeBaseData, DeleteKnowledgeBaseData, ListKnowledgeBasesData, KnowledgeBaseInfo,
    ImportDocumentData, ImportFileSuccess, ImportFileFailed,
    ImportTaskData, TaskStatusData, CancelTaskData,
    ListDocumentsData, DocumentInfo,
    DeleteDocumentData,
    SearchData, SearchChunk, GitHubSearchResult, GitHubIssue, GitHubCommit,
    GetDocumentChunksData, DocumentChunkInfo, ShowDocumentData
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

_db_instance: Optional[Database] = None
_db_path = os.path.join(current_dir, "database", "kb.db")


def _get_db() -> Database:
    """获取数据库实例（固定使用kb.db）"""
    global _db_instance
    if _db_instance is None:
        db_dir = os.path.dirname(_db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        _db_instance = Database(_db_path)
    return _db_instance


def create_success_response(data, message: str) -> BaseResponse:
    """创建成功响应"""
    return BaseResponse(success=True, message=message, data=data)


def create_error_response(message: str, data=None) -> BaseResponse:
    """创建错误响应"""
    return BaseResponse(success=False, message=message, data=data)


def kb_to_info(kb: KnowledgeBase) -> KnowledgeBaseInfo:
    """将 ORM KnowledgeBase 转换为 KnowledgeBaseInfo"""
    return KnowledgeBaseInfo(
        id=kb.id,
        name=kb.name,
        chunk_size=kb.chunk_size,
        embedding_model=kb.embedding_model,
        created_at=kb.created_at.isoformat() if kb.created_at else None
    )


def doc_to_info(doc: Document) -> DocumentInfo:
    """将 ORM Document 转换为 DocumentInfo"""
    return DocumentInfo(
        id=doc.id,
        name=doc.name,
        file_path=doc.file_path,
        file_type=doc.file_type,
        chunk_size=doc.chunk_size,
        created_at=doc.created_at.isoformat() if doc.created_at else None,
        updated_at=doc.updated_at.isoformat() if doc.updated_at else None
    )


def chunk_to_info(chunk: Chunk) -> DocumentChunkInfo:
    """将 ORM Chunk 转换为 DocumentChunkInfo"""
    return DocumentChunkInfo(
        id=chunk.id,
        doc_id=chunk.doc_id,
        content=chunk.content,
        tokens=chunk.tokens,
        chunk_index=chunk.chunk_index,
        created_at=chunk.created_at.isoformat() if chunk.created_at else None
    )




def create_knowledge_base(
    kb_name: str,
    chunk_size: int,
    embedding_model: Optional[str] = None,
    embedding_endpoint: Optional[str] = None,
    embedding_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    新增知识库
    
    :param kb_name: 知识库名称
    :param chunk_size: chunk 大小（token 数）
    :param embedding_model: 向量化模型名称（可选）
    :param embedding_endpoint: 向量化服务端点（可选）
    :param embedding_api_key: 向量化服务 API Key（可选）
    :return: 创建结果
    """
    try:
        db = _get_db()
        session = db.get_session()
        try:
            # 检查知识库名称是否已存在
            existing_kb = db.get_knowledge_base(kb_name)
            if existing_kb:
                return create_error_response(f"知识库 '{kb_name}' 已存在").model_dump()
            
            kb_id = str(uuid.uuid4())
            kb = KnowledgeBase(
                id=kb_id,
                name=kb_name,
                chunk_size=chunk_size,
                embedding_model=embedding_model,
                embedding_endpoint=embedding_endpoint,
                embedding_api_key=embedding_api_key
            )
            if db.add_knowledge_base(kb):
                data = CreateKnowledgeBaseData(
                    kb_id=kb_id,
                    kb_name=kb_name,
                    chunk_size=chunk_size
                )
                return create_success_response(data=data, message=f"成功创建知识库: {kb_name}").model_dump()
            else:
                return create_error_response("创建知识库失败").model_dump()
        finally:
            session.close()
    except Exception as e:
        logger.exception(f"[create_knowledge_base] 创建知识库失败: {e}")
        return create_error_response("创建知识库失败").model_dump()


def delete_knowledge_base(kb_names: List[str]) -> Dict[str, Any]:
    """
    批量软删除知识库（标记为deleted）
    
    :param kb_names: 知识库名称列表，每批最多删除1024个
    :return: 删除结果
    """
    if not kb_names:
        return create_error_response("知识库名称列表不能为空").model_dump()
    
    try:
        db = _get_db()
        # 获取所有知识库的ID
        kb_ids = []
        not_found = []
        for kb_name in kb_names:
            kb = db.get_knowledge_base(kb_name)
            if kb:
                kb_ids.append(kb.id)
            else:
                not_found.append(kb_name)
        
        if not kb_ids:
            message = "没有找到任何有效的知识库"
            if not_found:
                message += f"，未找到的知识库: {', '.join(not_found)}"
            return create_error_response(message).model_dump()
        
        # 批量软删除
        deleted_count = db.delete_knowledge_bases_batch(kb_ids)
        
        data = DeleteKnowledgeBaseData(
            requested_count=len(kb_names),
            deleted_count=deleted_count,
            not_found=not_found
        )
        return create_success_response(data=data, message=f"成功删除 {deleted_count} 个知识库").model_dump()
    except Exception as e:
        logger.exception(f"[delete_knowledge_base] 删除知识库失败: {e}")
        return create_error_response(f"删除知识库失败: {str(e)}").model_dump()


def list_knowledge_bases(keyword: Optional[str] = None) -> Dict[str, Any]:
    """
    查看知识库列表（只显示excited状态，支持关键词过滤）
    
    :param keyword: 关键词（可选），用于模糊查询知识库名称。如果用户未提供，大模型可以根据用户意图推断关键词，例如用户说"我要和医学有关的知识库"，可以传入"医学"。
    :return: 知识库列表
    """
    try:
        db = _get_db()
        kbs = db.list_knowledge_bases(keyword)
        
        knowledge_bases = [kb_to_info(kb) for kb in kbs]
        data = ListKnowledgeBasesData(
            knowledge_bases=knowledge_bases,
            count=len(knowledge_bases),
            keyword=keyword
        )
        keyword_msg = f"（关键词: {keyword}）" if keyword else ""
        return create_success_response(data=data, message=f"找到 {len(knowledge_bases)} 个知识库{keyword_msg}").model_dump()
    except Exception as e:
        logger.exception(f"[list_knowledge_bases] 获取知识库列表失败: {e}")
        return create_error_response("获取知识库列表失败").model_dump()


async def create_import_task(file_paths: List[str], kb_name: str, chunk_size: Optional[int] = None) -> Dict[str, Any]:
    """
    创建文档导入任务，立即返回 task_id，后台异步导入
    """
    try:
        from manager.task_manager import TaskManager
        from manager.database_manager import get_kb_id_by_name
        from sqlite.kb_sqlite import KnowledgeBase

        db = _get_db()
        temp = {"success": False, "message": ""}
        kb_id = get_kb_id_by_name(db, kb_name, temp)
        if not kb_id:
            return create_error_response(temp["message"]).model_dump()

        if not file_paths:
            return create_error_response("文件路径列表为空").model_dump()

        invalid = [p for p in file_paths if not os.path.exists(p)]
        if invalid:
            return create_error_response(f"文件路径不存在: {', '.join(invalid)}").model_dump()

        session = db.get_session()
        try:
            kb = session.query(KnowledgeBase).filter_by(id=kb_id).first()
            if not kb:
                return create_error_response("知识库不存在").model_dump()
            if chunk_size is None:
                chunk_size = kb.chunk_size
        finally:
            session.close()

        task_id = str(uuid.uuid4())
        params = json.dumps({"file_paths": file_paths, "kb_name": kb_name, "chunk_size": chunk_size})
        task_name = f"document_import - {len(file_paths)} files"
        ok = await TaskManager.create_task(task_id, task_name, params)
        if not ok:
            return create_error_response("创建任务失败").model_dump()

        data = ImportTaskData(task_id=task_id, file_count=len(file_paths), message="任务已创建，后台导入中")
        return create_success_response(data=data, message="导入任务已创建").model_dump()
    except Exception as e:
        logger.exception("[create_import_task] %s", e)
        return create_error_response(f"创建导入任务失败: {str(e)}").model_dump()


async def get_import_task_status(task_id: str) -> Dict[str, Any]:
    """查询导入任务状态"""
    try:
        from manager.task_manager import TaskManager
        task = await TaskManager.get_task_by_id(task_id)
        if not task:
            return create_error_response("任务不存在").model_dump()
        summary = {}
        if task.get("result_summary"):
            summary = json.loads(task["result_summary"])
        success_files = [ImportFileSuccess(**f) for f in summary.get("success_files", [])]
        failed_files = [ImportFileFailed(**f) for f in summary.get("failed_files", [])]
        data = TaskStatusData(
            task_id=task["task_id"],
            status=task["status"],
            completion_precent=task.get("completion_precent", 0.0) or 0.0,
            success_count=len(success_files),
            failed_count=len(failed_files),
            success_files=success_files,
            failed_files=failed_files,
        )
        return create_success_response(data=data, message="查询成功").model_dump()
    except Exception as e:
        logger.exception("[get_import_task_status] %s", e)
        return create_error_response(f"查询失败: {str(e)}").model_dump()


async def cancel_import_task(task_id: str) -> Dict[str, Any]:
    """取消导入任务"""
    try:
        from enums.task import TaskStatusEnum
        from manager.task_manager import TaskManager
        from common.task import remove_task

        task = await TaskManager.get_task_by_id(task_id)
        if not task:
            return create_error_response("任务不存在").model_dump()
        status = task.get("status", "")
        if status not in (TaskStatusEnum.PENDING.value, TaskStatusEnum.RUNNING.value):
            return create_error_response(f"任务状态为 {status}，无法取消").model_dump()
        await remove_task(task_id)
        await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.CANCELED.value})
        data = CancelTaskData(task_id=task_id, canceled=True, message   ="任务已取消")
        return create_success_response(data=data, message="任务已取消").model_dump()
    except Exception as e:
        logger.exception("[cancel_import_task] %s", e)
        return create_error_response(f"取消失败: {str(e)}").model_dump()


async def search(query: str, kb_names: List[str], top_k: Optional[int] = None, keyword_weight: Optional[float] = None, banned_chunk_ids: Optional[List[str]] = None, online: bool = False, online_top_k: Optional[int] = None) -> Dict[str, Any]:
    """
    在指定知识库列表中查询（异步）
    
    :param query: 查询文本
    :param kb_names: 知识库名称列表
    :param top_k: 返回数量（可选，默认从配置读取）
    :param keyword_weight: 关键词搜索权重（0-1之间，可选，默认0.3）。如果查询包含较多关键词，建议提高此值；如果查询更偏向语义理解，建议降低此值。向量权重自动为 1 - keyword_weight
    :param banned_chunk_ids: 可选的被禁用的chunk ID列表，用于过滤掉不想要的chunk（可以为空）。通常用于多次搜索中排除之前搜索结果中效果不好的chunk
    :param online: 是否启用GitHub线上检索（可选，默认False）。如果为True，会在GitHub上搜索相关的Issues和Commits
    :param online_top_k: GitHub检索的返回数量（可选，默认从配置读取，通常为5）
    :return: 检索结果
    """
    if not kb_names:
        return create_error_response("知识库名称列表不能为空").model_dump()
    
    if top_k is None:
        top_k = get_default_top_k()
    
    # 设置默认关键词权重
    if keyword_weight is None:
        keyword_weight = 0.3
    
    # 验证权重范围
    if keyword_weight < 0.0 or keyword_weight > 1.0:
        return create_error_response(f"keyword_weight 必须在 0-1 之间，当前值: {keyword_weight}").model_dump()
    
    # 设置GitHub检索的top_k
    if online_top_k is None:
        online_top_k = get_github_default_online_top_k()
    
    db = _get_db()
    temp_result = {"success": False, "message": "", "data": {}}
    kb_ids = get_kb_ids_by_names(db, kb_names, temp_result)
    if not kb_ids:
        return create_error_response(temp_result["message"]).model_dump()
    
    # 并行执行本地检索和GitHub检索
    session = None
    try:
        session = db.get_session()
        # 获取所有指定知识库的文档ID
        manager = DocumentManager(session)
        doc_ids = []
        for kb_id in kb_ids:
            docs = manager.list_documents_by_kb(kb_id)
            doc_ids.extend([doc.id for doc in docs])
        
        # 获取连接（在session关闭前获取）
        conn = session.connection()
        
        # 创建本地检索任务
        if doc_ids:
            local_search_task = weighted_keyword_and_vector_search(
                conn, query, top_k, keyword_weight, doc_ids, banned_chunk_ids
            )
        else:
            local_search_task = None
        
        # 如果启用GitHub检索且配置启用，并行执行GitHub检索
        if online and get_github_enabled():
            github_search_task = search_github_online(query, online_top_k)
            if local_search_task:
                chunks_dict, github_result = await asyncio.gather(
                    local_search_task,
                    github_search_task,
                    return_exceptions=True
                )
            else:
                chunks_dict = []
                github_result = await github_search_task
        else:
            if local_search_task:
                chunks_dict = await local_search_task
            else:
                chunks_dict = []
            github_result = None
        
        # 在异步任务执行完成后再关闭session
        if session:
            session.close()
            session = None
        
        # 处理本地检索结果
        if isinstance(chunks_dict, Exception):
            logger.exception(f"[search] 本地检索失败: {chunks_dict}")
            chunks_dict = []
        
        # 如果本地和GitHub都没有结果，返回错误
        if not chunks_dict and (not github_result or isinstance(github_result, Exception) or (not github_result.get("issues") and not github_result.get("commits"))):
            data = SearchData(chunks=[], count=0)
            return create_error_response("未找到相关结果", data=data).model_dump()
        
        # 将字典转换为 SearchChunk Schema
        chunks = [SearchChunk(**chunk) for chunk in chunks_dict]
        
        # 处理GitHub检索结果
        github_search_result = None
        if github_result and not isinstance(github_result, Exception):
            github_issues = [GitHubIssue(**issue) for issue in github_result.get("issues", [])]
            github_commits = [GitHubCommit(**commit) for commit in github_result.get("commits", [])]
            github_search_result = GitHubSearchResult(
                issues=github_issues,
                commits=github_commits,
                success=github_result.get("success", False),
                error_message=github_result.get("error_message")
            )
        elif isinstance(github_result, Exception):
            logger.warning(f"[search] GitHub检索异常: {github_result}")
            github_search_result = GitHubSearchResult(
                success=False,
                error_message=str(github_result)
            )
        
        # 构建返回数据
        data = SearchData(
            chunks=chunks,
            count=len(chunks),
            github_results=github_search_result
        )
        
        message = f"找到 {len(chunks)} 个本地相关结果"
        if github_search_result and github_search_result.success:
            message += f"，{len(github_search_result.issues)} 个GitHub Issues，{len(github_search_result.commits)} 个GitHub Commits"
        
        return create_success_response(data=data, message=message).model_dump()
    except Exception as e:
        logger.exception(f"[search] 搜索失败: {e}")
        return create_error_response("搜索失败").model_dump()
    finally:
        # 确保session被关闭
        if session:
            session.close()


def list_documents(kb_names: List[str], keyword: Optional[str] = None) -> Dict[str, Any]:
    """
    查看指定知识库列表下的文档列表（只显示excited状态，支持关键词过滤）
    
    :param kb_names: 知识库名称列表
    :param keyword: 关键词（可选），用于模糊查询文档名称。如果用户未提供，大模型可以根据用户意图推断关键词，例如用户说"我要和医学有关的所有文档"，可以传入"医学"。
    :return: 文档列表
    """
    if not kb_names:
        return create_error_response("知识库名称列表不能为空").model_dump()
    
    try:
        db = _get_db()
        temp_result = {"success": False, "message": "", "data": {}}
        kb_ids = get_kb_ids_by_names(db, kb_names, temp_result)
        if not kb_ids:
            return create_error_response(temp_result["message"]).model_dump()
        
        session = db.get_session()
        try:
            manager = DocumentManager(session)
            all_docs = []
            for kb_id in kb_ids:
                docs = manager.list_documents_by_kb(kb_id, keyword)
                all_docs.extend(docs)
        finally:
            session.close()
        
        documents = [doc_to_info(doc) for doc in all_docs]
        data = ListDocumentsData(
            documents=documents,
            count=len(documents),
            keyword=keyword
        )
        keyword_msg = f"（关键词: {keyword}）" if keyword else ""
        return create_success_response(data=data, message=f"找到 {len(documents)} 个文档{keyword_msg}").model_dump()
    except Exception as e:
        logger.exception(f"[list_documents] 获取文档列表失败: {e}")
        return create_error_response("获取文档列表失败").model_dump()


def delete_document(doc_names: List[str], kb_name: str) -> Dict[str, Any]:
    """
    批量软删除指定知识库下的文档（标记为deleted，每批最多删除1024个）
    
    :param doc_names: 文档名称列表，每批最多删除1024个
    :param kb_name: 知识库名称
    :return: 删除结果
    """
    if not doc_names:
        return create_error_response("文档名称列表不能为空").model_dump()
    
    try:
        db = _get_db()
        temp_result = {"success": False, "message": "", "data": {}}
        kb_id = get_kb_id_by_name(db, kb_name, temp_result)
        if not kb_id:
            return create_error_response(temp_result["message"]).model_dump()
        
        session = db.get_session()
        try:
            manager = DocumentManager(session)
            deleted_count = manager.delete_documents_batch(kb_id, doc_names)
            
            data = DeleteDocumentData(
                requested_count=len(doc_names),
                deleted_count=deleted_count,
                kb_name=kb_name
            )
            return create_success_response(data=data, message=f"成功删除 {deleted_count} 个文档").model_dump()
        finally:
            session.close()
    except Exception as e:
        logger.exception(f"[delete_document] 删除文档失败: {e}")
        return create_error_response(f"删除文档失败: {str(e)}").model_dump()


def get_document_chunks(doc_name: str, kb_name: str) -> Dict[str, Any]:
    """
    获取文档的解析结果（所有chunks）
    
    :param doc_name: 文档名称（必填，由用户给出）
    :param kb_name: 知识库名称（必填，如果用户未提供，大模型可以根据上下文推断或询问用户）
    :return: 文档解析结果
    """
    if not doc_name:
        return create_error_response("文档名称不能为空").model_dump()
    
    if not kb_name:
        return create_error_response("知识库名称不能为空").model_dump()
    
    try:
        db = _get_db()
        temp_result = {"success": False, "message": "", "data": {}}
        kb_id = get_kb_id_by_name(db, kb_name, temp_result)
        if not kb_id:
            return create_error_response(temp_result["message"]).model_dump()
        
        session = db.get_session()
        try:
            manager = DocumentManager(session)
            doc = manager.get_document(kb_id, doc_name)
            if not doc:
                return create_error_response(f"文档 '{doc_name}' 在知识库 '{kb_name}' 中不存在").model_dump()
            
            chunks = manager.get_document_chunks(doc.id)
            chunk_infos = [chunk_to_info(chunk) for chunk in chunks]
            
            data = GetDocumentChunksData(
                doc_id=doc.id,
                doc_name=doc.name,
                kb_name=kb_name,
                chunks=chunk_infos,
                count=len(chunk_infos)
            )
            return create_success_response(data=data, message=f"找到文档 '{doc_name}' 的 {len(chunk_infos)} 个chunk").model_dump()
        finally:
            session.close()
    except Exception as e:
        logger.exception(f"[get_document_chunks] 获取文档解析结果失败: {e}")
        return create_error_response(f"获取文档解析结果失败: {str(e)}").model_dump()


def show_document(doc_name: str, kb_name: str) -> Dict[str, Any]:
    """获取已导入文档的完整正文"""
    if not doc_name:
        return create_error_response("文档名称不能为空").model_dump()
    if not kb_name:
        return create_error_response("知识库名称不能为空").model_dump()
    try:
        db = _get_db()
        temp_result = {"success": False, "message": "", "data": {}}
        kb_id = get_kb_id_by_name(db, kb_name, temp_result)
        if not kb_id:
            return create_error_response(temp_result["message"]).model_dump()
        session = db.get_session()
        try:
            manager = DocumentManager(session)
            ok, msg, payload = manager.show_document_text(kb_id, doc_name)
            if not ok or not payload:
                return create_error_response(msg).model_dump()
            data = ShowDocumentData(
                doc_id=payload["doc_id"],
                doc_name=payload["doc_name"],
                kb_name=kb_name,
                content=payload["content"],
            )
            return create_success_response(data=data, message="获取文档正文成功").model_dump()
        finally:
            session.close()
    except Exception as e:
        logger.exception(f"[show_document] 失败: {e}")
        return create_error_response(f"获取文档正文失败: {str(e)}").model_dump()


def knowledge_base_manager(
    action: str,
    kb_name: Optional[str] = None,
    chunk_size: Optional[int] = None,
    embedding_model: Optional[str] = None,
    embedding_endpoint: Optional[str] = None,
    embedding_api_key: Optional[str] = None,
    keyword: Optional[str] = None
) -> Dict[str, Any]:
    """
    知识库管理器，支持创建和列出知识库
    
    :param action: 操作类型，"add" 表示创建知识库，"list" 表示列出知识库
    :param kb_name: 知识库名称（创建时必填）
    :param chunk_size: chunk 大小（创建时必填）
    :param embedding_model: 向量化模型名称（创建时可选）
    :param embedding_endpoint: 向量化服务端点（创建时可选）
    :param embedding_api_key: 向量化服务 API Key（创建时可选）
    :param keyword: 关键词（列出时可选，用于模糊查询）
    :return: 操作结果
    """
    if action == "add":
        if not kb_name or chunk_size is None:
            return create_error_response("创建知识库时，kb_name 和 chunk_size 必填").model_dump()
        return create_knowledge_base(kb_name, chunk_size, embedding_model, embedding_endpoint, embedding_api_key)
    elif action == "list":
        return list_knowledge_bases(keyword)
    else:
        return create_error_response(f"不支持的操作类型: {action}，支持的操作: 'add', 'list'").model_dump()


async def document_manager(
    action: str,
    file_paths: Optional[List[str]] = None,
    kb_name: Optional[str] = None,
    chunk_size: Optional[int] = None,
    doc_name: Optional[str] = None,
    task_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    文档管理器：add、getstatus、cancel、getchunks、show
    """
    if action == "add":
        if not file_paths or not kb_name:
            return create_error_response("导入文档时 file_paths 和 kb_name 必填").model_dump()
        return await create_import_task(file_paths, kb_name, chunk_size)
    if action == "getstatus":
        if not task_id:
            return create_error_response("查询状态时 task_id 必填").model_dump()
        return await get_import_task_status(task_id)
    if action == "cancel":
        if not task_id:
            return create_error_response("取消任务时 task_id 必填").model_dump()
        return await cancel_import_task(task_id)
    if action == "getchunks":
        if not doc_name or not kb_name:
            return create_error_response("获取解析结果时 doc_name 和 kb_name 必填").model_dump()
        return get_document_chunks(doc_name, kb_name)
    if action == "show":
        if not doc_name or not kb_name:
            return create_error_response("查看全文时 doc_name 和 kb_name 必填").model_dump()
        return show_document(doc_name, kb_name)
    return create_error_response(
        f"不支持的操作: {action}，支持: add, getstatus, cancel, getchunks, show"
    ).model_dump()


