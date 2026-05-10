from enum import Enum
from tkinter.tix import IMAGE


class ModelLabel(str, Enum):
    """模型标签"""

    TXT2TXT = "txt2txt"
    TXT2IMG = "txt2img"
    IMG2TXT = "img2txt"
    VOICETOTXT = "voicetotxt"
    VIDEOTOTXT = "videototxt"
    OCR = "ocr"
    FUNCTION_CALL = "function_call"
    RERANKER = "reranker"
    TXT2EMBEDDING = "txt2embedding"
    IMAGE2EMBEDDING = "image2embedding"
    VIDEO2EMBEDDING = "video2embedding"


class ModelProvider(str, Enum):
    """模型提供商"""

    OPENAI = "openai"
    ASCEND = "ascend"
    BAILIAN = "bailian"
    GUIJILIUDONG = "guijiliudong"
    VLLM = "vllm"
    OLLMA = "ollma"
    OTHER = "other"
