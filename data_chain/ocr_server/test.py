import requests


def call_ocr_api(image_path, api_url="http://localhost:9999/ocr"):
    """
    调用OCR接口识别图片中的文字

    参数:
        image_path: 本地图片文件路径
        api_url: OCR接口的URL地址

    返回:
        识别到的文字字符串
    """
    try:
        # 打开图片文件并准备上传
        with open(image_path, 'rb') as file:
            # 构造表单数据，键名需与接口中的参数名一致
            files = {'file': (image_path, file, 'image/jpeg')}
            # 发送GET请求
            response = requests.get(api_url, files=files)

            # 检查响应状态
            if response.status_code == 200:
                # 返回识别结果
                return response.json()
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                return None

    except FileNotFoundError:
        print(f"错误: 找不到图片文件 {image_path}")
        return None
    except Exception as e:
        print(f"调用接口时发生错误: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    # 替换为你的图片路径
    image_path = "test.jpg"
    # 调用OCR接口
    result = call_ocr_api(image_path)

    if result:
        print("OCR识别结果:")
        print("-" * 50)
        print(type(result))
        print(result)
        print("-" * 50)
