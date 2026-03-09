"""
图片文件解析器
支持 jpg, jpeg, png, gif, bmp 等格式
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PictureParser:
    """图片文件解析器"""
    
    @staticmethod
    async def parse(file_path: str) -> Optional[str]:
        """
        解析图片文件
        注意：此解析器仅标记图片，不进行 OCR 识别
        如需 OCR，请使用带 OCR 功能的解析器
        
        :param file_path: 文件路径
        :return: 图片标记文本
        """
        try:
            # 图片文件不直接提取文本，返回标记
            return f"[图片文件: {file_path}]"
        except Exception as e:
            logger.exception(f"[PictureParser] 解析图片文件失败: {e}")
            return None

