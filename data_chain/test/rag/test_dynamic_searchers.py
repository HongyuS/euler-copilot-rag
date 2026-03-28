# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
动态加权检索器测试

测试范围:
- DynamicKeywordVectorSearcher (动态加权关键词+向量)
- DynamicWeightKeyWordSearcher (纯动态加权关键词)
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from data_chain.rag.dynamic_weighted_keyword_and_vector_searcher import DynamicKeywordVectorSearcher
from data_chain.rag.dynamic_weighted_keyword_searcher import DynamicWeightKeyWordSearcher
from data_chain.entities.enum import SearchMethod


class TestDynamicKeywordVectorSearcher:
    """测试动态加权关键词向量检索器"""

    def test_searcher_name(self):
        """测试检索器名称"""
        assert DynamicKeywordVectorSearcher.name == SearchMethod.DYNAMIC_WEIGHTED_KEYWORD_AND_VECTOR.value

    @pytest.mark.asyncio
    async def test_search_basic(self):
        """测试基本检索功能"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源操作系统"
        
        keyword_chunks = [MagicMock() for _ in range(2)]
        dynamic_chunks = [MagicMock() for _ in range(2)]
        vector_chunks = [MagicMock() for _ in range(1)]
        
        with patch("data_chain.rag.dynamic_weighted_keyword_and_vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.dynamic_weighted_keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                mock_kw.return_value = keyword_chunks
                
                with patch("data_chain.rag.dynamic_weighted_keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_dyn:
                    mock_dyn.return_value = dynamic_chunks
                    
                    with patch("data_chain.rag.dynamic_weighted_keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                        mock_vec.return_value = vector_chunks
                        
                        result = await DynamicKeywordVectorSearcher.search(
                            query=query,
                            kb_id=kb_id,
                            top_k=5
                        )
                        
                        assert isinstance(result, list)
                        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_search_error_handling(self):
        """测试错误处理"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.dynamic_weighted_keyword_and_vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.dynamic_weighted_keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                mock_kw.side_effect = Exception("Database error")
                
                result = await DynamicKeywordVectorSearcher.search(
                    query="测试",
                    kb_id=kb_id,
                    top_k=5
                )
                
                assert result == []

    @pytest.mark.asyncio
    async def test_search_vector_timeout_retry(self):
        """测试向量检索超时重试"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.dynamic_weighted_keyword_and_vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.dynamic_weighted_keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                mock_kw.return_value = [MagicMock()]
                
                with patch("data_chain.rag.dynamic_weighted_keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_dyn:
                    mock_dyn.return_value = [MagicMock()]
                    
                    with patch("data_chain.rag.dynamic_weighted_keyword_and_vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                        # 前两次失败，第三次成功
                        mock_vec.side_effect = [
                            Exception("Timeout"),
                            Exception("Timeout"),
                            [MagicMock()]
                        ]
                        
                        result = await DynamicKeywordVectorSearcher.search(
                            query="测试",
                            kb_id=kb_id,
                            top_k=5
                        )
                        
                        assert mock_vec.call_count == 3
                        assert isinstance(result, list)


class TestDynamicWeightKeyWordSearcher:
    """测试动态加权关键词检索器"""

    def test_searcher_name(self):
        """测试检索器名称"""
        assert DynamicWeightKeyWordSearcher.name == SearchMethod.DYNAMIC_WEIGHTED_KEYWORD.value

    @pytest.mark.asyncio
    async def test_search_basic(self):
        """测试基本检索功能"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源"
        
        mock_chunks = [MagicMock() for _ in range(5)]
        
        with patch("data_chain.rag.dynamic_weighted_keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_search:
            mock_search.return_value = mock_chunks
            
            result = await DynamicWeightKeyWordSearcher.search(
                query=query,
                kb_id=kb_id,
                top_k=5
            )
            
            assert isinstance(result, list)
            assert len(result) == 5
            mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_error_handling(self):
        """测试错误处理"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.dynamic_weighted_keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_search:
            mock_search.side_effect = Exception("Database error")
            
            result = await DynamicWeightKeyWordSearcher.search(
                query="测试",
                kb_id=kb_id,
                top_k=5
            )
            
            assert result == []

    @pytest.mark.asyncio
    async def test_search_with_filters(self):
        """测试带过滤条件的检索"""
        kb_id = uuid.uuid4()
        doc_ids = [uuid.uuid4()]
        banned_ids = [uuid.uuid4()]
        
        with patch("data_chain.rag.dynamic_weighted_keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_search:
            mock_search.return_value = []
            
            await DynamicWeightKeyWordSearcher.search(
                query="测试",
                kb_id=kb_id,
                top_k=5,
                doc_ids=doc_ids,
                banned_ids=banned_ids
            )
            
            # 验证参数传递
            call_args = mock_search.call_args
            assert call_args[1]['doc_ids'] == doc_ids
            assert call_args[1]['banned_ids'] == banned_ids
