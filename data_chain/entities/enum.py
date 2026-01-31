# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
枚举类型

Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""

from enum import Enum


class EmbeddingType(str, Enum):
    """embedding 服务的类型"""
    OPENAI = "openai"
    MINDIE = "mindie"


class RerankType(str, Enum):
    """rerank 服务的类型"""
    EMPTY = ""
    ALGORITHM = "algorithm"
    BAILIAN = "bailian"
    GUIJILIUDONG = "guijiliudong"
    VLLM = "vllm"
    ASCEND = "ascend"


class TeamType(str, Enum):
    """团队类型"""
    MYCREATED = "mycreated"
    MYJOINED = "myjoined"
    PUBLIC = "public"


class TeamStatus(str, Enum):
    """团队状态"""
    EXISTED = "existed"
    DELETED = "deleted"


class TeamMessageStatus(str, Enum):
    """团队消息状态"""
    EXISTED = "existed"
    DELETED = "deleted"


class TeamUserStaus(str, Enum):
    """团队用户状态"""
    EXISTED = "existed"
    DELETED = "deleted"


class RoleStatus(str, Enum):
    """角色状态"""
    EXISTED = "existed"
    DELETED = "deleted"


class RoleActionStatus(str, Enum):
    """角色操作状态"""
    EXISTED = "existed"
    DELETED = "deleted"


class UserRoleStatus(str, Enum):
    """用户角色状态"""
    EXISTED = "existed"
    DELETED = "deleted"


class DeafaultRole(str, Enum):
    """默认角色"""
    OWENER = "owner"
    ADMINISTRATOR = "administrator"
    MEMBER = "member"


class Tokenizer(str, Enum):
    """分词器"""

    ZH = "中文"
    EN = "en"
    # MIX = "mix"


class Embedding(str, Enum):
    """嵌入模型"""
    BGEM3 = "bgem3"


class ParseMethod(str, Enum):
    """解析方法"""
    GENERAL = "general"
    OCR = "ocr"
    EHANCED = "enhanced"
    QA = "qa"
    TREE = "tree"
    DEEP = "deep"
    FINE = "fine"


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class UserMessageType(str, Enum):
    """用户消息类型"""
    INVITATION = "invitation"
    APPLICATION = "application"


class UserMessageStatus(str, Enum):
    """用户消息状态"""
    UNREAD = "unread"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DELETED = "deleted"


class KnowledgeBaseStatus(str, Enum):
    """知识库状态"""
    IDLE = "idle"
    PENDING = "pending"
    EXPORTING = "exporting"
    IMPORTING = "importing"
    DELETED = "deleted"


class DocParseRelutTopology(str, Enum):
    """解析结果拓扑"""
    LIST = "list"
    TREE = "tree"
    GRAPH = "graph"


class DocumentStatus(str, Enum):
    """文档状态"""
    IDLE = "idle"
    PENDING = "pending"
    RUNNING = "running"
    DELETED = "deleted"


class ImageStatus(str, Enum):
    """图片状态"""
    EXISTED = "existed"
    DELETED = "deleted"


class ChunkStatus(str, Enum):
    """分块状态"""
    EXISTED = "existed"
    DELETED = "deleted"


class ChunkType(str, Enum):
    """分块类型"""
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    CODE = "code"
    LINK = "link"
    QA = "qa"
    JSON = "json"
    UNKOWN = "unknown"


class ChunkParseTopology(str, Enum):
    """分块解析拓扑"""
    GERNERAL = "general"
    LISTHEAD = "listhead"
    LISTBODY = "listbody"
    LISTTAIL = "listtail"
    TREEROOT = "treeroot"
    TREENORMAL = "treenormal"
    TREELEAF = "treeleaf"
    GRAPHNODE = "graphnode"


class DataSetStatus(str, Enum):
    """数据集状态"""
    IDLE = "idle"
    PENDING = "pending"
    GENERATING = "running"
    EXPORTING = "exporting"
    IMPORTING = "importing"
    DELETED = "deleted"


class QAStatus(str, Enum):
    """问答状态"""
    EXISTED = "existed"
    DELETED = "deleted"


class TestingStatus(str, Enum):
    """测试状态"""
    IDLE = "idle"
    PENDING = "pending"
    RUNNING = "running"
    DELETED = "deleted"


class TestCaseStatus(str, Enum):
    """测试用例状态"""
    EXISTED = "existed"
    DELETED = "deleted"


class SearchMethod(str, Enum):
    """搜索方法"""
    KEYWORD = "keyword"
    VECTOR = "vector"
    DYNAMIC_WEIGHTED_KEYWORD_AND_VECTOR = "dynamic_weighted_keyword_and_vector"
    KEYWORD_AND_VECTOR = "keyword_and_vector"
    DOC2CHUNK = "doc2chunk"
    DOC2CHUNK_BFS = "doc2chunk_bfs"
    ENHANCED_BY_LLM = "enhanced_by_llm"
    QUERY_EXTEND = "query_extend"
    DYNAMIC_WEIGHTED_KEYWORD = "dynamic_weighted_keyword"


class TaskType(str, Enum):
    """任务类型"""
    DOC_PARSE = "doc_parse"
    KB_EXPORT = "kb_export"
    KB_IMPORT = "kb_import"
    DATASET_EXPORT = "dataset_export"
    DATASET_IMPORT = "dataset_import"
    DATASET_GENERATE = "dataset_generate"
    TESTING_RUN = "testing_run"


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCLED = "canceled"
    DELETED = "deleted"


class OrderType(str, Enum):
    """排序"""
    ASC = "asc"
    DESC = "desc"


class ActionType(str, Enum):
    """操作类型"""
    ZH_TEAM = "团队"
    ZH_USER = "用户"
    ZH_ROLE = "角色"
    ZH_KNOWLEDGE_BASE = "知识库"
    ZH_DOCUMENT = "文档"
    ZH_CHUNK = "文档片段"
    ZH_DATASET = "数据集"
    ZH_DATASET_DATA = "数据集数据"
    ZH_TESTING = "测试"
    ZH_TASK = "任务"
    EN_TEAM = "team"
    EN_USER = "user"
    EN_ROLE = "role"
    EN_KNOWLEDGE_BASE = "knowledge_base"
    EN_DOCUMENT = "document"
    EN_CHUNK = "chunk"
    EN_DATASET = "dataset"
    EN_DATASET_DATA = "dataset_data"
    EN_TESTING = "testing"
    EN_TASK = "task"


class IdType(str, Enum):
    """ID类型"""
    TEAM = "team"
    ROLE = "role"
    MSG = "msg"
    USER = "user"
    KNOWLEDGE_BASE = "knowledge_base"
    DOCUMENT = "document"
    CHUNK = "chunk"
    DATASET = "dataset"
    DATASET_DATA = "dataset_data"
    TESTING = "testing"
    TEST_CASE = "testing_case"
    TASK = "task"


class MessageLevel(str, Enum):
    """消息等级"""
    INFO = "info"
    WARNING = "warning"


class LanguageType(str, Enum):
    """语言类型"""

    CHINESE = "zh"
    ENGLISH = "en"
