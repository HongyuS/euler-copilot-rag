# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
文档解析性能测试

测试范围:
- 不同大小文件的解析性能
- 不同格式文件的解析性能
- 内存使用情况
"""

import time
from pathlib import Path

import pytest

from data_chain.parser.handler.txt_parser import TxtParser
from data_chain.parser.handler.json_parser import JsonParser
from data_chain.parser.handler.md_parser import MdParser


class TestParserPerformanceBenchmark:
    """文档解析性能基准测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_txt_parser_small_file_performance(self, temp_dir):
        """测试小文件（1KB）TXT 解析性能"""
        test_file = temp_dir / "small.txt"
        content = "OpenEuler 测试内容。" * 20  # 约 1KB
        test_file.write_text(content, encoding="utf-8")
        
        # 预热
        await TxtParser.parser(str(test_file))
        
        # 实际测试
        iterations = 100
        start_time = time.time()
        for _ in range(iterations):
            await TxtParser.parser(str(test_file))
        end_time = time.time()
        
        avg_time = (end_time - start_time) / iterations
        print(f"\n小文件 TXT 解析平均时间: {avg_time*1000:.2f}ms")
        
        # 断言：小文件应该在 50ms 内完成
        assert avg_time < 0.05

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_txt_parser_medium_file_performance(self, temp_dir):
        """测试中文件（100KB）TXT 解析性能"""
        test_file = temp_dir / "medium.txt"
        content = "OpenEuler 开源操作系统支持多种处理器架构，广泛应用于云计算和边缘计算场景。\n" * 800
        test_file.write_text(content, encoding="utf-8")
        
        iterations = 10
        start_time = time.time()
        for _ in range(iterations):
            await TxtParser.parser(str(test_file))
        end_time = time.time()
        
        avg_time = (end_time - start_time) / iterations
        print(f"\n中文件 TXT 解析平均时间: {avg_time*1000:.2f}ms")
        
        # 断言：100KB 文件应该在 200ms 内完成
        assert avg_time < 0.2

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_txt_parser_large_file_performance(self, temp_dir):
        """测试大文件（1MB）TXT 解析性能"""
        test_file = temp_dir / "large.txt"
        content = "OpenEuler 开源操作系统支持多种处理器架构，广泛应用于云计算和边缘计算场景。\n" * 8000
        test_file.write_text(content, encoding="utf-8")
        
        start_time = time.time()
        result = await TxtParser.parser(str(test_file))
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        print(f"\n大文件 TXT 解析时间: {elapsed_time*1000:.2f}ms")
        
        # 断言：1MB 文件应该在 2s 内完成
        assert elapsed_time < 2.0
        assert len(result.nodes) == 1


class TestJsonParserPerformance:
    """JSON 解析器性能测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_json_parser_small_object_performance(self, temp_dir):
        """测试小 JSON 对象解析性能"""
        import json
        
        test_file = temp_dir / "small.json"
        data = {"name": "test", "value": 123}
        test_file.write_text(json.dumps(data), encoding="utf-8")
        
        iterations = 1000
        start_time = time.time()
        for _ in range(iterations):
            await JsonParser.parser(str(test_file))
        end_time = time.time()
        
        avg_time = (end_time - start_time) / iterations
        print(f"\n小 JSON 解析平均时间: {avg_time*1000:.2f}ms")
        
        assert avg_time < 0.01

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_json_parser_large_array_performance(self, temp_dir):
        """测试大 JSON 数组解析性能"""
        import json
        
        test_file = temp_dir / "large_array.json"
        data = [{"id": i, "name": f"item_{i}", "data": "x" * 100} for i in range(10000)]
        test_file.write_text(json.dumps(data), encoding="utf-8")
        
        start_time = time.time()
        result = await JsonParser.parser(str(test_file))
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        print(f"\n大 JSON 数组解析时间: {elapsed_time*1000:.2f}ms")
        
        assert elapsed_time < 3.0


class TestMarkdownParserPerformance:
    """Markdown 解析器性能测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_md_parser_simple_performance(self, temp_dir):
        """测试简单 Markdown 解析性能"""
        test_file = temp_dir / "simple.md"
        content = "# 标题\n\n这是正文内容。\n\n## 子标题\n\n更多内容。"
        test_file.write_text(content, encoding="utf-8")
        
        iterations = 100
        start_time = time.time()
        for _ in range(iterations):
            await MdParser.parser(str(test_file))
        end_time = time.time()
        
        avg_time = (end_time - start_time) / iterations
        print(f"\n简单 Markdown 解析平均时间: {avg_time*1000:.2f}ms")
        
        assert avg_time < 0.1

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_md_parser_complex_performance(self, temp_dir):
        """测试复杂 Markdown 解析性能"""
        test_file = temp_dir / "complex.md"
        
        # 生成复杂 Markdown
        sections = []
        for i in range(100):
            sections.append(f"## 章节 {i}")
            sections.append("")
            sections.append(f"这是第 {i} 章节的详细内容，包含多行文本。")
            sections.append("")
            sections.append("- 列表项 1")
            sections.append("- 列表项 2")
            sections.append("- 列表项 3")
            sections.append("")
        
        content = "# 复杂文档\n\n" + "\n".join(sections)
        test_file.write_text(content, encoding="utf-8")
        
        start_time = time.time()
        result = await MdParser.parser(str(test_file))
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        print(f"\n复杂 Markdown 解析时间: {elapsed_time*1000:.2f}ms")
        
        assert elapsed_time < 5.0
        assert len(result.nodes) > 100


class TestParserMemoryUsage:
    """解析器内存使用测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_txt_parser_memory_efficiency(self, temp_dir):
        """测试 TXT 解析器内存效率"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # 创建大文件
        test_file = temp_dir / "memory_test.txt"
        content = "Memory test line.\n" * 50000
        test_file.write_text(content, encoding="utf-8")
        
        # 记录解析前的内存
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        result = await TxtParser.parser(str(test_file))
        
        # 记录解析后的内存
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        
        mem_increase = mem_after - mem_before
        print(f"\nTXT 解析内存增加: {mem_increase:.2f}MB")
        
        # 验证结果
        assert len(result.nodes) == 1
        # 内存增长应该合理（小于 100MB）
        assert mem_increase < 100


class TestParserConcurrency:
    """解析器并发性能测试"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_txt_parsing(self, temp_dir):
        """测试并发 TXT 解析"""
        import asyncio
        
        # 创建多个测试文件
        files = []
        for i in range(10):
            test_file = temp_dir / f"concurrent_{i}.txt"
            content = f"文件 {i} 的内容。" * 100
            test_file.write_text(content, encoding="utf-8")
            files.append(test_file)
        
        # 并发解析
        start_time = time.time()
        tasks = [TxtParser.parser(str(f)) for f in files]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        print(f"\n10 文件并发解析时间: {elapsed_time*1000:.2f}ms")
        
        assert len(results) == 10
        assert elapsed_time < 1.0  # 应该在 1 秒内完成


class TestParserThroughput:
    """解析器吞吐量测试"""

    @pytest.mark.slow
    def test_parser_throughput(self, tmp_path_factory):
        """测试解析器吞吐量"""
        import asyncio
        
        temp_dir = tmp_path_factory.mktemp("throughput")
        
        # 创建不同大小的测试文件
        file_sizes = {
            "small": 1024,      # 1KB
            "medium": 102400,   # 100KB
            "large": 1048576,   # 1MB
        }
        
        throughput_results = {}
        
        for size_name, size_bytes in file_sizes.items():
            test_file = temp_dir / f"{size_name}.txt"
            content = "A" * size_bytes
            test_file.write_text(content, encoding="utf-8")
            
            # 测量解析速度
            async def measure():
                start = time.time()
                await TxtParser.parser(str(test_file))
                return time.time() - start
            
            elapsed = asyncio.run(measure())
            throughput = size_bytes / elapsed / 1024 / 1024  # MB/s
            throughput_results[size_name] = throughput
            
            print(f"\n{size_name} 文件解析吞吐量: {throughput:.2f} MB/s")
        
        # 断言：至少小文件应该有合理的吞吐量
        assert throughput_results["small"] > 1.0  # 至少 1MB/s
