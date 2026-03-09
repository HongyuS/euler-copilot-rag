"""
JSON 文件解析器
"""
import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)


class JsonParser:
    """JSON 文档解析器"""
    
    @staticmethod
    async def parse(file_path: str) -> Optional[str]:
        """
        解析 JSON 文件
        
        :param file_path: 文件路径
        :return: 文件内容（格式化后的 JSON 文本）
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                data = json.loads(content)
            
            # 格式化为可读的 JSON 文本
            json_text = json.dumps(data, ensure_ascii=False, indent=2)
            return json_text
        except Exception as e:
            logger.exception(f"[JsonParser] 解析 JSON 文件失败: {e}")
            return None

