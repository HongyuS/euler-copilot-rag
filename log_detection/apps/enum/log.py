from enum import Enum


class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    TRACE = "TRACE"
    UNKNOWN = "UNKNOWN"
    FATAL = "FATAL"


class LogTypeEnum(str, Enum):
    BASE = "base"
    DMESG = "dmesg"
    KDUMP = "kdump"
    FTRACE = "ftrace"
    BASH = "bash"
    CODE = "code"
    OTHER = "other"
