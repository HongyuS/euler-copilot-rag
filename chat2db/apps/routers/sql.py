import logging
from fastapi import APIRouter, status
import sys

from apps.schemas.enum_var import RiskLevel, DatabaseType
from apps.schemas.request import SqlGenerateRequest, SqlExecuteRequest, SqlRepairRequest
from apps.schemas.response import ResponseData, SqlGenerateRsp, SqlExecuteRsp, SqlRepairRsp
from apps.services import database_service
from apps.services.sql_service import SqlService

router = APIRouter(prefix="/sql")


@router.post("/generate", response_model=ResponseData)
async def generate_sql(request: SqlGenerateRequest):
    try:
        _, table_info = await SqlService.get_connection_and_table_info(
            database_type=request.type,
            host=request.host,
            port=request.port,
            username=request.username,
            password=request.password,
            database=request.database,
            table_list=request.table_list,
        )

        sql = await SqlService.generator(
            database_type=request.type,
            goal=request.goal,
            table_info=table_info,
        )

        risk = await SqlService.risk_analysis(
            database_type=request.type, goal=request.goal, sql=sql, table_info=table_info
        )

    except Exception as e:
        logging.error(f"[SQL 生成失败]")
        return ResponseData(code=status.HTTP_400_BAD_REQUEST, message="SQL 生成失败", result={})

    return ResponseData(
        code=status.HTTP_200_OK,
        message="success",
        result=SqlGenerateRsp(
            risk=risk,
            sql=sql,
        ),
    )


@router.post("/repair", response_model=ResponseData)
async def repair_sql(request: SqlRepairRequest):
    try:
        _, table_info = await SqlService.get_connection_and_table_info(
            database_type=request.type,
            host=request.host,
            port=request.port,
            username=request.username,
            password=request.password,
            database=request.database,
            table_list=request.table_list,
        )

        repair_sql = await SqlService.repairer(
            database_type=request.type,
            goal=request.goal,
            table_info=table_info,
            error_sql=request.error_sql,
            error_msg=request.error_msg,
        )

        risk = await SqlService.risk_analysis(
            database_type=request.type,
            goal=request.goal,
            sql=repair_sql,
            table_info=table_info,
            error_sql=request.error_sql,
            error_msg=request.error_msg,
        )

    except Exception as e:
        logging.error(f"[SQL 修复失败]")
        return ResponseData(
            code=status.HTTP_400_BAD_REQUEST, message="SQL 修复失败", result={"Error": str(e)}
        )

    return ResponseData(
        code=status.HTTP_200_OK,
        message="success",
        result=SqlRepairRsp(
            risk=risk,
            sql=repair_sql,
        ),
    )


@router.post("/execute", response_model=ResponseData)
async def execute_sql(request: SqlExecuteRequest):
    try:
        connection = await database_service.connect_database(
            database_type=request.type,
            host=request.host,
            port=request.port,
            username=request.username,
            password=request.password,
            database=request.database,
        )
        execute_result = await SqlService.executer(
            database_type=request.type,
            sql=request.sql,
            connection=connection,
        )

    except Exception as e:
        logging.error(f"[SQL 执行失败]")
        return ResponseData(
            code=status.HTTP_400_BAD_REQUEST, message="SQL 执行失败", result={"Error": str(e)}
        )

    return ResponseData(
        code=status.HTTP_200_OK,
        message="success",
        result=SqlExecuteRsp(
            execute_result=execute_result,
        ),
    )


@router.post("/handler", response_model=ResponseData)
async def sql_handler(request: SqlGenerateRequest):
    try:
        connection, table_info = await SqlService.get_connection_and_table_info(
            database_type=request.type,
            host=request.host,
            port=request.port,
            username=request.username,
            password=request.password,
            database=request.database,
            table_list=request.table_list,
        )

        execute_result, sql, risk = await SqlService.sql_handler(
            database_type=request.type,
            goal=request.goal,
            table_info=table_info,
            connection=connection,
        )
    except Exception as e:
        logging.error(f"[查询失败]")
        return ResponseData(code=status.HTTP_400_BAD_REQUEST, message="查询失败", result={"Error": str(e)})

    return ResponseData(
        code=status.HTTP_200_OK,
        message="success",
        result=SqlExecuteRsp(
            sql=sql,
            execute_result=execute_result,
            risk=risk,
        ),
    )
