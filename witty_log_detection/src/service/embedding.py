# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import asyncio
import requests
import json
import urllib3
from src.config.config import Config
import logging
from src.enum.provider import ProviderEnum

logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Embedding():
    @staticmethod
    async def get_embedding(text_list: list[str]) -> list[list[float]] | None:
        """批量获取文本向量（一次API，多条文本）"""
        config = Config().get_config().embedding_model

        if config.provider == ProviderEnum.OPENAPI:
            headers = {"Authorization": f"Bearer {config.api_key}"}
            data = {
                "input": text_list,  # 直接传入列表，批量
                "model": config.model_name,
                "encoding_format": "float"
            }
            try:
                # 同步 requests 包装成异步
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(
                    None,
                    lambda: requests.post(
                        url=config.end_point,
                        headers=headers,
                        json=data,
                        verify=False
                    )
                )

                if not 200 <= res.status_code < 300:
                    logger.error(f"向量化接口失败 {res.status_code}")
                    return None

                result = res.json()
                vectors = []
                for item in result["data"]:
                    vec = item["embedding"]
                    while len(vec) < 1024:
                        vec.append(0.0)
                    vectors.append(vec[:1024])
                return vectors

            except Exception as e:
                logger.exception(f"[Embedding] 批量向量化失败: {e}")
                return None

        elif config.provider == ProviderEnum.ASCENDING:
            # 昇腾不支持批量，这里保持单条逻辑
            vectors = []
            for text in text_list:
                try:
                    data = {"inputs": text}
                    loop = asyncio.get_event_loop()
                    res = await loop.run_in_executor(
                        None,
                        lambda: requests.post(
                            url=config.end_point, json=data, verify=False
                        )
                    )
                    if not 200 <= res.status_code < 300:
                        vectors.append([0.0]*1024)
                        continue
                    vec = json.loads(res.text)[0]
                    while len(vec) < 1024:
                        vec.append(0.0)
                    vectors.append(vec[:1024])
                except Exception as e:
                    logger.exception(f"[Embedding] 昇腾向量化失败: {e}")
                    vectors.append([0.0]*1024)
            return vectors

        else:
            return None

    @staticmethod
    async def vectorize_embedding(text_list: list[str]) -> list[list[float]]:
        batch_size = Config().get_config().embedding_model.batch_size
        embeddings = []
        total_batch = (len(text_list) + batch_size - 1) // batch_size

        for i in range(0, len(text_list), batch_size):
            current_batch = i // batch_size + 1
            logger.info(f"开始向量化第 {current_batch}/{total_batch} 个批次")
            batch_texts = text_list[i:i + batch_size]

            # ✅ 一次调用，批量处理
            batch_embeddings = await Embedding.get_embedding(batch_texts)
            await asyncio.sleep(0.3)
            if batch_embeddings:
                embeddings.extend(batch_embeddings)
            else:
                embeddings.extend([[0.0]*1024 for _ in batch_texts])

        return embeddings