"""任务状态与类型枚举"""
from enum import Enum


class TaskStatusEnum(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    CANCELED = "canceled"
    SUCCESSFUL_PENDING_REMOVE = "successful_pending_remove"
    FAILED_PENDING_REMOVE = "failed_pending_remove"
    SUCCESSFUL = "successful"
    FAILED = "failed"


class TaskTypeEnum(str, Enum):
    """任务类型"""
    DOCUMENT_IMPORT = "document_import"
