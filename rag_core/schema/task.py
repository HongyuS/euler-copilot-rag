from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import uuid4
from ENUM.task import TaskType, TaskStatus
from ENUM.general import ExistedStatus


class TaskReport(BaseModel):
    """
    任务报告模型
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    task_id: str = Field(..., description="任务ID")
    message: str = Field(..., description="报告消息")
    status: TaskStatus = Field(..., description="报告状态")
    progress: float = Field(0.0, description="任务完成进度，范围0.0-1.0")
    existed_status: ExistedStatus = Field(
        ExistedStatus.EXISTED, description="报告存在状态"
    )
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="报告创建时间",
    )
    updated_at: Optional[str] = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="报告更新时间",
    )


class Task(BaseModel):
    """
    任务模型
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    access_key: str = Field("", description="任务所属访问密钥")
    type: TaskType = Field(..., description="任务类型")
    status: TaskStatus = Field(TaskStatus.PENDING, description="任务状态")
    op_id: Optional[str] = Field(None, description="关联操作ID")
    retry_times: int = Field(0, description="任务重试次数")
    task_resports: Optional[list[TaskReport]] = Field(
        default_factory=list, description="任务报告列表"
    )
    existed_status: ExistedStatus = Field(
        ExistedStatus.EXISTED, description="任务存在状态"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="任务创建时间",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="任务更新时间",
    )
