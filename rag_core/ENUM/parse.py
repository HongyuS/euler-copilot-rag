# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
枚举类型

Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""

from enum import Enum


class Language(str, Enum):
    """语言枚举"""

    CHINESE = "chinese"
    ENGLISH = "english"
    JAPANESE = "japanese"
    KOREAN = "korean"
    FRENCH = "french"
    GERMAN = "german"
    SPANISH = "spanish"
    RUSSIAN = "russian"
    OTHER = "other"


class ParseMode(str, Enum):
    """解析结果类型"""

    GENERAL = "general"
    PRO = "pro"
    EXPERT = "expert"
    DEEP = "deep"
    FINE = "fine"
    QA = "qa"


class ParseResultTopology(str, Enum):
    """解析结果拓扑"""

    LIST = "list"
    TREE = "tree"
    GRAPH = "graph"


class ChunkType(str, Enum):
    """分块类型"""

    TILE = "title"
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    CODE = "code"
    LINK = "link"
    QA = "qa"
    JSON = "json"
    VOICE = "voice"
    VIDEO = "video"
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
