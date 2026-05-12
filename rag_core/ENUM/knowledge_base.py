from enum import Enum


class ChunkSearchMethod(str, Enum):
    """知识库搜索方法"""

    DOC2CHUNK = "doc2chunk"
    HYBRID = "hybrid"
