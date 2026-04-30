# create-skill

## 触发条件

当用户明确提出"沉淀为 Skill"、"保存为技能"、"记录工作流程"等意图，或智能体完成一项复杂任务后主动询问是否沉淀时，触发本能力。

## 前置约束

- 所有新建 Skill 必须存放至 `data/skill_hub/` 目录下，以独立子目录形式组织。
- Skill 目录内必须包含 `skill_def.md` 文件，推荐包含 `database.yaml`（评测用例）、`references/`（参考资料）、`scripts/`（辅助脚本）等可选内容。
- 禁止在 skill_def.md 内容中包含恶意代码、敏感数据、隐私信息。

## 执行流程

### 第一步：检索查重

在创建新 Skill 之前，必须先执行检索查重，避免重复建设。

1. 使用 CLI 搜索现有 Skill：

```bash
cd scripts
uv run experience-skill search-experiences \
    --query "<待创建Skill的核心关键词>" \
    --type SKILL \
    --top-k 5
```

1. 若搜索结果中存在高度相似（名称相近、关键词重叠、描述雷同）的 Skill，应：
   - **优先推荐合并（merge-skill）**：告知用户存量资源情况，建议执行合并而非新建。
   - **其次推荐优化（optimize-skill）**：若存量 Skill 内容过时或质量不佳，建议以优化方式更新。
   - 仅当用户明确坚持新建且存量不构成冗余时，才继续创建流程。

### 第二步：生成 skill_def.md

若查重通过（无相似 Skill 或用户确认新建），按以下规范生成 `skill_def.md`：

1. **YAML front matter**（必须包含）：

```yaml
---
name: <skill-name>
description: <一句话描述 Skill 的功能、触发场景、输入输出要求>
keywords: [关键词1, 关键词2, 关键词3]
---
```

1. **正文结构**（推荐包含以下章节）：

```markdown
# <Skill 标题>
## 约束
- 描述 Skill 执行的约束条件、适用范围、环境要求等。

## 流程
- 列出清晰的执行步骤，每步可操作、可验证。

## 能力
- 描述 Skill 提供的核心能力 / 功能点。

## 结构
- 说明 Skill 目录结构、依赖文件等。

## 规则
- 补充执行规则、注意事项、边界条件。
```

1. **描述规范**：
   - `description` 字段需用中文撰写，清晰说明三点：Skill 的功能、触发语境、使用方式。
   - `keywords` 字段需选取 3-8 个最能代表 Skill 核心功能的关键词。

### 第三步：生成 database.yaml（可选）

在 Skill 目录下创建 `database.yaml`，包含评测用例：

```yaml
- testcase1:
    question: <测试问题>
    answer: <预期答案>
- testcase2:
    question: <测试问题>
    answer: <预期答案>
```

### 第四步：注册入库

将 Skill 目录注册到 SQLite 经验库：

```bash
cd scripts
uv run experience-skill add-experiences \
    --type SKILL \
    --source "<skill_hub下的子目录绝对路径>"
```

此命令会：

- 读取 `skill_def.md` 的 YAML front matter，提取 name、description、keywords。
- 检查 source 路径是否已存在（防重复）。
- 将 Skill 元信息写入 `experience_table`，启用 FTS5 全文索引。
- 将 keywords 写入 `keyword_table`，支持关键字过滤检索。

### 第五步：验证

注册成功后，执行一次检索验证 Skill 可被召回：

```bash
uv run experience-skill search-experiences \
    --query "<Skill核心关键词>" \
    --type SKILL \
    --top-k 3
```

确认新创建的 Skill 出现在搜索结果中。

## 错误处理

- 若 `skill_def.md` 不存在于 source 目录，CLI 会报 `FileNotFoundError`，需检查路径。
- 若 source 路径已注册过，CLI 会报 `ValueError`，需更换路径或先删除旧记录。
- 若 simple tokenizer 扩展未编译，需先执行 `bash scripts/src/experience_skill_cli/tokenizer/build.sh`。
