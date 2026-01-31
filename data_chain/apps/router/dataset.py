# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
from fastapi import APIRouter, Depends, Query, Body, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, Response
from httpx import AsyncClient
from typing import Annotated
import urllib
from uuid import UUID
from data_chain.entities.request_data import (
    ListDatasetRequest,
    ListDataInDatasetRequest,
    CreateDatasetRequest,
    UpdateDatasetRequest,
    UpdateDataRequest,
)

from data_chain.entities.response_data import (
    ListDatasetResponse,
    ListDataInDatasetResponse,
    IsDatasetHaveTestingResponse,
    CreateDatasetResponse,
    ImportDatasetResponse,
    ExportDatasetResponse,
    GenerateDatasetResponse,
    UpdateDatasetResponse,
    UpdateDataResponse,
    DeleteDatasetResponse,
    DeleteDataResponse
)
from data_chain.entities.enum import IdType, MessageLevel
from data_chain.apps.service.team_service import TeamService
from data_chain.apps.service.knwoledge_base_service import KnowledgeBaseService
from data_chain.apps.service.dataset_service import DataSetService
from data_chain.apps.service.task_service import TaskService
from data_chain.apps.service.session_service import get_user_sub, verify_user
from data_chain.apps.service.router_service import get_route_info
from data_chain.apps.exceptions import (
    DatasetPermissionDeniedException,
    KnowledgeBasePermissionDeniedException,
    TaskPermissionDeniedException
)
router = APIRouter(prefix='/dataset', tags=['Dataset'])


@router.post('/list', response_model=ListDatasetResponse, dependencies=[Depends(verify_user)])
async def list_dataset_by_kb_id(
    user_sub: Annotated[str, Depends(get_user_sub)],
    action: Annotated[str, Depends(get_route_info)],
    req: Annotated[ListDatasetRequest, Body()],
):
    if not (await KnowledgeBaseService.validate_user_action_to_knowledge_base(user_sub, req.kb_id, action)):
        raise KnowledgeBasePermissionDeniedException("访问该知识库的数据集", str(req.kb_id))
    list_dataset_msg = await DataSetService.list_dataset_by_kb_id(req)
    await TeamService.add_team_msg(user_sub, req.kb_id, IdType.KNOWLEDGE_BASE, MessageLevel.INFO, '查看了知识库{kbName}的数据集列表', 'knowledge base {kbName} Dataset list viewed')
    return ListDatasetResponse(result=list_dataset_msg)


@router.post('/data', response_model=ListDataInDatasetResponse, dependencies=[Depends(verify_user)])
async def list_data_in_dataset(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        req: Annotated[ListDataInDatasetRequest, Body()]):
    if not (await DataSetService.validate_user_action_to_dataset(user_sub, req.dataset_id, action)):
        raise DatasetPermissionDeniedException("访问该数据集的数据", str(req.dataset_id))
    list_data_in_dataset_msg = await DataSetService.list_data_in_dataset(req)
    await TeamService.add_team_msg(user_sub, req.dataset_id, IdType.DATASET, MessageLevel.INFO, '查看了知识库{kbName}的数据集{datasetName}的数据列表', 'knowledge base {kbName} Dataset {datasetName} data list viewed')
    return ListDataInDatasetResponse(result=list_data_in_dataset_msg)


@router.get('/testing/exist', response_model=IsDatasetHaveTestingResponse, dependencies=[Depends(verify_user)])
async def is_dataset_have_testing(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        dataset_id: Annotated[UUID, Query(alias="datasetId")]):
    if not (await DataSetService.validate_user_action_to_dataset(user_sub, dataset_id, action)):
        raise DatasetPermissionDeniedException("访问该数据集的数据", str(dataset_id))
    is_dataset_have_testing_response = await DataSetService.is_dataset_have_testing(dataset_id)
    return IsDatasetHaveTestingResponse(result=is_dataset_have_testing_response)


@router.get('/download', dependencies=[Depends(verify_user)])
async def download_dataset_by_task_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        task_id: Annotated[UUID, Query(alias="taskId")]):

    if not (await TaskService.validate_user_action_to_task(user_sub, task_id, action)):
        raise TaskPermissionDeniedException("访问该任务的数据集", str(task_id))
    dataset_link_url = await DataSetService.generate_dataset_download_url(task_id)
    document_name, extension = str(task_id)+".zip", "zip"
    async with AsyncClient() as async_client:
        response = await async_client.get(dataset_link_url)
        if response.status_code == 200:
            content_disposition = f"attachment; filename={urllib.parse.quote(document_name.encode('utf-8'))}"

            async def stream_generator():
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    yield chunk

            await TeamService.add_team_msg(user_sub, task_id, IdType.TASK, MessageLevel.INFO, '下载了知识库{kbName}的数据集{datasetName}', 'knowledge base {kbName} Dataset {datasetName} downloaded')

            return StreamingResponse(stream_generator(), headers={
                "Content-Disposition": content_disposition,
                "Content-Length": str(response.headers.get('content-length'))
            }, media_type="application/" + extension)
        else:
            raise Exception(f"下载数据集失败，状态码: {response.status_code}")


@router.post('', response_model=CreateDatasetResponse, dependencies=[Depends(verify_user)])
async def create_dataset(
    user_sub: Annotated[str, Depends(get_user_sub)],
    action: Annotated[str, Depends(get_route_info)],
    req: Annotated[CreateDatasetRequest, Body()]
):
    if not (await KnowledgeBaseService.validate_user_action_to_knowledge_base(user_sub, req.kb_id, action)):
        raise KnowledgeBasePermissionDeniedException("访问该知识库的数据集", str(req.kb_id))
    task_id = await DataSetService.create_dataset(user_sub, req)
    await TeamService.add_team_msg(user_sub, req.kb_id, IdType.KNOWLEDGE_BASE, MessageLevel.INFO, '创建了知识库{kbName}的数据集', 'knowledge base {kbName} Dataset created')
    return CreateDatasetResponse(result=task_id)


@router.post('/import', response_model=ImportDatasetResponse, dependencies=[Depends(verify_user)])
async def import_dataset(user_sub: Annotated[str, Depends(get_user_sub)],
                         action: Annotated[str, Depends(get_route_info)],
                         kb_id: Annotated[UUID, Query(alias="kbId")],
                         dataset_packages: list[UploadFile] = File(...)):
    if not (await KnowledgeBaseService.validate_user_action_to_knowledge_base(user_sub, kb_id, action)):
        raise KnowledgeBasePermissionDeniedException("在该知识库导入数据集", str(kb_id))
    dataset_import_task_ids = await DataSetService.import_dataset(user_sub, kb_id, dataset_packages)
    await TeamService.add_team_msg(user_sub, kb_id, IdType.KNOWLEDGE_BASE, MessageLevel.INFO, '导入了知识库{kbName}的数据集', 'knowledge base {kbName} Dataset imported')
    return ImportDatasetResponse(result=dataset_import_task_ids)


@router.post('/export', response_model=ExportDatasetResponse, dependencies=[Depends(verify_user)])
async def export_dataset_by_dataset_ids(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        dataset_ids: Annotated[list[UUID], Query(alias="datasetIds")]):
    for dataset_id in dataset_ids:
        if not (await DataSetService.validate_user_action_to_dataset(user_sub, dataset_id, action)):
            raise DatasetPermissionDeniedException("访问该数据集的数据", str(dataset_id))
    dataset_export_task_ids = await DataSetService.export_dataset(dataset_ids)
    for dataset_id in dataset_ids:
        await TeamService.add_team_msg(user_sub, dataset_id, IdType.DATASET, MessageLevel.INFO, '导出了知识库{kbName}的数据集{datasetName}', 'knowledge base {kbName} Dataset {datasetName} exported')
    return ExportDatasetResponse(result=dataset_export_task_ids)


@router.post('/generate', response_model=GenerateDatasetResponse, dependencies=[Depends(verify_user)])
async def generate_dataset_by_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        dataset_id: Annotated[UUID, Query(alias="datasetId")],
        generate: Annotated[bool, Query()]):
    if not (await DataSetService.validate_user_action_to_dataset(user_sub, dataset_id, action)):
        raise DatasetPermissionDeniedException("访问该数据集", str(dataset_id))
    dataset_id = await DataSetService.generate_dataset_by_id(dataset_id, generate)
    await TeamService.add_team_msg(user_sub, dataset_id, IdType.DATASET, MessageLevel.INFO, '生成了知识库{kbName}的数据集{datasetName}', 'knowledge base {kbName} Dataset {datasetName} generated')
    return GenerateDatasetResponse(result=dataset_id)


@router.put('', response_model=UpdateDatasetResponse, dependencies=[Depends(verify_user)])
async def update_dataset_by_dataset_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        database_id: Annotated[UUID, Query(alias="databaseId")],
        req: Annotated[UpdateDatasetRequest, Body(...)]):
    if not (await DataSetService.validate_user_action_to_dataset(user_sub, database_id, action)):
        raise DatasetPermissionDeniedException("访问该数据集", str(database_id))
    database_id = await DataSetService.update_dataset_by_dataset_id(database_id, req)
    await TeamService.add_team_msg(user_sub, database_id, IdType.DATASET, MessageLevel.INFO, '更新了知识库{kbName}的数据集{datasetName}', 'knowledge base {kbName} Dataset {datasetName} updated')
    return UpdateDatasetResponse(result=database_id)


@router.put('/data', response_model=UpdateDataResponse, dependencies=[Depends(verify_user)])
async def update_data_by_dataset_id(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        data_id: Annotated[UUID, Query(alias="dataId")],
        req: Annotated[UpdateDataRequest, Body(...)]):
    if not (await DataSetService.validate_user_action_to_data(user_sub, data_id, action)):
        raise DatasetPermissionDeniedException("访问该数据集的数据", str(req.dataset_id))
    data_id = await DataSetService.update_data(data_id, req)
    await TeamService.add_team_msg(user_sub, data_id, IdType.DATASET_DATA, MessageLevel.INFO, '更新了知识库{kbName}的数据集{datasetName}的数据', 'knowledge base {kbName} Dataset {datasetName} data updated')
    return UpdateDataResponse()


@router.delete('', response_model=DeleteDatasetResponse, dependencies=[Depends(verify_user)])
async def delete_dataset_by_dataset_ids(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        database_ids: Annotated[list[UUID], Body(alias="databaseId")]):
    for database_id in database_ids:
        if not (await DataSetService.validate_user_action_to_dataset(user_sub, database_id, action)):
            raise DatasetPermissionDeniedException("访问该数据集", str(database_id))
    dataset_ids = await DataSetService.delete_dataset_by_dataset_ids(database_ids)
    for dataset_id in dataset_ids:
        await TeamService.add_team_msg(user_sub, dataset_id, IdType.DATASET, MessageLevel.WARNING, '删除了知识库{kbName}的数据集{datasetName}', 'knowledge base {kbName} Dataset {datasetName} deleted')
    return DeleteDatasetResponse(result=dataset_ids)


@router.delete('/data', response_model=DeleteDataResponse, dependencies=[Depends(verify_user)])
async def delete_data_by_data_ids(
        user_sub: Annotated[str, Depends(get_user_sub)],
        action: Annotated[str, Depends(get_route_info)],
        data_ids: Annotated[list[UUID], Body(alias="dataIds")]):
    for data_id in data_ids:
        if not (await DataSetService.validate_user_action_to_data(user_sub, data_id, action)):
            raise DatasetPermissionDeniedException("访问该数据集的数据", str(data_id))
    for data_id in data_ids:
        await TeamService.add_team_msg(user_sub, data_id, IdType.DATASET_DATA, MessageLevel.WARNING, '删除了知识库{kbName}的数据集{datasetName}的数据', 'knowledge base {kbName} Dataset {datasetName} data deleted')
    await DataSetService.delete_data_by_data_ids(data_ids)
    return DeleteDataResponse()
