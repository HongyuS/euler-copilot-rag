# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.

from fastapi import APIRouter, Depends, Query, Body, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, Response
from typing import Annotated
import urllib
import time
from uuid import UUID
from httpx import AsyncClient
from typing import Annotated
from uuid import UUID
from data_chain.entities.enum import IdType, MessageLevel
from data_chain.entities.request_data import (
    ListDocumentRequest,
    UpdateDocumentRequest,
    GetTemporaryDocumentStatusRequest,
    UploadTemporaryRequest,
    DeleteTemporaryDocumentRequest
)

from data_chain.entities.response_data import (
    ListDocumentMsg,
    ListDocumentResponse,
    GetDocumentReportResponse,
    UploadDocumentResponse,
    ParseDocumentResponse,
    ParseDocumentRealTimeResponse,
    UpdateDocumentResponse,
    DeleteDocumentResponse,
    GetTemporaryDocumentStatusResponse,
    UploadTemporaryDocumentResponse,
    GetTemporaryDocumentTextResponse,
    DeleteTemporaryDocumentResponse,
    SpeedTestResult,
    SpeedTestResponse
)
from data_chain.apps.service.session_service import get_user_sub, verify_user
from data_chain.apps.service.router_service import get_route_info
from data_chain.apps.exceptions import (
    DocumentPermissionDeniedException,
    KnowledgeBasePermissionDeniedException
)
from data_chain.apps.service.team_service import TeamService
from data_chain.apps.service.knwoledge_base_service import KnowledgeBaseService
from data_chain.apps.service.document_service import DocumentService
router = APIRouter(prefix='/doc', tags=['Document'])


@router.post('/list', response_model=ListDocumentResponse, dependencies=[Depends(verify_user)])
async def list_doc(
    user_sub: Annotated[str, Depends(get_user_sub)],
    action: Annotated[str, Depends(get_route_info)],
    req: Annotated[ListDocumentRequest, Body()]
):
    if not (await KnowledgeBaseService.validate_user_action_to_knowledge_base(user_sub, req.kb_id, action)):
        raise KnowledgeBasePermissionDeniedException("访问该知识库的文档", str(req.kb_id))
    list_document_msg = await DocumentService.list_doc(req)
    await TeamService.add_team_msg(user_sub, req.kb_id, IdType.KNOWLEDGE_BASE, MessageLevel.INFO, '查看了知识库{kbName}的文档列表', 'knowledge base {kbName} Document list viewed')
    return ListDocumentResponse(result=list_document_msg)


@router.get('/download', dependencies=[Depends(verify_user)])
async def download_doc_by_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        doc_id: Annotated[UUID, Query(alias="docId")]):
    if not (await DocumentService.validate_user_action_to_document(user_sub, doc_id, action)):
        raise DocumentPermissionDeniedException("下载该文档，或者文档已被删除", str(doc_id))
    document_link_url = await DocumentService.generate_doc_download_url(doc_id)
    document_name, extension = await DocumentService.get_doc_name_and_extension(doc_id)
    async with AsyncClient() as async_client:
        response = await async_client.get(document_link_url)
        if response.status_code == 200:
            content_disposition = f"attachment; filename={urllib.parse.quote(document_name.encode('utf-8'))}"

            async def stream_generator():
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    yield chunk

            await TeamService.add_team_msg(user_sub, doc_id, IdType.DOCUMENT, MessageLevel.INFO, '下载了知识库{kbName}的文档《{documentName}》', 'knowledge base {kbName} Document <{documentName}> downloaded')

            return StreamingResponse(stream_generator(), headers={
                "Content-Disposition": content_disposition,
                "Content-Length": str(response.headers.get('content-length'))
            }, media_type="application/" + extension)
        else:
            raise Exception(f"下载文档失败，状态码: {response.status_code}")

@router.get('/report', response_model=GetDocumentReportResponse, dependencies=[Depends(verify_user)])
async def get_doc_report(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        doc_id: Annotated[UUID, Query(alias="docId")]):
    if not (await DocumentService.validate_user_action_to_document(user_sub, doc_id, action)):
        raise DocumentPermissionDeniedException("访问该文档的解析报告", str(doc_id))
    task_report = await DocumentService.get_doc_report(doc_id)
    await TeamService.add_team_msg(user_sub, doc_id, IdType.DOCUMENT, MessageLevel.INFO, '查看了知识库{kbName}的文档《{documentName}》的解析报告', 'knowledge base {kbName} Document <{documentName}> report viewed')
    return GetDocumentReportResponse(result=task_report)


@router.get('/report/download', dependencies=[Depends(verify_user)])
async def download_doc_report(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        doc_id: Annotated[UUID, Query(alias="docId")]):
    if not (await DocumentService.validate_user_action_to_document(user_sub, doc_id, action)):

        raise DocumentPermissionDeniedException("访问该文档", str(doc_id))
    report_link_url = await DocumentService.generate_doc_report_download_url(doc_id)
    report_name = 'report.txt'
    extension = 'txt'
    async with AsyncClient() as async_client:
        response = await async_client.get(report_link_url)
        if response.status_code == 200:
            content_disposition = f"attachment; filename={urllib.parse.quote(report_name.encode('utf-8'))}"

            async def stream_generator():
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    yield chunk

            await TeamService.add_team_msg(user_sub, doc_id, IdType.DOCUMENT, MessageLevel.INFO, '下载了知识库{kbName}的文档《{documentName}》的解析报告', 'knowledge base {kbName} Document <{documentName}> report downloaded')

            return StreamingResponse(stream_generator(), headers={
                "Content-Disposition": content_disposition,
                "Content-Length": str(response.headers.get('content-length'))
            }, media_type="application/" + extension)
        else:
            raise Exception(f"下载文档报告失败，状态码: {response.status_code}")

@router.post('', response_model=UploadDocumentResponse, dependencies=[Depends(verify_user)])
async def upload_docs(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        kb_id: Annotated[UUID, Query(alias="kbId")],
        docs: list[UploadFile] = File(...)):
    if not (await KnowledgeBaseService.validate_user_action_to_knowledge_base(user_sub, kb_id, action)):
        raise KnowledgeBasePermissionDeniedException("上传文档到该知识库", str(kb_id))
    doc_ids = await DocumentService.upload_docs(user_sub, kb_id, docs)
    await TeamService.add_team_msg(user_sub, kb_id, IdType.KNOWLEDGE_BASE, MessageLevel.INFO, '往{kbName}上传了文档', 'uploaded documents to {kbName}')
    return UploadDocumentResponse(result=doc_ids)


@router.post('/parse', response_model=ParseDocumentResponse, dependencies=[Depends(verify_user)])
async def parse_docuement_by_doc_ids(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        doc_ids: Annotated[list[UUID], Body(alias="docIds")],
        parse: Annotated[bool, Query()]):
    for doc_id in doc_ids:
        if not (await DocumentService.validate_user_action_to_document(user_sub, doc_id, action)):
            raise DocumentPermissionDeniedException("解析该文档", str(doc_id))
    doc_ids = await DocumentService.parse_docs(doc_ids, parse)
    for doc_id in doc_ids:
        await TeamService.add_team_msg(user_sub, doc_id, IdType.DOCUMENT, MessageLevel.INFO, '解析了知识库{kbName}的文档《{documentName}》', 'knowledge base {kbName} Document <{documentName}> parsed')
    return ParseDocumentResponse(result=doc_ids)


@router.post('/metadata', response_model=ParseDocumentRealTimeResponse, dependencies=[Depends(verify_user)])
async def parse_docuement_realtime(
    user_sub: Annotated[str, Depends(get_user_sub)],
    docs: list[UploadFile] = File(...)
):
    doc_contents = await DocumentService.parse_docs_realtime(docs)
    return ParseDocumentRealTimeResponse(result=doc_contents)


@router.put('', response_model=UpdateDocumentResponse, dependencies=[Depends(verify_user)])
async def update_doc_by_doc_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        doc_id: Annotated[UUID, Query(alias="docId")],
        req: Annotated[UpdateDocumentRequest, Body()]):
    if not (await DocumentService.validate_user_action_to_document(user_sub, doc_id, action)):
        raise DocumentPermissionDeniedException("更新该文档", str(doc_id))
    doc_id = await DocumentService.update_doc(doc_id, req)
    await TeamService.add_team_msg(user_sub, doc_id, IdType.DOCUMENT, MessageLevel.INFO, '更新了知识库{kbName}的文档《{documentName}》', 'knowledge base {kbName} Document <{documentName}> updated')
    return UpdateDocumentResponse(result=doc_id)


@router.delete('', response_model=DeleteDocumentResponse, dependencies=[Depends(verify_user)])
async def delete_docs_by_ids(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        doc_ids: Annotated[list[UUID], Body(alias="docIds")]):
    for doc_id in doc_ids:
        if not (await DocumentService.validate_user_action_to_document(user_sub, doc_id, action)):
            raise DocumentPermissionDeniedException("删除该文档", str(doc_id))
    for doc_id in doc_ids:
        await TeamService.add_team_msg(user_sub, doc_id, IdType.DOCUMENT, MessageLevel.WARNING, '删除了{kbName}的文档{documentName}', 'knowledge base {kbName} Document {documentName} deleted')
    await DocumentService.delete_docs_by_ids(doc_ids)
    return DeleteDocumentResponse(result=doc_ids)


@router.post('/temporary/status', response_model=GetTemporaryDocumentStatusResponse, dependencies=[
    Depends(verify_user)])
async def get_temporary_docs_status(
        user_sub: Annotated[str, Depends(get_user_sub)],
        req: Annotated[GetTemporaryDocumentStatusRequest, Body()]):
    doc_status_list = await DocumentService.get_temporary_docs_status(user_sub, req.ids)
    return GetTemporaryDocumentStatusResponse(result=doc_status_list)


@router.post('/temporary/parser', response_model=UploadTemporaryDocumentResponse, dependencies=[Depends(verify_user)])
async def upload_temporary_docs(
        user_sub: Annotated[str, Depends(get_user_sub)],
        req: Annotated[UploadTemporaryRequest, Body()]):
    doc_ids = await DocumentService.upload_temporary_docs(user_sub, req)
    return UploadTemporaryDocumentResponse(result=doc_ids)


@router.get('/temporary/text', response_model=GetTemporaryDocumentTextResponse,
            dependencies=[Depends(verify_user)])
async def get_temporary_docs_text(
        user_sub: Annotated[str, Depends(get_user_sub)],
        id: Annotated[UUID, Query()]):
    doc_text = await DocumentService.get_temporary_doc_text(user_sub, id)
    return GetTemporaryDocumentTextResponse(result=doc_text)


@router.post('/temporary/delete', response_model=DeleteTemporaryDocumentResponse, dependencies=[Depends(verify_user)])
async def delete_temporary_docs(
        user_sub: Annotated[str, Depends(get_user_sub)],
        req: Annotated[DeleteTemporaryDocumentRequest, Body()]):
    doc_ids = await DocumentService.delete_temporary_docs(user_sub, req.ids)
    return DeleteTemporaryDocumentResponse(result=doc_ids)


@router.post('/speed-test', response_model=SpeedTestResponse, dependencies=[Depends(verify_user)])
async def upload_speed_test(
        user_sub: Annotated[str, Depends(get_user_sub)],
        file: UploadFile = File(...)):
    """
    网络上传速度测试接口
    - 仅接受单个文件
    - 文件大小限制为最大 50KB
    - 文件接收后立即丢弃，不保存到存储系统
    - 返回处理时间用于前端计算上传速度
    """
    # 限制文件大小为 50KB
    MAX_FILE_SIZE = 50 * 1024  # 50KB
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 读取文件内容
        content = await file.read()
        
        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"文件大小超过限制，最大允许 {MAX_FILE_SIZE // 1024}KB"
            )
        
        # 记录结束时间
        end_time = time.time()
        
        # 计算处理时间（毫秒）
        processing_time = (end_time - start_time) * 1000
        
        # 文件大小（字节）
        file_size = len(content)
        
        # 立即丢弃文件内容，不保存
        del content

        _result = SpeedTestResult(
            success=True,
            file_size=file_size,
            processing_time_ms=processing_time,
        )
        return SpeedTestResponse(
            result=_result,
            message="速度测试完成，文件已丢弃"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"速度测试失败: {str(e)}")
    finally:
        # 确保文件句柄被关闭
        if hasattr(file, 'file') and file.file:
            file.file.close()
