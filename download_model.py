import tiktoken
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # 使用中文语言模型
enc = tiktoken.encoding_for_model("gpt-4") 
print(len(enc.encode('hello world')))