# optimize-skill

## 触发条件

当满足以下任一条件时触发本能力：

- `eval-skill` 质量评估发现 Skill 存在缺陷（内容过时、描述不清、代码有误、评测用例不足等）。
- 用户明确提出"优化这个 Skill"、"更新技能"、"改进 XX 技能"等意图。
- 定期维护存量 Skill，检查并修复过期流程、补充缺失内容。

## 执行流程

### 第一步：定位目标 Skill

通过 `find-skill` 或 `list-experiences` 定位待优化的 Skill：

```bash
# 按名称搜索
cd scripts
uv run python main.py search-experiences \
    --query "<Skill 名称或关键词>" \
    --type SKILL \
    --top-k 5

# 或浏览全量列表
uv run python main.py list-experiences --type SKILL
```

记录目标 Skill 的 ID（如 `a1b2c3d4-...`）和 source 路径。

### 第二步：读取现状 & 分析问题

读取 Skill 源文件，梳理优化点：

```bash
cat <skill_hub/目标Skill目录/SKILL.md>
cat <skill_hub/目标Skill目录/database.yaml>  # 如果存在
```

常见优化维度：

| 维度 | 典型问题 | 优化方向 |
| ---- | ------- | ------- |
| **准确性** | 流程步骤有误、API 已变更 | 修正为当前正确做法 |
| **完整性** | 缺少关键步骤、边界条件未覆盖 | 补充遗漏内容 |
| **可读性** | 描述不清、术语混乱、格式不规范 | 重写模糊段落，统一格式 |
| **时效性** | 引用的工具/库版本过时 | 更新为当前版本 |
| **评测覆盖** | database.yaml 缺失或用例不足 | 补充高质量评测用例 |
| **关键词** | 标签不准确、遗漏核心关键词 | 更新 keywords |

### 第三步：执行优化

根据问题分析结果，逐项改进：

#### 3a. 更新 SKILL.md 内容

直接编辑 `skill_hub/<Skill 目录>/SKILL.md`：

- 修正 front matter 中的 `name`、`description`、`keywords`（如有变更）。
- 更新正文各章节内容。

#### 3b. 更新 database.yaml（可选）

补充或修正评测用例，确保覆盖核心场景和边界条件。

#### 3c. 同步 DB 元信息

调用 Service 层 `optimize_experience()` 方法，将修改后的元信息同步到 SQLite：

```python
from service.experience_service import ExperienceService

updated = ExperienceService.optimize_experience(
    experience_id="<Skill ID>",
    name="<新名称，不需要改则传 None>",
    description="<新描述，不需要改则传 None>",
    keywords=["<新关键词列表>"],
)
```

此方法会自动：

- 更新 `experience_table` 中对应记录的 name / description（触发 FTS 索引更新）。
- 若传入 keywords，全量替换 `keyword_table` 中该 Skill 的关键词（先删后插）。
- 更新 `updated_at` 时间戳。

### 第四步：验证

```bash
# 确认 DB 记录已更新
uv run python main.py list-experiences --type SKILL --name "<Skill 名称>"

# 确认优化后的 Skill 可被检索召回
uv run python main.py search-experiences \
    --query "<优化后的核心关键词>" \
    --type SKILL \
    --top-k 5
```

## 优化原则

1. **增量改进**：只修改有问题的部分，不推翻重写已验证正确的内容。
2. **保持一致性**：SKILL.md 与 DB 记录的 name / description / keywords 必须一致。
3. **评测驱动**：优化后应在 database.yaml 中补充或更新对应评测用例，形成"评估 → 优化 → 再评估"的闭环。
4. **记录变更**：复杂优化建议在 SKILL.md 中添加变更日志，方便回溯。

## 错误处理

- 若 experience_id 不存在或已删除，抛出 `ValueError`。
- 若 SKILL.md 文件被外部修改但 DB 未同步，先手动确认文件内容，再调用 optimize 同步。
- keywords 传入 `None` 表示不修改关键词；传入空列表 `[]` 会清空所有关键词。
