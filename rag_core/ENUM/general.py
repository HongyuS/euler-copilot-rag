from enum import Enum


class SuccessStatus(str, Enum):
    """成功状态"""

    SUCCESS = "success"
    PENDING = "pending"


class OnlineStatus(str, Enum):
    """在线状态"""

    ONLINE = "online"
    OFFLINE = "offline"


class ExistedStatus(str, Enum):
    """存在状态"""

    EXISTED = "existed"
    DELETED = "deleted"


class LogLevel(str, Enum):
    """日志级别"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
