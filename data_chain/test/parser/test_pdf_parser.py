# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
PDF 解析器测试

测试范围:
- PDF 文本提取
- 表格提取
- 图片提取
- 边界框处理
- 多页文档处理
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest
import fitz
import numpy as np

from data_chain.parser.handler.pdf_parser import PdfParser, Bbox, ParseNodeWithBbox
from data_chain.parser.parse_result import ParseResult
from data_chain.entities.enum import ChunkType, DocParseRelutTopology, ChunkParseTopology


class TestPdfBbox:
    """测试 Bbox 类"""

    def test_bbox_creation(self):
        """测试 Bbox 创建"""
        bbox = Bbox(x0=0, y0=0, x1=100, y1=100)
        assert bbox.x0 == 0
        assert bbox.y0 == 0
        assert bbox.x1 == 100
        assert bbox.y1 == 100

    def test_bbox_contains(self):
        """测试 Bbox 包含关系"""
        outer = Bbox(x0=0, y0=0, x1=100, y1=100)
        inner = Bbox(x0=10, y0=10, x1=50, y1=50)
        
        assert outer.contains(inner) is True
        assert inner.contains(outer) is False

    def test_bbox_overlaps(self):
        """测试 Bbox 重叠检测"""
        bbox1 = Bbox(x0=0, y0=0, x1=100, y1=100)
        bbox2 = Bbox(x0=50, y0=50, x1=150, y1=150)
        
        assert bbox1.overlaps(bbox2) is True
        assert bbox2.overlaps(bbox1) is True

    def test_bbox_no_overlap(self):
        """测试无重叠的 Bbox"""
        bbox1 = Bbox(x0=0, y0=0, x1=50, y1=50)
        bbox2 = Bbox(x0=100, y0=100, x1=150, y1=150)
        
        assert bbox1.overlaps(bbox2) is False


class TestPdfParserTextExtraction:
    """测试 PDF 文本提取"""

    @pytest.mark.asyncio
    async def test_extract_text_from_page(self):
        """测试从页面提取文本"""
        mock_page = MagicMock()
        mock_page.get_text.return_value = [
            (0, 0, 100, 20, "Test text content", 0, 0)
        ]
        
        result = await PdfParser.extract_text_from_page(mock_page)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].node.content == "Test text content"

    @pytest.mark.asyncio
    async def test_extract_text_with_exclude_regions(self):
        """测试带排除区域的文本提取"""
        mock_page = MagicMock()
        mock_page.get_text.return_value = [
            (0, 0, 100, 20, "Text in excluded region", 0, 0),
            (0, 50, 100, 70, "Normal text", 0, 0)
        ]
        
        exclude_region = Bbox(x0=0, y0=0, x1=100, y1=30)
        result = await PdfParser.extract_text_from_page(mock_page, [exclude_region])
        
        assert len(result) == 1
        assert result[0].node.content == "Normal text"


class TestPdfParserTableExtraction:
    """测试 PDF 表格提取"""

    @pytest.mark.asyncio
    async def test_extract_table_to_array(self):
        """测试表格转数组"""
        import pandas as pd
        
        df = pd.DataFrame({
            'col1': ['a', 'b', 'c'],
            'col2': [1, 2, 3]
        })
        
        result = await PdfParser.extract_table_to_array(df)
        
        assert isinstance(result, list)
        assert len(result) == 3


class TestPdfParserImageExtraction:
    """测试 PDF 图片提取"""

    @pytest.mark.asyncio
    async def test_extract_image_from_page(self):
        """测试从页面提取图片"""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        
        mock_page.get_images.return_value = [(1, 0)]
        mock_doc.extract_image.return_value = {
            "image": b"fake_image_data",
            "width": 100,
            "height": 100
        }
        mock_page.get_image_rects.return_value = [fitz.Rect(0, 0, 100, 100)]
        
        result, regions = await PdfParser.extract_image_from_page(mock_doc, mock_page)
        
        assert isinstance(result, list)
        assert isinstance(regions, list)


class TestPdfParserNodeMerging:
    """测试节点合并"""

    @pytest.mark.asyncio
    async def test_merge_nodes_with_bbox(self):
        """测试合并带 Bbox 的节点"""
        from data_chain.parser.parse_result import ParseNode
        
        node1 = ParseNode(
            id=__import__('uuid').uuid4(),
            lv=0,
            parse_topology_type=ChunkParseTopology.GRAPHNODE,
            content="Node 1",
            type=ChunkType.TEXT,
            link_nodes=[]
        )
        bbox1 = Bbox(x0=0, y0=0, x1=100, y1=20)
        node_with_bbox1 = ParseNodeWithBbox(node=node1, bbox=bbox1)
        
        node2 = ParseNode(
            id=__import__('uuid').uuid4(),
            lv=0,
            parse_topology_type=ChunkParseTopology.GRAPHNODE,
            content="Node 2",
            type=ChunkType.TEXT,
            link_nodes=[]
        )
        bbox2 = Bbox(x0=0, y0=30, x1=100, y1=50)
        node_with_bbox2 = ParseNodeWithBbox(node=node2, bbox=bbox2)
        
        result = await PdfParser.merge_nodes_with_bbox(
            [node_with_bbox1],
            [node_with_bbox2]
        )
        
        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_merge_empty_nodes(self):
        """测试合并空节点列表"""
        result = await PdfParser.merge_nodes_with_bbox([], [])
        assert result == []
        
        result = await PdfParser.merge_nodes_with_bbox([], [MagicMock()])
        assert len(result) == 1


class TestPdfParserImageRelatedText:
    """测试图片相关文本处理"""

    @pytest.mark.asyncio
    async def test_image_related_text(self):
        """测试图片相关文本关联"""
        from data_chain.parser.parse_result import ParseNode
        
        image_node = ParseNode(
            id=__import__('uuid').uuid4(),
            lv=0,
            parse_topology_type=ChunkParseTopology.GRAPHNODE,
            content=b"image_data",
            type=ChunkType.IMAGE,
            link_nodes=[]
        )
        image_bbox = Bbox(x0=100, y0=100, x1=200, y1=200)
        image_with_bbox = ParseNodeWithBbox(node=image_node, bbox=image_bbox)
        
        text_node = ParseNode(
            id=__import__('uuid').uuid4(),
            lv=0,
            parse_topology_type=ChunkParseTopology.GRAPHNODE,
            content="Related text",
            type=ChunkType.TEXT,
            link_nodes=[]
        )
        text_bbox = Bbox(x0=100, y0=50, x1=200, y1=90)
        text_with_bbox = ParseNodeWithBbox(node=text_node, bbox=text_bbox)
        
        await PdfParser.image_related_text(image_with_bbox, [text_with_bbox])
        
        assert len(image_node.link_nodes) > 0


class TestPdfParserIntegration:
    """测试 PDF 解析器集成"""

    @pytest.mark.asyncio
    async def test_parser_basic(self, temp_dir):
        """测试基本解析功能"""
        # 创建一个简单的 PDF 文件进行测试
        test_file = temp_dir / "test.pdf"
        
        # 创建空白 PDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "OpenEuler 开源操作系统")
        doc.save(str(test_file))
        doc.close()
        
        try:
            result = await PdfParser.parser(str(test_file))
            
            assert isinstance(result, ParseResult)
            assert result.parse_topology_type == DocParseRelutTopology.GRAPH
            assert len(result.nodes) > 0
        finally:
            test_file.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_parser_nonexistent_file(self):
        """测试解析不存在的文件"""
        with pytest.raises(Exception):
            await PdfParser.parser("/nonexistent/file.pdf")

    @pytest.mark.asyncio
    async def test_parser_invalid_file(self, temp_dir):
        """测试解析无效文件"""
        test_file = temp_dir / "invalid.txt"
        test_file.write_text("This is not a PDF", encoding="utf-8")
        
        with pytest.raises(Exception):
            await PdfParser.parser(str(test_file))


class TestPdfParserPerformance:
    """测试 PDF 解析性能"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_parser_large_pdf(self, temp_dir):
        """测试大 PDF 文件解析"""
        import time
        
        test_file = temp_dir / "large.pdf"
        doc = fitz.open()
        
        # 创建多页 PDF
        for i in range(50):
            page = doc.new_page()
            for j in range(20):
                page.insert_text((50, 50 + j * 20), f"Page {i} Line {j}")
        
        doc.save(str(test_file))
        doc.close()
        
        try:
            start_time = time.time()
            result = await PdfParser.parser(str(test_file))
            elapsed = time.time() - start_time
            
            print(f"\n大 PDF 解析时间: {elapsed:.2f}s")
            assert elapsed < 30  # 应该在 30 秒内完成
            assert len(result.nodes) > 0
        finally:
            test_file.unlink(missing_ok=True)
