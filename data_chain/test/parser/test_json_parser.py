# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
JSON 解析器测试

测试范围:
- JSON 解析正确性
- 嵌套结构处理
- 错误处理
- 特殊值处理
"""

import json
from pathlib import Path

import pytest

from data_chain.parser.handler.json_parser import JsonParser
from data_chain.parser.parse_result import ParseResult
from data_chain.entities.enum import ChunkType, DocParseRelutTopology


class TestJsonParserBasic:
    """测试 JSON 解析器基本功能"""

    @pytest.mark.asyncio
    async def test_parse_simple_object(self, temp_dir: Path):
        """测试解析简单 JSON 对象"""
        test_file = temp_dir / "simple.json"
        test_data = {"name": "OpenEuler", "version": "22.03"}
        test_file.write_text(json.dumps(test_data), encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        
        assert isinstance(result, ParseResult)
        assert result.parse_topology_type == DocParseRelutTopology.LIST
        assert len(result.nodes) == 1
        assert result.nodes[0].type == ChunkType.JSON

    @pytest.mark.asyncio
    async def test_parse_nested_object(self, temp_dir: Path):
        """测试解析嵌套 JSON 对象"""
        test_file = temp_dir / "nested.json"
        test_data = {
            "os": {
                "name": "OpenEuler",
                "kernel": {"version": "5.10", "arch": "x86_64"}
            }
        }
        test_file.write_text(json.dumps(test_data, indent=2), encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        # 验证嵌套结构被正确解析
        assert "os" in result.nodes[0].content

    @pytest.mark.asyncio
    async def test_parse_array(self, temp_dir: Path):
        """测试解析 JSON 数组"""
        test_file = temp_dir / "array.json"
        test_data = [
            {"name": "package1", "version": "1.0"},
            {"name": "package2", "version": "2.0"}
        ]
        test_file.write_text(json.dumps(test_data), encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        parsed_content = result.nodes[0].content
        assert isinstance(parsed_content, list)
        assert len(parsed_content) == 2

    @pytest.mark.asyncio
    async def test_parse_complex_structure(self, temp_dir: Path):
        """测试解析复杂 JSON 结构"""
        test_file = temp_dir / "complex.json"
        test_data = {
            "name": "OpenEuler",
            "architectures": ["x86_64", "aarch64", "riscv64"],
            "features": {
                "security": True,
                "container": False,
                "nested": {"level": 3, "valid": True}
            },
            "metadata": None,
            "count": 42,
            "ratio": 3.14159
        }
        test_file.write_text(json.dumps(test_data, indent=2), encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        content = result.nodes[0].content
        assert content["name"] == "OpenEuler"
        assert "riscv64" in content["architectures"]
        assert content["metadata"] is None


class TestJsonParserDataTypes:
    """测试 JSON 数据类型处理"""

    @pytest.mark.asyncio
    async def test_parse_string_values(self, temp_dir: Path):
        """测试字符串值"""
        test_file = temp_dir / "strings.json"
        test_data = {"empty": "", "simple": "hello", "unicode": "你好世界 🌍"}
        test_file.write_text(json.dumps(test_data), encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        content = result.nodes[0].content
        
        assert content["empty"] == ""
        assert content["simple"] == "hello"
        assert content["unicode"] == "你好世界 🌍"

    @pytest.mark.asyncio
    async def test_parse_numeric_values(self, temp_dir: Path):
        """测试数值类型"""
        test_file = temp_dir / "numbers.json"
        test_data = {
            "integer": 42,
            "negative": -100,
            "float": 3.14159,
            "scientific": 1.23e-4,
            "zero": 0
        }
        test_file.write_text(json.dumps(test_data), encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        content = result.nodes[0].content
        
        assert content["integer"] == 42
        assert content["float"] == 3.14159
        assert content["scientific"] == 1.23e-4

    @pytest.mark.asyncio
    async def test_parse_boolean_values(self, temp_dir: Path):
        """测试布尔值"""
        test_file = temp_dir / "booleans.json"
        test_data = {"true_val": True, "false_val": False}
        test_file.write_text(json.dumps(test_data), encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        content = result.nodes[0].content
        
        assert content["true_val"] is True
        assert content["false_val"] is False

    @pytest.mark.asyncio
    async def test_parse_null_values(self, temp_dir: Path):
        """测试 null 值"""
        test_file = temp_dir / "nulls.json"
        test_data = {"null_val": None, "nested": {"inner_null": None}}
        test_file.write_text(json.dumps(test_data), encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        content = result.nodes[0].content
        
        assert content["null_val"] is None
        assert content["nested"]["inner_null"] is None


class TestJsonParserErrorHandling:
    """测试 JSON 解析器错误处理"""

    @pytest.mark.asyncio
    async def test_parse_invalid_json(self, temp_dir: Path):
        """测试解析无效 JSON"""
        test_file = temp_dir / "invalid.json"
        test_file.write_text("{invalid json content", encoding="utf-8")
        
        with pytest.raises(Exception):
            await JsonParser.parser(str(test_file))

    @pytest.mark.asyncio
    async def test_parse_incomplete_json(self, temp_dir: Path):
        """测试解析不完整的 JSON"""
        test_file = temp_dir / "incomplete.json"
        test_file.write_text('{"key": "value"', encoding="utf-8")
        
        with pytest.raises(Exception):
            await JsonParser.parser(str(test_file))

    @pytest.mark.asyncio
    async def test_parse_empty_json_object(self, temp_dir: Path):
        """测试解析空对象"""
        test_file = temp_dir / "empty_object.json"
        test_file.write_text("{}", encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        assert result.nodes[0].content == {}

    @pytest.mark.asyncio
    async def test_parse_empty_json_array(self, temp_dir: Path):
        """测试解析空数组"""
        test_file = temp_dir / "empty_array.json"
        test_file.write_text("[]", encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        assert result.nodes[0].content == []

    @pytest.mark.asyncio
    async def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        with pytest.raises(Exception):
            await JsonParser.parser("/nonexistent/file.json")


class TestJsonParserLargeFiles:
    """测试 JSON 大文件处理"""

    @pytest.mark.asyncio
    async def test_parse_large_array(self, temp_dir: Path):
        """测试解析大数组"""
        test_file = temp_dir / "large_array.json"
        large_data = [{"id": i, "name": f"item_{i}", "value": i * 1.5} for i in range(1000)]
        test_file.write_text(json.dumps(large_data), encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        content = result.nodes[0].content
        assert len(content) == 1000
        assert content[999]["id"] == 999

    @pytest.mark.asyncio
    async def test_parse_deeply_nested(self, temp_dir: Path):
        """测试解析深度嵌套"""
        test_file = temp_dir / "deep_nested.json"
        # 创建深度嵌套结构
        data = {"level": 0}
        current = data
        for i in range(1, 50):
            current["child"] = {"level": i}
            current = current["child"]
        
        test_file.write_text(json.dumps(data), encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        
        assert len(result.nodes) == 1


class TestJsonParserNodeStructure:
    """测试 JSON 解析器节点结构"""

    @pytest.mark.asyncio
    async def test_node_properties(self, temp_dir: Path):
        """测试节点属性"""
        test_file = temp_dir / "props.json"
        test_file.write_text('{"test": "value"}', encoding="utf-8")
        
        result = await JsonParser.parser(str(test_file))
        node = result.nodes[0]
        
        assert node.lv == 0
        assert node.type == ChunkType.JSON
        assert node.title == "" or node.title is None
        assert node.link_nodes == []
        assert node.id is not None
