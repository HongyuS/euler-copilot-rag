# experience-skill

经验技能管理组件，用于统一管理用户工作经验的能力沉淀。支持 **Skill**（标准化工作流程）与 **Wiki**（资料文档提炼）两类资源的全生命周期管理，为智能体能力持续迭代升级提供底层支撑。

## 功能特性

- **双模经验管理**：支持 Skill（工作流程技能）与 Wiki（资料知识库）两类经验资源
- **全生命周期覆盖**：创建、评估、检索、合并、优化五大标准化能力
- **高性能全文检索**：基于 SQLite + FTS5 + `simple` 中文/拼音分词器，支持模糊搜索与语义匹配
- **热门经验追踪**：自动标记高频使用经验（同类型 Top 20），支持 LRU 淘汰与按热门度筛选
- **CLI 命令行工具**：提供完整的命令行接口，便于集成到自动化流水线
- **Web 管理界面**：基于 FastAPI 的图形化管理前端，支持类型筛选、关键词过滤、分页浏览

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
│   ├── main.py                # CLI 入口（argparse 子命令）
│   ├── sqlite.py              # SQLite 数据库封装（含 FTS5 全文检索、表结构定义）
│   ├── web_server.py          # FastAPI Web 服务
│   ├── pyproject.toml         # uv 项目配置与依赖声明
│   ├── templates/
│   │   └── index.html         # Web 管理界面（HTML + 原生 JS）
│   ├── service/
│   │   └── experience_service.py   # 核心服务（增删改查、搜索、合并、优化）
│   ├── manager/
│   │   ├── experience_manager.py   # 数据库操作层（CRUD + FTS5 检索）
│   │   └── keyword_manager.py      # 关键词管理（keyword_table）
│   ├── schema/
│   │   ├── exprience.py            # Pydantic 数据模型（Experience）
│   │   └── enum.py                 # 枚举定义（ExperienceType / ExperienceStatus）
│   ├── common/
│   │   └── exprience.py            # 公共常量（热门阈值等）
│   └── tokenizer/
│       ├── build.sh                # simple 分词器编译脚本（自动获取最新版本）
│       └── libsimple -> ...        # 编译产物软链接
├── skill_hub/                 # Skill 资源仓库
│   └── exmaple_skill/
│       ├── skill_def.md
│       └── database.yaml
├── wiki_hub/                  # Wiki 资源仓库
│   ├── example.md             # 示例 Wiki（YAML front matter + Markdown）
│   └── ...
├── SKILL.md                   # 组件自描述 Skill 文档
├── README.md
└── .gitignore
```

## 快速开始

### 1. 编译 simple 分词器扩展

全文检索依赖 `simple` 分词器（支持中文与拼音分词），首次使用前需编译：

```bash
bash scripts/tokenizer/build.sh
```

脚本会自动查询 GitHub 最新 Release 版本并下载源码编译。若本地已存在对应版本的 `.tar.gz` 包则直接解压编译，无需重复下载。

### 2. 安装依赖（推荐使用 uv）

本项目使用 `uv` 管理 Python 依赖，在 `scripts/` 目录下执行：

```bash
cd scripts
uv sync
```

也可使用传统 pip 方式安装：

```bash
pip install fastapi uvicorn pydantic pyyaml
```

### 3. 使用 CLI

所有 CLI 命令需在 `scripts/` 目录下通过 `uv run python main.py` 执行：

```bash
cd scripts

# 添加 Skill 经验
uv run python main.py add-experiences --type SKILL --source ../skill_hub/exmaple_skill

# 添加 Wiki 经验
uv run python main.py add-experiences --type WIKI --source ../wiki_hub/example.md

# 列出所有经验（分页）
uv run python main.py list-experiences

# 按类型与名称过滤
uv run python main.py list-experiences --type SKILL --name example

# 按热门筛选
uv run python main.py list-experiences --is-hot true

# 全文检索（支持中文/拼音）
uv run python main.py search-experiences --query "数据库优化" --type SKILL --top-k 5

# 按 ID 删除
uv run python main.py delete-by-ids --ids <uuid1> <uuid2>

# 按来源路径删除
uv run python main.py delete-by-source --source ../skill_hub/exmaple_skill

# 清空所有数据
uv run python main.py delete-all
```

### 4. 启动 Web 管理界面

```bash
cd scripts
uv run python main.py web
```

Web 服务默认监听 `127.0.0.1:8080`，在 macOS 或有图形环境的 Linux 下会自动打开浏览器。支持自定义端口：

```bash
uv run python main.py web --port 9090 --no-browser
```

Web 页面功能：
- **类型筛选**：全部 / Skill / Wiki 标签切换
- **名称搜索**：模糊匹配经验名称
- **关键词过滤**：多选关键词标签联动过滤
- **热门筛选**：仅查看热门经验
- **分页浏览**：上一页 / 下一页翻页

## 核心概念

### Skill（技能）

聚焦个人标准化工作流程的沉淀描述。每个 Skill 以目录形式存放，目录内需包含：

- `skill_def.md`：技能定义文档（YAML Front Matter + Markdown）
- `database.yaml`（可选）：评测用例集

**skill_def.md 示例结构**：

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

工作过程中查阅的网页、文档等资料的提炼总结，与 Skill 采用相同的 **YAML front matter + Markdown 正文** 格式，以单个 `.md` 文件形式存放。仅 YAML header 中的 name、description、keywords、references 元信息存入数据库用于检索，Markdown 正文不入库，检索命中后按 source 路径读取完整文件。

```yaml
---
name: "Example Wiki Document"
description: "示例 Wiki 文档，展示标准化 Wiki 的 YAML front matter + Markdown 正文格式"
keywords:
  - keyword1
  - keyword2
  - keyword3
references:
  - name: "《example_1 的入门简介》"
    type: online
    source: "http://example.com"
---

# Example Wiki Document

## 简介
这是 Wiki 文档的正文内容区域，使用标准 Markdown 格式编写。

## 参考资料
- [《example_1 的入门简介》](http://example.com)（在线）
```

## 数据模型

### experience_table（经验主表）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | TEXT (UUID) | 主键，唯一标识 |
| `type` | TEXT | 类型：`skill` / `wiki` |
| `name` | TEXT | 经验名称（来自 YAML front matter） |
| `description` | TEXT | 描述文本（参与 FTS5 全文检索，入库前过滤特殊字符） |
| `references` | TEXT | 参考资料 JSON 字符串（来自 YAML front matter） |
| `status` | TEXT | 状态：`existed` / `deleted`（软删除） |
| `is_hot` | BOOLEAN | 是否热门（高频使用时自动标记，同类型 Top 20） |
| `source` | TEXT | 来源路径（唯一键，防重复注册） |
| `created_at` | TEXT | 创建时间 |
| `updated_at` | TEXT | 更新时间 |

### keyword_table（关键词表）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | TEXT (UUID) | 主键 |
| `experience_id` | TEXT | 关联的经验 ID |
| `name` | TEXT | 关键词名称 |

### experience_fts（全文索引 - 虚拟表）

基于 FTS5 + `simple` 分词器，对 `description` 字段建立全文索引，通过触发器自动同步增删改操作。

## 检索机制

1. **关键词过滤**：基于 `keyword_table` 的精确匹配，支持 Web 界面多选关键词联动过滤
2. **全文检索**：基于 SQLite FTS5 + `simple` 分词器，对 `description` 字段进行中文、拼音混合查询
3. **双阶段召回**：
   - 第一阶段：使用 `simple_query()` 做 AND 语义精确查询（取 `top_k // 2` 条）
   - 第二阶段：若结果不足，使用标准 OR 语法做松散查询补全（去重后补足至 `top_k` 条）
4. **检索过滤**：支持按 `fields`（关键词字段）、`is_hot`（热门）、`banned_experience_ids`（排除）、`experience_ids`（限定范围）多维度过滤

## 热门经验机制

- 每次全文检索命中后，命中经验会调用 `update_hot_experience` 更新热度
- 同类型（Skill / Wiki 分别计数）最多保留 **20 条**热门经验
- 超出阈值时，按 `updated_at` 升序淘汰最早的热门记录（LRU 策略）
- 热门标记通过 `is_hot` 字段持久化存储，支持 CLI 和 Web 界面按热门筛选

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
