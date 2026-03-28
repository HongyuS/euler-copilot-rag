# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
RAG 检索性能测试

测试范围:
- 向量检索性能
- 关键词检索性能
- 重排序性能
- 端到端检索性能
"""

import time
import uuid
from unittest.mock import MagicMock, patch

import pytest
import numpy as np

from data_chain.rag.base_searcher import BaseSearcher
from data_chain.rag.vector_searcher import VectorSearcher
from data_chain.rag.keyword_searcher import KeyWordSearcher
from data_chain.rerank.rerank import Rerank


class TestVectorSearcherPerformance:
    """向量检索器性能测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_vector_search_latency(self):
        """测试向量检索延迟"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源操作系统性能测试"
        
        mock_chunks = []
        for i in range(10):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.text = f"测试文档片段 {i}"
            mock_chunks.append(entity)
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                mock_get.return_value = mock_chunks
                
                # 预热
                await VectorSearcher.search(query=query, kb_id=kb_id, top_k=10)
                
                # 实际测试
                iterations = 50
                times = []
                for _ in range(iterations):
                    start = time.time()
                    await VectorSearcher.search(query=query, kb_id=kb_id, top_k=10)
                    times.append(time.time() - start)
                
                avg_time = np.mean(times) * 1000  # ms
                p95_time = np.percentile(times, 95) * 1000  # ms
                
                print(f"\n向量检索平均延迟: {avg_time:.2f}ms")
                print(f"向量检索 P95 延迟: {p95_time:.2f}ms")
                
                assert avg_time < 500  # 平均延迟应该小于 500ms
                assert p95_time < 1000  # P95 延迟应该小于 1000ms

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_vector_search_different_topk(self):
        """测试不同 top_k 对性能的影响"""
        kb_id = uuid.uuid4()
        query = "性能测试"
        
        top_k_values = [1, 5, 10, 50, 100]
        results = {}
        
        with patch("data_chain.rag.vector_searcher.Embedding.vectorize_embedding") as mock_embed:
            mock_embed.return_value = [0.1] * 1024
            
            for top_k in top_k_values:
                mock_chunks = [MagicMock() for _ in range(top_k)]
                
                with patch("data_chain.rag.vector_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_get:
                    mock_get.return_value = mock_chunks
                    
                    start = time.time()
                    await VectorSearcher.search(query=query, kb_id=kb_id, top_k=top_k)
                    elapsed = (time.time() - start) * 1000
                    
                    results[top_k] = elapsed
                    print(f"\ntop_k={top_k}: {elapsed:.2f}ms")
        
        # 验证性能随 top_k 增长的趋势
        assert results[100] >= results[1]  # 大 top_k 应该更慢或相当


class TestKeywordSearcherPerformance:
    """关键词检索器性能测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_keyword_search_latency(self):
        """测试关键词检索延迟"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源"
        
        mock_chunks = [MagicMock() for _ in range(10)]
        
        with patch("data_chain.rag.keyword_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_get:
            mock_get.return_value = mock_chunks
            
            iterations = 50
            times = []
            for _ in range(iterations):
                start = time.time()
                await KeyWordSearcher.search(query=query, kb_id=kb_id, top_k=10)
                times.append(time.time() - start)
            
            avg_time = np.mean(times) * 1000
            p95_time = np.percentile(times, 95) * 1000
            
            print(f"\n关键词检索平均延迟: {avg_time:.2f}ms")
            print(f"关键词检索 P95 延迟: {p95_time:.2f}ms")
            
            assert avg_time < 200


class TestRerankPerformance:
    """重排序性能测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_rerank_latency(self, mock_config):
        """测试重排序延迟"""
        mock_config['RERANK_TYPE'] = "algorithm"  # 使用算法重排序
        
        query = "测试查询"
        documents = [f"文档内容 {i}" for i in range(100)]
        
        with patch("data_chain.rag.base_searcher.Rerank.rerank") as mock_rerank:
            mock_rerank.return_value = list(range(len(documents)))
            
            from data_chain.stores.database.database import ChunkEntity
            
            mock_chunks = []
            for i, doc in enumerate(documents):
                entity = MagicMock(spec=ChunkEntity)
                entity.id = uuid.uuid4()
                entity.text = doc
                mock_chunks.append(entity)
            
            iterations = 100
            times = []
            for _ in range(iterations):
                start = time.time()
                await BaseSearcher.rerank(mock_chunks, "algorithm", query)
                times.append(time.time() - start)
            
            avg_time = np.mean(times) * 1000
            
            print(f"\n重排序平均延迟: {avg_time:.2f}ms")
            
            assert avg_time < 100


class TestBaseSearcherPerformance:
    """基础检索器性能测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_classify_by_doc_id_performance(self):
        """测试分类功能性能"""
        # 创建大量 chunks
        chunks = []
        for doc_idx in range(100):  # 100 个文档
            doc_id = uuid.uuid4()
            for chunk_idx in range(10):  # 每个文档 10 个 chunks
                entity = MagicMock()
                entity.id = uuid.uuid4()
                entity.doc_id = doc_id
                entity.doc_name = f"doc_{doc_idx}.txt"
                entity.text = f"内容 {chunk_idx}"
                entity.global_offset = chunk_idx
                chunks.append(entity)
        
        with patch("data_chain.rag.base_searcher.Convertor.convert_chunk_entity_to_chunk") as mock_convert:
            mock_convert.return_value = MagicMock()
            
            start = time.time()
            result = await BaseSearcher.classify_by_doc_id(chunks)
            elapsed = (time.time() - start) * 1000
            
            print(f"\n分类 1000 个 chunks 时间: {elapsed:.2f}ms")
            
            assert len(result) == 100
            assert elapsed < 500

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_unique_chunk_performance(self):
        """测试去重功能性能"""
        # 创建大量重复的 chunks
        chunks = []
        for i in range(1000):
            entity = MagicMock()
            entity.id = uuid.uuid4()
            entity.doc_id = uuid.uuid4() if i % 10 == 0 else chunks[i-1].doc_id
            entity.text = f"内容 {i}"
            chunks.append(entity)
        
        start = time.time()
        result = await BaseSearcher.unique_chunk(chunks)
        elapsed = (time.time() - start) * 1000
        
        print(f"\n去重 1000 个 chunks 时间: {elapsed:.2f}ms")
        
        assert elapsed < 100


class TestEndToEndPerformance:
    """端到端性能测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_search_pipeline(self):
        """测试完整搜索流程性能"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源操作系统"
        
        mock_chunks = [MagicMock() for _ in range(10)]
        
        with patch("data_chain.rag.base_searcher.BaseSearcher.search") as mock_search:
            mock_search.return_value = mock_chunks
            
            with patch("data_chain.rag.base_searcher.BaseSearcher.rerank") as mock_rerank:
                mock_rerank.return_value = mock_chunks
                
                start = time.time()
                
                # 执行完整流程
                chunks = await BaseSearcher.search("vector", kb_id, query, top_k=10)
                reranked = await BaseSearcher.rerank(chunks, "algorithm", query)
                classified = await BaseSearcher.classify_by_doc_id(reranked)
                
                elapsed = (time.time() - start) * 1000
                
                print(f"\n完整搜索流程时间: {elapsed:.2f}ms")
                
                assert elapsed < 2000


class TestRAGScalability:
    """RAG 可扩展性测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_rerank_scalability(self, mock_config):
        """测试重排序的可扩展性"""
        mock_config['RERANK_TYPE'] = "algorithm"
        
        query = "测试查询"
        
        sizes = [10, 50, 100, 500]
        results = {}
        
        for size in sizes:
            mock_chunks = []
            for i in range(size):
                entity = MagicMock()
                entity.id = uuid.uuid4()
                entity.text = f"文档内容 {i} " * 10
                mock_chunks.append(entity)
            
            with patch("data_chain.rag.base_searcher.Rerank.rerank") as mock_rerank:
                mock_rerank.return_value = list(range(size))
                
                start = time.time()
                await BaseSearcher.rerank(mock_chunks, "bailian", query)
                elapsed = (time.time() - start) * 1000
                
                results[size] = elapsed
                print(f"\n重排序 {size} 个文档: {elapsed:.2f}ms")
        
        # 验证可扩展性（增长应该是次线性的或合理的）
        ratio = results[500] / results[10]
        assert ratio < 100  # 50 倍数据不应该超过 100 倍时间
