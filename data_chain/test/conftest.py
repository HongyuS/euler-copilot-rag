# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
Pytest 全局配置和共享 Fixtures
"""

import asyncio
import json
import os
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# 事件循环配置
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """创建一个事件循环供所有异步测试使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# 测试数据 Fixtures
# =============================================================================

@pytest.fixture
def sample_text_content() -> str:
    """示例文本内容"""
    return """
    # OpenEuler 操作系统简介
    
    OpenEuler 是一款开源操作系统，支持多样性计算。
    
    ## 核心特性
    
    1. 支持 ARM、x86、RISC-V 等多种架构
    2. 提供企业级稳定性和安全性
    3. 拥有活跃的社区生态
    
    ## 应用场景
    
    - 云计算
    - 边缘计算
    - 嵌入式系统
    """


@pytest.fixture
def sample_markdown_content() -> str:
    """示例 Markdown 内容"""
    return """# 测试文档

## 第一部分：概述

这是一个测试文档，用于验证 Markdown 解析器的功能。

### 子章节

- 列表项 1
- 列表项 2
- 列表项 3

## 第二部分：代码示例

```python
def hello():
    print("Hello, OpenEuler!")
```

## 第三部分：表格

| 名称 | 版本 | 状态 |
|------|------|------|
| OpenEuler | 22.03 | LTS |
| OpenEuler | 24.03 | LTS |

## 第四部分：结语

感谢使用 OpenEuler！
"""


@pytest.fixture
def sample_json_content() -> dict:
    """示例 JSON 内容"""
    return {
        "name": "OpenEuler",
        "version": "22.03 LTS",
        "architectures": ["x86_64", "aarch64", "riscv64"],
        "features": {
            "security": True,
            "container": True,
            "virtualization": True
        },
        "packages": [
            {"name": "kernel", "version": "5.10"},
            {"name": "gcc", "version": "10.3"}
        ]
    }


@pytest.fixture
def sample_query_text() -> str:
    """示例查询文本"""
    return "OpenEuler 支持哪些处理器架构？"


@pytest.fixture
def sample_kb_id() -> uuid.UUID:
    """示例知识库 ID"""
    return uuid.uuid4()


@pytest.fixture
def sample_doc_id() -> uuid.UUID:
    """示例文档 ID"""
    return uuid.uuid4()


# =============================================================================
# 临时文件 Fixtures
# =============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_text_file(temp_dir: Path, sample_text_content: str) -> Path:
    """创建临时文本文件"""
    file_path = temp_dir / "test.txt"
    file_path.write_text(sample_text_content, encoding="utf-8")
    return file_path


@pytest.fixture
def temp_markdown_file(temp_dir: Path, sample_markdown_content: str) -> Path:
    """创建临时 Markdown 文件"""
    file_path = temp_dir / "test.md"
    file_path.write_text(sample_markdown_content, encoding="utf-8")
    return file_path


@pytest.fixture
def temp_json_file(temp_dir: Path, sample_json_content: dict) -> Path:
    """创建临时 JSON 文件"""
    file_path = temp_dir / "test.json"
    file_path.write_text(json.dumps(sample_json_content, indent=2), encoding="utf-8")
    return file_path


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_embedding_vector() -> list[float]:
    """模拟 Embedding 向量"""
    return [0.1] * 1024


class MockConfig:
    """模拟配置类"""
    def __init__(self):
        self.EMBEDDING_TYPE = "openai"
        self.EMBEDDING_API_KEY = "test-key"
        self.EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
        self.EMBEDDING_ENDPOINT = "https://api.test.com/embeddings"
        self.RERANK_TYPE = "algorithm"
        self.RERANK_API_KEY = "test-key"
        self.RERANK_ENDPOINT = "https://api.test.com/rerank"
        self.RERANK_MODEL_NAME = "rerank-model"
        self.STOP_WORDS_PATH = str(PROJECT_ROOT / "data_chain" / "config" / "stopwords.txt")
        self.PROMPT_PATH = str(PROJECT_ROOT / "test" / "prompt.yaml")
    
    def __getitem__(self, key):
        return getattr(self, key, None)


@pytest.fixture
def mock_config():
    """模拟配置对象"""
    return MockConfig()


@pytest.fixture(autouse=True)
def patch_config(mock_config):
    """自动 mock 配置"""
    with patch("data_chain.config.config.config", mock_config):
        # 同时 patch TokenTool 直接使用的路径
        with patch("data_chain.parser.tools.token_tool.TokenTool.stop_words_path", mock_config.STOP_WORDS_PATH):
            yield mock_config


@pytest.fixture
def mock_chunk_entity():
    """模拟 Chunk 实体"""
    entity = MagicMock()
    entity.id = uuid.uuid4()
    entity.doc_id = uuid.uuid4()
    entity.doc_name = "test_doc.txt"
    entity.text = "这是一个测试文档片段"
    entity.tokens = 10
    entity.global_offset = 0
    entity.vector = [0.1] * 1024
    return entity


@pytest.fixture
def mock_chunk_entities(mock_chunk_entity) -> list:
    """模拟 Chunk 实体列表"""
    entities = []
    for i in range(5):
        entity = MagicMock()
        entity.id = uuid.uuid4()
        entity.doc_id = uuid.uuid4()
        entity.doc_name = f"test_doc_{i}.txt"
        entity.text = f"这是第 {i} 个测试文档片段"
        entity.tokens = 10 + i
        entity.global_offset = i
        entity.vector = [0.1 + i * 0.01] * 1024
        entities.append(entity)
    return entities


# =============================================================================
# 性能测试 Fixtures
# =============================================================================

@pytest.fixture
def benchmark_data_small() -> str:
    """小规模基准测试数据 (1KB)"""
    return "OpenEuler 是一个开源操作系统。" * 50


@pytest.fixture
def benchmark_data_medium() -> str:
    """中规模基准测试数据 (10KB)"""
    return "OpenEuler 是一个开源操作系统，支持多种处理器架构。" * 500


@pytest.fixture
def benchmark_data_large() -> str:
    """大规模基准测试数据 (100KB)"""
    return "OpenEuler 是一个开源操作系统，支持 x86、ARM、RISC-V 等多种处理器架构，广泛应用于云计算、边缘计算和嵌入式系统。" * 2000


# =============================================================================
# 辅助函数
# =============================================================================

def create_test_file(temp_dir: Path, filename: str, content: str | bytes) -> Path:
    """创建测试文件"""
    file_path = temp_dir / filename
    if isinstance(content, str):
        file_path.write_text(content, encoding="utf-8")
    else:
        file_path.write_bytes(content)
    return file_path


def assert_parse_result_valid(result) -> None:
    """验证解析结果是否有效"""
    assert result is not None
    assert hasattr(result, 'parse_topology_type')
    assert hasattr(result, 'nodes')
    assert isinstance(result.nodes, list)
    assert len(result.nodes) > 0


def assert_chunk_valid(chunk) -> None:
    """验证 Chunk 是否有效"""
    assert chunk is not None
    assert hasattr(chunk, 'id')
    assert hasattr(chunk, 'content')
    assert hasattr(chunk, 'type')
