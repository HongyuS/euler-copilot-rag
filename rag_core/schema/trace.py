from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import uuid4
from ENUM.parse import (
    ParseResultTopology,
    ChunkType,
    ParseMode,
    Language,
)
from ENUM.general import ExistedStatus, SuccessStatus


class Trace(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    name: str = Field(..., description="跟踪名称")
    access_key: str = Field(..., description="跟踪访问密钥")
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="创建时间",
    )
    status: ExistedStatus = Field(ExistedStatus.EXISTED, description="跟踪存在状态")


class TraceDetail(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    trace_id: str = Field(..., description="所属跟踪ID")
    func_name: str = Field(..., description="函数名称")
    path: str = Field(..., description="函数路径")
    line_no: int = Field(..., description="函数调用行号")
    input: Any = Field(..., description="函数输入")
    output: Any = Field(..., description="函数输出")
    parent_func_name: Optional[str] = Field(None, description="父函数名称")
    parent_path: Optional[str] = Field(None, description="父函数路径")
    parent_line_no: Optional[int] = Field(None, description="父函数调用行号")
    success: SuccessStatus = Field(..., description="函数执行是否成功")
    start_time: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="函数执行开始时间",
    )
    end_time: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="函数执行结束时间",
    )
    cost_time: float = Field(0.0, description="函数执行耗时，单位为秒")
    exception: str = Field(None, description="函数执行异常信息")
