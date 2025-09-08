# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import requests
import json
import urllib3
from config import BaseConfig, EmbeddingType

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Embedding():
    @staticmethod
    async def vectorize_embedding(text):
        vector = None
        if BaseConfig().get_config().embedding.embedding_type == EmbeddingType.OPENAI:
            headers = {
                "Authorization": f"Bearer {BaseConfig().get_config().embedding.embedding_api_key}",
            }
            data = {
                "input": text,
                "model": BaseConfig().get_config().embedding.embedding_model_name,
                "encoding_format": "float"
            }
            try:
                res = requests.post(url=BaseConfig().get_config().embedding.embedding_endpoint,
                                    headers=headers, json=data, verify=False)
                if res.status_code != 200:
                    return None
                vector = res.json()['data'][0]['embedding']
            except Exception as e:
                err = f"[Embedding] 向量化失败 ，error: {e}"
                print(err)
                return None
        elif BaseConfig().get_config().embedding.embedding_type == 'mindie':
            try:
                data = {
                    "inputs": text,
                }
                res = requests.post(url=BaseConfig().get_config().embedding.embedding_endpoint, json=data, verify=False)
                if res.status_code != 200:
                    return None
                vector = json.loads(res.text)[0]
            except Exception as e:
                err = f"[Embedding] 向量化失败 ，error: {e}"
                print(err)
                return None
        else:
            return None
        while len(vector) < 1024:
            vector.append(0)
        return vector[:1024]
