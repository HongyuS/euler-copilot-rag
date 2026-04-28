# experience-skill

经验技能管理组件，用于统一管理用户工作经验的能力沉淀。支持 **Skill**（标准化工作流程）与 **Wiki**（资料文档提炼）两类资源的全生命周期管理，为智能体能力持续迭代升级提供底层支撑。

## 功能特性

- **双模经验管理**：支持 Skill（工作流程技能）与 Wiki（资料知识库）两类经验资源
- **全生命周期覆盖**：创建、评估、检索、合并、优化五大标准化能力
- **高性能全文检索**：基于 SQLite + FTS5 + `simple` 中文/拼音分词器，支持模糊搜索与语义匹配
- **热门经验追踪**：自动标记高频使用经验，支持按热门度筛选与排序
- **CLI 命令行工具**：提供完整的命令行接口，便于集成到自动化流水线

## 目录结构

```
experience_skill/
├── abilities/                 # 核心能力定义
│   ├── skill/                 # Skill 能力：创建、评估、检索、合并、优化
│   │   ├── create-skill.md
│   │   ├── eval-skill.md
│   │   ├── find-skill.md
│   │   ├── merge-skill.md
│   │   └── optimize-skill.md
│   └── wiki/                  # Wiki 能力：创建、评估、检索、合并、优化
│       ├── create-wiki.md
│       ├── eval-wiki.md
│       ├── find-wiki.md
│       ├── merge-wiki.md
│       └── optimize-wiki.md
├── scripts/                   # 业务逻辑实现
│   ├── main.py                # CLI 入口
│   ├── sqlite.py              # SQLite 数据库封装（含 FTS5 全文检索）
│   ├── service/
│   │   └── experience_service.py   # 核心服务（增删改查、搜索）
│   ├── manager/
│   │   ├── experience_manager.py   # 数据库操作层
│   │   └── keyword_manager.py      # 关键词管理
│   ├── schema/
│   │   └── exprience.py            # Pydantic 数据模型
│   ├── ENUM/
│   │   └── exprience.py            # 枚举定义（类型、状态）
│   └── tokenizer/
│       └── build.sh                # simple 分词器编译脚本
├── skill_hub/                 # Skill 资源仓库（示例）
│   └── exmaple_skill/
│       ├── SKILL.md
│       └── database.yaml
├── wiki_hub/                  # Wiki 资源仓库（示例）
│   └── example.yaml
└── README.md
```

## 快速开始

### 1. 编译 simple 分词器扩展

全文检索依赖 `simple` 分词器（支持中文与拼音分词），首次使用前需编译：

```bash
bash scripts/tokenizer/build.sh
```

脚本会自动下载最新 Release 源码并编译，若本地已存在 `v0.7.1.tar.gz` 则直接解压编译。

### 2. 安装依赖

```bash
pip install pyyaml pydantic
```

### 3. 使用 CLI

```bash
# 添加 Skill 经验
python scripts/main.py add-experiences --type SKILL --source skill_hub/exmaple_skill

# 添加 Wiki 经验
python scripts/main.py add-experiences --type WIKI --source wiki_hub/example.yaml

# 列出所有经验
python scripts/main.py list-experiences

# 按类型与名称过滤
python scripts/main.py list-experiences --type SKILL --name example

# 全文检索（支持中文/拼音）
python scripts/main.py search-experiences --query "数据库优化" --type SKILL --top-k 5

# 按 ID 删除
python scripts/main.py delete-by-ids --ids <uuid1> <uuid2>

# 按来源路径删除
python scripts/main.py delete-by-source --source skill_hub/exmaple_skill

# 清空所有数据
python scripts/main.py delete-all
```

## 核心概念

### Skill（技能）

聚焦个人标准化工作流程的沉淀描述。每个 Skill 以目录形式存放，目录内需包含：

- `SKILL.md`：技能定义文档（YAML Front Matter + Markdown）
- `database.yaml`（可选）：评测用例集

**SKILL.md 示例结构**：

```yaml
---
name: example-skill
description: 这是一个示例技能，用于展示 Skill 的标准文档结构。
keywords: [示例, 技能, 文档]
---

# Example Skill
## 约束
## 流程
## 能力
## 结构
## 规则
```

### Wiki（知识库）

工作过程中查阅的网页、文档等资料的提炼总结，以单个 YAML 文件形式存放：

```yaml
name: "Example Wiki Document"
author: ""
date: ""
description: ""
keywords:
  - keyword1
  - keyword2
content: ""
references:
  reference1:
    type: online
    name: 《example_1的入门简介》
    source: http://example.com
```

## 数据模型

| 字段 | 说明 |
|------|------|
| `id` | UUID，主键 |
| `type` | 类型：`skill` / `wiki` |
| `name` | 经验名称 |
| `description` | 描述文本（参与 FTS5 全文检索） |
| `status` | 状态：`existed` / `deleted`（软删除） |
| `is_hot` | 是否热门（高频使用时自动标记） |
| `source` | 来源路径 |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

## 检索机制

1. **关键词检索**：基于 `keyword_table` 的精确匹配，支持 `fields` 过滤
2. **全文检索**：基于 SQLite FTS5 + `simple` 分词器，支持中文、拼音混合查询
3. **双阶段召回**：
   - 第一阶段：使用 `simple_query()` 做 AND 语义精确查询
   - 第二阶段：若结果不足，使用标准 OR 语法做松散查询补全

## 约束规范

- 所有新建 Skill、Wiki 必须统一存放至 `skill_hub`、`wiki_hub` 目录，禁止自定义存储路径
- 沉淀内容禁止包含恶意代码、敏感数据、隐私信息及违规内容
- 新建前必须先执行检索查重；存在相似资源时，优先推荐合并、优化，而非重复新建
- 当存量资源体量较大时，定期合并同质化内容，精简资源库、降低冗余维护成本

## 能力说明

| 能力 | Skill | Wiki | 说明 |
|------|-------|------|------|
| 创建 | `create-skill` | `create-wiki` | 从对话或资料中沉淀标准化经验；创建前自动查重 |
| 评估 | `eval-skill` | `eval-wiki` | 基于评测集或抽样问答开展质量核验 |
| 检索 | `find-skill` | `find-wiki` | SQLite 关键字检索 + FTS5 全文检索 |
| 合并 | `merge-skill` | `merge-wiki` | 识别相似资源，多份内容合并整编 |
| 优化 | `optimize-skill` | `optimize-wiki` | 依据评估报告迭代优化，修复错误、补全内容 |
