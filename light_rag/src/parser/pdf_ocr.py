"""
PDF 文件解析器（带 OCR 功能）
提取文本内容并对 PDF 中的图片进行 OCR 识别
"""
import os
import logging
import tempfile
import asyncio
from typing import Optional
import fitz  # PyMuPDF
import cv2
import numpy as np

from parser.tools.ocr_tool import OcrTool

logger = logging.getLogger(__name__)


def _extract_images_from_pdf_page(page) -> list:
    """
    从 PDF 页面中提取所有图片
    
    :param page: PyMuPDF 页面对象
    :return: 图片列表，每个元素是 numpy 数组格式的图片
    """
    images = []
    try:
        # 获取页面中的所有图片
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                # 获取图片的 xref
                xref = img[0]
                
                # 提取图片数据
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                
                # 转换为 numpy 数组
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is not None:
                    images.append(image)
            except Exception as e:
                logger.warning(f"[PdfOcrParser] 提取页面图片 {img_index} 失败: {e}")
    except Exception as e:
        logger.warning(f"[PdfOcrParser] 提取页面图片失败: {e}")
    
    return images


async def _ocr_image_array(image: np.ndarray, page_num: int, image_index: int) -> str:
    """
    对 numpy 数组格式的图片进行 OCR 识别
    
    :param image: numpy 数组格式的图片（BGR 格式）
    :param page_num: 页码（从0开始）
    :param image_index: 图片在页面中的索引
    :return: OCR 识别的文本
    """
    try:
        # 使用 OCR 工具识别（直接使用 numpy 数组）
        ocr_result = await OcrTool.ocr_from_image(image)
        if ocr_result is None:
            return ""
        
        # 合并 OCR 结果
        ocr_text = await OcrTool.merge_text_from_ocr_result(ocr_result)
        
        if ocr_text and ocr_text.strip():
            return f"[第{page_num + 1}页图片{image_index + 1} OCR内容]:\n{ocr_text}"
        return ""
    except Exception as e:
        logger.warning(f"[PdfOcrParser] 第{page_num + 1}页图片{image_index + 1} OCR识别失败: {e}")
        return ""


async def parse_pdf_ocr(file_path: str) -> Optional[str]:
    """
    解析 PDF 文件，包括文本内容和图片 OCR
    
    :param file_path: PDF 文件路径
    :return: 提取的文本内容（包含文本和 OCR 结果），如果失败则返回 None
    """
    try:
        # 打开 PDF 文件
        pdf_doc = fitz.open(file_path)
        
        if not pdf_doc:
            logger.error("[PdfOcrParser] 无法打开 PDF 文件")
            return None
        
        all_content = []
        
        # 遍历每一页
        for page_num in range(len(pdf_doc)):
            page = pdf_doc.load_page(page_num)
            
            # 提取文本内容
            text_blocks = []
            blocks = page.get_text("blocks")
            
            for block in blocks:
                if block[6] == 0:  # 确保是文本块
                    text = block[4].strip()
                    if text:
                        bbox = block[:4]
                        text_blocks.append({
                            'text': text,
                            'y0': bbox[1],
                            'x0': bbox[0]
                        })
            
            # 按位置排序文本块
            if text_blocks:
                text_blocks.sort(key=lambda x: (x['y0'], x['x0']))
                
                # 合并文本块
                page_text = []
                prev_y0 = None
                for block in text_blocks:
                    text = block['text']
                    y0 = block['y0']
                    
                    if prev_y0 is not None and y0 - prev_y0 > 10:
                        page_text.append('')
                    
                    page_text.append(text)
                    prev_y0 = y0
                
                if page_text:
                    all_content.append('\n'.join(page_text))
            
            # 提取图片并进行 OCR
            try:
                images = _extract_images_from_pdf_page(page)
                if images:
                    logger.info(f"[PdfOcrParser] 第{page_num + 1}页找到 {len(images)} 张图片，开始 OCR 识别")
                    
                    # 并发处理该页面所有图片的 OCR
                    ocr_tasks = [
                        _ocr_image_array(image, page_num, idx)
                        for idx, image in enumerate(images)
                    ]
                    ocr_results = await asyncio.gather(*ocr_tasks, return_exceptions=True)
                    
                    # 添加 OCR 结果
                    for idx, ocr_result in enumerate(ocr_results):
                        if isinstance(ocr_result, Exception):
                            logger.warning(f"[PdfOcrParser] 第{page_num + 1}页图片{idx + 1} OCR处理异常: {ocr_result}")
                            continue
                        if ocr_result and ocr_result.strip():
                            all_content.append(ocr_result)
            except Exception as e:
                logger.warning(f"[PdfOcrParser] 第{page_num + 1}页图片 OCR 处理失败: {e}")
        
        # 关闭 PDF 文档
        pdf_doc.close()
        
        if not all_content:
            logger.warning("[PdfOcrParser] PDF 文件中没有找到文本内容和图片")
            return None
        
        content = '\n\n'.join(all_content)
        return content
        
    except Exception as e:
        logger.exception(f"[PdfOcrParser] 解析 PDF 文件失败: {e}")
        return None

