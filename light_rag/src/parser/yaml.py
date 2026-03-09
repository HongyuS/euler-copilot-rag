"""
YAML 文件解析器
"""
import logging
import yaml
from typing import Optional

logger = logging.getLogger(__name__)


class YamlParser:
    """YAML 文档解析器"""
    
    @staticmethod
    async def parse(file_path: str) -> Optional[str]:
        """
        解析 YAML 文件
        
        :param file_path: 文件路径
        :return: 文件内容（转换为文本格式）
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = yaml.load(file, Loader=yaml.SafeLoader)
            
            # 将 YAML 对象转换为文本
            if content is None:
                return None
            
            # 使用 yaml.dump 将对象转换回文本格式
            yaml_text = yaml.dump(content, allow_unicode=True, default_flow_style=False)
            return yaml_text
        except Exception as e:
            logger.exception(f"[YamlParser] 解析 YAML 文件失败: {e}")
            return None

