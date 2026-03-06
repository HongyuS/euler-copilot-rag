# Log Detection - 日志检测系统

## 目录

- [架构设计](#架构设计)
- [核心功能](#核心功能)
- [使用说明](#使用说明)
- [测试说明](#测试说明)

---

## 架构设计

### 整体架构

Log Detection 是一个基于 MCP (Model Context Protocol) 的日志检测系统，采用微服务架构设计，主要包含以下组件：

```
┌─────────────────────────────────────────────────────────────┐
│                        MCP Server                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    API Endpoints                        │ │
│  │  - create_log_parse_task                                │ │
│  │  - get_task_message                                     │ │
│  │  - stop_task                                            │ │
│  │  - get_task_result                                      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Task Service  │  │  Worker Pool    │  │  SQLite DB      │
│   (任务调度)     │  │  (检测引擎)     │  │  (数据存储)     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Log Parser     │  │  Embedding      │  │  OCR Tool       │
│  (日志解析)     │  │  (向量化)       │  │  (图像识别)     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| **框架** | FastMCP | MCP协议实现，提供RESTful API |
| **数据库** | SQLite | 本地数据库，存储任务和日志解析结果 |
| **机器学习** | scikit-learn | DBSCAN、KMeans聚类算法 |
| **向量检索** | FAISS | Facebook AI 相似度搜索 |
| **NLP处理** | jieba | 中文分词 |
| **深度学习** | OpenAI API | LLM日志检测 |
| **图像处理** | OpenCV、Pillow | OCR图像识别 |

### 模块结构

```
log_detection/
├── src/
│   ├── worker/                    # Worker检测引擎
│   │   ├── base.py               # 基础Worker类
│   │   ├── log_detection_base_on_keywords.py    # 基于关键词检测
│   │   ├── log_detection_base_on_clustering.py  # 基于聚类检测
│   │   └── log_detection_base_on_llm.py         # 基于LLM检测
│   ├── service/                   # 服务层
│   │   ├── task.py               # 任务服务
│   │   ├── process.py            # 进程管理
│   │   ├── cluster.py            # 聚类服务
│   │   ├── embedding.py          # 向量化服务
│   │   ├── llm.py                # LLM服务
│   │   ├── ocr.py                # OCR服务
│   │   └── log.py                # 日志处理服务
│   ├── parser/                    # 解析器
│   │   ├── parser.py             # 日志解析器
│   │   └── log_feature.py        # 日志特征定义
│   ├── sqlite/                    # 数据库层
│   │   ├── sqlite.py             # SQLite异步封装
│   │   ├── manager/              # 数据管理器
│   │   │   ├── task.py
│   │   │   └── log_parse_result.py
│   ├── schemas/                   # 数据模型
│   │   ├── task.py
│   │   ├── log.py
│   │   ├── cluster.py
│   │   └── config.py
│   ├── enum/                      # 枚举定义
│   │   ├── task.py
│   │   ├── log.py
│   │   └── ocr.py
│   ├── config/                    # 配置管理
│   │   └── config.py
│   ├── prompt/                    # 提示词模板
│   │   └── log_detection.py
│   ├── server.py                  # MCP服务器入口
│   └── common/                    # 公共资源
│       └── config.toml            # 配置文件
├── test/                          # 测试文件
│   └── test_worker.py
└── README.md
```

### 数据流

1. **任务创建**：前端调用 `create_log_parse_task` API 创建日志检测任务
2. **任务调度**：Task Service 将任务状态设置为 PENDING
3. **任务监听**：独立进程监听并处理待处理任务
4. **Worker执行**：根据任务类型选择对应的 Worker 执行检测
5. **结果存储**：检测结果存储到 SQLite 数据库
6. **结果查询**：前端调用 `get_task_result` API 查询结果

---

## 核心功能

### 1. 多种检测方法

系统支持三种日志异常检测方法：

#### 基于关键词检测 (LogDetectionBasedOnKeywordsWorker)
- 使用 jieba 中文分词进行关键词匹配
- 计算 Jaccard 相似度
- 结合日志类型的情感得分
- 适用于已知异常模式的场景

#### 基于聚类检测 (LogDetectionBasedOnClusteringWorker)
- 使用 FAISS 构建向量索引
- DBSCAN 聚类识别离群点
- 层次化聚类减少内存占用
- 适用于未知异常模式的场景

#### 基于LLM检测 (LogDetectionBasedOnLLMWorker)
- 使用 OpenAI API 进行智能分析
- 基于上下文的异常判断
- 支持自定义查询语句
- 适用于复杂场景和精确检测

### 2. 日志解析

- 支持多种日志格式（文本、JSON、XML等）
- 支持图像日志（通过 OCR 识别）
- 自动日志类型分类
- 日志模板提取和脱敏

### 3. 任务管理

- 任务状态管理（PENDING、RUNNING、SUCCESSFUL、FAILED）
- 任务生命周期管理
- 异步任务处理
- 进程隔离执行

### 4. 向量化与检索

- 使用 FAISS 构建高效向量索引
- 支持余弦相似度和欧氏距离计算
- 批量向量化处理
- 相似日志召回

### 5. 聚类分析

- DBSCAN 密度聚类
- KMeans 聚类
- 层次化聚类策略
- 离群点识别

---

## 使用说明

### 环境准备

#### 系统要求

- Python 3.9+
- Linux/Windows/macOS

#### 安装依赖

```bash
cd /home/zjq/euler-copilot-rag/log_detection/src
pip install -r requirements.txt
```

#### 配置文件

创建配置文件 `src/common/config.toml`：

```toml
# 日志解析配置主文件
# 日志解析方法，可选值：base、log_detection_base_on_keywords、log_detection_base_on_clustering、log_detection_base_on_llm
LOG_PARSE_METHOD = "log_detection_base_on_llm"

# SQLite数据库文件路径
SQL_LITE_DB_PATH = "log_detection_multi_process.db"

# Embedding模型配置
[EMBEDDING_MODEL]
EMBEDDING_PROVIDER = "openai"
EMBEDDING_END_POINT = "https://api.siliconflow.cn/v1/embeddings"
EMBEDDING_API_KEY = ""
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
EMBEDDING_BATCH_SIZE = 8192

# LLM模型配置
[LLM_MODEL]
LLM_PROVIDER = "openai"
LLM_END_POINT = "https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_API_KEY = ""
LLM_MODEL_NAME = "qwen3-max"
LLM_MAX_TOKENS = 32000
LLM_BATCH_SIZE = 32

# 服务运行配置
[RUN_CONFIG]
RUN_HOST = "0.0.0.0"
RUN_PORT = 12144

# OCR配置
[OCR_CONFIG]
OCR_METHOD = "offline" # 可选值：offline、online
OCR_API_URL = ""
```

### 启动服务

```bash
cd ../euler-copilot-rag/log_detection
export PYTHONPATH=$(pwd)
python server.py
```

服务启动后，MCP Server 将在配置的端口上运行。

### API 使用

#### 1. 创建日志解析任务

**接口**: `create_log_parse_task`

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_type | string | 否 | 任务类型：base、log_detection_base_on_keywords、log_detection_base_on_clustering、log_detection_base_on_llm |
| query | string | 否 | 查询语句，描述异常现象 |
| file_path_list | array | 是 | 日志文件路径列表 |
| max_anomaly_log_count | int | 否 | 最大异常日志数量，默认64 |
| anomaly_keywords | array | 否 | 异常关键词列表 |
| time_start | string | 否 | 时间范围起始，格式：YYYY-MM-DD HH:MM |
| time_end | string | 否 | 时间范围结束，格式：YYYY-MM-DD HH:MM |

**返回**:

```json
{
  "task_id": "uuid4格式的任务ID"
}
```

**示例**:

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

#### 2. 获取任务信息

**接口**: `get_task_message`

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |

**返回**:

```json
{
  "task_id": "uuid4格式的任务ID",
  "task_name": "任务名称",
  "task_type": "任务类型",
  "completion_percent": 0.0-100.0,
  "status": "任务状态",
  "task_related_params": "json字符串",
  "created_at": "创建时间"
}
```

#### 3. 停止任务

**接口**: `stop_task`

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |

**返回**:

```json
{
  "success": true/false
}
```

#### 4. 获取任务结果

**接口**: `get_task_result`

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 任务ID |
| offset | int | 否 | 偏移量，分页查询 |
| limit | int | 否 | 返回数量，分页查询 |
| is_anomalous | bool | 否 | 是否只返回异常日志 |

**返回**:

```json
{
  "total": 总结果数量,
  "results": [
    {
      "id": "日志解析结果ID",
      "file_path": "日志文件路径",
      "task_id": "任务ID",
      "is_anomalous": true/false,
      "content": "日志内容",
      "anomaly_reason": "异常原因",
      "anomaly_score": 0.0-100.0
    }
  ]
}
```

### Python 客户端示例

```python
import requests
import json

# 配置
BASE_URL = "http://localhost:8000"

# 1. 创建任务
response = requests.post(f"{BASE_URL}/tools/create_log_parse_task", json={
    "file_path_list": ["/path/to/log1.log", "/path/to/log2.log"],
    "query": "网络连接异常",
    "anomaly_keywords": ["error", "failed", "timeout"],
    "max_anomaly_log_count": 10
})
task_id = response.json()["task_id"]
print(f"任务ID: {task_id}")

# 2. 查询任务状态
response = requests.post(f"{BASE_URL}/tools/get_task_message", json={
    "task_id": task_id
})
task_info = response.json()
print(f"任务状态: {task_info['status']}")
print(f"完成度: {task_info['completion_percent']}%")

# 3. 获取任务结果
response = requests.post(f"{BASE_URL}/tools/get_task_result", json={
    "task_id": task_id,
    "is_anomalous": True,
    "limit": 10
})
results = response.json()
print(f"异常日志数量: {results['total']}")
for log in results['results']:
    print(f"内容: {log['content']}")
    print(f"异常分数: {log['anomaly_score']}")
    print(f"异常原因: {log['anomaly_reason']}")
```

### 命令行测试

```bash
# 运行测试
cd /home/zjq/euler-copilot-rag/log_detection
python test/test_worker.py

# 运行特定测试
python test/test_worker.py -k test_cal_keyword_similarity
```

---

## 测试说明

### 测试框架

系统使用 pytest 作为测试框架，支持异步测试（pytest-asyncio）。

### 测试文件

测试文件位于 `test/test_worker.py`，包含以下测试类别：

#### 1. Worker 测试

- `TestLogDetectionBasedOnKeywordsWorker` - 基于关键词Worker测试
  - `test_cal_keyword_similarity` - 关键词相似度计算
  - `test_cal_keyword_similarity_chinese` - 中文关键词相似度
  - `test_cal_keyword_similarity_no_match` - 无匹配测试
  - `test_cal_cosine_similarity` - 余弦相似度计算
  - `test_cal_cosine_similarity_no_match` - 无匹配余弦相似度

- `TestLogDetectionBasedOnClusteringWorker` - 基于聚类Worker测试
  - `test_cal_cosine_similarity` - 余弦相似度计算
  - `test_cal_cosine_similarity_no_match` - 无匹配测试
  - `test_cal_keyword_similarity` - 关键词相似度计算
  - `test_cal_keyword_similarity_chinese` - 中文关键词相似度

- `TestLogDetectionBasedOnLLMWorker` - 基于LLM Worker测试
  - `test_cal_keyword_similarity` - 关键词相似度计算
  - `test_cal_keyword_similarity_chinese` - 中文关键词相似度

#### 2. 聚类服务测试

- `TestClusterService` - 聚类服务测试
  - `test_single_DBSCAN` - 单次DBSCAN聚类
  - `test_single_DBSCAN_all_in_cluster` - 全部在簇中测试
  - `test_single_DBSCAN_all_outliers` - 全部离群点测试
  - `test_single_KMeans` - 单次KMeans聚类
  - `test_single_KMeans_all_in_cluster` - 全部在簇中测试
  - `test_single_KMeans_empty_clusters` - 空簇测试

#### 3. 任务服务测试

- `TestTaskService` - 任务服务测试
  - `test_process_successful_or_failed_tasks_empty` - 空任务处理
  - `test_process_pending_tasks_empty` - 空待处理任务

#### 4. 数据模型测试

- `TestLogModel` - 日志模型测试
  - `test_create_log_model` - 创建日志模型
  - `test_log_model_with_anomaly` - 异常日志模型
  - `test_log_model_with_template` - 模板日志模型
  - `test_log_model_with_time` - 时间日志模型
  - `test_log_model_with_all_fields` - 完整字段日志模型

- `TestTaskModel` - 任务模型测试
  - `test_create_task_model` - 创建任务模型
  - `test_task_model_with_pid` - 带进程ID任务模型
  - `test_task_model_with_time_range` - 时间范围任务模型
  - `test_task_model_with_all_fields` - 完整字段任务模型

#### 5. 集成测试

- `TestIntegration` - 集成测试
  - `test_full_task_workflow` - 完整任务流程
  - `test_worker_run_and_stop` - Worker运行和停止

### 运行测试

```bash
# 运行所有测试
cd /home/zjq/euler-copilot-rag/log_detection
python test/test_worker.py

# 运行特定测试类
python test/test_worker.py -k TestClusterService

# 运行特定测试
python test/test_worker.py -k test_cal_keyword_similarity

# 显示详细输出
python test/test_worker.py -v

# 显示打印信息
python test/test_worker.py -s
```

### 测试覆盖率

测试覆盖以下功能：

- ✅ Worker 类初始化和注册
- ✅ 关键词相似度计算（Jaccard）
- ✅ 余弦相似度计算
- ✅ 中文分词处理
- ✅ DBSCAN 聚类
- ✅ KMeans 聚类
- ✅ 空数据处理
- ✅ 任务生命周期管理
- ✅ 数据模型创建和验证
- ✅ 完整任务流程

### 测试配置

测试使用 SQLite 内存数据库，测试完成后自动清理。

---

## 常见问题

### 1. 如何选择检测方法？

- **基于关键词**: 适用于已知异常模式、需要快速检测的场景
- **基于聚类**: 适用于未知异常模式、需要发现新异常的场景
- **基于LLM**: 适用于复杂场景、需要精确判断的场景

### 2. 如何优化检测性能？

- 调整 `max_anomaly_log_count` 参数限制返回数量
- 使用时间范围过滤减少处理日志量
- 调整聚类参数（eps、min_samples）优化聚类效果

### 3. 如何添加新的日志格式？

在 `src/parser/log_feature.py` 中添加新的日志类型定义：

```python
LogTypeEnum.NEW_LOG = LogTypeFeature(
    name="new_log",
    keywords_regex_and_scores={
        "normal": {"pattern": score},
        "anomalous": {"pattern": score}
    },
    capture_patterns={
        LogValueEnum.IP.value: r"pattern",
        LogValueEnum.TIMESTAMP.value: r"pattern"
    }
)
```

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 代码规范

- 遵循 PEP 8 代码规范
- 添加必要的注释和文档
- 确保测试通过

### 提交流程

1. Fork 仓库
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

---

## 许可证

本项目采用木兰许可（UPL-1.0） - 详见 [LICENSE](LICENSE) 文件。

---

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件至项目维护者
