# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
LLM 增强检索器测试

测试范围:
- EnhancedByLLMSearcher (基于 LLM 的增强检索)
- QueryExtendSearcher (查询扩展检索)
"""

import uuid
from unittest.mock import MagicMock, patch, mock_open

import pytest

from data_chain.rag.enhanced_by_llm_searcher import EnhancedByLLMSearcher
from data_chain.rag.query_extend_searcher import QueryExtendSearcher
from data_chain.entities.enum import SearchMethod


class TestEnhancedByLLMSearcher:
    """测试基于 LLM 的增强检索器"""

    def test_searcher_name(self):
        """测试检索器名称"""
        assert EnhancedByLLMSearcher.name == SearchMethod.ENHANCED_BY_LLM.value

    @pytest.mark.asyncio
    async def test_search_basic(self):
        """测试基本检索功能"""
        kb_id = uuid.uuid4()
        query = "OpenEuler 开源操作系统"
        
        mock_chunk = MagicMock()
        mock_chunk.id = uuid.uuid4()
        mock_chunk.text = "OpenEuler 是一个开源操作系统"
        
        mock_yaml = """
CHUNK_QUERY_MATCH_PROMPT:
  zh: "Match chunk: {chunk} with question: {question}"
"""
        
        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            with patch("yaml.safe_load") as mock_yaml_load:
                mock_yaml_load.return_value = {
                    'CHUNK_QUERY_MATCH_PROMPT': {'zh': 'Match chunk: {chunk} with question: {question}'}
                }
                
                with patch("data_chain.rag.enhanced_by_llm_searcher.KnowledgeBaseManager.get_knowledge_base_by_kb_id") as mock_kb:
                    mock_kb.return_value = MagicMock(tokenizer='zh')
                    
                    with patch("data_chain.rag.enhanced_by_llm_searcher.Embedding.vectorize_embedding") as mock_embed:
                        mock_embed.return_value = [0.1] * 1024
                        
                        with patch("data_chain.rag.enhanced_by_llm_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_kw:
                            mock_kw.return_value = [mock_chunk]
                            
                            with patch("data_chain.rag.enhanced_by_llm_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                                mock_vec.return_value = []
                                
                                with patch("data_chain.rag.enhanced_by_llm_searcher.LLM") as mock_llm_class:
                                    mock_llm = MagicMock()
                                    mock_llm.max_tokens = 4096
                                    mock_llm.nostream.return_value = "YES"
                                    mock_llm_class.return_value = mock_llm
                                    
                                    result = await EnhancedByLLMSearcher.search(
                                        query=query,
                                        kb_id=kb_id,
                                        top_k=5
                                    )
                                    
                                    assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_no_match(self):
        """测试无匹配结果的情况"""
        kb_id = uuid.uuid4()
        
        mock_yaml = """
CHUNK_QUERY_MATCH_PROMPT:
  zh: "Prompt"
"""
        
        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            with patch("yaml.safe_load") as mock_yaml_load:
                mock_yaml_load.return_value = {
                    'CHUNK_QUERY_MATCH_PROMPT': {'zh': 'Prompt'}
                }
                
                with patch("data_chain.rag.enhanced_by_llm_searcher.KnowledgeBaseManager.get_knowledge_base_by_kb_id") as mock_kb:
                    mock_kb.return_value = MagicMock(tokenizer='zh')
                    
                    with patch("data_chain.rag.enhanced_by_llm_searcher.Embedding.vectorize_embedding") as mock_embed:
                        mock_embed.return_value = [0.1] * 1024
                        
                        with patch("data_chain.rag.enhanced_by_llm_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_kw:
                            mock_kw.return_value = [MagicMock(text="text")]
                            
                            with patch("data_chain.rag.enhanced_by_llm_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                                mock_vec.return_value = []
                                
                                with patch("data_chain.rag.enhanced_by_llm_searcher.LLM") as mock_llm_class:
                                    mock_llm = MagicMock()
                                    mock_llm.max_tokens = 4096
                                    mock_llm.nostream.return_value = "NO"
                                    mock_llm_class.return_value = mock_llm
                                    
                                    result = await EnhancedByLLMSearcher.search(
                                        query="测试",
                                        kb_id=kb_id,
                                        top_k=5
                                    )
                                    
                                    assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_max_retry(self):
        """测试最大重试次数"""
        kb_id = uuid.uuid4()
        
        mock_yaml = """
CHUNK_QUERY_MATCH_PROMPT:
  zh: "Prompt"
"""
        
        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            with patch("yaml.safe_load") as mock_yaml_load:
                mock_yaml_load.return_value = {
                    'CHUNK_QUERY_MATCH_PROMPT': {'zh': 'Prompt'}
                }
                
                with patch("data_chain.rag.enhanced_by_llm_searcher.KnowledgeBaseManager.get_knowledge_base_by_kb_id") as mock_kb:
                    mock_kb.return_value = MagicMock(tokenizer='zh')
                    
                    with patch("data_chain.rag.enhanced_by_llm_searcher.Embedding.vectorize_embedding") as mock_embed:
                        mock_embed.return_value = [0.1] * 1024
                        
                        with patch("data_chain.rag.enhanced_by_llm_searcher.ChunkManager.get_top_k_chunk_by_kb_id_dynamic_weighted_keyword") as mock_kw:
                            mock_kw.return_value = []
                            
                            with patch("data_chain.rag.enhanced_by_llm_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                                mock_vec.return_value = []
                                
                                with patch("data_chain.rag.enhanced_by_llm_searcher.LLM") as mock_llm_class:
                                    mock_llm = MagicMock()
                                    mock_llm_class.return_value = mock_llm
                                    
                                    result = await EnhancedByLLMSearcher.search(
                                        query="测试",
                                        kb_id=kb_id,
                                        top_k=5
                                    )
                                    
                                    assert isinstance(result, list)


class TestQueryExtendSearcher:
    """测试查询扩展检索器"""

    def test_searcher_name(self):
        """测试检索器名称"""
        assert QueryExtendSearcher.name == SearchMethod.QUERY_EXTEND.value

    @pytest.mark.asyncio
    async def test_search_basic(self):
        """测试基本检索功能"""
        kb_id = uuid.uuid4()
        query = "OpenEuler"
        
        mock_yaml = """
QUERY_EXTEND_PROMPT:
  zh: "Extend: {question}"
"""
        
        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            with patch("yaml.safe_load") as mock_yaml_load:
                mock_yaml_load.return_value = {
                    'QUERY_EXTEND_PROMPT': {'zh': 'Extend: {question}'}
                }
                
                with patch("data_chain.rag.query_extend_searcher.KnowledgeBaseManager.get_knowledge_base_by_kb_id") as mock_kb:
                    mock_kb.return_value = MagicMock(tokenizer='zh')
                    
                    with patch("data_chain.rag.query_extend_searcher.LLM") as mock_llm_class:
                        mock_llm = MagicMock()
                        mock_llm.nostream.return_value = '["OpenEuler 安装", "OpenEuler 配置"]'
                        mock_llm_class.return_value = mock_llm
                        
                        with patch("data_chain.rag.query_extend_searcher.Embedding.vectorize_embedding") as mock_embed:
                            mock_embed.return_value = [0.1] * 1024
                            
                            with patch("data_chain.rag.query_extend_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                                mock_kw.return_value = [MagicMock()]
                                
                                with patch("data_chain.rag.query_extend_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                                    mock_vec.return_value = [MagicMock()]
                                    
                                    result = await QueryExtendSearcher.search(
                                        query=query,
                                        kb_id=kb_id,
                                        top_k=5
                                    )
                                    
                                    assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_json_parse_error(self):
        """测试 JSON 解析错误处理"""
        kb_id = uuid.uuid4()
        
        mock_yaml = """
QUERY_EXTEND_PROMPT:
  zh: "Extend"
"""
        
        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            with patch("yaml.safe_load") as mock_yaml_load:
                mock_yaml_load.return_value = {
                    'QUERY_EXTEND_PROMPT': {'zh': 'Extend'}
                }
                
                with patch("data_chain.rag.query_extend_searcher.KnowledgeBaseManager.get_knowledge_base_by_kb_id") as mock_kb:
                    mock_kb.return_value = MagicMock(tokenizer='zh')
                    
                    with patch("data_chain.rag.query_extend_searcher.LLM") as mock_llm_class:
                        mock_llm = MagicMock()
                        mock_llm.nostream.return_value = "Invalid JSON"
                        mock_llm_class.return_value = mock_llm
                        
                        with patch("data_chain.rag.query_extend_searcher.Embedding.vectorize_embedding") as mock_embed:
                            mock_embed.return_value = [0.1] * 1024
                            
                            with patch("data_chain.rag.query_extend_searcher.ChunkManager.get_top_k_chunk_by_kb_id_keyword") as mock_kw:
                                mock_kw.return_value = []
                                
                                with patch("data_chain.rag.query_extend_searcher.ChunkManager.get_top_k_chunk_by_kb_id_vector") as mock_vec:
                                    mock_vec.return_value = []
                                    
                                    result = await QueryExtendSearcher.search(
                                        query="测试",
                                        kb_id=kb_id,
                                        top_k=5
                                    )
                                    
                                    # 即使 JSON 解析失败，也应该返回结果（使用原查询）
                                    assert isinstance(result, list)
