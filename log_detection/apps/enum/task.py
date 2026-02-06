from enum import Enum


class TaskTypeEnum(str, Enum):
    LOG_DETECTION = "log_detection"
    GA = "genetic_algorithm"


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNNING = "running"
    CANCLED = "cancled"
    SUCCESSFUL = "successful"
    FAILED = "failed"
