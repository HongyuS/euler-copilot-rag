from enum import Enum


class ScaleDbType(str, Enum):
    """
    数据库类型枚举
    """

    POSTGRES = "postgres"
    MYSQL = "mysql"
    JINCANG = "jincang"
    DAMENG = "dameng"
    ORACLE = "oracle"


class VectorDbType(str, Enum):
    """
    向量数据库类型枚举
    """

    MILVUS = "milvus"
    ES = "elasticsearch"
    QDRANT = "quadrant"


class GraphDbType(str, Enum):
    """
    图数据库类型枚举
    """

    NEo4j = "neo4j"
