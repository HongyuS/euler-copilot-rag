# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import warnings
# 过滤 APScheduler 中 pkg_resources 弃用警告
warnings.filterwarnings('ignore', message='pkg_resources is deprecated', category=UserWarning)

from typing import Annotated
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvicorn
import fastapi
import os
import shutil
from data_chain.config.config import config
from data_chain.logger.logger import logger as logging
from data_chain.entities.common import actions, DEFAULT_DOC_TYPE_ID
from data_chain.apps.router import (
    team,
    knowledge_base,
    document,
    chunk,
    dataset,
    acc_testing,
    health_check,
    other,
    role,
    usr_message,
    task,
    user
)
from data_chain.apps.base.task.worker import (
    base_worker,
    export_dataset_worker,
    import_dataset_worker,
    export_knowledge_base_worker,
    import_knowledge_base_worker,
    generate_dataset_worker,
    acc_testing_worker,
    parse_document_worker
)
from data_chain.parser.handler import (
    base_parser,
    doc_parser,
    docx_parser,
    html_parser,
    json_parser,
    md_parser,
    md_zip_parser,
    pdf_parser,
    pptx_parser,
    txt_parser,
    xlsx_parser,
    yaml_parser,
    picture_parser,
    deep_pdf_parser,
    fine_pdf_parser
)
from data_chain.rag import (
    base_searcher,
    keyword_searcher,
    vector_searcher,
    dynamic_weighted_keyword_and_vector_searcher,
    keyword_and_vector_searcher,
    doc2chunk_searcher,
    doc2chunk_bfs_searcher,
    enhanced_by_llm_searcher,
    query_extend_searcher,
    dynamic_weighted_keyword_searcher
)
from data_chain.stores.database.database import (
    DataBase,
    ActionEntity,
    KnowledgeBaseEntity,
    DocumentTypeEntity
)
from data_chain.manager.role_manager import RoleManager
from data_chain.manager.knowledge_manager import KnowledgeBaseManager
from data_chain.manager.document_type_manager import DocumentTypeManager
from data_chain.entities.enum import ParseMethod, LanguageType
from data_chain.entities.common import (
    DOC_PATH_IN_OS,
    EXPORT_KB_PATH_IN_OS,
    IMPORT_KB_PATH_IN_OS,
    EXPORT_DATASET_PATH_IN_OS,
    IMPORT_DATASET_PATH_IN_OS,
    TESTING_REPORT_PATH_IN_OS,
)
# 关闭APScheduler的运行日志
# logging.getLogger('apscheduler').setLevel(logging.ERROR)
from data_chain.apps.service.router_service import get_route_info
from data_chain.apps.service.task_queue_service import TaskQueueService
from data_chain.apps.exceptions import (
    PermissionDeniedException,
    permission_exception_handler,
    general_exception_handler,
    http_exception_handler,
    starlette_http_exception_handler
)

app = fastapi.FastAPI(docs_url=None, redoc_url=None)
scheduler = AsyncIOScheduler()

# 注册全局异常处理器
app.add_exception_handler(PermissionDeniedException, permission_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

import time
@app.on_event("startup")
async def startup_event():
    st= time.time()
    await configure()
    en = time.time()
    logging.info(f"[App] configure completed, time used: {en - st:.2f} seconds")
    st= time.time()
    await add_acitons()
    en = time.time()
    logging.info(f"[App] add_actions completed, time used: {en - st:.2f} seconds")
    st= time.time()
    await TaskQueueService.init_task_queue()
    en = time.time()
    logging.info(f"[App] init_task_queue completed, time used: {en - st:.2f} seconds")
    st= time.time()
    await add_knowledge_base()
    en = time.time()
    logging.info(f"[App] add_knowledge_base completed, time used: {en - st:.2f} seconds")
    st= time.time()
    await add_document_type()
    en = time.time()
    logging.info(f"[App] add_document_type completed, time used: {en - st:.2f} seconds")
    st= time.time()
    await init_path()
    en = time.time()
    logging.info(f"[App] init_path completed, time used: {en - st:.2f} seconds")
    scheduler.add_job(TaskQueueService.handle_tasks, 'interval', seconds=5)
    scheduler.start()


async def add_acitons():
    for action in actions:
        # 先检查action是否已存在,避免重复插入
        existing_action = await RoleManager.get_action_by_action(action['action'])
        if existing_action:
            continue

        action_entity = ActionEntity(
            action=action['action'],
            name=action['name'][LanguageType.CHINESE],
            type=action['type'][LanguageType.CHINESE]
        )
        await RoleManager.add_action(action_entity)


async def add_knowledge_base():
    # 先检查知识库是否已存在,避免重复插入
    existing_kb = await KnowledgeBaseManager.get_knowledge_base_by_kb_id(DEFAULT_DOC_TYPE_ID)
    if existing_kb:
        return

    knowledge_base_entity = KnowledgeBaseEntity(
        id=DEFAULT_DOC_TYPE_ID,
        default_parse_method=ParseMethod.OCR.value
    )
    await KnowledgeBaseManager.add_knowledge_base(knowledge_base_entity)


async def add_document_type():
    # 先检查文档类型是否已存在,避免重复插入
    existing_doc_type = await DocumentTypeManager.get_document_type_by_id(DEFAULT_DOC_TYPE_ID)
    if existing_doc_type:
        return

    document_type_entity = DocumentTypeEntity(
        id=DEFAULT_DOC_TYPE_ID,
        name="default",
    )
    await DocumentTypeManager.add_document_type(document_type_entity)


async def init_path():
    """初始化路径"""
    paths = [
        DOC_PATH_IN_OS,
        EXPORT_KB_PATH_IN_OS,
        IMPORT_KB_PATH_IN_OS,
        EXPORT_DATASET_PATH_IN_OS,
        IMPORT_DATASET_PATH_IN_OS,
        TESTING_REPORT_PATH_IN_OS
    ]
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)


async def configure():
    app.include_router(team.router)
    app.include_router(knowledge_base.router)
    app.include_router(chunk.router)
    app.include_router(document.router)
    app.include_router(health_check.router)
    app.include_router(dataset.router)
    app.include_router(other.router)
    app.include_router(acc_testing.router)
    app.include_router(role.router)
    app.include_router(usr_message.router)
    app.include_router(task.router)
    app.include_router(user.router)
# 定义一个路由来获取所有路由信息


@app.get("/routes")
def get_all_routes(action: Annotated[str, Depends(get_route_info)]):
    route_info = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            route_info.append(
                list(route.methods)[0]+' '+route.path
            )
    return route_info


def main():
    try:
        ssl_enable = config["SSL_ENABLE"]
        if ssl_enable:
            uvicorn.run(app, host=config["UVICORN_IP"], port=int(config["UVICORN_PORT"]),
                        proxy_headers=True, forwarded_allow_ips='*',
                        ssl_certfile=config["SSL_CERTFILE"],
                        ssl_keyfile=config["SSL_KEYFILE"],
                        )
        else:
            uvicorn.run(app, host=config["UVICORN_IP"], port=int(config["UVICORN_PORT"]),
                        proxy_headers=True, forwarded_allow_ips='*'
                        )
    except Exception as e:
        err = f"启动服务失败: {e}"
        logging.error(err)
        exit(1)


if __name__ == '__main__':
    main()
