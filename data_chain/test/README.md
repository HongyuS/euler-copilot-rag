# Data Chain 测试套件

本目录包含 euler-copilot-rag data_chain 模块的完整测试套件。

## 目录结构

```
test/
├── conftest.py              # Pytest 配置和共享 fixtures
├── pytest.ini              # Pytest 配置文件
├── README.md               # 本文档
├── fixtures/               # 测试数据
│   ├── __init__.py
│   └── sample_data.py      # 样本数据生成器
├── parser/                 # 文档解析模块测试
│   ├── __init__.py
│   ├── test_base_parser.py     # 基础解析器测试
│   ├── test_txt_parser.py      # TXT 解析器测试
│   ├── test_json_parser.py     # JSON 解析器测试
│   ├── test_md_parser.py       # Markdown 解析器测试
│   └── test_token_tool.py      # Token 工具测试
├── rag/                    # RAG 检索模块测试
│   ├── __init__.py
│   ├── test_base_searcher.py   # 基础检索器测试
│   ├── test_vector_searcher.py # 向量检索器测试
│   ├── test_keyword_searcher.py# 关键词检索器测试
│   ├── test_rerank.py          # 重排序测试
│   ├── test_rag_accuracy.py    # 准确率测试
│   └── test_rag_stability.py   # 稳定性测试
└── performance/            # 性能测试
    ├── __init__.py
    ├── test_parser_performance.py  # 解析器性能测试
    └── test_rag_performance.py     # RAG 性能测试
```

## 运行测试

### 安装依赖

```bash
pip install pytest pytest-asyncio
# 如果需要进行性能测试
pip install psutil
```

### 运行所有测试

```bash
cd /home/zjq/euler-copilot-rag/data_chain/test
pytest
```

### 运行特定模块测试

```bash
# 运行解析器测试
pytest parser/

# 运行 RAG 测试
pytest rag/

# 运行性能测试
pytest performance/ -v
```

### 运行特定测试

```bash
# 运行特定测试文件
pytest parser/test_txt_parser.py

# 运行特定测试类
pytest parser/test_txt_parser.py::TestTxtParserBasic

# 运行特定测试方法
pytest parser/test_txt_parser.py::TestTxtParserBasic::test_parse_simple_text
```

### 使用标记过滤

```bash
# 只运行单元测试（排除慢测试）
pytest -m "not slow"

# 只运行性能测试
pytest -m "performance"

# 只运行准确率测试
pytest -m "accuracy"

# 只运行稳定性测试
pytest -m "stability"
```

### 其他常用选项

```bash
# 显示详细的测试输出
pytest -v

# 显示测试覆盖率
pytest --cov=data_chain --cov-report=html

# 在失败时停止
pytest -x

# 重新运行上次失败的测试
pytest --lf

# 并行运行测试（需要 pytest-xdist）
pytest -n auto
```

## 测试分类

### 1. 文档解析测试 (parser/)

测试各种文档解析器的正确性、稳定性和性能。

| 文件 | 说明 |
|------|------|
| test_base_parser.py | 基础解析器工厂方法和通用功能测试 |
| test_txt_parser.py | TXT 文本解析器测试（编码检测、内容解析） |
| test_json_parser.py | JSON 解析器测试（结构解析、错误处理） |
| test_md_parser.py | Markdown 解析器测试（标题、表格、代码块） |
| test_token_tool.py | Token 工具测试（分词、关键词、相似度） |

### 2. RAG 检索测试 (rag/)

测试检索增强生成功能的准确性和稳定性。

| 文件 | 说明 |
|------|------|
| test_base_searcher.py | 基础检索器功能测试（工厂、重排序、分类） |
| test_vector_searcher.py | 向量检索器测试（Embedding、超时重试） |
| test_keyword_searcher.py | 关键词检索器测试（两阶段检索、错误处理） |
| test_rerank.py | 重排序模块测试（数据组装、响应解析） |
| test_rag_accuracy.py | 检索准确率测试（相关性、排名准确性） |
| test_rag_stability.py | 稳定性测试（异常处理、边界条件、并发） |

### 3. 性能测试 (performance/)

测试各模块的性能指标。

| 文件 | 说明 |
|------|------|
| test_parser_performance.py | 解析器性能测试（吞吐量、内存使用） |
| test_rag_performance.py | RAG 性能测试（延迟、可扩展性） |

## 测试设计原则

### 工程化实践

1. **模块化**：每个测试文件专注于一个模块或功能
2. **独立性**：测试之间不相互依赖，可以单独运行
3. **可重复性**：测试结果稳定，不受外部环境影响
4. **Mock 外部依赖**：数据库、API 等外部依赖使用 Mock

### 测试类型

1. **单元测试**：测试单个函数或类的功能
2. **集成测试**：测试多个组件协同工作
3. **性能测试**：测试响应时间、吞吐量
4. **准确率测试**：测试结果质量和相关性
5. **稳定性测试**：测试异常处理和边界条件

### 命名规范

- 测试文件：`test_<module>.py`
- 测试类：`Test<ClassName>` 或 `Test<Feature>`
- 测试方法：`test_<scenario>_<expected_result>`

## 添加新测试

1. 在对应目录创建测试文件
2. 继承测试类或使用函数式测试
3. 使用 fixtures 提供测试数据
4. 添加适当的标记（markers）
5. 运行测试确保通过

示例：

```python
import pytest
from data_chain.parser.handler.xxx_parser import XxxParser

class TestXxxParser:
    """XXX 解析器测试"""
    
    @pytest.mark.asyncio
    async def test_parse_valid_file(self, temp_dir):
        """测试解析有效文件"""
        test_file = temp_dir / "test.xxx"
        test_file.write_text("valid content")
        
        result = await XxxParser.parser(str(test_file))
        
        assert result is not None
        assert len(result.nodes) > 0
```

## 注意事项

1. 运行测试前确保项目依赖已安装
2. 某些测试需要特定的环境变量或配置文件
3. 性能测试可能需要较长时间，使用 `-m "not slow"` 跳过
4. 网络相关的测试使用 Mock 避免外部依赖
