"""
DOC 文件解析器（旧版 Word 格式）
使用 Apache Tika 进行解析
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DocParser:
    """DOC 文档解析器（使用 Apache Tika）"""
    
    @staticmethod
    async def parse(file_path: str) -> Optional[str]:
        """
        解析 DOC 文件（旧版 Word 格式）
        
        :param file_path: 文件路径
        :return: 文件内容
        """
        try:
            from tika import parser
            
            with open(file_path, 'rb') as binary:
                js = parser.from_buffer(binary)
                
                if js.get('status') != 200:
                    err = "tika服务异常"
                    logger.error(f"[DocParser] {err}")
                    return None
                
                content = js.get('content', '')
                
                if content:
                    return content.strip()
                else:
                    logger.warning("[DocParser] tika 未返回内容")
                    return None
                    
        except ImportError:
            logger.error("[DocParser] 缺少 tika 依赖，请安装: pip install tika")
            return None
        except Exception as e:
            logger.exception(f"[DocParser] 解析 DOC 文件失败: {e}")
            return None

