from pydantic import BaseModel, Field
from typing import Any, Optional
from rag_core.ENUM.json import LogicOperatorType, OperationType, SchemaType


class Condition(BaseModel):
    field: str | list[str] = Field(
        ..., description="条件字段，支持单字段或多字段（列表）"
    )
    type: Optional[SchemaType] = Field(None, description="条件值的数据类型")
    operator: OperationType = Field(..., description="条件运算符")
    value: Any = Field(..., description="条件值")


class LogicalExpression(BaseModel):
    operator: LogicOperatorType = Field(..., description="逻辑运算符")
    expressions: list["LogicalExpression" | Condition] = Field(
        ..., description="逻辑表达式列表"
    )
