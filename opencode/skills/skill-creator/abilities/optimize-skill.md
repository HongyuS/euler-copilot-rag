# 优化技能（Optimize）

## 目标

对已有 skill 做增量优化，提升质量、稳定性、触发准确率与执行效率。

## 触发条件

- 用户明确要求优化某个 skill
- 评测后发现通过率低、波动大、耗时或 token 异常
- 触发不准（漏触发/误触发）

## 执行步骤

### 步骤 1：建立基线

先记录当前版本：

- `name`、`description`
- 当前流程与输出要求
- 已知问题与用户反馈

### 步骤 2：定位问题

优先级：

1. 明确失败点（功能错误）
2. 重复劳动（可脚本化）
3. description 触发语义不清
4. 无效约束导致模型负担

### 步骤 3：实施优化

- 小步快改，避免一次性大重构
- 解释改动原因，不堆砌僵硬规则
- 重复任务可抽到 `scripts/`，并在 SKILL.md 明确引用

### 步骤 4：回归与量化

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
python eval-viewer/generate_review.py <workspace>/iteration-N --skill-name "<name>" --benchmark <workspace>/iteration-N/benchmark.json
```

必要时做 description 自动优化：

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id> \
  --max-iterations 5 \
  --verbose
```

注意：`run_loop` 内部依赖 `claude -p`。若环境无 `claude` 命令，改为人工优化 description 并手动回归验证。

分析 benchmark 时应读取 `agents/analyzer.md`；若做两版盲测优劣判断，应读取 `agents/comparator.md`。
涉及 `grading.json` 与 `benchmark.json` 字段时，统一对照 `references/schemas.md`。

## 输出要求

- 给出优化前后差异（通过率、时间、token、主观反馈）
- 明确是否需要下一轮迭代
