# 个人 AI Engineering Skill System

> 一套从需求到上线、从测试到迭代的端到端 AI 软件工程 Skill 体系设计
>
> 目标：把个人多年工程经验、架构经验、交付经验和最佳实践，沉淀成一套可复用、可组合、可验证、可持续进化的 **Personal AI Engineering Operating System**。

---

## 0. 文档定位

这不是一份“Skill 列表”，而是一份完整的体系设计规范。

核心思想：

```text
需求
  ↓
产品定义
  ↓
原型
  ↓
UI/UX
  ↓
技术架构
  ↓
前后端开发
  ↓
测试
  ↓
视觉还原度验证
  ↓
发布
  ↓
运行反馈
  ↓
问题复盘
  ↓
案例 / Pattern / Rule / Template 沉淀
  ↓
Skill 版本升级
  ↓
下一次开发更快、更稳、更一致
```

最终形成：

> **Skill 不只是提示词，而是一套个人工程方法论的可执行载体。**

---

# 1. 总体目标

## 1.1 最终想得到什么

最终不是拥有几十个 Markdown 文件，而是拥有一套：

- 有统一规范的 Skill
- 有明确输入输出的 Skill
- 有阶段边界的 Skill
- 有质量门禁的 Skill
- 有可复用 Pattern 的 Skill
- 有 Template 的 Skill
- 有 Evidence 的 Skill
- 有 Anti-Pattern 的 Skill
- 有自动验证机制的 Skill
- 有版本管理机制的 Skill
- 有持续反馈闭环的 Skill

最终效果：

```text
普通开发者：
    人脑 + 经验 + 搜索 + 临场决策

你的体系：
    需求
      ↓
    Orchestrator
      ↓
    Skill Graph
      ↓
    Pattern / Case Library
      ↓
    Templates
      ↓
    Tools / Scripts
      ↓
    Quality Gates
      ↓
    可审计交付物
```

## 1.2 体系的核心原则

### 原则 1：Skill 不负责“知道一切”

Skill 负责：

> 判断、流程、约束、执行方式。

知识和案例应该进入独立的 Reference / Pattern / Evidence 层。

### 原则 2：一个 Skill 只负责一个明确的工程职责

例如：

```text
product-requirement-skill
prototype-design-skill
ui-design-skill
backend-architecture-skill
frontend-architecture-skill
backend-development-skill
frontend-development-skill
testing-skill
visual-regression-skill
release-skill
iteration-skill
```

不要把几十个职责全部塞进一个 SKILL.md。

### 原则 3：Skill 是流程，Pattern 是知识，Template 是产物规范

三者必须解耦：

```text
Skill
  = 如何工作

Pattern
  = 如何解决某类问题

Template
  = 如何产出标准结果

Evidence
  = 为什么相信这个方案

Anti-Pattern
  = 什么情况下不要这么做
```

### 原则 4：所有阶段必须有“输入 → 处理 → 输出 → 验收”

没有明确输出的 Skill，很容易退化成聊天机器人。

### 原则 5：每次真实项目都应该反哺 Skill

```text
项目
 ↓
问题
 ↓
复盘
 ↓
新案例 / 新规则 / 新模板 / 新检查器
 ↓
Skill 更新
 ↓
下一个项目
```

### 原则 6：宁可少而精，也不要知识堆积

案例库的目标不是“收藏”，而是“决策时能被准确调用”。

---

# 2. 业界方法论映射

你的体系可以理解为多个成熟工程思想的组合，而不是完全从零发明。

## 2.1 Agent Skills

当前 Agent Skills 的主流定义已经非常接近：

> instructions + scripts + resources 的可复用能力包，并通过渐进式披露让 Agent 在需要时加载相关上下文。

参考：

- Anthropic Agent Skills：
  https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Microsoft Agent Skills：
  https://learn.microsoft.com/en-us/agent-framework/agents/skills
- GitHub Agent Skills：
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills

## 2.2 Architecture Pattern

解决“重复出现的工程问题如何标准化解决”。

参考：

- Azure Cloud Design Patterns：
  https://learn.microsoft.com/en-us/azure/architecture/patterns/
- Azure Architecture Center：
  https://learn.microsoft.com/en-us/azure/architecture/

## 2.3 ADR

解决：

> 为什么选择这个方案，而不是另外几个方案？

推荐引入 Architecture Decision Record 思路。

参考：

- ADR GitHub：
  https://adr.github.io/

## 2.4 Golden Path

企业工程体系中的成熟做法不是让所有人“自由发挥”，而是给出经过验证的、可重复执行的路径。

你的个人 Skill System 可以进一步理解为：

> Personal Golden Path + Personal Pattern Library + Personal Agent Skills

---

# 3. 总体架构

## 3.1 六层架构

建议最终采用六层模型：

```text
┌─────────────────────────────────────────────────────┐
│ Layer 6  Orchestration                              │
│ 项目级流程编排 / 阶段切换 / Agent 协作 / 状态机      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 5  Skills                                     │
│ Product / Design / Architecture / Development       │
│ Testing / Release / Iteration                       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 4  Pattern & Case Library                     │
│ Solution Pattern / Anti Pattern / Composite Pattern│
│ Production Case / Failure Case                      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 3  Knowledge & Evidence                        │
│ Official Docs / Standards / ADR / Benchmarks         │
│ Project Experience / Decisions                       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 2  Templates & Artifacts                       │
│ PRD / Prototype / API / DB / ADR / Test / Release    │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 1  Tools / Scripts / Validators / MCP          │
│ Browser / Image / Code / Test / Git / CI / Deploy    │
└─────────────────────────────────────────────────────┘
```

---

# 4. 第一大原则：Skill Graph，而不是 Skill List

不要只维护：

```text
A Skill
B Skill
C Skill
D Skill
```

而要维护一个有依赖关系的：

> **Skill Graph**

## 4.1 推荐的主流程

```text
00 Intake
   ↓
01 Product Requirement
   ↓
02 Product Clarification
   ↓
03 Prototype Design
   ↓
04 UI/UX Design
   ↓
05 Backend Architecture
   ↓
06 Frontend Architecture
   ↓
07 Data / API Contract
   ↓
08 Backend Development
   ↓
09 Frontend Development
   ↓
10 Integration
   ↓
11 Automated Testing
   ↓
12 Visual Fidelity Testing
   ↓
13 Performance Testing
   ↓
14 Security / Quality Review
   ↓
15 Release
   ↓
16 Post Release Verification
   ↓
17 Iteration
   ↓
18 Retrospective
   ↓
19 Knowledge Extraction
```

其中并不是所有项目都必须经过所有节点。

Orchestrator 应根据项目类型动态裁剪流程。

---

# 5. Skill 分类体系

## 5.1 产品层

```text
product-intake-skill
product-requirement-skill
product-clarification-skill
product-priority-skill
product-scope-skill
acceptance-criteria-skill
```

## 5.2 UX / Design 层

```text
ux-research-skill
information-architecture-skill
prototype-design-skill
ui-design-skill
responsive-design-skill
design-system-skill
accessibility-design-skill
```

## 5.3 Architecture 层

```text
system-architecture-skill
backend-architecture-skill
frontend-architecture-skill
database-design-skill
api-design-skill
security-architecture-skill
performance-architecture-skill
observability-architecture-skill
```

## 5.4 Development 层

```text
backend-development-skill
frontend-development-skill
database-development-skill
api-development-skill
integration-development-skill
refactoring-skill
code-review-skill
```

## 5.5 Testing 层

```text
test-strategy-skill
test-case-skill
unit-test-skill
integration-test-skill
e2e-test-skill
api-test-skill
performance-test-skill
security-test-skill
visual-regression-skill
responsive-test-skill
accessibility-test-skill
```

## 5.6 Delivery 层

```text
release-planning-skill
ci-cd-skill
deployment-skill
production-verification-skill
rollback-skill
monitoring-skill
```

## 5.7 Iteration 层

```text
incident-analysis-skill
bug-analysis-skill
performance-analysis-skill
user-feedback-analysis-skill
retrospective-skill
knowledge-extraction-skill
skill-evolution-skill
```

---

# 6. 不要让所有 Skill 都“自己决定”

必须引入一个顶层 Orchestrator。

## 6.1 Orchestrator 的职责

```text
Orchestrator
├── 判断当前项目处于哪个阶段
├── 判断下一个应该运行哪个 Skill
├── 检查输入是否完整
├── 调用 Skill
├── 保存阶段产物
├── 执行质量门禁
├── 记录决策
├── 允许返工
└── 更新项目状态
```

它不是业务 Skill。

它更像：

> **项目经理 + 工作流引擎 + 质量门禁控制器**

## 6.2 状态机

推荐每个项目都有一个 Project State：

```yaml
project:
  id: demo-project
  lifecycle: development
  stage: backend-development

stages:
  - product
  - prototype
  - design
  - architecture
  - development
  - testing
  - release
  - iteration

artifacts:
  prd: approved
  prototype: approved
  ui-spec: approved
  backend-architecture: approved
  frontend-architecture: approved
  api-contract: approved
  implementation: in-progress
  test-report: pending

quality_gates:
  product: passed
  design: passed
  architecture: passed
  development: pending
  testing: pending
```

---

# 7. Skill 的统一标准

每个 Skill 都必须遵循统一结构。

推荐：

```text
skill-name/
├── SKILL.md
├── references/
├── patterns/
├── templates/
├── examples/
├── anti-patterns/
├── checklists/
├── scripts/
├── tests/
└── metadata.yaml
```

其中不是每个目录都必须存在。

## 7.1 SKILL.md 负责什么

只放：

- Skill 定位
- 触发条件
- 输入要求
- 核心流程
- 决策原则
- 输出要求
- 质量门禁
- 引用哪些资源
- 何时停止
- 何时交回 Orchestrator

不要把所有知识全文塞入 SKILL.md。

这与当前 Agent Skills 强调的渐进式披露原则是一致的：先发现 Skill，再按需加载详细资源。 

---

# 8. 推荐的 SKILL.md 标准模板

```markdown
---
name: backend-architecture
version: 1.0.0
description: Design backend architecture based on product requirements and engineering constraints.
---

# Purpose

定义这个 Skill 的职责。

# Trigger

什么场景触发。

# Inputs

必须具备哪些输入。

# Outputs

必须产出哪些文件。

# Workflow

1. Analyze requirements
2. Identify constraints
3. Retrieve relevant patterns
4. Compare candidate architectures
5. Record decisions
6. Produce architecture
7. Run validation

# Pattern Selection

优先从 patterns/ 检索，而不是从头发明方案。

# Decision Rules

... 

# Quality Gate

...

# Stop Conditions

...

# References

...
```

---

# 9. Skill 的统一输入输出协议

这是整个体系能否规模化的核心。

每个 Skill 都要像 API 一样定义契约。

## 9.1 Input Contract

```yaml
input:
  project:
  requirement:
  upstream_artifacts:
  constraints:
  technical_context:
  business_context:
  current_stage:
```

## 9.2 Output Contract

```yaml
output:
  artifacts:
  decisions:
  unresolved_questions:
  risks:
  recommendations:
  quality_gate:
  next_stage:
```

## 9.3 阶段不能直接传“聊天上下文”

正确：

```text
产品 Skill
    ↓
PRD
    ↓
原型 Skill
    ↓
Prototype Spec
    ↓
UI Skill
    ↓
UI Spec
```

错误：

```text
Agent A
 ↓
长对话
 ↓
Agent B
 ↓
继续猜
```

你的体系必须以 **Artifact 驱动**，而不是以“聊天上下文驱动”。

---

# 10. Artifact First：所有阶段都必须产生可持久化资产

推荐把以下文件作为项目标准资产：

```text
project/
├── 00-context/
│   ├── project-context.md
│   └── constraints.md
│
├── 01-product/
│   ├── prd.md
│   ├── user-stories.md
│   ├── acceptance-criteria.md
│   └── scope.md
│
├── 02-prototype/
│   ├── information-architecture.md
│   └── prototype-spec.md
│
├── 03-design/
│   ├── ui-spec.md
│   ├── design-tokens.md
│   └── responsive-spec.md
│
├── 04-architecture/
│   ├── system-architecture.md
│   ├── backend-architecture.md
│   ├── frontend-architecture.md
│   ├── database-design.md
│   ├── api-spec.md
│   └── adrs/
│
├── 05-development/
│   ├── implementation-plan.md
│   └── change-log.md
│
├── 06-testing/
│   ├── test-plan.md
│   ├── test-cases.md
│   ├── test-report.md
│   └── visual-regression-report.md
│
├── 07-release/
│   ├── release-plan.md
│   ├── deployment-checklist.md
│   └── release-report.md
│
└── 08-iteration/
    ├── feedback.md
    ├── incidents.md
    ├── retrospective.md
    └── knowledge-extraction.md
```

---

# 11. 你真正的核心资产：Pattern / Case Library

案例库不要只叫“案例”。

建议统一叫：

> Engineering Pattern Library

下分：

```text
patterns/
├── solution-patterns/
├── anti-patterns/
├── composite-patterns/
├── production-cases/
├── failure-cases/
└── technology-patterns/
```

---

# 12. Solution Pattern 标准

每个 Pattern 至少包含：

```text
ID
Name
Problem
Context
Trigger
Preconditions
When To Use
When Not To Use
Solution
Architecture
Implementation
Trade-offs
Risks
Failure Modes
Observability
Security
Performance
Cost
Validation
Related Patterns
Anti Patterns
Examples
Evidence
```

## 12.1 示例：Cache Aside

```yaml
pattern:
  id: backend.cache.cache-aside
  version: 1.0.0
  category: caching
  name: Cache Aside

problem:
  - database read pressure
  - hot data repeated reads

context:
  workload:
    read_heavy: true

when_to_use:
  - read-heavy workloads
  - data can tolerate eventual consistency

when_not_to_use:
  - strong consistency is mandatory
  - cache hit rate is expected to be very low

solution:
  flow:
    - application checks cache
    - cache miss reads database
    - application writes result to cache

tradeoffs:
  benefits:
    - reduce database reads
    - reduce latency
  costs:
    - invalidation complexity
    - cache penetration risk
    - cache stampede risk

validation:
  metrics:
    - cache_hit_rate
    - p95_latency
    - p99_latency
    - database_qps

related_patterns:
  - cache-penetration-protection
  - cache-breakdown-protection
  - request-coalescing
```

重点：

> Pattern 不是“知识介绍”，而是“决策单元”。

---

# 13. Anti-Pattern 必须成为一级资产

每个大类都必须维护“不要怎么做”。

例如：

```text
backend/
├── solution-patterns/
└── anti-patterns/
```

示例：

```text
premature-sharding
redis-everywhere
retry-storm
unbounded-concurrency
fat-controller
shared-global-state
frontend-god-component
blind-microservice-splitting
```

AI 特别容易“过度工程化”，因此 Anti-Pattern 对你的体系非常重要。

---

# 14. Composite Pattern：把多个 Pattern 组合成标准方案

不要每次都让模型从零组合。

例如：

```text
High Concurrency Read System

=
Cache Aside
+
Multi-Level Cache
+
Request Coalescing
+
Rate Limiting
+
Circuit Breaker
+
Read Replica
```

沉淀后，它本身就成为：

> Composite Pattern

这样后面的 Skill 可以直接调用成熟组合。

---

# 15. Case 与 Pattern 要分开

这是非常关键的设计。

## Pattern

回答：

> 一般情况下怎么解决这一类问题？

## Case

回答：

> 我曾经在真实项目中怎么解决，并取得了什么结果？

案例结构：

```text
case:
  id: ecommerce.hot-product-v1
  context:
  problem:
  constraints:
  selected_patterns:
  implementation:
  metrics:
  failures:
  lessons:
  final_decision:
```

最终：

```text
Pattern = 通用知识
Case = 实战证据
```

---

# 16. Evidence 层

你的 Skill 体系不能全部来自模型记忆。

Evidence 来源建议分成：

```text
evidence/
├── official-docs/
├── standards/
├── benchmarks/
├── production-metrics/
├── project-decisions/
└── experiments/
```

可信度建议：

```text
L0  模型常识
L1  一般工程经验
L2  官方文档 / 标准
L3  自己实验 / Benchmark
L4  自己生产环境数据
```

在高风险决策中优先使用更高等级 Evidence。

---

# 17. ADR 必须贯穿 Architecture 和重要技术决策

每一个重大决策都有：

```text
Context
Options
Decision
Rationale
Consequences
```

例如：

```text
ADR-001-redis-cache-aside.md
ADR-002-postgresql-vs-mysql.md
ADR-003-monolith-vs-modular-monolith.md
ADR-004-rest-vs-grpc.md
```

这样以后 Agent 在迭代时不会重新猜测：“当初为什么这么设计？”

---

# 18. 每个 Skill 必须有 Quality Gate

这是把“Agent”变成“工程系统”的关键。

## 18.1 Product Gate

```text
[ ] 用户是谁明确
[ ] 问题明确
[ ] 目标明确
[ ] 非目标明确
[ ] 范围明确
[ ] 验收标准明确
[ ] 边界条件明确
```

## 18.2 Architecture Gate

```text
[ ] 功能需求覆盖
[ ] 非功能需求覆盖
[ ] 性能分析
[ ] 可用性分析
[ ] 安全分析
[ ] 数据一致性分析
[ ] 可观测性分析
[ ] 成本分析
[ ] ADR 已记录
```

## 18.3 Development Gate

```text
[ ] 编译通过
[ ] lint 通过
[ ] 类型检查通过
[ ] 单元测试通过
[ ] 静态检查通过
[ ] API 契约一致
```

## 18.4 Testing Gate

```text
[ ] 核心功能通过
[ ] 边界场景通过
[ ] 异常场景通过
[ ] E2E 通过
[ ] 性能达到目标
[ ] 安全检查通过
[ ] 视觉回归通过
```

## 18.5 Release Gate

```text
[ ] 构建产物正确
[ ] 配置正确
[ ] 数据库迁移安全
[ ] 回滚方案存在
[ ] 监控存在
[ ] 日志存在
[ ] 告警存在
[ ] 发布验证存在
```

---

# 19. Skill 与 Tool 必须分离

非常重要：

```text
Skill
= 决策 + 流程 + 专业方法

Tool
= 能力 / 执行动作
```

例如：

```text
Frontend Development Skill
    ↓
    可以使用
        ├── Git
        ├── Browser
        ├── Playwright
        ├── Figma
        ├── Image tools
        ├── npm
        └── TypeScript compiler
```

Skill 决定：

> 应该怎么做。

Tool 决定：

> 能实际做什么。

这也符合现代 Agent 架构中 Skills 与 Tools 分工逐步明确的方向。

---

# 20. Skill 与 Knowledge 必须分离

不要把整个技术文档直接塞进 Skill。

例如：

```text
backend-architecture/
├── SKILL.md
└── references/
    ├── distributed-systems.md
    ├── database.md
    ├── caching.md
    └── messaging.md
```

SKILL.md 负责告诉 Agent：

```text
遇到缓存问题
→ 检索 caching patterns
→ 判断是否满足条件
→ 选择 Pattern
```

而不是自己包含所有 Redis 知识。

---

# 21. Progressive Disclosure

你的体系必须遵守：

```text
Level 0
Skill Metadata
    ↓
Level 1
SKILL.md
    ↓
Level 2
相关 Pattern
    ↓
Level 3
具体 Case
    ↓
Level 4
Reference / Evidence
    ↓
Level 5
Scripts / Tools
```

只在需要时逐层展开。

这样才能控制上下文和维护成本。

---

# 22. 你的 Skill Repository 建议这样设计

```text
ai-engineering-system/
│
├── README.md
├── SYSTEM.md
├── VERSION.md
├── CHANGELOG.md
│
├── orchestrator/
│   ├── workflow.md
│   ├── state-machine.yaml
│   ├── routing-rules.yaml
│   └── gate-rules.yaml
│
├── skills/
│   ├── product/
│   ├── design/
│   ├── architecture/
│   ├── development/
│   ├── testing/
│   ├── release/
│   └── iteration/
│
├── patterns/
│   ├── solution-patterns/
│   ├── composite-patterns/
│   ├── anti-patterns/
│   ├── technology-patterns/
│   └── failure-patterns/
│
├── cases/
│   ├── production/
│   ├── project/
│   ├── experiment/
│   └── failure/
│
├── templates/
│   ├── product/
│   ├── design/
│   ├── architecture/
│   ├── development/
│   ├── testing/
│   └── release/
│
├── references/
│   ├── standards/
│   ├── official-docs/
│   ├── technology/
│   └── benchmarks/
│
├── checklists/
│
├── scripts/
│
├── evals/
│   ├── skill-evals/
│   ├── pattern-evals/
│   └── workflow-evals/
│
└── projects/
    └── <project-id>/
```

---

# 23. 每个 Skill 的目录标准

推荐：

```text
backend-architecture/
├── SKILL.md
├── metadata.yaml
├── references/
│   └── architecture-principles.md
├── patterns/
│   ├── cache-aside.md
│   ├── circuit-breaker.md
│   └── sharding.md
├── templates/
│   └── architecture-design.md
├── checklists/
│   └── architecture-review.md
├── scripts/
│   └── validate-architecture.py
└── tests/
    ├── case-001.md
    └── case-002.md
```

---

# 24. Skill Metadata 标准

```yaml
id: backend-architecture
name: Backend Architecture Skill
version: 1.2.0
status: active
owner: personal
category: architecture
stage: architecture

inputs:
  required:
    - prd
    - constraints

outputs:
  required:
    - backend-architecture
    - api-spec
    - database-design
    - adr

dependencies:
  skills:
    - product-requirement
  patterns:
    - backend/*

tools:
  - git
  - browser
  - diagram

quality_gate:
  id: backend-architecture-gate
```

---

# 25. Pattern 检索机制

不要让模型直接扫描整个 Pattern Library。

应该通过 Metadata 做第一层过滤。

例如：

```yaml
pattern:
  id: backend.cache.cache-aside
  category:
    - backend
    - caching
  problems:
    - high-read-load
    - database-pressure
  tags:
    - cache
    - redis
    - read-heavy
  constraints:
    - eventual-consistency-acceptable
```

然后 Skill 根据：

```text
Problem
+ Workload
+ Constraints
+ Technology
+ Reliability Requirement
+ Consistency Requirement
```

检索候选 Pattern。

---

# 26. Pattern 选择机制

建议不要让 AI “直接选择一个方案”。

先建立候选集合：

```text
Candidate Patterns
        ↓
Compatibility Filter
        ↓
Constraint Filter
        ↓
Risk Filter
        ↓
Evidence Check
        ↓
Trade-off Analysis
        ↓
Decision
```

输出：

```yaml
selection:
  selected:
    - backend.cache.cache-aside

  alternatives:
    - backend.cache.write-through
    - backend.read-replica

  reasons:
    - read-heavy
    - eventual-consistency-acceptable

  rejected:
    - write-through

  rejection_reasons:
    - unnecessary_write_path_complexity
```

这样你的 AI 才真正开始具备“工程决策能力”。

---

# 27. 不要让 AI 自己创造新 Pattern

默认规则：

```text
先搜索已有 Pattern
    ↓
找到就复用
    ↓
如果不满足
    ↓
允许组合已有 Pattern
    ↓
仍不满足
    ↓
提出新 Pattern 候选
    ↓
人工确认
    ↓
进入 Pattern Library
```

这条规则非常重要。

否则随着项目增加，AI 会创造：

```text
cache_strategy_v1
cache_strategy_v2
advanced_cache_strategy
smart_cache_strategy
hybrid_cache_strategy
```

最终体系失控。

---

# 28. Pattern 生命周期

每个 Pattern 都必须有生命周期：

```text
Draft
 ↓
Experimental
 ↓
Validated
 ↓
Stable
 ↓
Deprecated
 ↓
Retired
```

定义：

### Draft
刚沉淀出来，还没有实际验证。

### Experimental
至少有项目/实验使用。

### Validated
有明确结果和证据。

### Stable
可以作为默认 Pattern。

### Deprecated
新的方案已经替代它。

### Retired
不再建议使用。

---

# 29. Skill 生命周期

Skill 同样需要版本管理：

```text
Draft
 ↓
Experimental
 ↓
Stable
 ↓
Deprecated
 ↓
Retired
```

版本建议使用 SemVer：

```text
1.0.0
1.1.0
1.1.1
2.0.0
```

---

# 30. Skill 更新规则

Skill 的升级来源主要分为五类：

```text
1. 新技术
2. 新项目
3. 线上事故
4. 测试发现
5. 人工经验总结
```

每次修改都应该记录：

```text
Why
What
Evidence
Impact
```

不要凭感觉无限修改 SKILL.md。

---

# 31. 最重要的闭环：Postmortem → Skill Evolution

每次项目结束，自动问：

```text
哪里失败了？
哪里重复了？
哪里浪费了？
哪里决策错误？
哪里 Agent 做错？
哪里规则缺失？
哪里 Pattern 不够？
哪里 Template 不够？
哪里需要自动化？
```

然后分类：

```text
↓
新增 Pattern
修改 Pattern
新增 Anti-Pattern
修改 Skill
新增 Checklist
新增 Validator
新增 Template
```

这才是你真正建立“秘密武器”的地方。

---

# 32. Project Case Mining

每个项目完成后，不是简单总结一份 README，而是自动提取：

```text
Project
├── Decisions
├── Patterns Used
├── Unexpected Problems
├── Failures
├── Fixes
├── Metrics
├── Reusable Assets
└── Lessons
```

再由 Knowledge Extraction Skill 判断：

```text
哪些应该进入 Pattern
哪些应该进入 Case
哪些应该成为 Rule
哪些只是项目特例
```

---

# 33. 你需要建立“个人工程知识贡献规则”

以后任何经验都不要随便写成文档。

统一判断：

```text
这个经验是：

A. 一次性项目事实？
→ Project Artifact

B. 可重复解决的问题？
→ Pattern

C. 不应该做的事情？
→ Anti-Pattern

D. 决策原因？
→ ADR

E. 固定输出格式？
→ Template

F. 固定检查项？
→ Checklist

G. 可自动执行？
→ Script / Tool
```

这是整个体系最重要的知识分类规则之一。

---

# 34. 产品需求 Skill

输入：

```text
用户想法
业务背景
目标
约束
```

输出：

```text
prd.md
user-stories.md
scope.md
acceptance-criteria.md
open-questions.md
```

Quality Gate：

```text
没有明确目标 → 不允许进入原型阶段
没有验收条件 → 不允许进入设计阶段
存在关键未知项 → 标记 Blocked
```

---

# 35. 原型设计 Skill

职责：

```text
需求
 ↓
用户任务
 ↓
信息架构
 ↓
页面流程
 ↓
交互状态
 ↓
Prototype
```

核心输出：

```text
screen-map.md
interaction-flow.md
prototype-spec.md
```

不能自行修改产品目标。

---

# 36. UI Design Skill

输入：

```text
PRD
Prototype
Brand / Design System
```

输出：

```text
ui-spec.md
design-tokens.md
responsive-spec.md
component-spec.md
```

需要覆盖：

```text
Desktop
Tablet
Mobile
Loading
Empty
Error
Success
Disabled
Hover
Focus
Keyboard
Accessibility
```

---

# 37. Backend Architecture Skill

核心流程：

```text
需求
 ↓
Functional Requirements
 ↓
Non-functional Requirements
 ↓
Workload Model
 ↓
Pattern Retrieval
 ↓
Architecture Candidates
 ↓
Trade-off
 ↓
ADR
 ↓
Final Architecture
```

重点能力：

```text
High Concurrency
Caching
Database
Messaging
Distributed Systems
Security
Observability
Reliability
Cost
```

---

# 38. Frontend Architecture Skill

至少沉淀：

```text
State Management
Component Architecture
Data Fetching
Caching
Routing
Error Boundary
Performance
Accessibility
Design System
Testing
```

Pattern 示例：

```text
container-presentational
feature-sliced
state-machine-ui
optimistic-update
request-deduplication
code-splitting
virtual-list
```

---

# 39. Backend Development Skill

应该遵循：

```text
Read Architecture
 ↓
Read ADR
 ↓
Read API Contract
 ↓
Read DB Design
 ↓
Inspect Existing Codebase
 ↓
Implement
 ↓
Unit Test
 ↓
Integration Test
 ↓
Static Check
 ↓
Review
```

禁止：

```text
直接根据 PRD 写代码
```

因为架构、API、数据模型都可能尚未确定。

---

# 40. Frontend Development Skill

流程：

```text
Read UI Spec
 ↓
Read Prototype
 ↓
Read API Contract
 ↓
Read Design System
 ↓
Inspect Existing Components
 ↓
Implement
 ↓
Screenshot
 ↓
Visual Check
 ↓
E2E
```

这一 Skill 必须与 Visual Regression Skill 强绑定。

---

# 41. Testing Skill

Testing 不应该在最后才开始。

建议：

```text
Product Stage
→ Acceptance Tests

Architecture Stage
→ Architecture Test Strategy

Development Stage
→ Unit / Integration Tests

Integration Stage
→ E2E

Release Stage
→ Regression

Production
→ Smoke Test
```

也就是说：

> Testing 是贯穿整个生命周期的横切能力。

---

# 42. Visual Fidelity Skill

你提出的“页面还原度测试 Skill”应该独立存在。

职责：

```text
Design Reference
      ↓
Implemented Page
      ↓
Browser Screenshot
      ↓
Visual Comparison
      ↓
Difference Analysis
      ↓
Issue Classification
      ↓
Fix
      ↓
Re-test
```

差异应该分类：

```text
Layout
Spacing
Typography
Color
Border
Radius
Shadow
Icon
Image
Responsive
Interaction State
```

最终输出：

```text
visual-regression-report.md
```

---

# 43. Release Skill

Release Skill 不能只是执行 `git push`。

应该包含：

```text
Preflight
 ↓
Build
 ↓
Test
 ↓
Migration Check
 ↓
Artifact Validation
 ↓
Deploy
 ↓
Smoke Test
 ↓
Monitoring
 ↓
Release Complete
```

并且必须有：

```text
Rollback Strategy
```

---

# 44. Iteration Skill

上线后的问题不是新的项目，而是原项目生命周期的一部分。

流程：

```text
Production Signal
 ↓
Classify
 ↓
Reproduce
 ↓
Root Cause
 ↓
Fix
 ↓
Regression
 ↓
Release
 ↓
Postmortem
 ↓
Knowledge Extraction
```

---

# 45. Project Memory

每个项目应该拥有：

```text
project-memory/
├── decisions/
├── constraints/
├── assumptions/
├── incidents/
├── lessons/
└── unresolved/
```

这样 Agent 在项目后期不会失去上下文。

---

# 46. Global Memory 与 Project Memory 分离

不要把所有知识塞在一个地方。

## Global

```text
你的通用工程经验
Pattern
Anti-Pattern
Skill
Template
Checklist
```

## Project

```text
这个项目的特殊背景
业务规则
技术约束
决策
Bug
技术债
```

关系：

```text
Global
  ↓
Project
  ↓
Feedback
  ↓
Global Evolution
```

---

# 47. 个人“秘密武器”的真正组成

最终你的优势不是：

```text
我有 100 个 Skill
```

真正的壁垒应该是：

```text
Skill
+
Pattern
+
Cases
+
Decision History
+
Templates
+
Checklists
+
Validators
+
Production Evidence
+
Orchestration
```

也就是：

> **你的工程知识 + 你的工程判断 + 你的历史经验 + Agent 的执行能力。**

模型本身可以被替换。

你的这套资产不会因为模型变化而失效。

---

# 48. Evaluation：一定要建立 Skill 评测体系

这是很多个人 Skill 项目最后失败的原因。

Skill 不能只看“感觉很好用”。

应该给每一个核心 Skill 建立 Eval Cases。

例如：

```text
evals/backend-architecture/
├── simple-crud.yaml
├── high-concurrency.yaml
├── payment-system.yaml
├── distributed-transaction.yaml
└── legacy-system.yaml
```

每个 Case 定义：

```yaml
input:
  requirements: ...

expected:
  must_identify:
    - cache
    - idempotency

  must_consider:
    - consistency
    - failure

  must_not:
    - blindly_use_microservices
```

---

# 49. Skill Evaluation 指标

建议至少跟踪：

```text
Correctness
Completeness
Consistency
Constraint Adherence
Pattern Selection Accuracy
Artifact Quality
Test Pass Rate
Human Intervention Rate
Rework Rate
Token Efficiency
Execution Time
```

其中非常重要的三个指标：

```text
Rework Rate
Human Intervention Rate
Defect Escape Rate
```

如果 Skill 让你“生成得更多，但返工更多”，那么 Skill 实际上是在退化。

---

# 50. Golden Cases

为每个核心 Skill 建立少量高质量 Golden Cases。

例如：

```text
backend-architecture
├── golden-01-simple
├── golden-02-high-concurrency
├── golden-03-payment
├── golden-04-event-driven
└── golden-05-legacy
```

每次修改 Skill：

```text
Skill v1.3
 ↓
Run Golden Cases
 ↓
Compare
 ↓
Accept / Reject
```

这样 Skill 才能够像代码一样回归测试。

---

# 51. Skill 本身也要测试

推荐：

```text
Skill
 ├── Unit-like Eval
 ├── Workflow Eval
 ├── Regression Eval
 └── Adversarial Eval
```

例如对 Backend Architecture Skill 故意输入：

```text
“QPS 300 的管理后台，直接上 Kafka、Redis Cluster、K8s 微服务。”
```

看它是否会反对过度工程化，而不是顺着用户堆技术。

---

# 52. Anti-Hallucination / Anti-Overengineering 规则

你的工程体系建议加入一条总规则：

> **复杂度必须由问题证明，而不是由技术偏好证明。**

例如：

```text
低 QPS
简单业务
单体应用

→ 不主动引入：
Kafka
Kubernetes
微服务
分库分表
分布式事务
复杂缓存体系
```

除非有明确约束支持。

这类判断应沉淀为 Pattern / Rule，而不是依赖模型自由发挥。

---

# 53. Technology Decision Matrix

对于重要技术选型，建议维护决策矩阵。

例如：

```text
Cache
├── Redis
├── Local Cache
├── CDN
└── Database Read Replica
```

对比：

```text
Consistency
Latency
Scale
Operational Cost
Complexity
Failure Mode
Team Familiarity
```

最终 Skill 根据上下文筛选，而不是固定“Redis 永远是答案”。

---

# 54. Pattern Composition Rules

为组合 Pattern 定义显式规则：

```text
Allowed
Conflicting
Requires
Enhances
Replaces
```

例如：

```yaml
pattern:
  id: rate-limit

relationships:
  enhances:
    - cache
    - queue

  conflicts:
    - unbounded-concurrency

  commonly_composed_with:
    - circuit-breaker
```

这可以降低 Agent 随机组合方案的问题。

---

# 55. Decision Confidence

每次重大设计都输出：

```yaml
decision:
  choice: cache-aside
  confidence: medium
  evidence_level: L3
  assumptions:
    - read/write ratio > 10:1
    - eventual consistency acceptable
  uncertainty:
    - exact peak QPS unknown
```

注意：

> Confidence 不是“模型觉得自己对”，而是对证据和假设完整度的描述。

---

# 56. Human-in-the-loop

不是所有节点都应该自动通过。

建议分成：

```text
Auto
Human Review
Human Approval
Blocked
```

例如：

```text
PRD
→ Human Approval

Prototype
→ Human Approval

Architecture
→ Human Approval

Implementation
→ Mostly Auto

Testing
→ Mostly Auto

Release
→ Human Approval

Production Migration
→ Human Approval
```

---

# 57. 风险分级

项目应该有风险等级：

```text
L0 Experimental
L1 Internal
L2 Production Low Risk
L3 Production Medium Risk
L4 Critical
```

风险越高：

```text
越多人工审批
越高 Evidence 要求
越严格 Quality Gate
越多自动验证
越不允许 Agent 自主决策
```

---

# 58. 你真正需要的不是“一个超级 Skill”

不要做：

```text
software-development-super-skill
```

里面塞：

```text
产品
UI
后端
前端
测试
部署
```

这样会导致：

- 上下文过大
- 维护困难
- 触发边界模糊
- 修改一个流程影响全部
- 无法单独评估

正确模型：

```text
Orchestrator
     ↓
Many focused Skills
     ↓
Shared Patterns / Templates / Tools
```

---

# 59. Skill 之间如何协作

推荐通过 Artifact 协作，而不是 Agent-to-Agent 自由聊天。

```text
Product Skill
   ↓
prd.md
   ↓
Prototype Skill
   ↓
prototype-spec.md
   ↓
UI Skill
   ↓
ui-spec.md
   ↓
Architecture Skills
   ↓
architecture/*.md
   ↓
Development Skills
   ↓
code
   ↓
Testing Skills
   ↓
test-report.md
   ↓
Release Skill
   ↓
release-report.md
```

---

# 60. Build / Run / Verify 三态模型

每一个 Skill 都建议遵循：

```text
Build
 ↓
Run
 ↓
Verify
```

例如 Frontend Skill：

```text
Build
→ 写代码

Run
→ 启动项目

Verify
→ 浏览器截图 + E2E + API 检查
```

Backend：

```text
Build
→ 写代码

Run
→ 启动服务

Verify
→ Test + Logs + Metrics
```

---

# 61. “不会只生成代码”原则

所有 Development Skill 都必须遵守：

```text
代码
+
测试
+
验证结果
+
变更说明
```

否则 Agent 会倾向于把“代码生成”误当成“任务完成”。

---

# 62. Definition of Done

全局定义 DoD：

```text
A task is Done only when:

[ ] Artifact complete
[ ] Implementation complete
[ ] Tests pass
[ ] Quality gate pass
[ ] Documentation complete
[ ] Relevant evidence recorded
[ ] Unresolved risks recorded
```

项目级 DoD 可以扩展。

---

# 63. 每阶段的 DoD

例如 Architecture：

```text
[ ] Architecture diagram
[ ] API design
[ ] Data model
[ ] Non-functional analysis
[ ] Pattern decisions
[ ] ADR
[ ] Risks
[ ] Validation strategy
```

Testing：

```text
[ ] Functional test
[ ] Regression
[ ] Edge cases
[ ] Performance
[ ] Visual
[ ] Security
[ ] Final report
```

---

# 64. 个人工程风格文件

建立一个顶层：

```text
ENGINEERING_PRINCIPLES.md
```

里面写你的长期原则：

```text
Simplicity First

Explicit Over Implicit

Artifact First

Evidence Over Guess

Reuse Before Reinvent

Measure Before Optimize

Prefer Reversible Decisions

Automate Repetition

Human Approval for High Risk
```

所有 Skill 都继承这些原则。

---

# 65. 项目级覆盖规则

同时允许：

```text
Global Principles
        ↓
Skill Rules
        ↓
Project Rules
        ↓
Task Rules
```

优先级明确，避免冲突。

推荐：

```text
System Safety
>
Global Engineering Rules
>
Project Constraints
>
Skill Rules
>
Task Preferences
```

---

# 66. Naming Convention

Skill：

```text
backend-architecture
frontend-development
visual-regression
```

Pattern：

```text
backend.cache.cache-aside
backend.reliability.circuit-breaker
frontend.performance.code-splitting
```

Case：

```text
ecommerce.hot-product-traffic
saas.multi-tenant-api
```

ADR：

```text
ADR-001-cache-strategy
ADR-002-database-choice
```

---

# 67. Versioning Convention

Skill：SemVer

Pattern：SemVer

Template：SemVer

Case：不可变记录，必要时增加 revision

项目 Artifact：跟随项目版本。

---

# 68. Git 管理策略

建议整个体系本身就是一个 Git Repository。

```text
git
 ↓
skill change
 ↓
commit
 ↓
eval
 ↓
review
 ↓
merge
```

提交信息例如：

```text
feat(skill): improve backend architecture decision flow
fix(pattern): correct cache stampede guidance
feat(eval): add payment architecture golden case
refactor(template): simplify technical design output
```

---

# 69. Skill Pull Request 思维

以后修改核心 Skill，不要直接覆盖。

走类似代码 PR：

```text
Proposal
 ↓
Change
 ↓
Eval
 ↓
Regression
 ↓
Review
 ↓
Merge
```

特别是影响多个项目的核心 Skill。

---

# 70. Personal Skill Registry

最终可以有一个：

```yaml
skills:
  - id: product-requirement
    version: 1.4.0
    status: stable

  - id: backend-architecture
    version: 2.1.0
    status: stable

  - id: visual-regression
    version: 1.2.0
    status: experimental
```

让 Orchestrator 知道当前哪些 Skill 可用。

---

# 71. Pattern Registry

同理：

```yaml
patterns:
  - id: backend.cache.cache-aside
    version: 1.2.0
    status: stable

  - id: backend.distributed.saga
    version: 0.4.0
    status: experimental
```

---

# 72. Skill Dependency Graph

例如：

```text
product-requirement
        ↓
prototype-design
        ↓
ui-design
        ↓
frontend-architecture
        ↓
frontend-development
        ↓
visual-regression
```

后端：

```text
product-requirement
        ↓
backend-architecture
        ↓
api-design
        ↓
backend-development
        ↓
backend-testing
```

跨域汇合：

```text
frontend-development ─┐
                      ├→ integration-testing
backend-development ──┘
                              ↓
                       release-validation
```

---

# 73. Parallel Execution

并不是所有阶段必须串行。

例如：

```text
                  ┌→ Backend Architecture
Product ──────────┤
                  └→ UX Architecture
```

设计和后端架构可以部分并行。

但必须有同步点：

```text
API Contract
Design System
Acceptance Criteria
```

---

# 74. Gate Based Orchestration

推荐使用 Gate 而不是简单顺序执行：

```text
Stage
 ↓
Artifact
 ↓
Gate
 ↓
Pass → Next
Fail → Rework
Blocked → Human Input
```

这样：

```text
UI Skill
 ↓
UI Spec
 ↓
Gate Fail
 ↓
回到 Prototype
```

而不是一路生成错误结果。

---

# 75. Rework Loop

每个阶段都应该允许返回上游：

```text
Testing
 ↓
发现需求错误
 ↓
回到 Product
```

或者：

```text
Frontend
 ↓
发现 API 无法支持
 ↓
回到 Backend Architecture
```

因此 Skill Graph 必须是 DAG + controlled feedback loops，而不是单纯流水线。

---

# 76. Global Engineering Dashboard

长期建议建立一个 dashboard，观察：

```text
Projects
Skill Versions
Pattern Versions
Gate Pass Rate
Rework Rate
Defect Rate
Release Success
Skill Eval Score
Most Used Patterns
Most Failed Patterns
```

这样你可以真正发现：

> 哪个 Skill 在拖慢整个系统。

---

# 77. Skill ROI

每一个 Skill 都应该回答：

```text
Without Skill
需要多少人工？

With Skill
需要多少人工？

Quality
是否提升？

Rework
是否下降？
```

如果一个 Skill 长期：

```text
增加 token
增加等待
增加返工
没有提高质量
```

就应该重构甚至删除。

---

# 78. 成本控制

不要让所有 Skill 每次都读取整个知识库。

推荐：

```text
Metadata
 ↓
Candidate Retrieval
 ↓
Top-N Pattern
 ↓
Detailed Load
 ↓
Execute
```

对于常用 Pattern，可以做缓存或局部索引。

---

# 79. 知识去重

案例库发展到一定规模以后，会出现：

```text
cache-aside
cache-aside-best-practice
redis-cache-aside
hot-data-cache
read-cache-strategy
```

需要建立：

```text
Canonical Pattern
Aliases
Related Patterns
Deprecated Patterns
```

例如：

```yaml
canonical: backend.cache.cache-aside
aliases:
  - redis-cache-aside
  - cache-aside
```

---

# 80. “一事一源”原则

同一个规则只维护一个 canonical source。

例如：

```text
cache invalidation rule
```

不能同时复制到：

```text
Backend Skill
Cache Pattern
Testing Skill
Architecture Guide
```

其他地方只引用它。

否则最终必然出现版本冲突。

---

# 81. Documentation 与 Execution 分离

建议区分：

```text
Explain
Reference
Execute
Validate
```

例如：

```text
references/cache.md
patterns/cache-aside.md
scripts/test-cache.py
checklists/cache-review.md
```

而不是一个 2000 行 Markdown 把所有东西混起来。

---

# 82. 你的“案例库模板”建议正式定义成四种

不要所有案例只有一种格式。

### Solution Pattern

通用解法。

### Production Case

真实项目案例。

### Failure Case

真实失败案例。

### Experiment Case

实验验证案例。

分别服务不同目的：

```text
Pattern → 决策
Production Case → 证据
Failure Case → 避坑
Experiment Case → 技术验证
```

---

# 83. 案例评分不要做“主观好坏分数”

建议使用属性：

```text
status
maturity
evidence_level
usage_count
last_validated
known_limitations
```

例如：

```yaml
maturity: stable
evidence_level: L4
usage_count: 8
last_validated: 2026-09-01
```

这样比一个“9.5 分”更有工程意义。

---

# 84. 你的体系应该支持“领域包”

最终可以进一步拆成：

```text
personal-engineering-system/

core/

web-platform/

backend/

frontend/

mobile/

data/

ai-agent/

devops/

security/
```

每个领域都有：

```text
Skills
Patterns
Cases
Templates
Tools
Evals
```

---

# 85. 第一阶段不要做太大

这是最重要的落地建议。

第一版不要一次做 50 个 Skill。

先做一条完整的 Vertical Slice：

```text
Product Requirement
        ↓
Prototype
        ↓
UI Design
        ↓
Backend Architecture
        ↓
Frontend Architecture
        ↓
Backend Development
        ↓
Frontend Development
        ↓
Testing
        ↓
Visual Regression
        ↓
Release
```

这 10 个 Skill 全部打通。

先证明：

> 一套 Skill 真能把项目从头做到尾。

---

# 86. 第一批 Pattern 不超过 30~50 个

建议第一版：

```text
Backend
10~15

Frontend
8~12

Testing
5~8

Architecture
5~10
```

优先覆盖高频问题，而不是追求完整。

---

# 87. 第一版建议的 Backend Pattern

```text
cache-aside
cache-penetration-protection
cache-breakdown-protection
rate-limit
circuit-breaker
retry
idempotency
outbox
saga
read-replica
sharding
queue-based-load-leveling
request-coalescing
bulkhead
```

---

# 88. 第一版建议的 Frontend Pattern

```text
feature-based-architecture
component-composition
state-machine-ui
request-deduplication
optimistic-update
error-boundary
code-splitting
virtual-list
image-optimization
```

---

# 89. 第一版建议的 Testing Pattern

```text
unit-test-boundary
contract-testing
integration-test-boundary
e2e-critical-path
visual-regression
risk-based-testing
```

---

# 90. 第一版建议的 Cross-cutting Pattern

```text
observability
structured-logging
error-classification
security-boundary
configuration-management
feature-flag
rollback
```

---

# 91. 建立“项目黄金路径”

建议第一条黄金路径叫：

```text
standard-web-app-golden-path
```

它规定：

```text
Product
→ Prototype
→ UI
→ Architecture
→ Development
→ Testing
→ Visual Verification
→ Release
```

这是你的第一条 Personal Golden Path。

之后再建立：

```text
high-concurrency-golden-path
saas-golden-path
admin-system-golden-path
ai-agent-golden-path
mobile-app-golden-path
```

---

# 92. Golden Path 与 Skill 的关系

```text
Golden Path
    ↓
引用 Skills
    ↓
引用 Patterns
    ↓
引用 Templates
    ↓
执行 Gates
```

Golden Path 解决：

> 一类项目整体应该怎么做。

Skill 解决：

> 某一个工程环节应该怎么做。

Pattern 解决：

> 某一个技术问题应该怎么解决。

---

# 93. 最终你会得到三个层级

```text
Level 1：Capability

Skill

Level 2：Method

Pattern / Golden Path

Level 3：Evidence

Case / ADR / Metrics / Experiment
```

这是一个非常稳定的知识体系。

---

# 94. 推荐的最终顶层模型

```text
                    PERSONAL AI ENGINEERING OS

                           ORCHESTRATOR
                                │
                ┌───────────────┼───────────────┐
                │               │               │
             SKILLS          PATTERNS         TOOLS
                │               │               │
                │               ├─ Solution     ├─ Git
                │               ├─ Composite    ├─ Browser
                │               ├─ Anti         ├─ Test
                │               └─ Failure      ├─ CI/CD
                │                               └─ MCP
                │
                ├─ Product
                ├─ Design
                ├─ Architecture
                ├─ Development
                ├─ Testing
                ├─ Release
                └─ Iteration

                        ↓

                    ARTIFACTS

                        ↓

                QUALITY GATES / EVALS

                        ↓

                     PRODUCTION

                        ↓

                  FEEDBACK / INCIDENT

                        ↓

               KNOWLEDGE EXTRACTION

                        ↓

            PATTERN / SKILL EVOLUTION
```

---

# 95. 实施路线图

下面是建议的实际落地顺序。

## Phase 0：定义原则

先建立：

```text
ENGINEERING_PRINCIPLES.md
SYSTEM.md
SKILL_SPEC.md
PATTERN_SPEC.md
CASE_SPEC.md
ADR_SPEC.md
QUALITY_GATE_SPEC.md
```

此阶段不要疯狂写 Skill。

目标：

> 先定义语言和规则。

---

## Phase 1：建立 Repository

建立：

```text
skills/
patterns/
cases/
templates/
references/
checklists/
evals/
orchestrator/
```

---

## Phase 2：做第一条 Golden Path

只选择：

```text
Product
→ Prototype
→ UI
→ Architecture
→ Dev
→ Test
→ Visual
→ Release
```

跑通一个真实项目。

---

## Phase 3：建立第一批 Pattern

优先：

```text
Backend 高频问题
Frontend 高频问题
Testing 高频问题
```

不要追求数量。

---

## Phase 4：建立 Eval

每个核心 Skill 至少：

```text
3~5 Golden Cases
```

每次 Skill 改动都跑回归。

---

## Phase 5：建立 Orchestrator

一开始可以非常简单：

```text
state.yaml
workflow.md
```

后面再逐步自动化。

---

## Phase 6：建立 Knowledge Extraction

项目完成后自动生成：

```text
new-pattern-candidates
new-anti-pattern-candidates
new-rule-candidates
skill-improvement-candidates
```

人工审核后合入主库。

---

# 96. Phase 7：建立“个人工程数据飞轮”

最终形成：

```text
更多项目
   ↓
更多真实案例
   ↓
更多 Evidence
   ↓
更好的 Pattern
   ↓
更好的 Skill
   ↓
更好的项目结果
   ↓
更多项目
```

这就是你的长期壁垒。

---

# 97. 90 天实施计划

## Day 1~7

完成：

```text
SYSTEM.md
SKILL_SPEC.md
PATTERN_SPEC.md
CASE_SPEC.md
QUALITY_GATE_SPEC.md
Repository skeleton
```

## Day 8~21

完成第一批：

```text
Product Requirement
Prototype
UI Design
Backend Architecture
Frontend Architecture
```

## Day 22~35

完成：

```text
Backend Development
Frontend Development
Testing
Visual Regression
Release
```

## Day 36~50

建立第一批 20~30 个 Pattern。

## Day 51~65

建立 Golden Cases 和 Evals。

## Day 66~75

打通 Orchestrator。

## Day 76~90

选 2~3 个真实项目验证整套体系。

最终输出：

```text
Skill v1.0
Pattern Library v1.0
Golden Path v1.0
Eval Suite v1.0
```

---

# 98. 你现在最应该做的事情

不要马上写：

```text
backend-architecture/SKILL.md
```

第一步应该是先建立：

```text
PERSONAL_AI_ENGINEERING_SYSTEM/
```

然后定义五个核心规范：

```text
01 Skill Specification
02 Pattern Specification
03 Case Specification
04 Artifact Specification
05 Quality Gate Specification
```

因为这五个东西一旦稳定，后面几十个 Skill 才不会越写越乱。

---

# 99. 最终目标不是“让 AI 按我的 Prompt 写代码”

真正目标是：

```text
你的工程经验
       ↓
结构化
       ↓
Pattern
       ↓
Skill
       ↓
Workflow
       ↓
Orchestrator
       ↓
Agent
       ↓
真实项目
       ↓
结果
       ↓
Evidence
       ↓
反哺 Pattern
```

最终形成一个不断变强的闭环：

> **Your Experience → Structured Knowledge → Executable Skill → Project Result → New Experience**

---

# 100. 终极形态

最终你维护的不是“Skill 文件夹”。

而是：

```text
┌──────────────────────────────────────────┐
│       PERSONAL AI ENGINEERING OS         │
├──────────────────────────────────────────┤
│                                          │
│  Engineering Principles                  │
│             ↓                            │
│  Golden Paths                             │
│             ↓                            │
│  Skill Graph                              │
│             ↓                            │
│  Skills                                   │
│             ↓                            │
│  Pattern Library                          │
│             ↓                            │
│  Cases / ADR / Evidence                   │
│             ↓                            │
│  Templates / Checklists                   │
│             ↓                            │
│  Tools / Scripts / MCP                    │
│             ↓                            │
│  Quality Gates / Eval                     │
│             ↓                            │
│  Production                               │
│             ↓                            │
│  Feedback                                 │
│             ↓                            │
│  Knowledge Extraction                     │
│             ↓                            │
│  Skill Evolution                          │
│                                          │
└──────────────────────────────────────────┘
```

这套系统的价值不在于“某一个 Skill 多厉害”，而在于：

1. 每个 Skill 都有明确边界。
2. Skill 之间通过 Artifact 和 Contract 协作。
3. Pattern 把技术经验结构化。
4. Case 给 Pattern 提供真实证据。
5. Anti-Pattern 防止 AI 过度设计和错误复用。
6. ADR 保存重要技术决策。
7. Quality Gate 保证每个阶段不是“生成完成”，而是“验证完成”。
8. Eval 保证 Skill 自己也可以被测试。
9. Orchestrator 把一组 Skill 变成完整开发流程。
10. Production feedback 持续反哺 Skill 和 Pattern。

最终形成的是：

> **一个属于你自己的、可版本化、可测试、可进化的 AI 软件工程操作系统。**

---

# 附录 A：核心文件模板清单

建议第一阶段至少创建：

```text
SYSTEM.md
ENGINEERING_PRINCIPLES.md
SKILL_SPEC.md
PATTERN_SPEC.md
CASE_SPEC.md
ARTIFACT_SPEC.md
QUALITY_GATE_SPEC.md
EVAL_SPEC.md
VERSIONING.md
GOVERNANCE.md
```

---

# 附录 B：第一批必须落地的 Skill

```text
01 product-requirement
02 prototype-design
03 ui-design
04 backend-architecture
05 frontend-architecture
06 api-design
07 database-design
08 backend-development
09 frontend-development
10 integration-testing
11 e2e-testing
12 visual-regression
13 performance-testing
14 release
15 production-verification
16 iteration
17 retrospective
18 knowledge-extraction
19 skill-evolution
```

---

# 附录 C：第一批核心 Pattern

```text
Cache Aside
Circuit Breaker
Retry
Rate Limit
Bulkhead
Idempotency
Saga
Outbox
Read Replica
Sharding
Queue-Based Load Leveling
Request Coalescing
Feature Flag
Rollback
Observability
Structured Logging
Error Boundary
Code Splitting
Virtual List
Optimistic Update
Contract Testing
Visual Regression
Risk-Based Testing
```

---

# 附录 D：最重要的判断标准

以后当你准备加入任何新的 Skill / Pattern / Case 时，都先问四个问题：

```text
1. 这个东西是否会被重复使用？

2. 是否能够定义明确输入和输出？

3. 是否能够被验证？

4. 是否能够在真实项目中积累证据？
```

四个问题都能回答“是”，才值得进入你的长期体系。

---

# 附录 E：最终一句话定义

> **把你的软件工程经验拆成可执行的 Skill，把重复问题沉淀成 Pattern，把真实项目沉淀成 Case，把关键决策沉淀成 ADR，把固定产出沉淀成 Template，把工程质量沉淀成 Gate，再用 Orchestrator 把这些能力连接成一条从需求到生产的 Personal Golden Path。**

这就是这套体系真正应该建设的方向。
