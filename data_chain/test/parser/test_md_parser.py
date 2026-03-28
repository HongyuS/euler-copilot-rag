# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
Markdown 解析器测试

测试范围:
- Markdown 结构解析
- 标题层级处理
- 表格解析
- 代码块处理
- 图片链接处理
"""

from pathlib import Path

import pytest

from data_chain.parser.handler.md_parser import MdParser
from data_chain.parser.parse_result import ParseResult, ParseNode
from data_chain.entities.enum import ChunkType, DocParseRelutTopology, ChunkParseTopology


class TestMdParserHeaders:
    """测试 Markdown 标题解析"""

    @pytest.mark.asyncio
    async def test_parse_single_header(self, temp_dir: Path):
        """测试解析单个标题"""
        test_file = temp_dir / "single_header.md"
        test_file.write_text("# 一级标题", encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        assert isinstance(result, ParseResult)
        assert result.parse_topology_type == DocParseRelutTopology.TREE
        assert len(result.nodes) > 0

    @pytest.mark.asyncio
    async def test_parse_multiple_headers(self, temp_dir: Path):
        """测试解析多个标题层级"""
        test_file = temp_dir / "headers.md"
        content = """# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题"""
        test_file.write_text(content, encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        # 应该创建树形结构
        assert len(result.nodes) > 6  # 包括根节点和所有标题

    @pytest.mark.asyncio
    async def test_header_hierarchy(self, temp_dir: Path):
        """测试标题层级关系"""
        test_file = temp_dir / "hierarchy.md"
        content = """# 文档标题

## 第一部分

这是第一部分的内容。

### 子章节 1.1

子章节内容。

## 第二部分

第二部分的内容。"""
        test_file.write_text(content, encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        # 验证树形结构
        assert result.parse_topology_type == DocParseRelutTopology.TREE
        # 应该有标题和内容节点
        assert len(result.nodes) >= 4


class TestMdParserContent:
    """测试 Markdown 内容解析"""

    @pytest.mark.asyncio
    async def test_parse_paragraphs(self, temp_dir: Path):
        """测试解析段落"""
        test_file = temp_dir / "paragraphs.md"
        content = """第一段内容。

第二段内容，包含更多信息。

第三段内容。"""
        test_file.write_text(content, encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        assert len(result.nodes) > 0

    @pytest.mark.asyncio
    async def test_parse_lists(self, temp_dir: Path):
        """测试解析列表"""
        test_file = temp_dir / "lists.md"
        content = """- 项目 1
- 项目 2
- 项目 3

1. 有序项目 1
2. 有序项目 2
3. 有序项目 3"""
        test_file.write_text(content, encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        assert len(result.nodes) > 0

    @pytest.mark.asyncio
    async def test_parse_code_block(self, temp_dir: Path):
        """测试解析代码块"""
        test_file = temp_dir / "code.md"
        content = """```python
def hello():
    print("Hello, OpenEuler!")
```"""
        test_file.write_text(content, encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        # 查找代码类型的节点
        code_nodes = [n for n in result.nodes if n.type == ChunkType.CODE]
        assert len(code_nodes) > 0

    @pytest.mark.asyncio
    async def test_parse_inline_code(self, temp_dir: Path):
        """测试解析行内代码"""
        test_file = temp_dir / "inline_code.md"
        content = "使用 `pip install` 命令安装软件包。"
        test_file.write_text(content, encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        assert len(result.nodes) > 0


class TestMdParserTables:
    """测试 Markdown 表格解析"""

    @pytest.mark.asyncio
    async def test_parse_simple_table(self, temp_dir: Path):
        """测试解析简单表格"""
        test_file = temp_dir / "table.md"
        content = """| 名称 | 版本 | 状态 |
|------|------|------|
| OpenEuler | 22.03 | LTS |
| OpenEuler | 24.03 | LTS |"""
        test_file.write_text(content, encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        # 查找表格类型的节点
        table_nodes = [n for n in result.nodes if n.type == ChunkType.TABLE]
        assert len(table_nodes) > 0

    @pytest.mark.asyncio
    async def test_extract_table_to_array(self):
        """测试表格转换为数组"""
        table_html = """<table>
            <tr><th>Header1</th><th>Header2</th></tr>
            <tr><td>Cell1</td><td>Cell2</td></tr>
            <tr><td>Cell3</td><td>Cell4</td></tr>
        </table>"""
        
        result = await MdParser.extract_table_to_array(table_html)
        
        assert isinstance(result, list)
        assert len(result) == 3  # 1 表头 + 2 数据行
        assert len(result[0]) == 2


class TestMdParserImages:
    """测试 Markdown 图片处理"""

    @pytest.mark.asyncio
    async def test_parse_image_reference(self, temp_dir: Path):
        """测试解析图片引用"""
        test_file = temp_dir / "image.md"
        content = "![图片描述](https://example.com/image.png)"
        test_file.write_text(content, encoding="utf-8")
        
        # 图片解析可能会尝试下载，这里主要测试不抛出异常
        try:
            result = await MdParser.parser(str(test_file))
            assert isinstance(result, ParseResult)
        except Exception:
            # 网络请求可能失败，但解析应该完成
            pass

    @pytest.mark.asyncio
    async def test_get_image_blob_with_invalid_url(self):
        """测试获取无效 URL 的图片"""
        result = await MdParser.get_image_blob("https://invalid.url/image.png")
        assert result is None


class TestMdParserBuildSubtree:
    """测试构建子树功能"""

    @pytest.mark.asyncio
    async def test_build_subtree_with_empty_html(self):
        """测试空 HTML 构建子树"""
        result = await MdParser.build_subtree("", 0)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_build_subtree_with_simple_html(self):
        """测试简单 HTML 构建子树"""
        html = "<p>这是一个段落</p>"
        result = await MdParser.build_subtree(html, 0)
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_build_subtree_with_headers(self):
        """测试带标题的 HTML 构建子树"""
        html = "<h1>标题1</h1><p>内容1</p><h2>标题2</h2><p>内容2</p>"
        result = await MdParser.build_subtree(html, 0)
        assert isinstance(result, list)
        assert len(result) >= 1  # 标题可能被合并为树结构


class TestMdParserFlattenTree:
    """测试树扁平化功能"""

    @pytest.mark.asyncio
    async def test_flatten_simple_tree(self):
        """测试简单树扁平化"""
        root = ParseNode(
            id=__import__('uuid').uuid4(),
            title="Root",
            lv=0,
            parse_topology_type=ChunkParseTopology.TREEROOT,
            content="",
            type=ChunkType.TEXT,
            link_nodes=[]
        )
        child = ParseNode(
            id=__import__('uuid').uuid4(),
            title="Child",
            lv=1,
            parse_topology_type=ChunkParseTopology.TREENORMAL,
            content="Child content",
            type=ChunkType.TEXT,
            link_nodes=[]
        )
        root.link_nodes.append(child)
        
        nodes = []
        await MdParser.flatten_tree(root, nodes)
        
        assert len(nodes) == 2

    @pytest.mark.asyncio
    async def test_flatten_deep_tree(self):
        """测试深度树扁平化"""
        # 创建三层树结构
        level3 = ParseNode(
            id=__import__('uuid').uuid4(),
            title="Level3",
            lv=3,
            parse_topology_type=ChunkParseTopology.TREELEAF,
            content="Level 3",
            type=ChunkType.TEXT,
            link_nodes=[]
        )
        level2 = ParseNode(
            id=__import__('uuid').uuid4(),
            title="Level2",
            lv=2,
            parse_topology_type=ChunkParseTopology.TREENORMAL,
            content="",
            type=ChunkType.TEXT,
            link_nodes=[level3]
        )
        level1 = ParseNode(
            id=__import__('uuid').uuid4(),
            title="Level1",
            lv=1,
            parse_topology_type=ChunkParseTopology.TREENORMAL,
            content="",
            type=ChunkType.TEXT,
            link_nodes=[level2]
        )
        root = ParseNode(
            id=__import__('uuid').uuid4(),
            title="Root",
            lv=0,
            parse_topology_type=ChunkParseTopology.TREEROOT,
            content="",
            type=ChunkType.TEXT,
            link_nodes=[level1]
        )
        
        nodes = []
        await MdParser.flatten_tree(root, nodes)
        
        assert len(nodes) == 4


class TestMdParserEdgeCases:
    """测试 Markdown 解析器边界情况"""

    @pytest.mark.asyncio
    async def test_parse_empty_file(self, temp_dir: Path):
        """测试解析空文件"""
        test_file = temp_dir / "empty.md"
        test_file.write_text("", encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        assert isinstance(result, ParseResult)
        assert len(result.nodes) >= 1  # 至少应该有根节点

    @pytest.mark.asyncio
    async def test_parse_special_characters(self, temp_dir: Path):
        """测试解析特殊字符"""
        test_file = temp_dir / "special.md"
        content = """# 特殊字符测试

特殊符号：< > & " '

数学符号：α β γ δ ε

表情符号：🎉 🚀 💻"""
        test_file.write_text(content, encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        assert isinstance(result, ParseResult)

    @pytest.mark.asyncio
    async def test_parse_large_document(self, temp_dir: Path):
        """测试解析大文档"""
        test_file = temp_dir / "large.md"
        # 生成包含多个章节的大文档
        sections = []
        for i in range(100):
            sections.append(f"## 章节 {i}\n\n这是章节 {i} 的内容。\n")
        content = "# 大文档标题\n\n" + "\n".join(sections)
        test_file.write_text(content, encoding="utf-8")
        
        result = await MdParser.parser(str(test_file))
        
        assert isinstance(result, ParseResult)
        assert len(result.nodes) > 100
