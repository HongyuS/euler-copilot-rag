import uuid
from pydantic import BaseModel, Field
from typing import Optional

from chat2db.apps.schemas.enum_var import DatabaseType

class SqlGenerateRequest(BaseModel):
    """
    生成SQL请求
    """
    type: DatabaseType = Field(..., description="数据库类型")
    host: str = Field(..., description="数据库地址")
    port: int = Field(..., description="数据库端口")
    username: str = Field(..., description="数据库用户名")
    password: str = Field(..., description="数据库密码")
    database: str = Field(..., description="数据库名称")
    goal: str = Field(..., description="生成目标")

    table_list: list[str] = Field(None, description="表名列表")

class SqlRepairRequest(BaseModel):
    """
    修复SQL请求
    """
    type: DatabaseType = Field(..., description="数据库类型")

    host: str = Field(..., description="数据库地址")
    port: int = Field(..., description="数据库端口")
    username: str = Field(..., description="数据库用户名")
    password: str = Field(..., description="数据库密码")
    database: str = Field(..., description="数据库名称")
    goal: str = Field(..., description="生成目标")

    error_sql: str = Field(..., description="错误 SQL 语句")
    error_msg: str = Field(..., description="错误信息")
    table_list: list[str] = Field(None, description="表名列表")


class SqlExecuteRequest(BaseModel):
    """
    执行SQL请求
    """
    type: DatabaseType = Field(..., description="数据库类型")
    
    host: str = Field(..., description="数据库地址")
    port: int = Field(..., description="数据库端口")
    username: str = Field(..., description="数据库用户名")
    password: str = Field(..., description="数据库密码")
    database: str = Field(..., description="数据库名称")
    sql: str = Field(..., description="执行SQL")
