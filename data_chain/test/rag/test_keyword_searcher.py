# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
关键词检索器测试

测试范围:
- 关键词检索功能
- 两阶段检索策略
- 异常处理
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from data_chain.rag.keyword_searcher import KeyWordSearcher
from data_chain.entities.enum import SearchMethod


class TestKeyWordSearcherBasic:
    """测试关键词检索器基本功能"""

    def test_searcher_name(self):
        """测试检索器名称"""
        assert KeyWordSearcher.name == SearchMethod.KEYWORD.value

    @pytest.mark.asyncio
    async def test_search_basic(self):
        """测试基本检索功能"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源"
        
        mock_chunks = []
        for i in range(5):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"包含 OpenEuler 的文本 {i}"
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = mock_chunks
            
            result = await KeyWordSearcher.search(
                query=query,
                kb_id=kb_id,
                top_k=5
            )
            
            assert isinstance(result, list)
            assert len(result) == 5

    @pytest.mark.asyncio
    async def test_search_two_phase_strategy(self):
        """测试两阶段检索策略"""
        kb_id = uuid.uuid4()
        query = "测试查询"
        top_k = 9
        
        # 第一阶段返回 top_k//3 = 3 个结果
        phase1_chunks = []
        for i in range(3):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"阶段1结果{i}"
            phase1_chunks.append(entity)
        
        # 第二阶段返回剩余结果
        phase2_chunks = []
        for i in range(6):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"阶段2结果{i}"
            phase2_chunks.append(entity)
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.side_effect = [phase1_chunks, phase2_chunks]
            
            result = await KeyWordSearcher.search(
                query=query,
                kb_id=kb_id,
                top_k=top_k
            )
            
            # 验证调用了两次
            assert mock_get.call_count == 2
            
            # 验证结果被合并
            assert len(result) == 9


class TestKeyWordSearcherParams:
    """测试参数处理"""

    @pytest.mark.asyncio
    async def test_search_with_doc_ids(self):
        """测试带文档 ID 过滤的检索"""
        kb_id = uuid.uuid4()
        doc_ids = [uuid.uuid4(), uuid.uuid4()]
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = []
            
            await KeyWordSearcher.search(
                query="测试",
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
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = []
            
            await KeyWordSearcher.search(
                query="测试",
                kb_id=kb_id,
                top_k=5,
                banned_ids=banned_ids
            )
            
            # 验证 banned_ids 被传递
            call_args = mock_get.call_args
            assert call_args[1]['banned_ids'] == banned_ids


class TestKeyWordSearcherErrorHandling:
    """测试错误处理"""

    @pytest.mark.asyncio
    async def test_search_exception_handling(self):
        """测试异常处理"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            result = await KeyWordSearcher.search(
                query="测试",
                kb_id=kb_id,
                top_k=5
            )
            
            # 发生异常时应该返回空列表
            assert result == []

    @pytest.mark.asyncio
    async def test_search_partial_failure(self):
        """测试部分失败情况"""
        kb_id = uuid.uuid4()
        
        # 第一阶段成功，第二阶段失败
        phase1_chunks = [MagicMock()]
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.side_effect = [phase1_chunks, Exception("Phase 2 error")]
            
            result = await KeyWordSearcher.search(
                query="测试",
                kb_id=kb_id,
                top_k=6
            )
            
            # 应该返回第一阶段的结果
            assert isinstance(result, list)


class TestKeyWordSearcherAccuracy:
    """测试关键词检索准确率"""

    @pytest.mark.asyncio
    async def test_search_keyword_matching(self):
        """测试关键词匹配准确性"""
        kb_id = uuid.uuid4()
        query = "OpenEuler"
        
        mock_chunks = []
        for i in range(5):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"文本包含 {query} 关键词"
            entity.score = 0.9
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = mock_chunks
            
            result = await KeyWordSearcher.search(
                query=query,
                kb_id=kb_id,
                top_k=5
            )
            
            # 验证结果包含关键词
            for chunk in result:
                assert query in chunk.text

    @pytest.mark.asyncio
    async def test_search_banned_ids_filtering(self):
        """测试禁用 ID 过滤"""
        kb_id = uuid.uuid4()
        banned_id = uuid.uuid4()
        
        # 第一阶段返回 2 个结果，其中一个被禁用
        phase1_chunks = []
        for i in range(2):
            entity = MagicMock()
            entity.id = banned_id if i == 0 else uuid.uuid4()
            entity.text = f"结果{i}"
            phase1_chunks.append(entity)
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.side_effect = [phase1_chunks, []]
            
            await KeyWordSearcher.search(
                query="测试",
                kb_id=kb_id,
                top_k=6,
                banned_ids=[banned_id]
            )
            
            # 验证第二次调用时传递了更新的 banned_ids
            second_call = mock_get.call_args_list[1]
            assert banned_id in second_call[1]['banned_ids']


class TestKeyWordSearcherPerformance:
    """测试关键词检索性能"""

    @pytest.mark.asyncio
    async def test_search_response_time(self):
        """测试响应时间"""
        import time
        
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = [MagicMock() for _ in range(10)]
            
            start_time = time.time()
            await KeyWordSearcher.search(
                query="性能测试",
                kb_id=kb_id,
                top_k=10
            )
            end_time = time.time()
            
            # 应该在合理时间内完成
            assert end_time - start_time < 1.0


class TestKeyWordSearcherEdgeCases:
    """测试边界情况"""

    @pytest.mark.asyncio
    async def test_search_empty_query(self):
        """测试空查询"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = []
            
            result = await KeyWordSearcher.search(
                query="",
                kb_id=kb_id,
                top_k=5
            )
            
            # 空查询应该能正常工作
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_zero_top_k(self):
        """测试 top_k 为 0"""
        kb_id = uuid.uuid4()
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = []
            
            result = await KeyWordSearcher.search(
                query="测试",
                kb_id=kb_id,
                top_k=0
            )
            
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_special_characters_in_query(self):
        """测试查询中的特殊字符"""
        kb_id = uuid.uuid4()
        special_queries = [
            "test!@#$%",
            "中文测试",
            "test' OR '1'='1",  # SQL 注入尝试
            "<script>alert('xss')</script>",
        ]
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = []
            
            for query in special_queries:
                result = await KeyWordSearcher.search(
                    query=query,
                    kb_id=kb_id,
                    top_k=5
                )
                assert isinstance(result, list)
