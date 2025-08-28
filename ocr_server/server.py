from typing import Any
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import logging
import os
import aiofiles
import cv2
import numpy as np
from paddleocr import PaddleOCR
import uuid
from datetime import datetime

import os
# 强制离线模式
os.environ["PADDLEX_OFFLINE"] = "True"
# 禁用Paddle的网络请求
os.environ["PADDLE_NO_NETWORK"] = "True"
# 指定模型缓存路径（确保已放置模型）
os.environ["PADDLEX_HOME"] = "/root/.paddlex"


class ResponseData(BaseModel):
    """基础返回数据结构"""

    code: int
    message: str
    result: list


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化FastAPI应用
app = FastAPI()

# 创建保存上传文件的目录
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 初始化PaddleOCR，使用角度分类，中文识别
ocr = PaddleOCR(
    # 1. 指定本地文本检测模型目录（PP-OCRv5_server_det）
    text_detection_model_dir="/root/.paddlex/official_models/PP-OCRv5_server_det",
    # 2. 指定本地文本识别模型目录（PP-OCRv5_server_rec）
    text_recognition_model_dir="/root/.paddlex/official_models/PP-OCRv5_server_rec",
    # （可选）若需要文档方向分类/文本行方向分类，也可指定对应本地模型
    doc_orientation_classify_model_dir="/root/.paddlex/official_models/PP-LCNet_x1_0_doc_ori",
    textline_orientation_model_dir="/root/.paddlex/official_models/PP-LCNet_x1_0_textline_ori",
    # （可选）关闭不需要的功能（如文档矫正，根据需求调整）
    use_doc_unwarping=False,  # 若不需要 UVDoc 文档矫正，可关闭
    lang=None,  # 因已指定本地模型，lang/ocr_version 会被自动忽略（符合原代码逻辑）
    ocr_version=None
)


@app.get("/ocr", response_model=ResponseData)
async def ocr_recognition(file: UploadFile = File(...)) -> JSONResponse:
    """
    接收上传的图片文件，先保存到本地，再进行OCR识别并返回结果字符串
    """
    try:
        # 生成唯一的文件名，避免冲突
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # 异步保存文件到本地
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()  # 读取文件内容
            await out_file.write(content)  # 写入到本地文件

        logger.info(f"文件已保存到: {file_path}, 大小: {len(content)} bytes")

        # 使用cv2读取本地文件
        image = cv2.imread(file_path)
        if image is None:
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error("无法读取上传的图片文件，可能格式不支持或文件损坏")
            return JSONResponse(
                status_code=400,
                content=ResponseData(
                    code=400,
                    message="无法读取上传的图片文件，可能格式不支持或文件损坏",
                    result=[]
                ).model_dump(exclude_none=True)
            )

        logger.info(f"图片读取成功，尺寸: {image.shape}")

        # 进行OCR识别
        # PaddleOCR可以直接处理numpy数组(cv2格式)
        result = ocr.predict(image)
        if not result:
            if os.path.exists(file_path):
                os.remove(file_path)
            return JSONResponse(
                status_code=200,
                content=ResponseData(
                    code=200,
                    message="OCR识别完成，但未识别到任何文本",
                    result=[]
                ).model_dump(exclude_none=True)
            )
        if not result[0]:
            if os.path.exists(file_path):
                os.remove(file_path)
            return JSONResponse(
                status_code=200,
                content=ResponseData(
                    code=200,
                    message="OCR识别完成，但未识别到任何文本",
                    result=[]
                ).model_dump(exclude_none=True)
            )
        rec_texts = result[0].get("rec_texts", [])
        rec_scores = result[0].get("rec_scores", [])
        rec_polys = result[0].get("rec_polys", [])
        rt = [[]]
        for i, text in enumerate(rec_texts):
            rt[0].append([rec_polys[i].tolist(), [text, float(f"{rec_scores[i]:.4f}")]])
        if os.path.exists(file_path):
            os.remove(file_path)
        return JSONResponse(
            status_code=200,
            content=ResponseData(
                code=200,
                message="OCR识别成功",
                result=rt
            ).model_dump(exclude_none=True)
        )

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"处理过程出错: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ResponseData(
                code=500,
                message=f"处理过程出错: {str(e)}",
                result=[]
            ).model_dump(exclude_none=True)
        )
if __name__ == "__main__":
    import uvicorn
    # 在9999端口启动服务，允许外部访问
    uvicorn.run(app, host="0.0.0.0", port=9999)
