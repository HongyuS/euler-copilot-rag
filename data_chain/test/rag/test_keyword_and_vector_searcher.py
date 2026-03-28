# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
关键词+向量检索器测试

测试范围:
- 混合检索策略
- 关键词粗排+向量精排
- 结果合并
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from data_chain.rag.keyword_and_vector_searcher import KeywordVectorSearcher
from data_chain.entities.enum import SearchMethod


class TestKeywordVectorSearcherBasic:
    """测试关键词向量检索器基本功能"""

    def test_searcher_name(self):
        """测试检索器名称"""
        assert KeywordVectorSearcher.name == SearchMethod.KEYWORD_AND_VECTOR.value

    @pytest.mark.asyncio
    async def test_search_basic(self):
        """测试基本检索功能"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源"
        
        keyword_chunks = [MagicMock() for _ in range(2)]
        vector_chunks = [MagicMock() for _ in range(3)]
        
        with patch("data_chain.rag.keyword_and_vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                mock_kw.return_value = keyword_chunks
                
                with patch("data_chain.rag.keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                    mock_vec.return_value = vector_chunks
                    
                    result = await KeywordVectorSearcher.search(
                        query=query,
                        kb_id=kb_id,
                        top_k=5
                    )
                    
                    assert isinstance(result, list)
                    assert len(result) == 5

    @pytest.mark.asyncio
    async def test_search_tight_then_loose_keyword(self):
        """测试先紧后松的关键词检索"""
        kb_id = uuid.uuid4()
        
        tight_results = [MagicMock() for _ in range(1)]
        loose_results = [MagicMock() for _ in range(2)]
        vector_results = [MagicMock() for _ in range(2)]
        
        with patch("data_chain.rag.keyword_and_vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                mock_kw.side_effect = [tight_results, loose_results]
                
                with patch("data_chain.rag.keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                    mock_vec.return_value = vector_results
                    
                    result = await KeywordVectorSearcher.search(
                        query="测试",
                        kb_id=kb_id,
                        top_k=5
                    )
                    
                    # 验证调用了两次关键词检索
                    assert mock_kw.call_count == 2
                    # 第一次是紧匹配
                    assert mock_kw.call_args_list[0][1].get('is_tight') is True
                    # 第二次是松匹配
                    assert mock_kw.call_args_list[1][1].get('is_tight') is False


class TestKeywordVectorSearcherErrorHandling:
    """测试错误处理"""

    @pytest.mark.asyncio
    async def test_search_exception_handling(self):
        """测试异常处理"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.keyword_and_vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                mock_kw.side_effect = Exception("Database error")
                
                result = await KeywordVectorSearcher.search(
                    query="测试",
                    kb_id=kb_id,
                    top_k=5
                )
                
                assert result == []

    @pytest.mark.asyncio
    async def test_search_vector_retry(self):
        """测试向量检索重试"""
        kb_id = uuid.uuid4()
        
        keyword_chunks = [MagicMock()]
        
        with patch("data_chain.rag.keyword_and_vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                mock_kw.return_value = keyword_chunks
                
                with patch("data_chain.rag.keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                    # 前两次失败，第三次成功
                    mock_vec.side_effect = [
                        Exception("Timeout"),
                        Exception("Timeout"),
                        [MagicMock()]
                    ]
                    
                    result = await KeywordVectorSearcher.search(
                        query="测试",
                        kb_id=kb_id,
                        top_k=5
                    )
                    
                    assert mock_vec.call_count == 3
                    assert isinstance(result, list)


class TestKeywordVectorSearcherResultCombination:
    """测试结果合并"""

    @pytest.mark.asyncio
    async def test_result_merge(self):
        """测试结果合并逻辑"""
        kb_id = uuid.uuid4()
        
        keyword_chunk = MagicMock()
        keyword_chunk.id = uuid.uuid4()
        vector_chunk = MagicMock()
        vector_chunk.id = uuid.uuid4()
        
        with patch("data_chain.rag.keyword_and_vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                mock_kw.side_effect = [[keyword_chunk], []]
                
                with patch("data_chain.rag.keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                    mock_vec.return_value = [vector_chunk]
                    
                    result = await KeywordVectorSearcher.search(
                        query="测试",
                        kb_id=kb_id,
                        top_k=5
                    )
                    
                    # 验证结果被合并
                    assert len(result) == 2
                    assert keyword_chunk in result
                    assert vector_chunk in result
