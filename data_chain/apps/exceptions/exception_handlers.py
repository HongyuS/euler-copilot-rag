# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from data_chain.logger.logger import logger as logging
from .permission_exceptions import PermissionDeniedException
import traceback


async def permission_exception_handler(request: Request, exc: PermissionDeniedException) -> JSONResponse:
    """权限异常处理器
    
    捕获权限相关异常，返回标准的403响应格式
    """
    logging.warning(f"权限拒绝: {exc.detail} - 请求路径: {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "retcode": exc.retcode,
            "rtmsg": exc.rtmsg or exc.detail,
            "data": None,
            "message": exc.detail
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器
    
    捕获所有未处理的异常，特别是权限相关的Exception
    """
    error_message = str(exc)
    
    # 检查是否是权限相关的异常
    if "权限" in error_message or "没有权限" in error_message or "权限不足" in error_message:
        logging.warning(f"检测到权限相关异常: {error_message} - 请求路径: {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "retcode": 403,
                "rtmsg": error_message,
                "data": None,
                "message": error_message
            }
        )
    
    # 记录其他异常的详细信息
    logging.error(f"未处理的异常: {error_message}")
    logging.error(f"异常类型: {type(exc).__name__}")
    logging.error(f"请求路径: {request.url.path}")
    logging.error(f"异常堆栈: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "retcode": 500,
            "rtmsg": "内部服务器错误",
            "data": None,
            "message": "服务器内部错误，请联系管理员"
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器
    
    处理FastAPI的HTTPException
    """
    logging.warning(f"HTTP异常: {exc.detail} - 状态码: {exc.status_code} - 请求路径: {request.url.path}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "retcode": exc.status_code,
            "rtmsg": exc.detail,
            "data": None,
            "message": exc.detail
        }
    )


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Starlette HTTP异常处理器
    
    处理Starlette的HTTPException
    """
    logging.warning(f"Starlette HTTP异常: {exc.detail} - 状态码: {exc.status_code} - 请求路径: {request.url.path}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "retcode": exc.status_code,
            "rtmsg": exc.detail,
            "data": None,
            "message": exc.detail
        }
    )
