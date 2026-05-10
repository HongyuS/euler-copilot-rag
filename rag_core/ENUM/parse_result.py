# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
枚举类型

Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""

from enum import Enum


class ParseResultTopology(str, Enum):
    """解析结果拓扑"""

    LIST = "list"
    TREE = "tree"
    GRAPH = "graph"


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
