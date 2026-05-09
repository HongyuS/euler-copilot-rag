from enum import Enum


class TaskType(str, Enum):
    """
    任务类型枚举
    """

    KNOWLEDGE_BASE_IMPORT_TASK = "knowledge_base_import_task"
    KNOWLEDGE_BASE_EXPORT_TASK = "knowledge_base_export_task"
    DOCUMENT_PARSE_TASK = "document_parse_task"
    JSON_PARSE_TASK = "json_parse_task"


class TaskStatus(str, Enum):
    """
    任务状态枚举
    """

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS_PENDING = "success_pending"
    SUCCESS = "success"
    FAILED = "failed"
    FAILED_PENDING = "failed_pending"
