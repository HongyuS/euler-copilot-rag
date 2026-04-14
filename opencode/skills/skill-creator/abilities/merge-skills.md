# 合并技能（Merge）

## 目标

将相同或高度相似的 skill 合并，减少重复技能、降低维护成本、避免触发冲突。

## 触发条件

- 查找阶段发现多个技能覆盖同类任务
- 用户反馈技能过多且边界混乱
- 新建前发现“已有多个近似版本”

## 合并判定

满足任一项即可进入合并评估：

- 任务目标基本一致
- 触发语境显著重叠
- 输入输出结构可兼容
- 差异主要是写法而非能力本质

## 执行步骤

### 步骤 1：盘点候选

调用 `abilities/find-skill.md` 获取候选列表，并标注：

- 共性能力
- 差异能力
- 风险（命名冲突、脚本冲突、输出不兼容）

### 步骤 2：选择主技能

优先保留：

1. 实际使用更频繁
2. 测试覆盖更完整
3. 结构更清晰、维护成本更低

### 步骤 3：执行合并

- 保留主技能 `name` 与目录
- 将有价值内容迁移进主技能（步骤、示例、脚本）
- 统一术语与输出格式
- 对旧技能做归档说明或标记弃用

### 步骤 4：回归验证

使用关键测试集验证合并后无能力回退；必要时用：

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
python eval-viewer/generate_review.py <workspace>/iteration-N --skill-name "<name>"
```

## 输出要求

- 合并决策理由
- 保留/删除/迁移清单
- 兼容性风险与回滚方案
- 若需客观比较合并前后质量，读取 `agents/comparator.md` 做盲测，再用 `agents/analyzer.md` 总结原因。
- 若输出结构化评测文件，字段格式对照 `references/schemas.md`。
