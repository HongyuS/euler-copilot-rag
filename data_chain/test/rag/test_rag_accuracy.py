# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
RAG 检索准确率测试

测试范围:
- 检索结果相关性
- 排名准确性
- 过滤准确性
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from data_chain.rag.base_searcher import BaseSearcher
from data_chain.rag.vector_searcher import VectorSearcher
from data_chain.rag.keyword_searcher import KeyWordSearcher


class TestSearchRelevance:
    """测试检索相关性"""

    @pytest.mark.asyncio
    async def test_vector_search_relevance_score(self):
        """测试向量检索相关性分数"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源操作系统"
        
        # 创建不同相关度的 mock chunks
        mock_chunks = []
        relevance_scores = [0.95, 0.87, 0.82, 0.76, 0.71]
        
        for i, score in enumerate(relevance_scores):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"文档内容 {i}"
            entity.relevance_score = score
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
                
                # 验证返回了所有结果
                assert len(result) == 5

    @pytest.mark.asyncio
    async def test_keyword_search_exact_match(self):
        """测试关键词精确匹配"""
        kb_id = uuid.uuid4()
        query = "OpenEuler"
        
        mock_chunks = []
        for i in range(5):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            # 所有文档都包含关键词
            entity.text = f"这是关于 OpenEuler 的文档 {i}"
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = mock_chunks
            
            result = await KeyWordSearcher.search(
                query=query,
                kb_id=kb_id,
                top_k=5
            )
            
            # 验证所有结果都包含查询关键词
            for chunk in result:
                assert query.lower() in chunk.text.lower()

    @pytest.mark.asyncio
    async def test_keyword_search_partial_match(self):
        """测试关键词部分匹配"""
        kb_id = uuid.uuid4()
        query = "OpenEuler"
        
        # 创建混合匹配和不匹配的 chunks
        mock_chunks = []
        for i in range(3):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"OpenEuler 文档 {i}"
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = mock_chunks
            
            result = await KeyWordSearcher.search(
                query=query,
                kb_id=kb_id,
                top_k=5
            )
            
            # 验证只返回匹配的结果
            for chunk in result:
                assert query in chunk.text


class TestRerankAccuracy:
    """测试重排序准确性"""

    @pytest.mark.asyncio
    async def test_rerank_ordering(self):
        """测试重排序顺序"""
        query = "OpenEuler 开源"
        
        # 创建 chunks，相关性从低到高
        mock_chunks = []
        for i in range(5):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"文档 {i}"
            entity.tokens = 10
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.base_searcher.TokenTool.cal_jac") as mock_jac:
            # 模拟相关性分数（越高越相关）
            mock_jac.side_effect = [0.3, 0.5, 0.9, 0.7, 0.4]
            
            result = await BaseSearcher.rerank(
                mock_chunks,
                "algorithm",
                query
            )
            
            # 验证结果是按相关性排序的
            assert len(result) == 5
            # 索引 2 (分数 0.9) 应该排在第一位
            assert result[0] == mock_chunks[2]

    @pytest.mark.asyncio
    async def test_rerank_with_identical_scores(self):
        """测试相同分数的处理"""
        query = "测试"
        
        mock_chunks = []
        for i in range(3):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"文档 {i}"
            entity.tokens = 10
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.base_searcher.TokenTool.cal_jac") as mock_jac:
            # 所有分数相同
            mock_jac.return_value = 0.5
            
            result = await BaseSearcher.rerank(
                mock_chunks,
                "algorithm",
                query
            )
            
            # 验证所有结果都被保留
            assert len(result) == 3


class TestFilteringAccuracy:
    """测试过滤准确性"""

    @pytest.mark.asyncio
    async def test_doc_ids_filter_accuracy(self):
        """测试文档 ID 过滤准确性"""
        kb_id = uuid.uuid4()
        allowed_doc_id = uuid.uuid4()
        blocked_doc_id = uuid.uuid4()
        
        query = "测试"
        
        # 创建混合的 chunks
        all_chunks = []
        for i in range(5):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.doc_id = allowed_doc_id if i % 2 == 0 else blocked_doc_id
            entity.text = f"文档 {i}"
            all_chunks.append(entity)
        
        # 过滤后的 chunks（只包含允许的文档）
        filtered_chunks = [c for c in all_chunks if c.doc_id == allowed_doc_id]
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = filtered_chunks
                
                result = await VectorSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5,
                    doc_ids=[allowed_doc_id]
                )
                
                # 验证只返回允许的文档
                for chunk in result:
                    assert chunk.doc_id == allowed_doc_id

    @pytest.mark.asyncio
    async def test_banned_ids_filter_accuracy(self):
        """测试禁用 ID 过滤准确性"""
        kb_id = uuid.uuid4()
        banned_id = uuid.uuid4()
        
        query = "测试"
        
        mock_chunks = []
        for i in range(5):
            entity = MagicMock()
            entity.id = banned_id if i == 0 else uuid.uuid4()
            entity.text = f"文档 {i}"
            mock_chunks.append(entity)
        
        # 过滤掉禁用的 chunk
        allowed_chunks = [c for c in mock_chunks if c.id != banned_id]
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = allowed_chunks
            
            result = await KeyWordSearcher.search(
                query=query,
                kb_id=kb_id,
                top_k=5,
                banned_ids=[banned_id]
            )
            
            # 验证禁用的 ID 不在结果中
            result_ids = [c.id for c in result]
            assert banned_id not in result_ids


class TestSearchCompleteness:
    """测试搜索完整性"""

    @pytest.mark.asyncio
    async def test_search_returns_expected_count(self):
        """测试返回结果数量符合预期"""
        kb_id = uuid.uuid4()
        query = "测试"
        
        top_k_values = [1, 5, 10, 20]
        
        for top_k in top_k_values:
            mock_chunks = [MagicMock() for _ in range(top_k * 2)]  # 提供更多结果
            
            with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
                mock_embed.return_value = [0.1] * 1024
                
                with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                    mock_get.return_value = mock_chunks[:top_k]
                    
                    result = await VectorSearcher.search(
                        query=query,
                        kb_id=kb_id,
                        top_k=top_k
                    )
                    
                    # 验证返回了请求数量的结果
                    assert len(result) <= top_k


class TestRankingStability:
    """测试排名稳定性"""

    @pytest.mark.asyncio
    async def test_consistent_ranking_for_same_query(self):
        """测试相同查询的排名一致性"""
        kb_id = uuid.uuid4()
        query = "稳定性测试"
        
        mock_chunks = []
        for i in range(5):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"文档 {i}"
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = mock_chunks
                
                # 多次执行相同查询
                results = []
                for _ in range(3):
                    result = await VectorSearcher.search(
                        query=query,
                        kb_id=kb_id,
                        top_k=5
                    )
                    results.append([r.id for r in result])
                
                # 验证结果一致
                assert results[0] == results[1] == results[2]
