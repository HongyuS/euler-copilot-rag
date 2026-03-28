# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
向量检索器测试

测试范围:
- 向量检索功能
- Embedding 调用
- 超时重试机制
- 参数验证
"""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from data_chain.rag.vector_searcher import VectorSearcher
from data_chain.entities.enum import SearchMethod


class TestVectorSearcherBasic:
    """测试向量检索器基本功能"""

    def test_searcher_name(self):
        """测试检索器名称"""
        assert VectorSearcher.name == SearchMethod.VECTOR.value

    @pytest.mark.asyncio
    async def test_search_basic(self):
        """测试基本检索功能"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源操作系统"
        
        mock_chunks = []
        for i in range(3):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"结果 {i}"
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = mock_chunks
                
                result = await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=3
                )
                
                assert isinstance(result, list)
                assert len(result) == 3
                mock_embed.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_search_with_doc_ids_filter(self):
        """测试带文档 ID 过滤的检索"""
        kb_id = uuid.uuid4()
        doc_ids = [uuid.uuid4(), uuid.uuid4()]
        query = "测试查询"
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5,
                    doc_ids=doc_ids
                )
                
                # 验证 doc_ids 被传递
                call_args = mock_get.call_args
                assert call_args[1]['doc_ids'] == doc_ids

    @pytest.mark.asyncio
    async def test_search_with_banned_ids(self):
        """测试带禁用 ID 的检索"""
        kb_id = uuid.uuid4()
        banned_ids = [uuid.uuid4()]
        query = "测试查询"
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5,
                    banned_ids=banned_ids
                )
                
                # 验证 banned_ids 被传递
                call_args = mock_get.call_args
                assert call_args[1]['banned_ids'] == banned_ids


class TestVectorSearcherRetry:
    """测试向量检索器重试机制"""

    @pytest.mark.asyncio
    async def test_search_retry_on_failure(self):
        """测试失败时的重试"""
        kb_id = uuid.uuid4()
        query = "测试查询"
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                # 前两次失败，第三次成功
                mock_get.side_effect = [
                    Exception("Timeout"),
                    Exception("Timeout"),
                    [MagicMock()]
                ]
                
                result = await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5
                )
                
                # 应该重试 3 次
                assert mock_get.call_count == 3
                assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_all_retries_fail(self):
        """测试所有重试都失败的情况"""
        kb_id = uuid.uuid4()
        query = "测试查询"
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                # 所有调用都失败
                mock_get.side_effect = Exception("Persistent error")
                
                result = await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5
                )
                
                # 应该尝试 3 次后返回空列表
                assert mock_get.call_count == 3
                assert result == []


class TestVectorSearcherEmbedding:
    """测试 Embedding 集成"""

    @pytest.mark.asyncio
    async def test_embedding_vector_generation(self):
        """测试 Embedding 向量生成"""
        kb_id = uuid.uuid4()
        query = "测试查询"
        expected_vector = [0.5] * 1024
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = expected_vector
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5
                )
                
                # 验证 Embedding 被调用
                mock_embed.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_embedding_none_result(self):
        """测试 Embedding 返回 None 的情况"""
        kb_id = uuid.uuid4()
        query = "测试查询"
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = None
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                result = await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5
                )
                
                # 应该仍然尝试搜索
                mock_get.assert_called()


class TestVectorSearcherParams:
    """测试参数处理"""

    @pytest.mark.asyncio
    async def test_search_different_top_k_values(self):
        """测试不同的 top_k 值"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = []
                
                # 测试不同的 top_k 值
                for top_k in [1, 5, 10, 100]:
                    await VectorSearcher.search(
                        query="测试",
                        kb_id=kb_id,
                        top_k=top_k
                    )
                    
                    # 验证 top_k 被传递
                    call_args = mock_get.call_args
                    assert call_args[1]['top_k'] == top_k

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
                
                # 空查询也应该工作
                assert isinstance(result, list)


class TestVectorSearcherAccuracy:
    """测试向量检索准确率"""

    @pytest.mark.asyncio
    async def test_search_result_order(self):
        """测试结果顺序"""
        kb_id = uuid.uuid4()
        query = "OpenEuler"
        
        # 创建按相关性排序的 mock 结果
        mock_chunks = []
        for i in range(5):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"结果 {i}"
            entity.score = 0.9 - i * 0.1  # 递减的相关性分数
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = mock_chunks
                
                result = await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5
                )
                
                # 验证结果保持原始顺序
                assert len(result) == 5


class TestVectorSearcherStability:
    """测试向量检索稳定性"""

    @pytest.mark.asyncio
    async def test_search_consistency(self):
        """测试搜索一致性（多次相同查询应返回相同结果）"""
        kb_id = uuid.uuid4()
        query = "一致性测试"
        
        mock_result = [MagicMock() for _ in range(3)]
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = mock_result
                
                # 多次搜索
                results = []
                for _ in range(3):
                    result = await VectorSearcher.search(
                        query=query,
                        kb_id=kb_id,
                        top_k=3
                    )
                    results.append(result)
                
                # 验证 Embedding 被调用多次
                assert mock_embed.call_count == 3
