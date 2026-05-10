import logging
from PIL import Image, ImageEnhance
import yaml
import cv2
import numpy as np
import requests
from rag_core.config.config import Config
from rag_core.common.instruct_scan_tool import InstructScanTool
from rag_core.ENUM.general import OnlineStatus

logger = logging.getLogger(__name__)


class OcrTool:
    det_model_dir = "data_chain/parser/model/ocr/ch_PP-OCRv4_det_infer"
    rec_model_dir = "data_chain/parser/model/ocr/ch_PP-OCRv4_rec_infer"
    cls_model_dir = "data_chain/parser/model/ocr/ch_ppocr_mobile_v2.0_cls_infer"
    # 优化 OCR 参数配置
    if (
        InstructScanTool.check_avx512_support()
        and Config().get_config().ocr_online_status == OnlineStatus.OFFLINE
    ):
        from paddleocr import PaddleOCR

        model = PaddleOCR(
            det_model_dir=det_model_dir,
            rec_model_dir=rec_model_dir,
            cls_model_dir=cls_model_dir,
            use_angle_cls=True,
            lang="ch",
            show_log=False,
        )
    else:
        model = None

    @staticmethod
    async def ocr_from_image_path(image_path: str) -> list:
        try:
            # 打开图片
            if (
                Config().get_config().ocr_model.online_status == OnlineStatus.ONLINE
                and Config().get_config().ocr_model.end_point
            ):
                result = requests.get(
                    Config().get_config().ocr_model.end_point,
                    files={"file": (image_path, open(image_path, "rb"), "image/jpeg")},
                ).json()
                return result.get("result", [])
            if OcrTool.model is None:
                err = "[OCRTool] 当前机器不支持 AVX-512，无法进行OCR识别"
                logger.error(err)
                return ""
            image = cv2.imread(image_path)
            result = OcrTool.model.ocr(image, cls=True)
            return result
        except Exception as e:
            err = f"[OCRTool] OCR识别失败: {e}"
            logger.exception(err)
            return ""

    @staticmethod
    async def merge_text_from_ocr_result(ocr_result: list) -> str:
        text = ""
        try:
            if ocr_result[0] is None or len(ocr_result[0]) == 0:
                return ""
            for _ in ocr_result[0]:
                text += str(_[1][0])
            return text
        except Exception as e:
            err = f"[OCRTool] OCR结果合并失败 {e}"
            logger.exception(err)
            return ""

    @staticmethod
    async def image_to_text(
        image_file_path: str,
    ) -> str:
        try:
            ocr_result = await OcrTool.ocr_from_image_path(image_file_path)
            return await OcrTool.merge_text_from_ocr_result(ocr_result)
        except Exception as e:
            err = f"[OCRTool] 图片转文本失败 {e}"
            logger.exception(err)
            return ""
