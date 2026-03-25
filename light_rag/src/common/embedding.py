import json
import logging
from typing import List, Optional, Tuple

import aiohttp
from common.config import (
    get_embedding_api_key,
    get_embedding_batch_size,
    get_embedding_endpoint,
    get_embedding_model_name,
    get_embedding_timeout,
    get_embedding_type,
    get_embedding_vector_dimension,
)

logger = logging.getLogger(__name__)


class Embedding:
    """Embedding 服务类"""
    
    @staticmethod
    def _get_config():
        """获取配置（延迟加载）"""
        return {
            "type": get_embedding_type(),
            "api_key": get_embedding_api_key(),
            "endpoint": get_embedding_endpoint(),
            "model_name": get_embedding_model_name(),
            "timeout": get_embedding_timeout(),
            "vector_dimension": get_embedding_vector_dimension(),
            "batch_size": get_embedding_batch_size(),
        }
    
    @staticmethod
    def is_configured() -> bool:
        config = Embedding._get_config()
        return bool(config["api_key"] and config["endpoint"])

    @staticmethod
    def _normalize_vector(vector: Optional[List[float]], vector_dim: int) -> Optional[List[float]]:
        """标准化向量维度（不足补 0，超出截断）"""
        if not vector:
            return None
        normalized = list(vector)
        while len(normalized) < vector_dim:
            normalized.append(0.0)
        return normalized[:vector_dim]

    @staticmethod
    async def _vectorize_openai_batch(
        texts: List[str],
        session: aiohttp.ClientSession,
        config: dict
    ) -> Tuple[bool, List[Optional[List[float]]]]:
        """
        尝试一次请求批量向量化（OpenAI 兼容接口）
        :return: (是否成功, 向量结果)
        """
        headers = {
            "Authorization": f"Bearer {config['api_key']}"
        }
        data = {
            "input": texts,
            "model": config["model_name"],
            "encoding_format": "float"
        }
        try:
            async with session.post(
                url=config["endpoint"],
                headers=headers,
                json=data
            ) as res:
                if res.status != 200:
                    body = (await res.text())[:200]
                    logger.warning(f"[Embedding] 批量请求失败，status={res.status}, body={body}")
                    return False, [None] * len(texts)

                result = await res.json()
                data_list = result.get("data", [])
                if not isinstance(data_list, list) or len(data_list) != len(texts):
                    logger.warning(
                        f"[Embedding] 批量响应长度异常，input={len(texts)}, output={len(data_list) if isinstance(data_list, list) else 'invalid'}"
                    )
                    return False, [None] * len(texts)

                vector_dim = config["vector_dimension"]
                vectors: List[Optional[List[float]]] = [None] * len(texts)
                for item in data_list:
                    idx = item.get("index")
                    embedding = item.get("embedding")
                    if isinstance(idx, int) and 0 <= idx < len(texts):
                        vectors[idx] = Embedding._normalize_vector(embedding, vector_dim)

                if any(v is None for v in vectors):
                    logger.warning("[Embedding] 批量响应缺少部分向量")
                    return False, [None] * len(texts)
                return True, vectors
        except Exception as e:
            logger.warning(f"[Embedding] 批量请求异常: {e}")
            return False, [None] * len(texts)
    
    @staticmethod
    async def vectorize_embedding(text: str, session: Optional[aiohttp.ClientSession] = None) -> Optional[List[float]]:
        """
        将文本向量化（异步实现）
        :param text: 文本内容
        :param session: 可选的 aiohttp 会话
        :return: 向量列表
        """
        config = Embedding._get_config()
        vector = None
        should_close_session = False
        
        # 如果没有提供会话，创建一个新的
        if session is None:
            timeout = aiohttp.ClientTimeout(total=config["timeout"])
            connector = aiohttp.TCPConnector(ssl=False)
            session = aiohttp.ClientSession(timeout=timeout, connector=connector)
            should_close_session = True
        
        try:
            if config["type"] == "openai":
                headers = {
                    "Authorization": f"Bearer {config['api_key']}"
                }
                data = {
                    "input": text,
                    "model": config["model_name"],
                    "encoding_format": "float"
                }
                try:
                    async with session.post(
                        url=config["endpoint"],
                        headers=headers,
                        json=data
                    ) as res:
                        if res.status != 200:
                            return None
                        result = await res.json()
                        vector = result['data'][0]['embedding']
                except Exception:
                    return None
            elif config["type"] == "mindie":
                try:
                    data = {
                        "inputs": text,
                    }
                    async with session.post(
                        url=config["endpoint"],
                        json=data
                    ) as res:
                        if res.status != 200:
                            return None
                        text_result = await res.text()
                        vector = json.loads(text_result)[0]
                except Exception:
                    return None
            else:
                return None
            
            return Embedding._normalize_vector(vector, config["vector_dimension"])
        finally:
            if should_close_session:
                await session.close()
    
    @staticmethod
    async def vectorize_embeddings_batch(texts: List[str], max_concurrent: int = 5) -> List[Optional[List[float]]]:
        """
        批量向量化（按 config 中的 embedding_batch_size 分批请求服务端）
        :param texts: 文本列表
        :param max_concurrent: 兼容保留，未使用
        :return: 向量列表（与输入文本顺序对应）
        """
        config = Embedding._get_config()
        if not texts:
            return []
        if not config["api_key"] or not config["endpoint"]:
            return [None] * len(texts)

        bs = config["batch_size"]
        timeout = aiohttp.ClientTimeout(total=config["timeout"])
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            vectors: List[Optional[List[float]]] = [None] * len(texts)

            if config["type"] == "openai":
                for start in range(0, len(texts), bs):
                    sub_texts = texts[start:start + bs]
                    ok, sub_vectors = await Embedding._vectorize_openai_batch(sub_texts, session, config)
                    if ok:
                        for offset, vec in enumerate(sub_vectors):
                            vectors[start + offset] = vec
            else:
                for i, txt in enumerate(texts):
                    vectors[i] = await Embedding.vectorize_embedding(txt, session=session)

            return vectors
    

