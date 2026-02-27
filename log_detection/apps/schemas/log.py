
from apps.enum.log import LogLevelEnum, LogTypeEnum
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class LogModel(BaseModel):
    id: str = Field(default_factory=lambda: str(
        uuid.uuid4()), description="日志ID")
    file_path: str = Field(..., description="日志文件路径")
    log_type: LogTypeEnum | None = Field(default=None, description="日志类型")
    offset: int = Field(..., description="日志偏移量")
    start_time: datetime | None = Field(default=None, description="日志开始时间")
    end_time: datetime | None = Field(default=None, description="日志结束时间")
    level: LogLevelEnum = Field(
        default=LogLevelEnum.UNKNOWN, description="日志级别")
    content: str = Field(..., description="日志消息内容")
    vector: list[float] | None = Field(
        default=None, description="日志的嵌入向量表示")
    save_path: str | None = Field(
        default=None, description="日志存储路径")
    is_anomalous: bool = Field(
        default=False, description="日志是否异常")
    anomaly_reason: str | None = Field(
        default=None, description="日志异常原因")
    anomaly_score: float | None = Field(
        default=None, description="日志异常分数")


class LogTemplateModel(BaseModel):
    id: str = Field(default_factory=lambda: str(
        uuid.uuid4()), description="日志模板ID")
    log_id: str = Field(..., description="关联的日志ID")
    template: str = Field(..., description="日志模板内容")
    is_anomalous: bool = Field(..., description="是否异常")
    vector: list[float] | None = Field(
        default=None, description="日志模板的嵌入向量表示")

    # 并查集参数
    parent_id: str | None = Field(
        default=None, description="并查集父节点ID")
    rank: int = Field(default=1, description="并查集秩")
    sz: int = Field(default=1, description="并查集大小")
