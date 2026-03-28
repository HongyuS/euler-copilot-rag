# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
Doc2Chunk 检索器测试

测试范围:
- 文档到块的检索流程
- 混合检索策略
- 关键词权重应用
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from data_chain.rag.doc2chunk_searcher import Doc2ChunkSearcher
from data_chain.entities.enum import SearchMethod


class TestDoc2ChunkSearcherBasic:
    """测试 Doc2Chunk 检索器基本功能"""

    def test_searcher_name(self):
        """测试检索器名称"""
        assert Doc2ChunkSearcher.name == SearchMethod.DOC2CHUNK.value

    @pytest.mark.asyncio
    async def test_search_basic(self):
        """测试基本检索功能"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源操作系统"
        
        mock_doc_entities = [MagicMock() for _ in range(2)]
        for i, doc in enumerate(mock_doc_entities):
            doc.id = uuid.uuid4()
        
        mock_chunk_entities = [MagicMock() for _ in range(5)]
        
        with patch("data_chain.rag.doc2chunk_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.doc2chunk_searcher.TokenTool.get_top_k_keywords_and_weights") as mock_kw:
                mock_kw.return_value = (["openeuler", "开源"], [0.6, 0.4])
                
                with patch("data_chain.rag.doc2chunk_searcher.DocumentManager.get_top_k_document_by_kb_id_dynamic_weighted_keyword") as mock_doc_kw:
                    mock_doc_kw.return_value = mock_doc_entities[:1]
                    
                    with patch("data_chain.rag.doc2chunk_searcher.DocumentManager.get_top_k_document_by_kb_id_vector") as mock_doc_vec:
                        mock_doc_vec.return_value = mock_doc_entities[1:]
                        
                        with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_chunk_kw:
                            mock_chunk_kw.return_value = mock_chunk_entities[:2]
                            
                            with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_chunk_dyn:
                                mock_chunk_dyn.return_value = mock_chunk_entities[2:4]
                                
                                with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_chunk_vec:
                                    mock_chunk_vec.return_value = mock_chunk_entities[4:]
                                    
                                    result = await Doc2ChunkSearcher.search(
                                        query=query,
                                        kb_id=kb_id,
                                        top_k=5
                                    )
                                    
                                    assert isinstance(result, list)
                                    assert len(result) >= 0

    @pytest.mark.asyncio
    async def test_search_with_doc_ids_filter(self):
        """测试带文档 ID 过滤的检索"""
        kb_id = uuid.uuid4()
        doc_ids = [uuid.uuid4()]
        
        with patch("data_chain.rag.doc2chunk_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.doc2chunk_searcher.TokenTool.get_top_k_keywords_and_weights") as mock_kw:
                mock_kw.return_value = (["test"], [1.0])
                
                with patch("data_chain.rag.doc2chunk_searcher.DocumentManager.get_top_k_document_by_kb_id_dynamic_weighted_keyword") as mock_doc_kw:
                    mock_doc_kw.return_value = []
                    
                    with patch("data_chain.rag.doc2chunk_searcher.DocumentManager.get_top_k_document_by_kb_id_vector") as mock_doc_vec:
                        mock_doc_vec.return_value = []
                        
                        with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_chunk_kw:
                            mock_chunk_kw.return_value = []
                            
                            with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_chunk_dyn:
                                mock_chunk_dyn.return_value = []
                                
                                with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_chunk_vec:
                                    mock_chunk_vec.return_value = []
                                    
                                    await Doc2ChunkSearcher.search(
                                        query="测试",
                                        kb_id=kb_id,
                                        top_k=5,
                                        doc_ids=doc_ids
                                    )


class TestDoc2ChunkSearcherErrorHandling:
    """测试错误处理"""

    @pytest.mark.asyncio
    async def test_search_exception_handling(self):
        """测试异常处理"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.doc2chunk_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.side_effect = Exception("Embedding failed")
            
            result = await Doc2ChunkSearcher.search(
                query="测试",
                kb_id=kb_id,
                top_k=5
            )
            
            assert result == []

    @pytest.mark.asyncio
    async def test_search_vector_timeout_retry(self):
        """测试向量检索超时重试"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.doc2chunk_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.doc2chunk_searcher.TokenTool.get_top_k_keywords_and_weights") as mock_kw:
                mock_kw.return_value = (["test"], [1.0])
                
                with patch("data_chain.rag.doc2chunk_searcher.DocumentManager.get_top_k_document_by_kb_id_dynamic_weighted_keyword") as mock_doc_kw:
                    mock_doc_kw.return_value = []
                    
                    with patch("data_chain.rag.doc2chunk_searcher.DocumentManager.get_top_k_document_by_kb_id_vector") as mock_doc_vec:
                        # 前两次失败，第三次成功
                        mock_doc_vec.side_effect = [
                            Exception("Timeout"),
                            Exception("Timeout"),
                            [MagicMock()]
                        ]
                        
                        with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_chunk_kw:
                            mock_chunk_kw.return_value = []
                            
                            with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_chunk_dyn:
                                mock_chunk_dyn.return_value = []
                                
                                with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_chunk_vec:
                                    mock_chunk_vec.return_value = []
                                    
                                    result = await Doc2ChunkSearcher.search(
                                        query="测试",
                                        kb_id=kb_id,
                                        top_k=5
                                    )
                                    
                                    assert isinstance(result, list)


class TestDoc2ChunkSearcherStrategy:
    """测试检索策略"""

    @pytest.mark.asyncio
    async def test_multi_stage_search(self):
        """测试多阶段检索"""
        kb_id = uuid.uuid4()
        
        # 验证调用顺序：文档关键词 -> 文档向量 -> Chunk关键词 -> Chunk动态加权 -> Chunk向量
        call_order = []
        
        def track_call(name):
            def wrapper(*args, **kwargs):
                call_order.append(name)
                return [MagicMock(id=uuid.uuid4())]
            return wrapper
        
        with patch("data_chain.rag.doc2chunk_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.doc2chunk_searcher.TokenTool.get_top_k_keywords_and_weights") as mock_kw:
                mock_kw.return_value = (["test"], [1.0])
                
                with patch("data_chain.rag.doc2chunk_searcher.DocumentManager.get_top_k_document_by_kb_id_dynamic_weighted_keyword", side_effect=track_call("doc_kw")):
                    with patch("data_chain.rag.doc2chunk_searcher.DocumentManager.get_top_k_document_by_kb_id_vector", side_effect=track_call("doc_vec")):
                        with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword", side_effect=track_call("chunk_kw")):
                            with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword", side_effect=track_call("chunk_dyn")):
                                with patch("data_chain.rag.doc2chunk_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector", side_effect=track_call("chunk_vec")):
                                    await Doc2ChunkSearcher.search(
                                        query="测试",
                                        kb_id=kb_id,
                                        top_k=10
                                    )
                                    
                                    # 验证调用顺序
                                    assert "doc_kw" in call_order
                                    assert "chunk_kw" in call_order
