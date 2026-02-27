import uuid
from pydantic import BaseModel, Field
from datetime import datetime
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


class TaskRelatedParamsModel(BaseModel):
    query: str = Field(default="", description="查询语句")
    file_path_list: list[str] = Field(
        default_factory=list, description="日志文件路径列表")
    max_anomaly_log_count: int = Field(default=100, description="最大异常日志数量")
    anomaly_keywords: list[str] = Field(
        default_factory=list, description="异常关键词列表")
    time_start: datetime | None = Field(None, description="日志时间范围起始时间")
    time_end: datetime | None = Field(None, description="日志时间范围结束时间")
