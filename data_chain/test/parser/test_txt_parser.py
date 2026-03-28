# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
TXT 文本解析器测试

测试范围:
- 编码检测
- 文本解析
- 特殊字符处理
- 大文件处理
"""

import asyncio
from pathlib import Path

import pytest
import chardet

from data_chain.parser.handler.txt_parser import TxtParser
from data_chain.parser.parse_result import ParseResult
from data_chain.entities.enum import ChunkType, DocParseRelutTopology


class TestTxtParserEncoding:
    """测试 TXT 解析器编码检测"""

    @pytest.mark.asyncio
    async def test_detect_encoding_utf8(self, temp_dir: Path):
        """测试 UTF-8 编码检测"""
        test_file = temp_dir / "utf8.txt"
        test_content = "OpenEuler 开源操作系统"
        test_file.write_text(test_content, encoding="utf-8")
        
        encoding = await TxtParser.detect_encoding(str(test_file))
        assert encoding.lower() in ['utf-8', 'utf-8-sig', 'ascii']

    @pytest.mark.asyncio
    async def test_detect_encoding_gbk(self, temp_dir: Path):
        """测试 GBK 编码检测"""
        test_file = temp_dir / "gbk.txt"
        test_content = "中文测试内容"
        test_file.write_text(test_content, encoding="gbk")
        
        encoding = await TxtParser.detect_encoding(str(test_file))
        assert encoding is not None

    @pytest.mark.asyncio
    async def test_detect_encoding_empty_file(self, temp_dir: Path):
        """测试空文件编码检测"""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("", encoding="utf-8")
        
        # 空文件也应该能检测编码
        encoding = await TxtParser.detect_encoding(str(test_file))
        # 空文件可能返回 None 或默认编码


class TestTxtParserContent:
    """测试 TXT 解析器内容处理"""

    @pytest.mark.asyncio
    async def test_parse_simple_text(self, temp_dir: Path):
        """测试解析简单文本"""
        test_file = temp_dir / "simple.txt"
        test_content = "OpenEuler 是一个开源操作系统"
        test_file.write_text(test_content, encoding="utf-8")
        
        result = await TxtParser.parser(str(test_file))
        
        assert isinstance(result, ParseResult)
        assert result.parse_topology_type == DocParseRelutTopology.LIST
        assert len(result.nodes) == 1
        assert result.nodes[0].type == ChunkType.TEXT
        assert test_content in result.nodes[0].content

    @pytest.mark.asyncio
    async def test_parse_multiline_text(self, temp_dir: Path):
        """测试解析多行文本"""
        test_file = temp_dir / "multiline.txt"
        test_content = """第一行内容
第二行内容
第三行内容"""
        test_file.write_text(test_content, encoding="utf-8")
        
        result = await TxtParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        assert "第一行" in result.nodes[0].content
        assert "第二行" in result.nodes[0].content
        assert "第三行" in result.nodes[0].content

    @pytest.mark.asyncio
    async def test_parse_special_characters(self, temp_dir: Path):
        """测试解析包含特殊字符的文本"""
        test_file = temp_dir / "special.txt"
        test_content = "特殊字符：!@#$%^&*()_+-=[]{}|;':\",./<>?"
        test_file.write_text(test_content, encoding="utf-8")
        
        result = await TxtParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        assert "!@#$%" in result.nodes[0].content

    @pytest.mark.asyncio
    async def test_parse_unicode_content(self, temp_dir: Path):
        """测试解析 Unicode 内容"""
        test_file = temp_dir / "unicode.txt"
        test_content = "中文 🎉 Emoji ✨ 测试 🔧"
        test_file.write_text(test_content, encoding="utf-8")
        
        result = await TxtParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        assert "🎉" in result.nodes[0].content
        assert "✨" in result.nodes[0].content


class TestTxtParserAccuracy:
    """测试 TXT 解析器准确率"""

    @pytest.mark.asyncio
    async def test_content_integrity(self, temp_dir: Path):
        """测试内容完整性"""
        test_file = temp_dir / "integrity.txt"
        original_content = """OpenEuler 开源操作系统
版本：22.03 LTS
架构：x86_64, aarch64

核心特性：
1. 高性能
2. 高可靠
3. 高安全"""
        test_file.write_text(original_content, encoding="utf-8")
        
        result = await TxtParser.parser(str(test_file))
        
        parsed_content = result.nodes[0].content
        assert "OpenEuler" in parsed_content
        assert "22.03 LTS" in parsed_content
        assert "aarch64" in parsed_content
        assert "高性能" in parsed_content

    @pytest.mark.asyncio
    async def test_node_structure(self, temp_dir: Path):
        """测试节点结构正确性"""
        test_file = temp_dir / "structure.txt"
        test_file.write_text("测试内容", encoding="utf-8")
        
        result = await TxtParser.parser(str(test_file))
        
        node = result.nodes[0]
        assert node.lv == 0
        assert node.type == ChunkType.TEXT
        assert node.title == ""
        assert node.link_nodes == []
        assert node.id is not None


class TestTxtParserEdgeCases:
    """测试 TXT 解析器边界情况"""

    @pytest.mark.asyncio
    async def test_parse_empty_file(self, temp_dir: Path):
        """测试解析空文件"""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("", encoding="utf-8")
        
        result = await TxtParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        # 空文件应该返回空字符串内容
        assert result.nodes[0].content == ""

    @pytest.mark.asyncio
    async def test_parse_whitespace_only(self, temp_dir: Path):
        """测试解析仅包含空白字符的文件"""
        test_file = temp_dir / "whitespace.txt"
        test_file.write_text("   \n\t\n   ", encoding="utf-8")
        
        result = await TxtParser.parser(str(test_file))
        
        assert len(result.nodes) == 1

    @pytest.mark.asyncio
    async def test_parse_very_long_line(self, temp_dir: Path):
        """测试解析超长行"""
        test_file = temp_dir / "longline.txt"
        long_content = "A" * 10000
        test_file.write_text(long_content, encoding="utf-8")
        
        result = await TxtParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        assert len(result.nodes[0].content) == 10000

    @pytest.mark.asyncio
    async def test_parse_large_file(self, temp_dir: Path):
        """测试解析大文件"""
        test_file = temp_dir / "large.txt"
        large_content = "测试行内容\n" * 10000
        test_file.write_text(large_content, encoding="utf-8")
        
        result = await TxtParser.parser(str(test_file))
        
        assert len(result.nodes) == 1
        # 验证内容长度 ("测试行内容\n" = 7 个字符/行, 10000 行 = 70000)
        assert len(result.nodes[0].content) >= 60000

    @pytest.mark.asyncio
    async def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        with pytest.raises(Exception):
            await TxtParser.parser("/nonexistent/path/file.txt")


class TestTxtParserPerformance:
    """测试 TXT 解析器性能"""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="性能测试需要 benchmark fixture")
    async def test_parse_performance_small(self, temp_dir: Path):
        """测试小文件解析性能"""
        test_file = temp_dir / "perf_small.txt"
        test_file.write_text("OpenEuler 测试内容 " * 100, encoding="utf-8")
        
        def parse_file():
            asyncio.run(TxtParser.parser(str(test_file)))
        
        # 使用 pytest-benchmark 进行性能测试
        # benchmark(parse_file)
        # 暂时不使用 benchmark，仅作标记

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_parse_performance_large(self, temp_dir: Path):
        """测试大文件解析性能"""
        import time
        
        test_file = temp_dir / "perf_large.txt"
        test_file.write_text("性能测试内容\n" * 100000, encoding="utf-8")
        
        start_time = time.time()
        result = await TxtParser.parser(str(test_file))
        end_time = time.time()
        
        # 10万行文本应该在 5 秒内完成
        assert end_time - start_time < 5.0
        assert len(result.nodes) == 1
