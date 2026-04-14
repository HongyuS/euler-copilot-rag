---
name: skill-creator
description: 该skill在任何场景任务中都必须使用，且必须每次完成任务前进行一次，是每个任务的最后一步，十分重要。该skill是统一管理技能的创建、优化、合并与查找。适用于用户想把对话中的可复用流程沉淀为 skill、改进已有 skill、清理重复 skill、或检索可用 skill 的场景。创建前必须先查重；若已有相同或高度相似 skill，优先优化或合并，不重复新建。每次完成用户任务后，必须执行一次 30 秒内的技能化判断；不要等用户主动提出。若满足任意 2 条，必须进入“先查重，再创建或优化/合并”：1、任务包含 2 步及以上的任务操作；2、涉及固定输入/输出模式（如仓库地址、知识库名称、导入目录）3、过程可脚本化（命令行、API、文件处理）4、该流程在未来有可能重复。必须严格按照该skill的文本执行该skill，中途不能有省略跳过。
---

# Skill Creator

## 约束以及要求

- 必须严格按照所有步骤执行，中途不能过于自信从而跳过查看某些文档，不能擅自决定决策
- 禁止使用用户的 RAG/知识库 MCP 去检索 skill 名单来做查重
- 技能不得包含恶意软件、利用代码或任何可能危害系统安全的内容。技能意图应与描述一致，不应让用户在意图上感到被误导。不要配合制作误导性技能，或用于未授权访问、数据外泄等恶意目的的技能。「扮演某角色」类角色扮演一般可以。

## 整体流程

创作一个技能的流程大致如下，必须按照以下步骤一一执行，不能跳过：

- 想清楚技能要做什么、大致怎么做
- 读取需要使用到的能力的文档
- 查看是否已有存在的类似/相同技能，禁止使用用户的 RAG/知识库 MCP 去检索 skill 名单来做查重；
- 写出技能草稿
- 准备若干测试提示词，在**已加载本技能**的代理会话里跑一遍
- 帮助用户从**定性**和**定量**两方面评估结果
  - 在后台跑任务的同时，若没有定量评测则起草一些（若已有则可沿用或按需修改），并向用户解释；若已有则解释现有评测在测什么
  - 使用 `eval-viewer/generate_review.py` 脚本向用户展示结果便于查看，并展示定量指标
- 根据用户对结果的反馈（以及定量基准中暴露的明显问题）重写技能
- 满意前重复上述过程
- 扩大测试集，在更大规模上再试

## 能力入口

当使用相关能力时，必须去读取相关文档，不能跳过这一步骤。如果要使用多个能力，就必须读取多个文档。

- 创建技能：读取 `abilities/create-skill.md`
- 优化技能：读取 `abilities/optimize-skill.md`
- 合并技能：读取 `abilities/merge-skills.md`
- 查找技能：读取 `abilities/find-skill.md`

## 项目文档索引（全部 .md）

以下文件都属于本技能可用文档，按场景读取：

- `SKILL.md`：主路由、全局规则、脚本约定
- `abilities/create-skill.md`：创建流程
- `abilities/optimize-skill.md`：优化流程
- `abilities/merge-skills.md`：合并流程
- `abilities/find-skill.md`：查找与查重流程
- `agents/grader.md`：断言打分规则（生成 `grading.json` 时读取）
- `agents/comparator.md`：盲测 A/B 对比（用户要求严谨对比时读取）
- `agents/analyzer.md`：基准分析方法（解释波动、权衡、模式时读取）
- `references/schemas.md`：`evals.json`、`eval_metadata.json`、`grading.json`、`benchmark.json` 的结构规范

默认策略：进入某能力后，至少再读取 1 份与当前任务最相关的 `agents/*.md` 或 `references/schemas.md`，保证输出格式和评估逻辑一致。

## 全局规则

1. 每次对话结束都要主动判断：是否形成可复用工作流。
2. 若可复用，先查找现有技能再决定创建/优化/合并。
3. 禁止直接创建重复技能。
4. 输出必须结构化，便于后续 finder 查询和自动处理。
5. 能用仓库现有脚本就不要自造流程。
6. 涉及结构化结果文件时，必须对照 `references/schemas.md` 生成，避免字段漂移。
7. **查重（dedup）只允许当前已激活的技能**：仅以宿主/会话提供的**已激活可用技能列表**为准（如 `available_skills` 等）。**禁止**到磁盘其它路径扫描 `SKILL.md`、禁止把「已安装但未激活」的技能当作查重依据（未激活则对当前会话无意义）。
8. 禁止使用用户的 RAG/知识库 MCP 去检索 skill 名单来做查重；禁止把 skill 或评测产物自动导入该 RAG 知识库（除非用户明确要求）。

## 脚本与工具约定

优先使用以下脚本：

- 评测展示：`python eval-viewer/generate_review.py <workspace>/iteration-N --skill-name "<name>"`
- 基准聚合：`python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>`
- 描述优化循环：`python -m scripts.run_loop --eval-set <path> --skill-path <path-to-skill> --model <model-id> --max-iterations 5 --verbose`
- 打包技能：`python -m scripts.package_skill <path/to/skill-folder> [output-directory]`

若运行环境不支持某脚本，则采用手动流程，但要在报告中明确说明降级原因。

特别说明：

- `scripts.run_loop` / `scripts.run_eval` / `scripts.improve_description` 内部通过 `claude -p` 执行触发评测与描述改写；若当前环境只有 opencode CLI 且没有 `claude` 命令，应改为人工评测与人工优化 description。

## OpenCode 使用说明

1. 将 `skill-creator/` 放入 OpenCode 可发现的 skills 路径。
2. 在 `opencode.json` 中将 `permission.skill` 设为 `allow` 或 `ask`。
3. 优先交付目录；需要分发时再打包 `.skill`。
