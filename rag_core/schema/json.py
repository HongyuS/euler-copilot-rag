from pydantic import BaseModel, Field
from typing import Any
from rag_core.ENUM.json import LogicOperator, OperationType, FieldType


class Condition(BaseModel):
    field: str | list[str] = Field(
        ..., description="条件字段，支持单字段或多字段（列表）"
    )
    operator: OperationType = Field(..., description="条件运算符")
    value: Any = Field(..., description="条件值")
    field_type: FieldType = Field(..., description="条件字段类型")


class LogicalExpression(BaseModel):
    operator: LogicOperator = Field(..., description="逻辑运算符")
    expressions: list["LogicalExpression" | Condition] = Field(
        ..., description="逻辑表达式列表"
    )
