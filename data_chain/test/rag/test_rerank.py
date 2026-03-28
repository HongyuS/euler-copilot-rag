# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
重排序模块测试

测试范围:
- 数据组装
- 响应解析
- Rerank API 调用
- 不同 Rerank 类型支持
"""

from unittest.mock import MagicMock, patch

import pytest

from data_chain.rerank.rerank import Rerank
from data_chain.entities.enum import RerankType


class TestRerankDataAssembly:
    """测试数据组装功能"""

    @pytest.mark.asyncio
    async def test_assemable_data_bailian(self, mock_config):
        """测试 Bailian 类型数据组装"""
        mock_config['RERANK_TYPE'] = RerankType.BAILIAN.value
        
        query = "测试查询"
        documents = ["文档1", "文档2", "文档3"]
        top_k = 2
        
        data = await Rerank.assemable_data(query, documents, top_k)
        
        assert "model" in data
        assert "input" in data
        assert data["input"]["query"] == query
        assert data["input"]["documents"] == documents
        assert data["parameters"]["top_n"] == top_k

    @pytest.mark.asyncio
    async def test_assemable_data_guijiliudong(self, mock_config):
        """测试 GUIJILIUDONG 类型数据组装"""
        mock_config['RERANK_TYPE'] = RerankType.GUIJILIUDONG.value
        
        query = "测试查询"
        documents = ["文档1", "文档2"]
        
        data = await Rerank.assemable_data(query, documents)
        
        assert "model" in data
        assert data["query"] == query
        assert data["documents"] == documents

    @pytest.mark.asyncio
    async def test_assemable_data_vllm(self, mock_config):
        """测试 VLLM 类型数据组装"""
        mock_config['RERANK_TYPE'] = RerankType.VLLM.value
        
        query = "测试查询"
        documents = ["文档1", "文档2"]
        
        data = await Rerank.assemable_data(query, documents)
        
        assert "model" in data
        assert data["text_1"] == query
        assert data["text_2"] == documents

    @pytest.mark.asyncio
    async def test_assemable_data_ascend(self, mock_config):
        """测试 Ascend 类型数据组装"""
        mock_config['RERANK_TYPE'] = RerankType.ASCEND.value
        
        query = "测试查询"
        documents = ["文档1", "文档2"]
        
        data = await Rerank.assemable_data(query, documents)
        
        assert "query" in data
        assert "texts" in data
        assert data["query"] == query
        assert data["texts"] == documents


class TestRerankResponseParsing:
    """测试响应解析功能"""

    @pytest.mark.asyncio
    async def test_parse_response_bailian(self, mock_config):
        """测试 Bailian 响应解析"""
        mock_config['RERANK_TYPE'] = RerankType.BAILIAN.value
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "output": {
                "results": [
                    {"index": 2, "score": 0.9},
                    {"index": 0, "score": 0.8},
                    {"index": 1, "score": 0.7}
                ]
            }
        }
        
        result = await Rerank.parse_response(mock_response, top_k=3)
        
        assert isinstance(result, list)
        assert result == [2, 0, 1]

    @pytest.mark.asyncio
    async def test_parse_response_guijiliudong(self, mock_config):
        """测试 GUIJILIUDONG 响应解析"""
        mock_config['RERANK_TYPE'] = RerankType.GUIJILIUDONG.value
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"index": 1, "score": 0.95},
                {"index": 0, "score": 0.85}
            ]
        }
        
        result = await Rerank.parse_response(mock_response, top_k=2)
        
        assert isinstance(result, list)
        assert result == [1, 0]

    @pytest.mark.asyncio
    async def test_parse_response_vllm(self, mock_config):
        """测试 VLLM 响应解析"""
        mock_config['RERANK_TYPE'] = RerankType.VLLM.value
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"index": 0, "score": 0.9},
                {"index": 2, "score": 0.8}
            ]
        }
        
        result = await Rerank.parse_response(mock_response, top_k=2)
        
        assert isinstance(result, list)
        assert result == [0, 2]

    @pytest.mark.asyncio
    async def test_parse_response_ascend(self, mock_config):
        """测试 Ascend 响应解析"""
        mock_config['RERANK_TYPE'] = RerankType.ASCEND.value
        
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"index": 2, "score": 0.99},
            {"index": 1, "score": 0.88}
        ]
        
        result = await Rerank.parse_response(mock_response, top_k=2)
        
        assert isinstance(result, list)
        assert result == [2, 1]

    @pytest.mark.asyncio
    async def test_parse_response_top_k_limit(self, mock_config):
        """测试 top_k 限制"""
        mock_config['RERANK_TYPE'] = RerankType.BAILIAN.value
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "output": {
                "results": [
                    {"index": 0},
                    {"index": 1},
                    {"index": 2},
                    {"index": 3},
                    {"index": 4}
                ]
            }
        }
        
        result = await Rerank.parse_response(mock_response, top_k=3)
        
        # 应该只返回 top_k 个结果
        assert len(result) == 3


class TestRerankMainFunction:
    """测试主重排序功能"""

    @pytest.mark.asyncio
    async def test_rerank_success(self, mock_config):
        """测试成功重排序"""
        mock_config['RERANK_TYPE'] = RerankType.BAILIAN.value
        
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "output": {
                    "results": [
                        {"index": 1},
                        {"index": 0},
                        {"index": 2}
                    ]
                }
            }
            mock_post.return_value = mock_response
            
            result = await Rerank.rerank(
                query="测试查询",
                documents=["文档A", "文档B", "文档C"],
                top_k=3
            )
            
            assert isinstance(result, list)
            assert result == [1, 0, 2]

    @pytest.mark.asyncio
    async def test_rerank_documents_less_than_top_k(self, mock_config):
        """测试文档数少于 top_k 的情况"""
        result = await Rerank.rerank(
            query="测试",
            documents=["文档1", "文档2"],
            top_k=5
        )
        
        # 应该返回所有文档的索引
        assert isinstance(result, list)
        assert result == [0, 1]

    @pytest.mark.asyncio
    async def test_rerank_api_failure(self, mock_config):
        """测试 API 失败处理"""
        mock_config['RERANK_TYPE'] = RerankType.BAILIAN.value
        
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            result = await Rerank.rerank(
                query="测试查询",
                documents=["文档1", "文档2", "文档3"],
                top_k=2
            )
            
            # 失败时返回默认顺序
            assert isinstance(result, list)
            assert result == [0, 1]

    @pytest.mark.asyncio
    async def test_rerank_empty_documents(self, mock_config):
        """测试空文档列表"""
        result = await Rerank.rerank(
            query="测试",
            documents=[],
            top_k=5
        )
        
        assert result == []

    @pytest.mark.asyncio
    async def test_rerank_single_document(self, mock_config):
        """测试单个文档"""
        result = await Rerank.rerank(
            query="测试",
            documents=["只有一个文档"],
            top_k=5
        )
        
        assert result == [0]


class TestRerankConfiguration:
    """测试配置处理"""

    @pytest.mark.asyncio
    async def test_rerank_uses_config_api_key(self, mock_config):
        """测试使用配置中的 API Key"""
        mock_config['RERANK_TYPE'] = RerankType.BAILIAN.value
        mock_config['RERANK_API_KEY'] = 'test-api-key-123'
        mock_config['RERANK_ENDPOINT'] = 'https://api.test.com/rerank'
        
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "output": {"results": [{"index": 0}]}
            }
            mock_post.return_value = mock_response
            
            await Rerank.rerank(
                query="测试",
                documents=["文档"],
                top_k=1
            )
            
            # 验证使用了正确的 headers
            call_args = mock_post.call_args
            headers = call_args[1]['headers']
            assert 'Authorization' in headers
            assert 'test-api-key-123' in headers['Authorization']


class TestRerankEdgeCases:
    """测试边界情况"""

    @pytest.mark.asyncio
    async def test_rerank_special_characters_in_documents(self, mock_config):
        """测试文档中的特殊字符"""
        mock_config['RERANK_TYPE'] = RerankType.BAILIAN.value
        
        documents = [
            "包含 <html> 标签",
            "包含 \"引号\" 和 '单引号'",
            "包含换行\n和\t制表符",
            "包含 Unicode 🎉 🚀"
        ]
        
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "output": {
                    "results": [{"index": i} for i in range(len(documents))]
                }
            }
            mock_post.return_value = mock_response
            
            result = await Rerank.rerank(
                query="测试",
                documents=documents,
                top_k=len(documents)
            )
            
            assert len(result) == len(documents)

    @pytest.mark.asyncio
    async def test_rerank_very_long_documents(self, mock_config):
        """测试超长文档"""
        mock_config['RERANK_TYPE'] = RerankType.BAILIAN.value
        
        documents = ["A" * 10000, "B" * 10000, "C" * 10000]
        
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "output": {
                    "results": [{"index": 0}, {"index": 1}, {"index": 2}]
                }
            }
            mock_post.return_value = mock_response
            
            result = await Rerank.rerank(
                query="测试",
                documents=documents,
                top_k=3
            )
            
            assert isinstance(result, list)
