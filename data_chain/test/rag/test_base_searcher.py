# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
基础检索器测试

测试范围:
- 检索器工厂方法
- Rerank 功能
- 相关上下文获取
- 去重和分类功能
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from data_chain.rag.base_searcher import BaseSearcher
from data_chain.rag.vector_searcher import VectorSearcher
from data_chain.rag.keyword_searcher import KeyWordSearcher
from data_chain.entities.enum import RerankType, SearchMethod


class TestBaseSearcherFactory:
    """测试 BaseSearcher 工厂方法"""

    def test_find_worker_class_vector(self):
        """测试查找向量检索器"""
        worker_class = BaseSearcher.find_worker_class(SearchMethod.VECTOR.value)
        assert worker_class == VectorSearcher

    def test_find_worker_class_keyword(self):
        """测试查找关键词检索器"""
        worker_class = BaseSearcher.find_worker_class(SearchMethod.KEYWORD.value)
        assert worker_class == KeyWordSearcher

    def test_find_worker_class_invalid(self):
        """测试查找无效检索器"""
        worker_class = BaseSearcher.find_worker_class("nonexistent")
        assert worker_class is None


class TestBaseSearcherRerank:
    """测试 Rerank 功能"""

    @pytest.fixture
    def sample_chunk_entities(self):
        """创建示例 Chunk 实体"""
        entities = []
        for i in range(5):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.doc_id = uuid.uuid4()
            entity.text = f"这是第 {i} 个测试文档片段，包含 OpenEuler 关键词"
            entity.tokens = 10 + i
            entities.append(entity)
        return entities

    @pytest.mark.asyncio
    async def test_rerank_with_algorithm(self, sample_chunk_entities):
        """测试算法重排序"""
        query = "OpenEuler 开源"
        
        result = await BaseSearcher.rerank(
            sample_chunk_entities, 
            RerankType.ALGORITHM.value, 
            query
        )
        
        assert isinstance(result, list)
        assert len(result) == len(sample_chunk_entities)

    @pytest.mark.asyncio
    async def test_rerank_empty_list(self):
        """测试空列表重排序"""
        result = await BaseSearcher.rerank([], RerankType.ALGORITHM.value, "query")
        assert result == []

    @pytest.mark.asyncio
    async def test_rerank_with_model(self, sample_chunk_entities):
        """测试模型重排序"""
        with patch("data_chain.rag.base_searcher.Rerank.rerank") as mock_rerank:
            mock_rerank.return_value = [2, 1, 0, 3, 4]  # 返回重排序后的索引
            
            result = await BaseSearcher.rerank(
                sample_chunk_entities,
                RerankType.BAILIAN.value,
                "测试查询"
            )
            
            assert isinstance(result, list)


class TestBaseSearcherUniqueChunk:
    """测试 Chunk 去重功能"""

    @pytest.fixture
    def duplicate_chunks(self):
        """创建包含重复的 Chunk 实体"""
        doc_id_1 = uuid.uuid4()
        doc_id_2 = uuid.uuid4()
        
        entities = []
        # 第一个文档的多个 chunk
        for i in range(3):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.doc_id = doc_id_1
            entity.text = f"Document 1 chunk {i}"
            entities.append(entity)
        
        # 第二个文档的 chunk
        for i in range(2):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.doc_id = doc_id_2
            entity.text = f"Document 2 chunk {i}"
            entities.append(entity)
        
        return entities

    @pytest.mark.asyncio
    async def test_unique_chunk_removes_duplicates(self, duplicate_chunks):
        """测试去重功能"""
        result = await BaseSearcher.unique_chunk(duplicate_chunks)
        
        # 应该只保留每个文档的第一个 chunk
        assert len(result) == 2
        
        # 验证保留了正确的文档
        doc_ids = {chunk.doc_id for chunk in result}
        assert len(doc_ids) == 2

    @pytest.mark.asyncio
    async def test_unique_chunk_empty_list(self):
        """测试空列表去重"""
        result = await BaseSearcher.unique_chunk([])
        assert result == []


class TestBaseSearcherClassifyByDocId:
    """测试按文档 ID 分类功能"""

    @pytest.fixture
    def mixed_chunks(self):
        """创建混合的 Chunk 实体"""
        doc_id_1 = uuid.uuid4()
        doc_id_2 = uuid.uuid4()
        
        entities = []
        # 文档 1 的 chunks (打乱顺序)
        for i in [2, 0, 1]:
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.doc_id = doc_id_1
            entity.doc_name = "doc1.txt"
            entity.text = f"Chunk {i}"
            entity.global_offset = i
            entities.append(entity)
        
        # 文档 2 的 chunks
        for i in [1, 0]:
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.doc_id = doc_id_2
            entity.doc_name = "doc2.txt"
            entity.text = f"Chunk {i}"
            entity.global_offset = i
            entities.append(entity)
        
        return entities

    @pytest.mark.asyncio
    async def test_classify_by_doc_id(self, mixed_chunks):
        """测试按文档 ID 分类"""
        with patch("data_chain.rag.base_searcher.Convertor.convert_chunk_entity_to_chunk") as mock_convert:
            mock_chunk = MagicMock()
            mock_convert.return_value = mock_chunk
            
            result = await BaseSearcher.classify_by_doc_id(mixed_chunks)
            
            assert isinstance(result, list)
            assert len(result) == 2  # 两个文档

    @pytest.mark.asyncio
    async def test_classify_empty_list(self):
        """测试空列表分类"""
        result = await BaseSearcher.classify_by_doc_id([])
        assert result == []


class TestBaseSearcherRelatedSurroundChunk:
    """测试相关上下文获取功能"""

    @pytest.fixture
    def center_chunk(self):
        """创建中心 chunk"""
        entity = MagicMock()
        entity.id = uuid.uuid4()
        entity.doc_id = uuid.uuid4()
        entity.global_offset = 5
        entity.tokens = 10
        return entity

    @pytest.fixture
    def surrounding_chunks(self, center_chunk):
        """创建周围 chunks"""
        entities = []
        for i in range(10):
            if i == 5:
                continue
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.doc_id = center_chunk.doc_id
            entity.global_offset = i
            entity.tokens = 10
            entities.append(entity)
        return entities

    @pytest.mark.asyncio
    async def test_related_surround_chunk(self, center_chunk, surrounding_chunks):
        """测试获取相关上下文"""
        all_chunks = [center_chunk] + surrounding_chunks
        
        with patch("data_chain.rag.base_searcher.ChunkManager.fetch_surrounding_chunk_by_doc_id_and_global_offset") as mock_fetch:
            mock_fetch.return_value = all_chunks
            
            result = await BaseSearcher.related_surround_chunk(center_chunk, tokens_limit=50)
            
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_related_surround_chunk_with_banned_ids(self, center_chunk, surrounding_chunks):
        """测试带禁用 ID 的上下文获取"""
        all_chunks = [center_chunk] + surrounding_chunks
        banned_ids = [surrounding_chunks[0].id]
        
        with patch("data_chain.rag.base_searcher.ChunkManager.fetch_surrounding_chunk_by_doc_id_and_global_offset") as mock_fetch:
            mock_fetch.return_value = all_chunks
            
            result = await BaseSearcher.related_surround_chunk(
                center_chunk, 
                tokens_limit=50,
                banned_ids=banned_ids
            )
            
            assert isinstance(result, list)


class TestBaseSearcherIntegration:
    """测试 BaseSearcher 集成"""

    @pytest.mark.asyncio
    async def test_search_with_valid_method(self):
        """测试使用有效方法进行搜索"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 测试"
        
        with patch("data_chain.rag.vector_searcher.VectorSearcher.search") as mock_search:
            mock_search.return_value = []
            
            result = await BaseSearcher.search(
                SearchMethod.VECTOR.value,
                kb_id,
                query,
                top_k=5
            )
            
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_with_invalid_method(self):
        """测试使用无效方法时的错误处理"""
        with pytest.raises(Exception) as exc_info:
            await BaseSearcher.search(
                "invalid_method",
                uuid.uuid4(),
                "query"
            )
        
        assert "检索器不存在" in str(exc_info.value)
