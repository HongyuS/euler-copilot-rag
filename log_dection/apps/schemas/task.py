import uuid
from pydantic import BaseModel, Field
from apps.enum.task import TaskStatusEnum


class TaskModel(BaseModel):
    task_id: str = Field(default_factory=lambda: str(
        uuid.uuid4()), description="任务ID")
    task_name: str = Field(..., description="任务名称")
    task_type: str = Field(..., description="任务类型")
    compltetion_precent: float = Field(..., description="任务完成百分比")
    status: TaskStatusEnum = Field(..., description="任务状态")
    task_related_params: str | None = Field(None, description="任务相关参数")
    created_at: str = Field(..., description="任务创建时间")
