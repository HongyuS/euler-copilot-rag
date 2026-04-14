# 创建技能（Create）

## 目标

将对话中可复用的工作流沉淀为新 skill；创建前强制查重，避免重复。

## 触发条件

- 用户明确说要创建 skill
- 用户未明说，但当前对话已经出现稳定、可复用、多步骤流程
- 用户任务完成后命中“技能化检查”条件（见 `SKILL.md`）

## 必须规则

1. 先读取 `abilities/find-skill.md` 执行查找与查重（**查重仅对比当前已激活技能列表**，不得扫磁盘、不得调用 RAG 知识库 MCP）。
2. 若已有高度相似 skill（建议阈值 >= 70%），不新建，转入优化或合并。
3. 仅在确无可复用技能时创建新 skill。

## 执行步骤

### 步骤 1：提炼需求

至少确认：

- 任务目标（skill 到底做什么）
- 触发语境（用户会怎么说）
- 输入输出（文件、格式、验收标准）

### 步骤 2：查重决策

- 单个强匹配：转 `abilities/optimize-skill.md`
- 多个重叠匹配：转 `abilities/merge-skills.md`
- 无匹配：继续创建

### 步骤 3：创建基础结构

```text
<skill-name>/
├── SKILL.md
├── evals/evals.json
├── references/        (可选)
└── scripts/           (可选)
```

`SKILL.md` 要包含：

- frontmatter: `name` + `description`
- 使用时机（写进 description，不只写正文）
- 执行步骤（简洁、可操作）
- 输出规范

### 步骤 4：编写 SKILL.md

根据结果填写：

- **name**：技能标识符（通常应与目录名一致）
- **description**：何时触发、做什么。这是技能被发现和选用的主要依据——既要写技能做什么，也要写**具体在哪些情形下使用**。所有「何时使用」的信息放在这里，不要只写在正文里。注意：代理仍可能**少加载**技能（该用时没用上）。为缓解这一点，description 可以写得略**主动**一些。例如不要只写「如何搭建简单快速的仪表盘展示内部数据」，可以写成「如何搭建……。只要用户提到仪表盘、数据可视化、内部指标，或希望展示任何公司业务数据，即使没明确说『仪表盘』，也应使用本技能。」
- **compatibility**：所需工具、依赖（可选）
- **其余技能正文**

样例如下，严格按照样例编写，不然无法被检测到：
```text
---
name: skill-name
description: skill-description
---
其余技能正文
```

### 步骤 5：最小评测闭环

1. 在 `evals/evals.json` 写 2-3 条真实测试提示词
2. 跑 with-skill 与 baseline（能并行就并行）
3. 用脚本生成可审阅结果：

```bash
python eval-viewer/generate_review.py <workspace>/iteration-N --skill-name "<name>"
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

4. 若用户反馈存在问题，立刻进入优化流程

## 注意

- 这是创建能力，不在此文档内展开优化/合并细则。
- 若环境不支持并行或浏览器，使用静态 HTML 或对话内审阅，但流程顺序不变。
- 若需要打包分发：`python -m scripts.package_skill <path/to/skill-folder> [output-directory]`。
- 生成 `evals/evals.json`、`eval_metadata.json` 时，字段结构必须对照 `references/schemas.md`。
- 若进入断言打分阶段，先读取 `agents/grader.md` 再写 `grading.json`。
