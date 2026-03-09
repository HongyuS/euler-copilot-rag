"""
OCR 工具类 - 仅使用离线 PaddleOCR 模型
适配 RAG 项目，无需配置 OCR_METHOD 和 OCR_API_URL
"""
import os
import logging
import cv2
import numpy as np
from typing import Optional, List

# 导入 CPU 指令集检测工具
from parser.tools.instruct_scan_tool import InstructScanTool

logger = logging.getLogger(__name__)

# 禁用 OneDNN（在导入 PaddlePaddle 之前设置环境变量）
# 这样可以避免 OneDNN 兼容性问题
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['FLAGS_use_mkldnn_bfloat16'] = '0'
os.environ["DISABLE_MODEL_SOURCE_CHECK"] = "TRUE"

class OcrTool:
    """OCR 工具类，仅使用离线 PaddleOCR 模型"""
    
    # 模型路径（相对于 parser 目录）
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    text_detection_model_dir = os.path.join(_base_dir, 'model', 'ocr', 'PP-OCRv5_server_det')
    text_recognition_model_dir = os.path.join(_base_dir, 'model', 'ocr', 'PP-OCRv5_server_rec')
    
    # 初始化 PaddleOCR 模型（仅离线模式）
    model = None
    
    @staticmethod
    def _init_model():
        """延迟初始化模型"""
        if OcrTool.model is not None:
            return OcrTool.model
        
        try:
            # 检查 AVX-512 支持（ARM 架构也支持）
            avx512_support = InstructScanTool.check_avx512_support()
            if not avx512_support:
                logger.warning("[OcrTool] 当前机器可能不支持 AVX-512，但会尝试加载 OCR 模型")
            
            from paddleocr import PaddleOCR
            
            # 检查模型目录是否存在
            if not os.path.exists(OcrTool.text_detection_model_dir):
                logger.error(f"[OcrTool] 检测模型目录不存在: {OcrTool.text_detection_model_dir}")
                return None
            if not os.path.exists(OcrTool.text_recognition_model_dir):
                logger.error(f"[OcrTool] 识别模型目录不存在: {OcrTool.text_recognition_model_dir}")
                return None
            
            # 初始化 PaddleOCR（OCRv5）
            # 禁用 OneDNN 以避免兼容性问题（Windows 和某些 CPU 上会出现错误）
            OcrTool.model = PaddleOCR(
                text_detection_model_dir=OcrTool.text_detection_model_dir,
                text_recognition_model_dir=OcrTool.text_recognition_model_dir,
                # OCRv5 的新参数控制方式
                use_doc_orientation_classify=False,  # 禁用文档方向分类（如果不需要）
                use_doc_unwarping=False,  # 禁用文档矫正（如果不需要）
                use_textline_orientation=False,  # 禁用文本行方向分类（OCRv5 通常不需要）
                lang='ch',  # 因为使用本地模型，lang 会被自动忽略
            )
            logger.info("[OcrTool] PaddleOCR v5 模型初始化成功")
            return OcrTool.model
        except ImportError as e:
            error_msg = str(e)
            logger.error(f"[OcrTool] 缺少 PaddlePaddle 依赖: {error_msg}")
            return None
        except Exception as e:
            logger.exception(f"[OcrTool] 初始化 OCR 模型失败: {e}")
            return None
    
    @staticmethod
    async def ocr_from_image_path(image_path: str) -> Optional[List]:
        """
        从图片路径进行 OCR 识别
        
        :param image_path: 图片文件路径
        :return: OCR 识别结果列表，失败返回 None
        """
        try:
            # 延迟初始化模型
            model = OcrTool._init_model()
            if model is None:
                logger.error("[OcrTool] OCR 模型未初始化，无法进行识别")
                return None
            
            # 检查文件是否存在
            if not os.path.exists(image_path):
                logger.error(f"[OcrTool] 图片文件不存在: {image_path}")
                return None
            
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"[OcrTool] 无法读取图片: {image_path}")
                return None
            
            # 进行 OCR 识别
            result = model.ocr(image)
            return result
        except Exception as e:
            logger.exception(f"[OcrTool] OCR识别失败: {e}")
            return None
    
    @staticmethod
    async def ocr_from_image(image: np.ndarray) -> Optional[List]:
        """
        从 numpy 数组图片进行 OCR 识别
        
        :param image: numpy 数组格式的图片（BGR 格式，OpenCV 读取）
        :return: OCR 识别结果列表，失败返回 None
        """
        try:
            # 延迟初始化模型
            model = OcrTool._init_model()
            if model is None:
                logger.error("[OcrTool] OCR 模型未初始化，无法进行识别")
                return None
            
            if image is None or image.size == 0:
                logger.error("[OcrTool] 图片数据为空")
                return None
            
            # 进行 OCR 识别
            ocr_result = model.ocr(image, cls=True)
            return ocr_result
        except Exception as e:
            logger.exception(f"[OcrTool] OCR识别失败: {e}")
            return None
    
    @staticmethod
    async def merge_text_from_ocr_result(ocr_result: Optional[List]) -> str:
        """
        将 OCR 识别结果合并为文本字符串
        支持 OCRv4 和 OCRv5 两种返回格式
        
        :param ocr_result: OCR 识别结果列表
        :return: 合并后的文本字符串
        """
        if ocr_result is None:
            return ""
        
        text = ''
        try:
            # 处理空结果
            if len(ocr_result) == 0:
                return ""
            
            # OCRv5 可能返回字典格式（使用 predict 方法时）
            # OCRv4/v5 使用 ocr 方法时返回: [[[坐标], (文本, 置信度)], ...]
            # 先尝试检查是否是 OCRv5 的新格式（字典格式）
            if isinstance(ocr_result, dict) or (len(ocr_result) > 0 and isinstance(ocr_result[0], dict)):
                # OCRv5 字典格式: {"rec_texts": [...], "rec_scores": [...], "rec_polys": [...]}
                if isinstance(ocr_result, dict):
                    rec_texts = ocr_result.get("rec_texts", [])
                else:
                    rec_texts = ocr_result[0].get("rec_texts", []) if isinstance(ocr_result[0], dict) else []
                
                for rec_text in rec_texts:
                    if rec_text:
                        text += str(rec_text) + "\n"
                return text.strip()
            
            # 处理传统的列表格式（OCRv4 和 OCRv5 使用 ocr 方法）
            # 处理第一页的结果（PaddleOCR 可能返回多页）
            page_result = ocr_result[0] if isinstance(ocr_result[0], list) else ocr_result
            
            if page_result is None or len(page_result) == 0:
                return ""
            
            # 提取文本内容
            for item in page_result:
                if not item:
                    continue
                
                # 尝试多种格式兼容
                try:
                    # 标准格式: [[坐标], (文本, 置信度)]
                    # 先检查是否是列表或元组（而不是字典）
                    if isinstance(item, (list, tuple)):
                        if len(item) >= 2:
                            text_info = item[1]
                            if isinstance(text_info, (list, tuple)) and len(text_info) >= 1:
                                text_content = str(text_info[0])
                                text += text_content + "\n"
                            elif isinstance(text_info, str):
                                text += text_info + "\n"
                            else:
                                text += str(text_info) + "\n"
                        elif len(item) == 1:
                            # 只有一个元素的情况
                            text_content = str(item[0])
                            text += text_content + "\n"
                    # 如果 item 是字典格式（OCRv5 可能的情况）
                    elif isinstance(item, dict):
                        # 尝试从字典中获取文本
                        if 'text' in item:
                            text += str(item['text']) + "\n"
                        elif 'rec_text' in item:
                            text += str(item['rec_text']) + "\n"
                        elif 'content' in item:
                            text += str(item['content']) + "\n"
                        else:
                            logger.warning(f"[OcrTool] 字典格式的OCR结果项缺少文本字段: {item}")
                    # 如果 item 是字符串，直接添加
                    elif isinstance(item, str):
                        text += item + "\n"
                    else:
                        # 尝试通过属性访问（OCRv5 可能使用对象）
                        if hasattr(item, 'text'):
                            text += str(item.text) + "\n"
                        elif hasattr(item, 'rec_text'):
                            text += str(item.rec_text) + "\n"
                        else:
                            logger.warning(f"[OcrTool] 无法识别的OCR结果项格式: {type(item)}, 值: {item}")
                except (IndexError, KeyError, TypeError, AttributeError) as e:
                    logger.warning(f"[OcrTool] 解析OCR结果项时出错: {e}, 项类型: {type(item)}, 项: {item}")
                    continue
            
            return text.strip()
        except Exception as e:
            logger.exception(f"[OcrTool] OCR结果合并失败: {e}, 结果类型: {type(ocr_result)}, 结果: {ocr_result}")
            return ''
    
    @staticmethod
    async def image_to_text(image_file_path: str) -> str:
        """
        将图片文件转换为文本（完整流程）
        
        :param image_file_path: 图片文件路径
        :return: 识别出的文本内容
        """
        try:
            ocr_result = await OcrTool.ocr_from_image_path(image_file_path)
            if ocr_result is None:
                return ''
            
            text = await OcrTool.merge_text_from_ocr_result(ocr_result)
            return text
        except Exception as e:
            logger.exception(f"[OcrTool] 图片转文本失败: {e}")
            return ''
