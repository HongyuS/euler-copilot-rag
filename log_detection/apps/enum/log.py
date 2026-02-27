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
    DMESG = "dmesg"
    KDUMP = "kdump"
    FTRACE = "ftrace"
    BASH = "bash"
    PYTHON = "python"
    JAVA = "java"
    GO = "go"
    JS = "javascript"
    C = "c"
    CPP = "cpp"
    OTHER = "other"

# log数值的枚举


class LogValueEnum(str, Enum):
    TIMESTAMP = "timestamp"
    LEVEL = "level"
    IP = "ip"
    PORT = "port"
    PID = "pid"
    TID = "tid"
