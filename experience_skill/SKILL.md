---
name: experience-skill
description: >
  用于统一管理用户工作经验的能力组件。用户经验分为两类：Skill 与 Wiki。
  Skill 聚焦个人标准化工作流程的沉淀描述；Wiki 是工作过程中查阅的网页、文档等资料的提炼总结。
  本组件完整提供 Skill 与 Wiki 的创建、评估、优化、合并、检索全生命周期管理能力，为智能体能力持续迭代升级提供底层支撑。
---

# experience-skill

## 目录结构

experience-skill 完整目录结构如下：

```
experience_skill/
├── abilities
│   ├── skill
│   │   ├── create-skill.md
│   │   ├── eval-skill.md
│   │   ├── find-skill.md
│   │   ├── merge-skill.md
│   │   └── optimize-skill.md
│   └── wiki
│       ├── create-wiki.md
│       ├── eval-wiki.md
│       ├── find-wiki.md
│       ├── merge-wiki.md
│       └── optimize-wiki.md
├── scripts
│   ├── pyproject.toml
│   ├── uv.lock
│   └── src
│       └── experience_skill_cli
│           ├── common
│           │   └── exprience.py
│           ├── cli.py
│           ├── console.py
│           ├── manager
│           │   ├── experience_manager.py
│           │   └── keyword_manager.py
│           ├── schema
│           │   ├── enum.py
│           │   └── exprience.py
│           ├── service
│           │   └── experience_service.py
│           ├── sqlite.py
│           ├── templates
│           │   └── index.html
│           ├── tokenizer
│           │   ├── build.sh
│           │   └── libsimple
│           └── web_server.py
├── example
│   ├── skill
│   │   └── example_skill
│   │       ├── skill_def.md
│   │       ├── database.yaml
│   │       ├── scripts/
│   │       ├── references/
│   │       └── assets/
│   └── wiki
│       └── example.md
├── data                          # 用户数据目录（不纳入版本控制）
│   ├── experience.db             # SQLite 数据库
│   ├── skill_hub                 # 用户 Skill 仓库
│   └── wiki_hub                  # 用户 Wiki 仓库
├── SKILL.md                      # 本组件自身的 Skill 入口
└── .gitignore
```

目录说明：

1. `abilities`：核心能力目录，承载 Skill、Wiki 两类资源的创建、评估、检索、合并、优化能力定义；
2. `scripts`：Python 项目目录，使用 `uv` 管理依赖。`pyproject.toml` 为项目配置，通过 `uv run experience-skill` 调用，`uv.lock` 为依赖锁定文件。所有 Python 源码位于 `src/experience_skill_cli/` 包内，`cli.py` 为主命令实现，其余模块包括核心服务、数据库交互、Web 服务、控制台工具等；
3. `example`：示例 Skill 与 Wiki，作为项目参考模板纳入版本控制；
4. `data`：用户数据目录（已加入 `.gitignore`），存放 SQLite 数据库、`skill_hub`（用户 Skill 仓库）和 `wiki_hub`（用户 Wiki 仓库）。

## 约束规范

- 所有新建 Skill、Wiki 必须统一存放至 `data/skill_hub`、`data/wiki_hub` 专属目录，禁止自定义存储路径；
- Skill 采用 `skill_def.md`（YAML front matter + Markdown 正文）格式，内容结构遵循 [Agent Skills 规范](https://agentskills.io/specification)。包含 name、description 等必需字段，以及 license、compatibility、metadata（含 keywords）、allowed-tools 等可选字段；
- Skill 目录结构：主文件 `skill_def.md`（必需）、`scripts/`（可执行脚本）、`references/`（参考文档）、`assets/`（静态资源）、`database.yaml`（评测用例）；
- 使用 `skill_def.md` 而非 `SKILL.md` 命名，是为了防止部分 Agent 框架通过 `~/.agents/skills/` 递归扫描自动发现并加载 skill_hub 中的 Skill。格式完全遵循 Agent Skills 规范，仅文件名不同；
- Wiki 采用 `.md`（YAML front matter + Markdown 正文）格式，与 Skill 相同的文件结构，包含 name、description、keywords、references 等元信息；
- 沉淀的 Skill 禁止包含恶意代码、敏感数据、隐私信息及违规内容；
- Wiki 内容仅限提炼、整合工作场景内查阅的网页、文档等资料，不得混入无关冗余信息；
- 所有 Skill 与 Wiki 需满足统一质量规范，必经评估与优化流程，杜绝明显错误、逻辑漏洞与无效内容。

## CLI & Web 使用方式

组件提供 **命令行（CLI）** 与 **Web 管理界面** 两种交互方式，底层共享同一套 Service 层与 SQLite 数据库。

### 环境准备

> 以下命令假设当前工作目录为 skill 安装根目录（即本 `SKILL.md` 所在目录）。

本组件使用 `uv` 管理 Python 依赖。首次使用前执行：

```bash
uv sync
```

### CLI 命令概览

所有 CLI 命令需在 `scripts/` 目录下通过 `uv run experience-skill` 执行：

| 子命令               | 用途                                 |
| -------------------- | ------------------------------------ |
| `sync`               | 同步 data/ 中所有经验到数据库 |
| `add-experiences`    | 添加 Skill/Wiki 经验到数据库         |
| `list-experiences`   | 分页列出经验，支持类型/名称/热门过滤 |
| `search-experiences` | 全文检索经验（FTS5 + 关键字）        |
| `delete-by-ids`      | 按 ID 列表删除经验                   |
| `delete-by-source`   | 按来源路径删除经验                   |
| `delete-all`         | 清空所有经验数据                     |
| `web`                | 启动 Web 管理界面                    |

查看子命令详细参数：

```bash
uv run experience-skill <子命令> --help
```

### Web 管理界面

通过 `web` 子命令启动 FastAPI Web 服务，提供图形化管理界面：

```bash
uv run experience-skill web
```

- **自动打开浏览器**：在 macOS 或有 `DISPLAY`/`WAYLAND_DISPLAY` 的 Linux 环境下自动调用系统浏览器打开 `http://127.0.0.1:8080`。
- **纯 TTY 环境**：无图形环境时仅显示访问链接，用户手动复制到浏览器打开。
- 自定义端口：`uv run experience-skill web --port 9090`
- 禁用自动打开：`uv run experience-skill web --no-browser`

Web 页面功能：

- **类型筛选**：全部 / Skill / Wiki 标签切换
- **名称搜索**：模糊匹配经验名称
- **全文检索**：基于 FTS5 的关键词语义搜索
- **热门筛选**：仅查看热门经验（Top 20）
- **分页浏览**：上一页 / 下一页翻页

## 核心能力

组件针对 Skill、Wiki 分别提供**创建、评估、检索、合并、优化**五大标准化能力，具体说明如下：

### Skill 能力

- **create-skill**：从对话会话中沉淀可复用工作流程，生成标准化 Skill；创建前自动检索查重，避免资源重复建设。
- **eval-skill**：基于 Skill 内置评测集开展质量核验，综合评估实用性、准确性、完整性与可读性。
- **find-skill**：结合 SQLite 关键字检索 + 全文检索，快速定位目标 Skill，适配海量资源检索场景。
- **merge-skill**：检索识别相似 Skill，支持多份同质内容合并整合，统一梳理内容、剔除重复片段。
- **optimize-skill**：依据质量评估报告迭代优化，更新过期流程、修复代码问题、完善评测用例，保障长期可用性。

### Wiki 能力

- **create-wiki**：对工作查阅的网页、文档等资料进行提炼精简，沉淀为标准化 Wiki；创建前自动查重，减少冗余沉淀。
- **eval-wiki**：通过随机抽样、问答核验等方式，校验 Wiki 召回命中率，同时评估内容实用性、准确性与可读性。
- **find-wiki**：依托数据库检索与全文检索能力，快速筛选、定位所需 Wiki 文档。
- **merge-wiki**：识别同质化 Wiki 资源，支持多文档合并整编，保留有效内容、剔除重复信息。
- **optimize-wiki**：根据评估结果迭代优化，包含错误修正、内容补全、格式规整、可读性提升等优化动作。

## 执行规则

1. 单次工作任务结束后，主动询问用户，确认是否沉淀本次工作流程为 Skill、或整合参考资料为 Wiki；
2. 工作执行过程中，若检索不到可用资源、或现有 Skill/Wiki 存在缺陷，主动提示用户开展评测与优化；
3. 新建 Skill 或 Wiki 前，必须先执行检索查重；存在相似资源时，优先推荐合并、优化，而非重复新建；
4. 当存量资源体量较大时，定期主动提醒用户合并同质化内容，精简资源库、降低冗余维护成本。
