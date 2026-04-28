---
name: experience-skill
description: 用于统一管理用户工作经验的能力组件。用户经验分为两类：Skill 与 Wiki。
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
│   ├── common
│   │   └── exprience.py
│   ├── ENUM
│   │   └── exprience.py
│   ├── main.py
│   ├── manager
│   │   ├── experience_manager.py
│   │   └── keyword_manager.py
│   ├── schema
│   │   └── exprience.py
│   ├── service
│   │   ├── document_service.py
│   │   └── experience_service.py
│   └── sqlite.py
├── skill_hub
│   └── exmaple_skill
│       ├── database.yaml
│       ├── references
│       ├── scripts
│       └── SKILL.md
├── SKILL.md
└── wiki_hub
    └── example.yaml
```

目录说明：
1. `abilities`：核心能力目录，承载 Skill、Wiki 两类资源的创建、评估、检索、合并、优化能力定义；
2. `scripts`：业务逻辑目录，包含经验管理核心代码实现、命令行接口等脚本文件，main.py 提供命令行入口，experience_service.py、document_service.py 等提供核心服务实现，experience_manager.py、keyword_manager.py 等提供数据库交互支持；
3. `skill_hub`：存量 Skill 资源仓库，存放用户沉淀的所有工作流程技能；
4. `wiki_hub`：存量 Wiki 资源仓库，集中保管资料类沉淀文档。

## 约束规范
- 所有新建 Skill、Wiki 必须统一存放至 `skill_hub`、`wiki_hub` 专属目录，禁止自定义存储路径；
- 沉淀的 Skill 禁止包含恶意代码、敏感数据、隐私信息及违规内容；
- Wiki 内容仅限提炼、整合工作场景内查阅的网页、文档等资料，不得混入无关冗余信息；
- 所有 Skill 与 Wiki 需满足统一质量规范，必经评估与优化流程，杜绝明显错误、逻辑漏洞与无效内容。

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
