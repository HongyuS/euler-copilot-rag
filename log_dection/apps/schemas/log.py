from apps.enum.log import LogLevelEnum
from pydantic import BaseModel, Field
import uuid


class LogModel(BaseModel):
    id: str = Field(default_factory=lambda: str(
        uuid.uuid4()), description="日志ID")
    offset: int = Field(..., description="日志偏移量")
    timestamp: str = Field(..., description="日志时间戳")
    level: LogLevelEnum = Field(..., description="日志级别")
    message: str = Field(..., description="日志消息内容")
    vector: list[float] | None = Field(
        default=None, description="日志的嵌入向量表示")
    save_path: str | None = Field(
        default=None, description="日志存储路径")


class LogTemplateModel(BaseModel):
    id: str = Field(default_factory=lambda: str(
        uuid.uuid4()), description="日志模板ID")
    log_id: str = Field(..., description="关联的日志ID")
    template: str = Field(..., description="日志模板内容")
    occurrence_count: int = Field(..., description="该模板出现的次数")
    is_anomalous: bool = Field(..., description="是否异常")
    vector: list[float] | None = Field(
        default=None, description="日志模板的嵌入向量表示")
