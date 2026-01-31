# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import requests
import json
import urllib3
from data_chain.config.config import config
from data_chain.logger.logger import logger as logging
from data_chain.entities.enum import RerankType

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class Rerank():
    @staticmethod
    async def assemable_data(query:str, documents:list[str], top_k:int=3)->dict:
        if config['RERANK_TYPE'] == RerankType.BAILIAN:
            data={
                "model": config["RERANK_MODEL_NAME"],
                "input":{
                     "query": query,
                     "documents": documents
                },
                "parameters": {
                    "return_documents": True,
                    "top_n": top_k
                }
            }
        elif config['RERANK_TYPE'] == RerankType.GUIJILIUDONG:
            data={
                "model": config["RERANK_MODEL_NAME"],
                "query": query,
                "documents": documents
            }
        elif config['RERANK_TYPE'] == RerankType.VLLM:
            data={
                "model": config["RERANK_MODEL_NAME"],
                "text_1": query,
                "text_2": documents
            }
        elif config['RERANK_TYPE'] == RerankType.ASCEND:
            data={
                "query": query,
                "texts": documents
            }
        return data
    @staticmethod
    async def parse_response(response: requests.Response, top_k:int=3)->list[int]:
        documents_index=[]
        if config['RERANK_TYPE'] == RerankType.BAILIAN:
            for item in response.json()["output"]["results"]:
                documents_index.append(item['index'])
        elif config['RERANK_TYPE'] == RerankType.GUIJILIUDONG:
            for item in response.json()['results']:
                documents_index.append(item['index'])
        elif config['RERANK_TYPE'] == RerankType.VLLM:
            for item in response.json()['data']:
                documents_index.append(item['index'])
        elif config['RERANK_TYPE'] == RerankType.ASCEND:
            for i in range(len(response.json())):
                documents_index.append(response.json()[i]['index'])
        return documents_index[:top_k]
    @staticmethod
    async def rerank(query:str, documents:list[str],top_k:int=3)->list[int]:
        if len(documents) <= top_k:
            return list(range(len(documents)))
        api_key = config["RERANK_API_KEY"]
        url = config["RERANK_ENDPOINT"]
        headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type' : 'application/json'
        }

        data = await Rerank.assemable_data(query, documents, top_k)
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            err = f"[Rerank] 重排序失败 ，error: {response.text}"
            logging.error(err)
            return list(range(top_k))
        documents_index = await Rerank.parse_response(response, top_k)
        return documents_index
