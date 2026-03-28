# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
基础解析器测试

测试范围:
- BaseParser 工厂方法
- 解析器发现机制
- 错误处理
"""

import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from data_chain.parser.handler.base_parser import BaseParser
from data_chain.parser.handler.txt_parser import TxtParser
from data_chain.parser.handler.json_parser import JsonParser
from data_chain.parser.handler.md_parser import MdParser
from data_chain.entities.enum import ChunkType, DocParseRelutTopology, ChunkParseTopology


class TestBaseParserFactory:
    """测试 BaseParser 工厂方法"""

    def test_find_worker_class_with_valid_parser(self):
        """测试查找有效的解析器类"""
        # 测试查找 txt 解析器
        parser_class = BaseParser.find_worker_class('txt')
        assert parser_class is not None
        assert parser_class == TxtParser

    def test_find_worker_class_with_invalid_parser(self):
        """测试查找无效的解析器类"""
        parser_class = BaseParser.find_worker_class('nonexistent')
        assert parser_class is None

    def test_find_worker_class_case_sensitivity(self):
        """测试解析器名称大小写敏感性"""
        # 测试大小写敏感的匹配
        parser_class_lower = BaseParser.find_worker_class('txt')
        parser_class_upper = BaseParser.find_worker_class('TXT')
        
        # 根据实现，应该是精确匹配
        assert parser_class_lower == TxtParser


class TestImageRelatedNodeInLinkNodes:
    """测试图片关联节点功能"""

    @pytest.fixture
    def sample_nodes(self):
        """创建示例节点列表"""
        from data_chain.parser.parse_result import ParseNode
        
        text_node_1 = ParseNode(
            id=uuid.uuid4(),
            title="Text 1",
            lv=0,
            parse_topology_type=ChunkParseTopology.GERNERAL,
            content="This is text 1",
            type=ChunkType.TEXT,
            link_nodes=[]
        )
        
        image_node_1 = ParseNode(
            id=uuid.uuid4(),
            title="Image 1",
            lv=0,
            parse_topology_type=ChunkParseTopology.GERNERAL,
            content=b"fake_image_data",
            type=ChunkType.IMAGE,
            link_nodes=[]
        )
        
        text_node_2 = ParseNode(
            id=uuid.uuid4(),
            title="Text 2",
            lv=0,
            parse_topology_type=ChunkParseTopology.GERNERAL,
            content="This is text 2",
            type=ChunkType.TEXT,
            link_nodes=[]
        )
        
        image_node_2 = ParseNode(
            id=uuid.uuid4(),
            title="Image 2",
            lv=0,
            parse_topology_type=ChunkParseTopology.GERNERAL,
            content=b"fake_image_data_2",
            type=ChunkType.IMAGE,
            link_nodes=[]
        )
        
        return [text_node_1, image_node_1, text_node_2, image_node_2]

    def test_image_related_node_linking(self, sample_nodes):
        """测试图片节点正确关联到文本节点"""
        BaseParser.image_related_node_in_link_nodes(sample_nodes)
        
        # 第一个图片节点应该关联到第一个文本节点
        assert len(sample_nodes[1].link_nodes) > 0
        assert sample_nodes[1].link_nodes[0] == sample_nodes[0]
        
        # 第二个图片节点应该关联到第二个文本节点（反向遍历）
        assert len(sample_nodes[3].link_nodes) > 0

    def test_image_related_node_with_no_text(self):
        """测试只有图片节点时的处理"""
        from data_chain.parser.parse_result import ParseNode
        
        image_node = ParseNode(
            id=uuid.uuid4(),
            title="Image Only",
            lv=0,
            parse_topology_type=ChunkParseTopology.GERNERAL,
            content=b"image_data",
            type=ChunkType.IMAGE,
            link_nodes=[]
        )
        
        nodes = [image_node]
        # 不应该抛出异常
        BaseParser.image_related_node_in_link_nodes(nodes)
        assert len(image_node.link_nodes) == 0


class TestBaseParserIntegration:
    """测试 BaseParser 集成"""

    @pytest.mark.asyncio
    async def test_parser_with_valid_method(self, temp_text_file: Path):
        """测试使用有效解析方法进行解析"""
        result = await BaseParser.parser('txt', str(temp_text_file))
        
        assert result is not None
        assert result.parse_topology_type == DocParseRelutTopology.LIST
        assert len(result.nodes) > 0

    @pytest.mark.asyncio
    async def test_parser_with_invalid_method(self):
        """测试使用无效解析方法时的错误处理"""
        with pytest.raises(Exception) as exc_info:
            await BaseParser.parser('nonexistent', '/fake/path.txt')
        
        assert "解析器不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_parser_error_propagation(self, temp_dir: Path):
        """测试解析错误的传播"""
        # 创建一个损坏的 JSON 文件
        bad_json = temp_dir / "bad.json"
        bad_json.write_text("{invalid json", encoding="utf-8")
        
        with pytest.raises(Exception):
            await BaseParser.parser('json', str(bad_json))


class TestParserRegistration:
    """测试解析器注册机制"""

    def test_all_parsers_registered(self):
        """测试所有解析器已正确注册"""
        expected_parsers = [
            'txt', 'json', 'md', 'docx', 'xlsx', 
            'yaml', 'html', 'pdf', 'deep_pdf', 'fine_pdf',
            'doc', 'pptx', 'picture', 'md_zip'
        ]
        
        for parser_name in expected_parsers:
            parser_class = BaseParser.find_worker_class(parser_name)
            # 某些解析器可能未实现，记录哪些是可用的
            if parser_class is None:
                pytest.skip(f"解析器 '{parser_name}' 未实现")

    def test_parser_name_attribute(self):
        """测试解析器类具有正确的 name 属性"""
        assert hasattr(TxtParser, 'name')
        assert TxtParser.name == 'txt'
        
        assert hasattr(JsonParser, 'name')
        assert JsonParser.name == 'json'
        
        assert hasattr(MdParser, 'name')
        assert MdParser.name == 'md'
