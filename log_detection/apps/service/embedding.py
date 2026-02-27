# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import asyncio
import requests
import json
import urllib3
from apps.config.config import Config
import logging
from apps.enum.provider import ProviderEnum
logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Embedding():
    @staticmethod
    async def get_embedding(text: str) -> list[float]:
        """获取文本的嵌入向量表示"""
        if Config().get_config().embedding_model.provider == ProviderEnum.OPENAPI:
            headers = {
                "Authorization": f"Bearer {Config().get_config().embedding_model.api_key}"
            }
            data = {
                "input": text,
                "model": Config().get_config().embedding_model.model_name,
                "encoding_format": "float"
            }
            try:
                res = requests.post(
                    url=Config().get_config().embedding_model.end_point, headers=headers, json=data, verify=False)
                if res.status_code != 200:
                    return None
                vector = res.json()['data'][0]['embedding']
            except Exception as e:
                err = f"[Embedding] 向量化失败 ，error: {e}"
                logging.exception(err)
                return None
        elif Config().get_config().embedding_model.provider == ProviderEnum.ASCENDING:
            try:
                data = {
                    "inputs": text,
                }
                res = requests.post(
                    url=Config().get_config().embedding_model.end_point, json=data, verify=False)
                if res.status_code != 200:
                    return None
                vector = json.loads(res.text)[0]
            except Exception as e:
                err = f"[Embedding] 向量化失败 ，error: {e}"
                logging.exception(err)
                return None
        else:
            return None
        while len(vector) < 1024:
            vector.append(0)
        return vector[:1024]

    @staticmethod
    async def vectorize_embedding(text_list: list[str]) -> list[list[float]]:
        batch_size = Config().get_config().embedding_model.batch_size
        embeddings = []
        for i in range(0, len(text_list), batch_size):
            batch_texts = text_list[i:i + batch_size]
            text_embedding_tasks = []
            for text in batch_texts:
                text_embedding_tasks.append(Embedding.get_embedding(text))
            batch_embeddings = await asyncio.gather(*text_embedding_tasks)
            embeddings.extend(batch_embeddings)
        return embeddings
