from paddleocr import PaddleOCR
import cv2
ocr = PaddleOCR(use_angle_cls=True, lang="ch")
image_path = 'test.jpg'
image = cv2.imread(image_path)
result = ocr.predict(image)
