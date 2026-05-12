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


class TmpFilePath(str, Enum):
    """临时文件路径"""

    FILE_UPLOAD_PATH = "rag_core/tmp/file_upload/"
    FILE_PARSE_PATH = "rag_core/tmp/file_parse/"
    FILE_PARSE_RESULT_PATH = "rag_core/tmp/file_parse_result/"
    KNOWLEDGE_BASE_UPLOAD_PATH = "rag_core/tmp/knowledge_base_upload/"
    KNOWLEDGE_BASE_EXPORT_PATH = "rag_core/tmp/knowledge_base_export/"
    KNOWLEDGE_BASE_IMPORT_PATH = "rag_core/tmp/knowledge_base_import/"
