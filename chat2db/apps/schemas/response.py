from pydantic import BaseModel, Field
from typing import Any

from apps.schemas.enum_var import RiskLevel

class ResponseData(BaseModel):
    code: int
    message: str
    result: Any
    
class RiskInfo(BaseModel):
    risk: RiskLevel = Field(..., description="风险等级")
    message: str = Field(..., description="风险提示信息")

class SqlGenerateRsp(BaseModel):
    """
    SQL生成请求
    """
    sql: str | dict = Field(..., description="生成的SQL")
    risk: RiskInfo  = Field(..., description="SQL 风险等级")
    

class SqlRepairRsp(BaseModel):
    """
    修复SQL请求
    """
    sql: str | dict = Field(..., description="修复的SQL")
    risk: RiskInfo = Field(..., description="SQL 风险等级")
    

class SqlExecuteRsp(BaseModel):
    """
    执行SQL请求
    """
    execute_result: list[dict[str, Any]] = Field(..., description="执行结果")
    sql: str | dict = Field(..., description="执行的SQL")
    risk: RiskInfo = Field(..., description="SQL 风险等级")

