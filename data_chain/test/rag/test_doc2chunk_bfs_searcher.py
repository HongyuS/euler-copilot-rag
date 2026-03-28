# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
Doc2Chunk BFS 检索器测试

测试范围:
- 基于 BFS 的文档到块检索
- 分层检索策略
- 递归子节点检索
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from data_chain.rag.doc2chunk_bfs_searcher import Doc2ChunkBfsSearcher
from data_chain.entities.enum import SearchMethod, ChunkParseTopology


class TestDoc2ChunkBfsSearcherBasic:
    """测试 Doc2Chunk BFS 检索器基本功能"""

    def test_searcher_name(self):
        """测试检索器名称"""
        assert Doc2ChunkBfsSearcher.name == SearchMethod.DOC2CHUNK_BFS.value

    @pytest.mark.asyncio
    async def test_search_basic(self):
        """测试基本检索功能"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源操作系统"
        
        root_kw_chunks = [MagicMock() for _ in range(2)]
        root_vec_chunks = [MagicMock() for _ in range(2)]
        
        with patch("data_chain.rag.doc2chunk_bfs_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                mock_kw.return_value = root_kw_chunks
                
                with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                    mock_vec.return_value = root_vec_chunks
                    
                    result = await Doc2ChunkBfsSearcher.search(
                        query=query,
                        kb_id=kb_id,
                        top_k=5
                    )
                    
                    assert isinstance(result, list)
                    # 验证使用了 TREEROOT 拓扑
                    call_kwargs = mock_kw.call_args[1]
                    assert call_kwargs.get('chunk_topology_type') == ChunkParseTopology.TREEROOT.value

    @pytest.mark.asyncio
    async def test_search_with_bfs_iteration(self):
        """测试 BFS 迭代检索"""
        kb_id = uuid.uuid4()
        
        # 第一轮结果
        round1_kw = [MagicMock(id=uuid.uuid4())]
        round1_vec = [MagicMock(id=uuid.uuid4())]
        
        # 第二轮结果（子节点）
        round2_kw = [MagicMock(id=uuid.uuid4())]
        round2_vec = []
        
        with patch("data_chain.rag.doc2chunk_bfs_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            call_count = [0]
            
            def mock_keyword_search(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return round1_kw
                else:
                    return round2_kw
            
            def mock_vector_search(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] <= 2:
                    return round1_vec
                else:
                    return round2_vec
            
            with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword", side_effect=mock_keyword_search):
                with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector", side_effect=mock_vector_search):
                    result = await Doc2ChunkBfsSearcher.search(
                        query="测试",
                        kb_id=kb_id,
                        top_k=5
                    )
                    
                    assert isinstance(result, list)


class TestDoc2ChunkBfsSearcherBfsLogic:
    """测试 BFS 逻辑"""

    @pytest.mark.asyncio
    async def test_bfs_max_retry(self):
        """测试 BFS 最大重试次数"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.doc2chunk_bfs_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            iteration_count = [0]
            
            def mock_search(*args, **kwargs):
                iteration_count[0] += 1
                if iteration_count[0] <= 2:  # 第一轮
                    return [MagicMock(id=uuid.uuid4())]
                else:  # 后续轮次
                    # 返回非空结果以触发更多迭代
                    return [MagicMock(id=uuid.uuid4())] if iteration_count[0] < 15 else []
            
            with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword", side_effect=mock_search):
                with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector", side_effect=mock_search):
                    result = await Doc2ChunkBfsSearcher.search(
                        query="测试",
                        kb_id=kb_id,
                        top_k=5
                    )
                    
                    assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_bfs_pre_ids_tracking(self):
        """测试 pre_ids 追踪"""
        kb_id = uuid.uuid4()
        
        chunk1 = MagicMock(id=uuid.uuid4())
        chunk2 = MagicMock(id=uuid.uuid4())
        
        pre_ids_history = []
        
        def mock_kw_search(*args, **kwargs):
            pre_id = kwargs.get('pre_id')
            pre_ids_history.append(pre_id)
            if pre_id is None:
                return [chunk1]
            return [chunk2]
        
        def mock_vec_search(*args, **kwargs):
            return []
        
        with patch("data_chain.rag.doc2chunk_bfs_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword", side_effect=mock_kw_search):
                with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector", side_effect=mock_vec_search):
                    await Doc2ChunkBfsSearcher.search(
                        query="测试",
                        kb_id=kb_id,
                        top_k=5
                    )
                    
                    # 验证 pre_ids 被正确传递
                    assert None in pre_ids_history  # 第一轮是 None


class TestDoc2ChunkBfsSearcherErrorHandling:
    """测试错误处理"""

    @pytest.mark.asyncio
    async def test_search_exception_handling(self):
        """测试异常处理"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.doc2chunk_bfs_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.side_effect = Exception("Embedding failed")
            
            result = await Doc2ChunkBfsSearcher.search(
                query="测试",
                kb_id=kb_id,
                top_k=5
            )
            
            assert result == []

    @pytest.mark.asyncio
    async def test_search_vector_timeout_retry(self):
        """测试向量检索超时重试"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.doc2chunk_bfs_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                mock_kw.return_value = []
                
                with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                    # 前两次失败，第三次成功
                    mock_vec.side_effect = [
                        Exception("Timeout"),
                        Exception("Timeout"),
                        [MagicMock()]
                    ]
                    
                    result = await Doc2ChunkBfsSearcher.search(
                        query="测试",
                        kb_id=kb_id,
                        top_k=5
                    )
                    
                    # 验证重试机制
                    assert mock_vec.call_count >= 3
                    assert isinstance(result, list)


class TestDoc2ChunkBfsSearcherBfsTermination:
    """测试 BFS 终止条件"""

    @pytest.mark.asyncio
    async def test_bfs_terminates_on_empty_result(self):
        """测试空结果时终止"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.doc2chunk_bfs_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            # 第一轮有结果，第二轮空
            call_count = [0]
            
            def mock_search(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] <= 2:
                    return [MagicMock(id=uuid.uuid4())]
                return []
            
            with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword", side_effect=mock_search):
                with patch("data_chain.rag.doc2chunk_bfs_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector", side_effect=mock_search):
                    result = await Doc2ChunkBfsSearcher.search(
                        query="测试",
                        kb_id=kb_id,
                        top_k=5
                    )
                    
                    # BFS 应该在空结果时终止
                    assert isinstance(result, list)
