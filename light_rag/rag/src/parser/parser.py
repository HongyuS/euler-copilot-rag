"""
文档解析器模块
支持同步和异步解析器
"""
import asyncio
import inspect
import logging
from typing import Optional, Dict, Callable, Union

logger = logging.getLogger(__name__)

from parser.txt import parse_txt
from parser.doc import DocParser
from parser.pdf import parse_pdf
from parser.docx_ocr import DocxOcrParser
from parser.pdf_ocr import parse_pdf_ocr
from parser.deep_pdf import DeepPdfParser
from parser.md import MdParser
from parser.html import HtmlParser
from parser.picture import PictureParser
from parser.pptx import PptxParser
from parser.xlsx import XlsxParser
from parser.yaml import YamlParser
from parser.json import JsonParser

_parsers: Dict[str, Callable] = {}


def register_parser(file_ext: str, parser_func: Callable):
    """
    注册解析器（支持同步和异步函数）
    :param file_ext: 文件扩展名（如 'txt', 'docx'）
    :param parser_func: 解析函数，接收 file_path 参数，返回 Optional[str] 或协程
    """
    _parsers[file_ext.lower()] = parser_func
    logger.debug(f"[Parser] 注册解析器: {file_ext}")


async def parse_async(file_path: str) -> Optional[str]:
    """
    根据文件类型自动选择解析器（异步版本）
    
    :param file_path: 文件路径
    :return: 文件内容
    """
    file_ext = file_path.lower().split('.')[-1]
    
    if file_ext not in _parsers:
        logger.error(f"[Parser] 不支持的文件类型: {file_ext}")
        return None
    
    try:
        parser_func = _parsers[file_ext]
        
        # 检查是否是异步函数
        if inspect.iscoroutinefunction(parser_func):
            return await parser_func(file_path)
        else:
            # 同步函数在事件循环中运行
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, parser_func, file_path)
    except Exception as e:
        logger.exception(f"[Parser] 解析文件失败: {file_path}, {e}")
        return None


# 注册解析器
register_parser('txt', parse_txt)
register_parser('docx', DocxOcrParser.parse)  # 使用带 OCR 的版本
register_parser('doc', DocParser.parse)
#register_parser('pdf', parse_pdf_ocr)  # 使用带 OCR 的版本
register_parser('pdf', DeepPdfParser.parse)  # 深度 PDF 解析器
register_parser('md', MdParser.parse)
register_parser('markdown', MdParser.parse)
register_parser('html', HtmlParser.parse)
register_parser('htm', HtmlParser.parse)
register_parser('jpg', PictureParser.parse)
register_parser('jpeg', PictureParser.parse)
register_parser('png', PictureParser.parse)
register_parser('gif', PictureParser.parse)
register_parser('bmp', PictureParser.parse)
register_parser('pptx', PptxParser.parse)
register_parser('xlsx', XlsxParser.parse)
register_parser('xls', XlsxParser.parse)
register_parser('csv', XlsxParser.parse)
register_parser('yaml', YamlParser.parse)
register_parser('yml', YamlParser.parse)
register_parser('json', JsonParser.parse)


class Parser:
    """文档解析器类"""
    
    @staticmethod
    async def parse_async(file_path: str) -> Optional[str]:
        """异步解析"""
        # 直接使用模块级的 parse_async 函数逻辑
        file_ext = file_path.lower().split('.')[-1]
        
        if file_ext not in _parsers:
            logger.error(f"[Parser] 不支持的文件类型: {file_ext}")
            return None
        
        try:
            parser_func = _parsers[file_ext]
            
            # 检查是否是异步函数
            if inspect.iscoroutinefunction(parser_func):
                return await parser_func(file_path)
            else:
                # 同步函数在事件循环中运行
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, parser_func, file_path)
        except Exception as e:
            logger.exception(f"[Parser] 解析文件失败: {file_path}, {e}")
            return None

