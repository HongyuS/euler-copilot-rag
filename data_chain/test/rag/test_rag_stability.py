# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
RAG 检索稳定性测试

测试范围:
- 异常处理
- 边界条件
- 并发稳定性
- 长时间运行稳定性
"""

import asyncio
import uuid
from unittest.mock import MagicMock, patch

import pytest

from data_chain.rag.base_searcher import BaseSearcher
from data_chain.rag.vector_searcher import VectorSearcher
from data_chain.rag.keyword_searcher import KeyWordSearcher
from data_chain.rerank.rerank import Rerank


class TestSearchErrorHandling:
    """测试搜索错误处理"""

    @pytest.mark.asyncio
    async def test_vector_search_embedding_failure(self):
        """测试 Embedding 失败处理"""
        kb_id = uuid.uuid4()
        query = "测试"
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = None  # Embedding 失败
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                # 不应该抛出异常
                result = await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5
                )
                
                assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_keyword_search_database_failure(self):
        """测试数据库失败处理"""
        kb_id = uuid.uuid4()
        query = "测试"
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.side_effect = Exception("Database connection failed")
            
            # 不应该抛出异常，应该返回空列表
            result = await KeyWordSearcher.search(
                query=query,
                kb_id=kb_id,
                top_k=5
            )
            
            assert result == []

    @pytest.mark.asyncio
    async def test_search_timeout_handling(self):
        """测试超时处理"""
        kb_id = uuid.uuid4()
        query = "测试"
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                # 模拟超时异常
                mock_get.side_effect = asyncio.TimeoutError("Connection timeout")
                
                # 应该重试并最终返回空列表
                result = await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5
                )
                
                assert result == []


class TestRerankErrorHandling:
    """测试重排序错误处理"""

    @pytest.mark.asyncio
    async def test_rerank_api_failure(self, mock_config):
        """测试 API 失败处理"""
        mock_config['RERANK_TYPE'] = "bailian"
        
        query = "测试"
        documents = ["文档1", "文档2", "文档3"]
        
        with patch("requests.post") as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            # 应该返回默认顺序
            result = await Rerank.rerank(query, documents, top_k=3)
            
            assert isinstance(result, list)
            assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_rerank_invalid_response(self, mock_config):
        """测试无效响应处理"""
        mock_config['RERANK_TYPE'] = "bailian"
        
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}  # 无效响应
            mock_post.return_value = mock_response
            
            # 应该处理无效响应
            result = await Rerank.rerank("测试", ["文档"], top_k=1)
            
            # 应该有某种处理方式
            assert isinstance(result, list)


class TestEdgeCases:
    """测试边界情况"""

    @pytest.mark.asyncio
    async def test_search_empty_query(self):
        """测试空查询"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                result = await VectorSearcher.search(
                    query="",
                    kb_id=kb_id,
                    top_k=5
                )
                
                assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_very_long_query(self):
        """测试超长查询"""
        kb_id = uuid.uuid4()
        query = "测试 " * 1000  # 很长的查询
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                result = await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5
                )
                
                assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_special_characters_query(self):
        """测试特殊字符查询"""
        kb_id = uuid.uuid4()
        special_queries = [
            "test!@#$%",
            "<script>alert('xss')</script>",
            "'; DROP TABLE chunks; --",
            "测试\n换行\t制表",
            "🎉 Emoji 测试 🚀",
        ]
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                for query in special_queries:
                    result = await VectorSearcher.search(
                        query=query,
                        kb_id=kb_id,
                        top_k=5
                    )
                    assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_zero_top_k(self):
        """测试 top_k 为 0"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                result = await VectorSearcher.search(
                    query="测试",
                    kb_id=kb_id,
                    top_k=0
                )
                
                assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_negative_top_k(self):
        """测试负的 top_k"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                # 应该处理或拒绝负值
                result = await VectorSearcher.search(
                    query="测试",
                    kb_id=kb_id,
                    top_k=-1
                )
                
                assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_very_large_top_k(self):
        """测试非常大的 top_k"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                result = await VectorSearcher.search(
                    query="测试",
                    kb_id=kb_id,
                    top_k=1000000
                )
                
                assert isinstance(result, list)


class TestConcurrencyStability:
    """测试并发稳定性"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_searches(self):
        """测试并发搜索"""
        kb_id = uuid.uuid4()
        
        async def search_task(query_id):
            with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
                mock_embed.return_value = [0.1] * 1024
                
                with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                    mock_get.return_value = [MagicMock() for _ in range(5)]
                    
                    return await VectorSearcher.search(
                        query=f"并发查询 {query_id}",
                        kb_id=kb_id,
                        top_k=5
                    )
        
        # 并发执行多个搜索
        tasks = [search_task(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        
        # 验证所有搜索都成功完成
        assert len(results) == 20
        for result in results:
            assert isinstance(result, list)
            assert len(result) == 5


class TestDataIntegrity:
    """测试数据完整性"""

    @pytest.mark.asyncio
    async def test_rerank_preserves_all_chunks(self):
        """测试重排序保留所有 chunks"""
        query = "测试"
        
        mock_chunks = []
        for i in range(10):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"文档 {i}"
            entity.tokens = 10
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.base_searcher.TokenTool.cal_jac") as mock_jac:
            mock_jac.return_value = 0.5
            
            result = await BaseSearcher.rerank(
                mock_chunks,
                "algorithm",
                query
            )
            
            # 验证所有 chunks 都被保留
            assert len(result) == len(mock_chunks)
            
            # 验证没有重复的 chunks
            result_ids = [r.id for r in result]
            assert len(result_ids) == len(set(result_ids))

    @pytest.mark.asyncio
    async def test_classify_preserves_all_chunks(self):
        """测试分类保留所有 chunks"""
        mock_chunks = []
        for i in range(10):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.doc_id = uuid.uuid4()
            entity.doc_name = f"doc_{i}.txt"
            entity.text = f"内容 {i}"
            entity.global_offset = i
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.base_searcher.Convertor.convert_chunk_entity_to_chunk") as mock_convert:
            mock_convert.return_value = MagicMock()
            
            result = await BaseSearcher.classify_by_doc_id(mock_chunks)
            
            # 统计所有分类后的 chunks
            total_chunks = sum(len(doc_chunk.chunks) for doc_chunk in result)
            assert total_chunks == len(mock_chunks)


class TestResourceCleanup:
    """测试资源清理"""

    @pytest.mark.asyncio
    async def test_search_no_resource_leak(self):
        """测试搜索没有资源泄漏"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                # 执行多次搜索
                for i in range(100):
                    await VectorSearcher.search(
                        query=f"查询 {i}",
                        kb_id=kb_id,
                        top_k=5
                    )
                
                # 验证 Embedding 被调用 100 次
                assert mock_embed.call_count == 100
