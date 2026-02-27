from enum import Enum


class TaskTypeEnum(str, Enum):
    BASE = "base"
    LOG_DETECTION_BASE_ON_KEYWORDS = "log_detection_base_on_keywords"
    LOG_DETECTION_BASE_ON_CLUSTERING = "log_detection_base_on_clustering"
    LOG_DETECTION_BASE_ON_LLM = "log_detection_base_on_llm"


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNNING = "running"
    CANCLED = "cancled"
    SUCCESSFUL = "successful"
    FAILED = "failed"
