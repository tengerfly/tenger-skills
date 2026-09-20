# Skill 工作流系统重构计划 v2

> 状态：规划稿
>
> 创建时间：2026-09-20
>
> 工作分支：`refactor/workflow-system-v2`
>
> 适用范围：本仓库的 `Workflow`、产品/设计/开发/测试相关 Skill、公共契约、产物目录和验证机制。
>
> 本计划先定义目标架构、迁移顺序、每一步的输入/输出/验收标准；后续重构严格按本计划推进。除非发现计划本身存在问题，否则不在执行过程中随意改变主架构。

---

## 0. 本轮重构要解决的问题

当前仓库已经拥有较多专业 Skill，但整体仍然主要表现为：

```text
多个专业 Skill + 一个线性 Workflow + Markdown 产物
```

本轮要升级为：

```text
一个总编排 Workflow
+ 四个领域 Workflow
+ 职责单一的原子 Skill
+ 统一的产物契约
+ 统一的状态机和门禁
+ 可追踪的决策链
+ 可验证的运行场景
```

重点不是简单重命名或把目录重新分类，而是建立以下能力：

1. 用户的模糊想法不会被直接当成确定需求。
2. AI 在代替用户做产品推演时，必须区分事实、证据、假设、推荐和待确认决策。
3. 竞品分析能够转化为产品取舍，而不是停留在竞品功能罗列。
4. 每个阶段都有清晰的输入、输出、前置条件、完成条件和失败回退路径。
5. PRD、原型、设计、技术方案、代码和测试可以互相追踪。
6. Workflow 负责调度和守门，原子 Skill 负责执行一个聚焦任务。
7. 工作流可以回退到正确的上游阶段，而不是让下游用补丁掩盖上游问题。
8. 重构可以逐步迁移，旧 Skill 在新架构稳定前仍然可用。

---

## 0.1 最终战略目标：个人工程操作系统与核心竞争力

本体系的最终交付物不是一组孤立的 Skill，也不是只服务一次项目的开发脚本，而是一个可由个人长期掌握、持续积累、跨项目复用的**个人工程操作系统（Personal Engineering Operating System，简称 PEOS）**。

它应当让一个人具备类似完整工程团队的稳定交付能力：

```text
一个人
+ 一套可复用的工程流程
+ 一套可验证的产品/设计/开发/测试/发布/运维能力
+ 一套 AI 能力资产与组件知识库
+ 一套日志/监控/运行反馈闭环
= 可持续交付新产品、公司项目和客户项目的个人工程体系
```

### 0.1.1 核心竞争力不在“会使用 AI”

本体系的竞争力不应建立在某个模型、某个 Prompt 或某个单次生成结果上，而应建立在以下长期资产上：

1. **流程资产**：从模糊想法到运行优化的完整工作流、状态机、门禁和回退机制；
2. **知识资产**：`skills-knowledge` 中的能力卡、平台 Profile、Pattern、Composite、Adapter 和反例；
3. **工程资产**：可复用组件、脚手架、技术方案、测试方案、部署方式和运行手册；
4. **证据资产**：真实项目中的构建、测试、发布、日志、监控、缺陷和优化结果；
5. **反馈资产**：问题模式、失败案例、产品数据和运行信号对 Skill 的持续反哺；
6. **交付资产**：在不同项目、不同平台和不同技术栈下仍能稳定复用的黄金场景。

因此，真正的护城河是：

```text
流程可复制
→ 产物可验证
→ 结果可追踪
→ 问题可回流
→ 经验可沉淀
→ 下一次交付更快、更稳、更准确
```

### 0.1.2 三种使用形态

同一套核心体系应支持三种使用形态，而不是为每种场景维护三套流程：

| 使用形态 | 目标 | 需要隔离的内容 |
|---|---|---|
| `PERSONAL_OPC` | 个人独立发现、开发、运营产品 | 个人产品代码、商业数据、私有资产 |
| `COMPANY_PROJECT` | 在公司项目中提升研发质量和交付效率 | 公司代码、公司数据、公司规则、公司知识产权 |
| `CLIENT_PROJECT` | 为外部客户或合作方提供工程交付 | 客户代码、客户数据、客户专属业务与交付边界 |

公共流程可以复用，但项目事实、业务数据、源代码和客户资产必须按项目隔离。默认规则是：

- `tenger-skills`：沉淀通用流程、Skill 契约和不含客户机密的工程方法；
- `skills-knowledge`：沉淀可复用能力和资产，但每项资产必须记录来源、授权范围和是否允许跨项目使用；
- 具体业务项目：保存项目专属 PRD、代码、配置、日志、监控数据、发布记录和业务决策；
- 公司或客户专属资产：未经授权不得回流到个人公共资产库；只能沉淀为去敏后的通用模式、反例或方法。

### 0.1.3 个人工程体系的正向飞轮

```text
承接一个新想法 / 公司需求 / 旧项目
→ 通过统一 Workflow 交付
→ 通过 web-monitor / server-log / server-monitor 获得运行证据
→ 发现缺陷、性能问题、产品机会和工程重复劳动
→ 修复当前项目
→ 更新项目基线
→ 提炼去敏后的通用 Pattern / Adapter / 反例
→ 优化 Skill 和组件库
→ 下一次项目更快、更稳、更低成本
```

这里的关键不是“自动化改代码”，而是把每一次真实交付都转化成下一次交付的能力增长。随着项目数量增加，体系应当产生规模效应：

- 相同问题不再重复分析；
- 相同平台不再重复搭建；
- 相同组件不再重复开发；
- 相同事故不再重复发生；
- 相同质量门禁不再依赖个人记忆；
- 新模型或新成员可以按照体系工作，而不是依赖某个人的隐性经验。

### 0.1.4 成功标准

本体系完成后的判断标准不是“创建了多少个 Skill”，而是：

- 一个人可以用它独立完成一个新产品的主要工程链路；
- 可以接管一个陌生旧项目，并在不破坏现有业务的前提下建立基线；
- 可以对公司项目进行功能迭代、Bug 修复和应用重构；
- 可以把发布后的真实错误和指标转成下一轮工程行动；
- 可以支持 Web 和后端，并通过 Profile/Adapter 扩展到小程序、桌面端、iOS、Android、鸿蒙等平台；
- 每次交付都有可追踪的需求、决策、代码、测试、发布和运行证据；
- 核心通用资产可以跨项目复用，同时公司/客户私有信息不会泄露；
- 体系的能力随着真实项目数量增加而增强，而不是随着项目增加而失控。

### 0.1.5 一个重要边界

这套体系可以成为个人的核心竞争力，但不能把“个人资产复用”误解为“无条件复制公司或客户资产”。工程体系的复用对象应优先是：

```text
方法、契约、工具、抽象模式、去敏案例、可授权组件
```

而不是：

```text
公司源代码、客户数据、内部业务规则、私有凭证、未授权的设计和文档
```

### 0.1.6 模型无关的恒定质量与定期巡检

这套体系的目标不是让某一个模型偶尔生成一份“看起来能跑”的代码，而是让**不同模型、不同时间、不同项目**都必须在同一套工程契约和质量门禁下工作。模型只是执行者，不能决定质量标准。

质量恒定依赖以下机制，而不是依赖模型记忆：

1. **统一契约**：需求、设计、代码、测试、发布和运行信号使用统一的状态、产物、追踪关系和 Gate。
2. **证据优先**：每个关键结论都要绑定代码、测试、构建、日志、监控或运行数据证据；事实、推断、假设和待确认事项不得混写。
3. **可维护性门禁**：代码必须遵守项目结构、命名、模块边界、错误处理、日志、测试和依赖规则；禁止为了“快速生成”堆叠重复逻辑、超大文件、隐式副作用和无法解释的抽象。
4. **反 AI 味门禁**：审查“是否像能长期维护的工程代码”，重点检查无意义封装、过度注释、泛化命名、重复类型、异常吞噬、魔法值、复制粘贴、未经解释的复杂度和与项目既有风格冲突。
5. **模型可替换**：任何模型都只能通过 Skill Contract 交付；模型更换后重新执行确定性校验、测试、代码审查和运行验证，不能因为“模型不同”降低标准。
6. **定期巡检**：除了变更时的 Gate，还要按周期对代码质量、依赖、测试健康度、架构漂移、可观测性覆盖、运行错误、性能和成本进行巡检，生成可排序的问题清单，并通过 `CHANGE`、`DEFECT`、`REFACTOR` 或 `OPTIMIZE` 路由进入主流程。

定期巡检不是一次性报告，而是闭环入口：

```text
定期巡检
→ 发现证据
→ 归一化问题
→ 判断缺陷 / 变更 / 重构 / 优化
→ 进入对应 Workflow
→ 修复并验证
→ 发布后观测
→ 更新巡检基线与通用资产
```

因此，“不生成屎山”的验收标准必须可观察：代码可读、边界清楚、测试可运行、日志可关联、问题可定位、变更可回滚、后续巡检可重复。

---
## 1. 当前分支与执行安全规则

### 1.1 分支

已创建并切换到：

```text
refactor/workflow-system-v2
```

所有重构工作在此分支进行，不直接修改原有主线分支。

### 1.2 当前工作区保护

创建分支前工作区已经存在用户未提交内容：

- `README.md`：已修改
- `Other/Essence-Distill/`：未跟踪

这些内容不属于本轮重构的初始变更，不删除、不覆盖、不重置、不混入重构提交。后续每次提交前都要执行：

```powershell
git status --short
 git diff -- README.md
 git ls-files --others --exclude-standard
```

提交时只暂存本轮明确修改的文件。

### 1.3 提交策略

采用“小步、可回滚、每阶段一个提交组”的方式：

```text
00-baseline       基线与盘点
01-contract       契约与公共规范
02-prd-workflow   PRD 工作流试点
03-ui-workflow    UI 工作流
04-dev-workflow   DEV 工作流
05-testing        Testing 工作流
06-integration    总编排、迁移与验证
```

每个阶段完成后先运行验证，再提交。禁止在没有通过阶段验收的情况下批量重写所有 `SKILL.md`。

---

## 2. 目标架构

### 2.1 总体层级

```text
Workflow
├── PRD-Workflow
│   ├── Idea Intake
│   ├── Product Discovery
│   ├── Competitive Research
│   ├── Product Definition
│   ├── Application Blueprint
│   ├── Feature Decision / MVP Scope
│   ├── PRD Design
│   ├── Prototype Design
│   ├── Review
│   └── Product Baseline Freeze
│
├── UI-Workflow
│   ├── UX Architecture
│   ├── Design Direction
│   ├── Design System / Component Mapping
│   ├── Screen Design
│   ├── Interaction / State Completion
│   └── UI Review / Baseline Freeze
│
├── DEV-Workflow
│   ├── Technical Discovery
│   ├── Backend Technical Design
│   ├── Frontend Technical Design
│   ├── Component / Asset Decision
│   ├── Implementation Planning
│   ├── Backend Development
│   ├── Frontend Development
│   └── Code Review / Engineering Baseline
│
└── Testing-Workflow
    ├── Test Strategy
    ├── Test Case / Traceability Planning
    ├── Deterministic Quality Gates
    ├── Contract / Integration Testing
    ├── E2E / Visual / Accessibility Testing
    ├── Performance / Security Testing
    ├── Defect Triage
    └── Regression / Release Gate
```

### 2.2 命名策略

本轮先沿用仓库现有命名风格，新增四个领域编排目录：

```text
WorkFlow/
PRD-Workflow/
UI-Workflow/
DEV-Workflow/
Testing-Workflow/
```

暂不同时进行全仓目录小写迁移。原因：目录重命名会制造大量无关 diff，也会影响已有引用、安装副本和历史产物。稳定后再单独做 canonical naming 迁移。

### 2.3 职责边界

| 层级 | 负责什么 | 不负责什么 |
|---|---|---|
| `Workflow` | 判断起点、调度领域工作流、维护项目状态、执行跨阶段门禁、处理回退 | 不编写 PRD、设计稿、代码、测试报告 |
| `*-Workflow` | 编排领域内的原子 Skill，形成完整阶段闭环 | 不替代原子 Skill 的专业执行 |
| 原子 Skill | 聚焦完成一件可验证的事情 | 不擅自扩大职责、不越权改变上游基线 |
| Review Skill | 检查产物是否满足契约，给出证据和问题 | 默认不直接改被审产物 |
| 公共契约 | 规定状态、产物、追踪、证据、门禁的共同语言 | 不承载具体领域方法论 |

---

## 3. 核心设计原则

### 3.1 Artifact First

阶段之间不依赖聊天上下文作为唯一事实源。所有下游决策必须优先读取项目 `.spec/` 中的已冻结产物和 manifest。

```text
聊天内容 = 临时输入 / 讨论记录
.spec/产物 = 可消费的事实源
manifest = 产物清单和版本关系
PIPELINE = 状态与调度事实源
```

### 3.2 Evidence Before Claims

所有外部事实、竞品结论、技术可行性判断和测试结论都必须标注证据来源或明确标记为：

- `FACT`：已有证据支持的事实
- `INFERENCE`：基于事实的推断
- `ASSUMPTION`：尚未验证的设计假设
- `RECOMMENDATION`：AI 的推荐
- `DECISION`：用户或授权角色已确认的决策
- `OPEN`：尚未解决的问题

### 3.3 先决策，后生产

不能把“写文档”当成“做产品决策”。尤其是 PRD 阶段，必须先完成：

```text
问题定义 → 用户与场景 → 竞品证据 → 产品定位 → 全链路 → 功能取舍 → MVP 范围
```

再生成正式 PRD。

### 3.4 每个阶段都要有可回退路径

回退由问题归属决定，而不是由当前正在运行的 Skill 决定：

| 问题归属 | 回退位置 |
|---|---|
| 产品目标、用户问题、产品定位错误 | PRD-Workflow 产品定义阶段 |
| 功能范围、业务流程、异常场景缺失 | PRD-Workflow 应用全景/功能决策阶段 |
| 页面结构、信息架构、交互流错误 | PRD-Workflow 原型或 UI-Workflow UX 阶段 |
| 视觉系统、组件状态、还原问题 | UI-Workflow |
| 技术方案或架构问题 | DEV-Workflow 技术设计阶段 |
| 代码实现问题 | DEV-Workflow 开发阶段 |
| 测试策略或用例问题 | Testing-Workflow 测试设计阶段 |
| 运行缺陷 | DEV-Workflow 修复 + Testing-Workflow 回归 |

### 3.5 只在不可逆决策处暂停

工作流不再默认每完成一个原子 Skill 都停下。暂停规则改为：

- 低风险、可逆、已有默认规则的动作：AI 执行并记录。
- 影响产品定位、目标用户、MVP 范围、预算、外部付费、不可逆架构的动作：给出推荐和备选，等待用户确认。
- 阶段 Gate：必须停下展示结论、证据、未决问题和下一步。

---

## 4. 统一 Skill 契约

每个新的或重构后的 Skill 都采用同一套结构：

```text
Purpose             解决什么问题
Trigger             什么请求触发
Inputs              必须读取的输入
Preconditions       运行前必须满足什么
Responsibilities    只负责哪些事情
Non-goals           明确不做哪些事情
Procedure           执行步骤
Outputs             输出哪些产物
Evidence            结论需要什么证据
Gate                怎样算完成
Failure Route       失败或发现上游问题时回退哪里
Downstream Contract 下游如何消费
State Changes       修改哪些工作流状态
```

在 `SKILL.md` 中只保留入口、核心决策和强约束；详细清单、模板、案例和工具用法下沉到：

```text
references/     方法、检查清单、案例
assets/         产物模板
scripts/        确定性检查或生成辅助脚本
```

### 4.1 原子 Skill 的最小可验证性

一个 Skill 必须满足：

1. 有单一主要责任。
2. 输入可以明确列出。
3. 输出可以结构化描述。
4. 完成条件可以被另一个 Skill 或脚本检查。
5. 失败时知道停在哪里、回退到哪里。
6. 不依赖模型记忆隐藏上下文。
7. 不把用户未确认的假设伪装成事实。

不满足的 Skill 先拆职责或补契约，不直接继续扩写正文。

---

## 5. 统一项目状态与产物结构

### 5.1 新的项目级状态文件

在被开发项目的 `.spec/` 下逐步引入：

```text
.spec/
├── WORKFLOW.yaml              # 机器可读的全局状态
├── PIPELINE.md                # 人类可读的续跑记录，继续兼容
├── manifest.yaml              # 产物清单、版本、来源和状态
├── decisions/
│   ├── product-decisions.md
│   ├── design-decisions.md
│   ├── technical-decisions.md
│   └── testing-decisions.md
├── traceability/
│   ├── requirements-map.md
│   ├── design-map.md
│   ├── implementation-map.md
│   └── test-map.md
├── PRD/
├── 原型/
├── 设计稿/
├── 技术方案/
├── 代码评审/
├── 测试/
└── 问题日志.md
```

本轮不立即强制迁移旧项目所有目录；先建立兼容读取逻辑：

1. 有 `WORKFLOW.yaml` 时优先读取。
2. 无 `WORKFLOW.yaml` 时读取旧 `PIPELINE.md` 和既有目录推断。
3. 推断结果必须报告给用户确认，不能静默改变阶段。

### 5.2 统一产物元数据

每个正式产物增加机器可读的元数据区块，至少包括：

```yaml
artifact_id: PRD-v1
artifact_type: prd
status: draft | in_review | approved | superseded
version: 1
workflow: prd-workflow
source_artifacts:
  - product-definition-v1
  - feature-decision-v1
owner_skill: PRD-Design
review_skill: PRD-Review
created_at: 2026-09-20
updated_at: 2026-09-20
decision_refs:
  - DEC-PROD-001
open_issues: []
```

具体字段在 Phase 1 定稿前不写死到所有旧文档中，先通过试点验证字段是否足够。

---

## 6. 四大 Workflow 的详细重构方向

## 6.1 `Workflow`：总编排器

### 目标

从“编号节点串联器”升级为“基于状态、产物和门禁的项目交付编排器”。

### 要保留

- 任意起点
- PIPELINE 续跑
- 产物与评审闭环
- P0/P1 门禁
- 问题沉淀
- 浏览器和环境依赖检查

### 要改变

1. 不再把编号节点作为唯一真相，改用稳定节点 ID。
2. 不再默认每个小节点都停下，只在关键决策和阶段 Gate 停下。
3. 不再仅凭目录存在判断进度，改为读取 manifest + 状态。
4. 将四个领域 Workflow 作为一级调度单元。
5. 增加跨工作流回退和变更影响分析。
6. 将“跳过”改为带理由、风险和替代验证的显式动作。
7. 将 `P0/P1` 门禁与“用户风险接受”区分，禁止无条件强制放行未解决 P0。

### 主要产物

- `WorkFlow/SKILL.md`：总调度规则
- `WorkFlow/references/state-machine.md`
- `WorkFlow/references/routing-rules.md`
- `WorkFlow/references/change-impact.md`
- `WorkFlow/assets/workflow-template.yaml`
- 项目侧 `.spec/WORKFLOW.yaml`

### 完成标准

- 能从空项目、已有 PRD、已有代码三类入口正确路由。
- 能识别缺失产物并给出阻塞原因。
- 能在 PRD/UI/DEV/Testing 之间按问题归属回退。
- 能保留旧 `PIPELINE.md` 的兼容续跑行为。
- 不代替子 Skill 生成领域产物。

---

## 6.2 `PRD-Workflow`：从模糊想法到产品基线

这是第一优先级，也是本轮的试点 Workflow。

### 目标

把用户的点子变成经过证据、推理、取舍和评审后冻结的产品定义与需求基线。

### 目标流程

```text
P0 Idea Intake
→ P1 Product Discovery
→ P2 Competitive / Market Research
→ P3 Product Definition
→ P4 Application Blueprint
→ P5 Feature Decision / MVP Scope
→ P6 PRD Authoring
→ P7 Prototype
→ P8 Review & Rework
→ P9 Product Baseline Freeze
```

### 原子 Skill 规划

| 阶段 | 建议 Skill | 现有能力复用 |
|---|---|---|
| P0 | `Idea-Intake` | 从 `PRD-Design` 提取想法澄清能力 |
| P1 | `Product-Discovery` | 从 `PRD-Design` 的场景推演、苏格拉底提问中提取 |
| P2 | `Competitive-Analysis` | 保留并改造为“研究 + 决策输入”，不是只交报告 |
| P3 | `Product-Definition` | 新建 |
| P4 | `Application-Blueprint` | 新建，输出角色、旅程、模块、状态和端到端闭环 |
| P5 | `Feature-Decision` | 新建，输出 Adopt/Adapt/Reject/Defer + Must/Should/Could/Won’t |
| P6 | `PRD-Design` | 保留生成能力，改为消费前述基线，不再独自定义产品 |
| P7 | `Prototype-Design` | 保留，输入升级为冻结的 PRD + 页面/流程清单 |
| P8 | `PRD-Review` + `Prototype-Review` | 保留，补充产品基线偏差检查 |
| P9 | `Product-Baseline` | 新建，冻结版本、范围、未决风险和追踪关系 |

### P0：Idea Intake

输入：用户原始描述、已有资料、已存在项目上下文。

输出：

- 原始想法，不改写
- 当前理解
- 已知事实
- 未知信息
- 隐含假设
- 可能的产品解释分支
- 需要研究的问题

硬规则：不能把用户一句话直接改写为确定需求；不能在此阶段产出正式 PRD。

### P1：Product Discovery

输出：

- 目标用户候选
- 用户问题候选
- 用户当前替代方案
- 核心场景候选
- 端到端用户旅程
- 用户成功结果
- 风险与待验证假设

AI 必须先给出推荐解释和理由，再提出少量高价值问题；不能把所有产品思考都退回给用户。

### P2：Competitive / Market Research

竞品 Skill 的交付从“报告”升级为“证据 + 决策输入”：

- 直接、间接、参照竞品
- 功能矩阵
- 用户痛点和替代方案
- 竞品业务闭环
- 竞品空白和失败模式
- 竞品功能的 Adopt / Adapt / Reject / Defer 建议
- 事实、推测和假设分离

### P3：Product Definition

必须回答：

- 为谁解决什么问题
- 为什么现在做
- 产品不解决什么
- 核心价值是什么
- 与竞品相比存在的理由
- 核心产品闭环
- 成功如何判断
- 主要风险是什么

产物：`product-definition.md`。

### P4：Application Blueprint

必须规划完整应用链路，不只规划用户提出的单个功能：

- 角色与权限
- 首次使用
- 核心日常流程
- 空状态、加载、失败、中断、重复提交、无权限
- 历史记录和数据生命周期
- 设置、通知、反馈
- 管理端或运营端需要性
- 页面地图
- 模块关系
- 核心对象关系
- 状态机和终态

产物：`application-blueprint.md`、页面/流程索引和状态清单。

### P5：Feature Decision / MVP Scope

每个候选功能必须记录：

- 要解决的用户问题
- 证据来源
- 竞品情况
- 战略价值
- 用户价值
- 实现成本和风险
- 是否影响核心闭环
- 首版决策
- 不做的后果
- 后续验证方式

禁止“竞品有所以我们也做”。

### P6~P8：PRD、原型和评审

正式 PRD 只消费已确认的产品定义、蓝图、功能矩阵和 MVP 范围。原型用于验证结构和业务闭环，不提前承担视觉设计。

评审必须额外检查：

- PRD 是否仍然回答原始用户问题
- 是否出现无证据加戏
- 是否漏掉完整应用链路
- 是否混淆已确认决策和设计假设
- 是否出现需求、原型和产品定义互相冲突

### P9：Product Baseline Freeze

冻结内容：

- 产品定义版本
- MVP 功能范围
- 明确不做清单
- 页面和流程基线
- 关键产品决策
- 未决问题和接受的风险
- PRD / 原型 / 验收标准追踪表

只有完成该冻结，`PRD-Workflow` 才能交接给 `UI-Workflow`。

---

## 6.3 `UI-Workflow`：从结构基线到可实现设计基线

### 目标

先验证体验和信息架构，再生成视觉设计；避免把结构错误直接美化。

### 目标流程

```text
U0 Consume Product Baseline
→ U1 UX Architecture Check
→ U2 Interaction / State Completion
→ U3 Design Direction Decision
→ U4 Design System / Component Mapping
→ U5 Screen Design
→ U6 UI Review
→ U7 Design Baseline Freeze
```

### 现有能力调整

- `Prototype-Design` / `Prototype-Review` 仍属于 PRD-Workflow，因为它们验证产品结构。
- `UI-UX-Design` 拆清“UX 结构问题发现”和“视觉设计执行”两个模式。
- `UI-UX-Review` 负责视觉、交互状态、设计规范和可实现性检查。
- `Fidelity-Review` 作为实现后还原验收保留，不与设计阶段评审混淆。

### 关键规则

1. UI 不能静默改变已确认的页面结构。
2. 发现结构问题时，提交变更请求回到 UX/原型阶段。
3. 每个页面必须覆盖 loading、empty、error、success、permission、long-content 等必要状态。
4. 设计系统必须包含颜色、字体、间距、层级、状态、组件和使用边界。
5. 新组件优先映射已有组件资产；新建组件必须有 asset-gap 说明。
6. 设计稿必须能被下游技术方案和前端开发消费，不能只交图片。

### 主要产物

- `ux-architecture.md`
- `design-system.md`
- `design-task-list.md`
- 页面设计稿与状态清单
- `UI-BASELINE.md`
- 组件映射表

---

## 6.4 `DEV-Workflow`：从技术基线到可维护实现

### 目标

让 AI 开发前先理解已有资产、架构边界和组件库，再开始写代码；新代码必须可读、可测试、可审查、可追踪。

### 目标流程

```text
D0 Consume Product / UI Baseline
→ D1 Technical Discovery
→ D2 OSS / Existing Asset Research
→ D3 Backend Technical Design
→ D4 Frontend Technical Design
→ D5 Component / Module Decision
→ D6 Implementation Plan
→ D7 Backend Development
→ D8 Frontend Development
→ D9 Code Review
→ D10 Engineering Baseline
```

### 重点重构方向

#### 1. 组件和资产决策链

组件使用顺序固定为：

```text
精确匹配 → 组合已有组件 → 扩展已有组件 → 新建通用组件 → 新建业务组件
```

新建前必须说明：

- 现有组件为什么不能满足
- 组合或扩展为什么不合适
- 是否有两个以上复用场景
- 放入公共组件库还是业务模块
- 需要哪些状态、示例和测试

#### 2. 工程基线

每个模块需要明确：

- 职责边界
- 依赖方向
- 公共类型来源
- 业务规则归属
- 错误处理边界
- 日志和可观测性
- 测试入口
- 删除和迁移计划

#### 3. 技术方案与开发解耦

技术方案 Skill 负责决策和设计；开发 Skill 负责按方案实现；代码评审不替代技术方案评审，也不擅自改变业务需求。

#### 4. 代码评审分流

- 业务逻辑错：回 PRD 或技术方案
- 接口契约错：回技术方案
- 代码实现错：回开发
- 视觉还原错：进入 Fidelity-Review / UI-Workflow 反馈
- 架构债务：记录工程基线和后续任务

### 主要产物

- `technical-discovery.md`
- `TDD` / `FTDD`
- `component-decision-log.md`
- `implementation-plan.md`
- 代码评审报告与任务清单
- `ENGINEERING-BASELINE.md`

---

## 6.5 `Testing-Workflow`：从验收策略到发布门禁

### 目标

测试不是开发结束后的单一动作，而是从需求基线开始建立追踪，开发完成后执行证据化验收。

### 目标流程

```text
T0 Consume Product / UI / Engineering Baseline
→ T1 Test Strategy
→ T2 Traceability / Test Planning
→ T3 Deterministic Gates
→ T4 Contract / Integration Tests
→ T5 E2E / Visual / Accessibility
→ T6 Performance / Security / Compatibility
→ T7 Defect Triage
→ T8 Fix & Regression
→ T9 Release Gate
```

### 现有能力调整

- `auto-test` 作为自动化验收执行器保留并接入 Testing-Workflow。
- `Testing` 作为人工/探索式测试能力保留，收敛为专门的执行模式，避免与 `auto-test` 的职责重叠。
- `Fidelity-Review` 作为视觉还原专项检查接入 T5。
- `Bug-Fix` 作为缺陷定位与修复委托入口接入 T7/T8，但不代替测试回归。

### 测试计划必须从以下内容生成

- PRD 验收标准
- 应用蓝图中的业务状态
- 原型/设计中的交互状态
- 技术方案中的接口契约
- 代码模块和组件清单
- 风险与历史缺陷模式

### 缺陷回退规则

| 缺陷 | 处置 |
|---|---|
| 需求不明确或验收标准错误 | 回 PRD-Workflow |
| 页面结构/交互设计错误 | 回 UI-Workflow 或原型阶段 |
| 接口契约、架构和数据流错误 | 回 DEV-Workflow 技术设计 |
| 代码实现错误 | 回 DEV-Workflow 开发 |
| 测试环境、数据或用例错误 | 回 Testing-Workflow 测试计划 |

### 发布 Gate

必须有：

- 本次执行的命令和结果
- 关键页面/API/业务链路证据
- 未解决问题及风险接受记录
- 需求到测试的覆盖摘要
- 回归范围和结果
- 明确的 `PASS` / `CONDITIONAL` / `BLOCKED`

---

## 7. 分阶段执行计划

## Phase 0：基线盘点与重构边界（先做）

### 目标

在不改变现有 Skill 行为的情况下，完整记录现状并确定迁移边界。

### 操作步骤

1. 记录当前分支、工作区和用户未提交变更。
2. 盘点所有含 `SKILL.md` 的目录。
3. 建立现有 Skill → 目标 Workflow 的映射表。
4. 为每个 Skill 标记当前职责、输入、输出、依赖、问题和迁移动作：保留 / 拆分 / 合并 / 重命名 / 归档。
5. 梳理现有 `Workflow` 的节点、门禁、回退规则和产物路径。
6. 梳理现有公共规则，标记重复、冲突和应下沉的内容。
7. 记录现有 `.spec/` 目录约定和安装副本同步约定。
8. 盘点已有文档计划，避免新架构与历史计划互相冲突。

### 产出

```text
docs/workflow-v2/00-baseline-inventory.md
docs/workflow-v2/skill-workflow-mapping.md
docs/workflow-v2/artifact-inventory.md
docs/workflow-v2/decision-log.md
docs/workflow-v2/compatibility-notes.md
```

### 验收

- 所有现有 Skill 都有归属和迁移策略。
- 没有在未盘点前直接删除或移动目录。
- 能说明每个旧 Skill 在新架构中的位置。

---

## Phase 1：建立公共契约和状态基础

### 目标

先让所有 Workflow 共享同一套状态、产物、证据和门禁语言。

### 操作步骤

1. 定义 Workflow 节点 ID、状态值和状态转移规则。
2. 定义 Skill Contract 模板。
3. 定义 Artifact Metadata 模板。
4. 定义 `.spec/WORKFLOW.yaml` schema。
5. 定义 `.spec/manifest.yaml` schema。
6. 定义决策记录模板和决策类型。
7. 定义追踪关系格式。
8. 定义 Gate 结果：`PASS`、`CONDITIONAL`、`BLOCKED`。
9. 定义回退和变更影响规则。
10. 定义旧 `PIPELINE.md` 的兼容读取策略。
11. 编写最小确定性校验脚本，不依赖模型判断。

### 产出

```text
governance/
├── skill-registry.yaml
├── workflow-registry.yaml
├── artifact-registry.yaml
├── state-registry.yaml
└── schemas/

shared/
├── skill-contract.md
├── artifact-contract.md
├── decision-record.md
├── traceability.md
└── gate-policy.md

scripts/
├── validate-skill-contract.ps1
├── validate-artifact-manifest.ps1
└── validate-workflow-graph.ps1
```

### 验收

- 新增 Skill 可以按模板填写，不需要重新发明字段。
- 同一个状态和门禁不会在不同 Skill 中使用不同含义。
- 脚本可以识别缺失 frontmatter、无效引用、未知节点和坏的 manifest。

---

## Phase 2：PRD-Workflow 试点

### 目标

先把最关键的“从模糊想法到明确产品”跑通。

### 操作步骤

1. 创建 `PRD-Workflow/` 编排 Skill，不立即删除旧 `Workflow` 节点。
2. 从现有 `PRD-Design` 中提取 Idea Intake、Discovery、问题澄清和场景推演规则。
3. 改造 `Competitive-Analysis`，增加“竞品功能 → 产品决策”的输出。
4. 新建 `Product-Definition`。
5. 新建 `Application-Blueprint`。
6. 新建 `Feature-Decision`。
7. 将 `PRD-Design` 改成“基于产品基线生成 PRD”，不再独立决定完整产品范围。
8. 将 `Prototype-Design` 的输入改为 PRD + 页面/流程基线。
9. 将 `PRD-Review` 和 `Prototype-Review` 增加产品基线偏差检查。
10. 新建 `Product-Baseline`，冻结产品定义、范围、明确不做、风险和追踪。
11. 用一个模糊点子作为黄金场景运行完整 PRD-Workflow。
12. 记录每一步模型是否越权脑补、是否遗漏全链路、是否把假设当事实。

### 验收

给出一个只有一句话的产品想法时，最终至少能得到：

- 产品定义
- 用户与场景
- 竞品证据和功能决策
- 应用全景与异常状态
- MVP 范围和明确不做
- PRD
- 可点击低保真原型
- 评审问题和复核结果
- 产品基线

且用户无需在每个小问题上自己填写完整答案；AI 需要先研究、推演并提供推荐选项。

---

## Phase 3：UI-Workflow

### 目标

在不破坏产品结构基线的前提下，形成可实现的 UX/UI 基线。

### 操作步骤

1. 新建 `UI-Workflow/`。
2. 将原型视为结构输入，不与视觉设计稿混淆。
3. 从 `UI-UX-Design` 中拆出 UX 检查和视觉生成两个模式。
4. 补齐页面状态清单、交互状态、可访问性和响应式规则。
5. 接入现有组件库/资产决策链。
6. 完善设计系统产物和组件映射表。
7. 改造 `UI-UX-Review` 以检查视觉、交互状态、设计系统一致性和可实现性。
8. 新建 `UI-BASELINE` 冻结设计版本。
9. 用 PRD-Workflow 的黄金场景生成并验收设计稿。

### 验收

- 设计不会偷偷改变已经确认的产品流程。
- 发现结构问题能够回退到原型/PRD，而不是在设计稿里自行改需求。
- 每个页面有完整状态清单。
- 下游开发可以直接消费设计系统和组件映射。

---

## Phase 4：DEV-Workflow

### 目标

建立“先检索资产和方案，再实施”的开发闭环，降低重复造轮子和代码腐化。

### 操作步骤

1. 新建 `DEV-Workflow/`。
2. 将 OSS-Radar、Backend-Tech-Design、Frontend-Tech-Design、Tech-Review 接入技术设计阶段。
3. 统一 TDD/FTDD 的输入和输出契约。
4. 新建或整理组件/资产注册表。
5. 统一组件决策链和 asset-gap 记录。
6. 将 Backend-Dev、Frontend-Dev 的共同工程约束下沉到 `shared/dev-common.md`，各自只保留领域规则。
7. 规定实现计划、模块边界、依赖方向和测试入口。
8. 改造 Code-Review，使它按问题归属给出正确回退路径。
9. 新建 `ENGINEERING-BASELINE`，记录可维护性、债务和已知风险。
10. 在一个真实小功能上验证：检索已有组件、复用、扩展、新建和沉淀全链路。

### 验收

- AI 开发前会检索已有组件和资产。
- 新建组件有明确差异说明和测试要求。
- 方案、代码和评审使用同一组契约。
- 代码评审能区分需求问题、方案问题、实现问题和视觉问题。

---

## Phase 5：Testing-Workflow

### 目标

把测试从“最后跑一下”升级为“基于基线和追踪关系的证据化发布门禁”。

### 操作步骤

1. 新建 `Testing-Workflow/`。
2. 整理 `Testing` 与 `auto-test` 的职责边界。
3. 新建测试策略和测试追踪产物。
4. 将 PRD AC、业务状态、API 契约、组件和代码模块映射到测试用例。
5. 将确定性门禁、契约测试、E2E、视觉、可访问性、性能和安全检查分层。
6. 接入 `Fidelity-Review` 和 `Bug-Fix` 的正确位置。
7. 规定缺陷分级、回退分类、修复和回归规则。
8. 新建发布 Gate 产物，明确 PASS / CONDITIONAL / BLOCKED。
9. 用 Phase 2 的黄金场景执行完整测试工作流。

### 验收

- 测试计划能够从需求和设计基线生成，不依赖临时聊天记忆。
- 每个关键验收标准都有测试覆盖或明确豁免理由。
- 测试结果带命令、日志、截图或其他证据。
- 发现问题后能回退到正确的工作流。
- 发布结论不会把“没测到”写成“通过”。

---

## Phase 6：总编排整合、兼容和迁移

### 目标

让总 `Workflow` 真正调度四个领域 Workflow，并保持旧项目可续跑。

### 操作步骤

1. 将四个领域 Workflow 注册到总 Workflow。
2. 用稳定节点 ID 替换旧编号作为内部状态。
3. 保留旧编号作为显示层兼容字段一段时间。
4. 实现从 `.spec/WORKFLOW.yaml` 读取状态。
5. 对没有新状态文件的旧项目执行兼容推断，并要求确认。
6. 实现跨工作流回退和变更影响提示。
7. 更新根 `README.md`，但不覆盖用户已有修改。
8. 更新各 Workflow README、目录树和迁移说明。
9. 对旧 Skill 增加兼容入口或迁移说明。
10. 运行完整静态校验和黄金场景回归。
11. 记录仍然保留的旧流程、暂未迁移的 Skill 和已知差异。

### 验收

- 新项目可以从模糊想法跑到测试发布 Gate。
- 已有 PRD 项目可以从 PRD、原型、UI、DEV 或 Testing 任一合理入口续跑。
- 已有旧 `.spec/PIPELINE.md` 的项目不会被错误识别为新项目。
- 跳过、暂停、回退和重新运行均有记录。
- 四个领域 Workflow 可以独立调用，也可以由总 Workflow 调度。

---

## 8. 每个阶段的验证方式

### 8.1 静态验证

每次修改 Skill 后至少运行：

1. Skill frontmatter 校验。
2. 名称和目录校验。
3. 内部引用存在性校验。
4. 模板和资源可发现性校验。
5. Workflow 节点依赖和回退图校验。
6. manifest/schema 校验。
7. Markdown 编码和基本结构检查。

### 8.2 行为验证

至少准备三类黄金场景：

#### 场景 A：模糊想法

输入只有一句产品想法，验证 PRD-Workflow 是否会先发现、调研、定义和取舍，而不是直接写 PRD。

#### 场景 B：已有 PRD

输入为已有 PRD 和部分原型，验证总 Workflow 是否从正确节点开始，并能跳过已完成阶段。

#### 场景 C：开发后发现问题

输入为实现代码、测试失败和截图，验证问题能被分流到 PRD、UI、DEV 或 Testing 的正确位置。

### 8.3 质量指标

本轮不追求“文档更长”，重点观察：

- 需求澄清前是否减少无依据脑补。
- 竞品结论是否真正产生功能取舍。
- 产品全链路是否覆盖正常、异常和生命周期。
- 阶段交接是否能仅靠产物完成。
- 回退位置是否正确。
- 新建组件是否减少重复实现。
- 测试结论是否有证据。
- 旧项目兼容是否稳定。

---

## 9. 迁移与兼容策略

### 9.1 不做一次性大爆炸重构

不采用以下方式：

- 一次性重命名全部 Skill 目录。
- 一次性重写所有 `SKILL.md`。
- 一次性删除现有产物格式。
- 先造大量新 Skill，再寻找真实使用场景。
- 将现有规则全部复制到四个 Workflow，制造四份漂移版本。

### 9.2 采用适配层

旧 Skill 先作为执行能力被新 Workflow 调用：

```text
新 Workflow 编排层
        ↓
旧 Skill / 新原子 Skill
        ↓
标准化产物与状态适配器
```

验证新 Workflow 确实比旧 Workflow 更好后，再逐个替换旧入口。

### 9.3 删除条件

只有满足以下条件，才允许删除或归档旧入口：

1. 新入口已覆盖旧入口的全部必要能力。
2. 至少一个真实黄金场景使用新入口通过。
3. 旧项目兼容路径已验证。
4. README、引用和安装副本已同步。
5. 有明确迁移说明和回滚方法。

---

## 10. 风险与应对

| 风险 | 应对 |
|---|---|
| 重构变成大量文档搬运 | 每个新增文件必须绑定一个契约、状态、验证或真实场景 |
| 四个 Workflow 内容重复 | 公共规则下沉 `shared/`，领域只保留差异 |
| Skill 越拆越多，调度变复杂 | 新 Skill 必须满足单一责任和可验证输出；优先复用，不为拆而拆 |
| AI 仍然根据用户一句话自由发挥 | PRD-Workflow 增加 Product Definition、Blueprint、Feature Decision 和 Baseline Gate |
| 评审发现问题后下游打补丁 | 强制记录问题归属和回退路径 |
| 旧项目无法续跑 | `WORKFLOW.yaml` 优先、`PIPELINE.md` 兼容、推断须确认 |
| 组件库成为第二个垃圾场 | 注册表、asset-gap、复用优先、组件沉淀 Gate |
| 流程太重，用户不愿使用 | 只在高影响决策暂停；提供轻量路径和完整路径 |
| 旧工作区变更被误提交 | 每次提交前检查状态，只暂存本轮文件 |
| 测试结果不可信 | evidence before claims；没有证据不能声明通过 |

---

## 11. 总体完成定义

本轮重构完成，不以“新增了多少 Skill”作为标准，而以以下结果为标准：

### 架构层

- [ ] 存在一个总 `Workflow`。
- [ ] 存在 `PRD-Workflow`、`UI-Workflow`、`DEV-Workflow`、`Testing-Workflow`。
- [ ] 四个 Workflow 可以独立调用，也可以由总 Workflow 调度。
- [ ] 原子 Skill 有统一契约和单一职责。

### PRD 层

- [ ] 一句模糊想法不会直接进入正式 PRD。
- [ ] 竞品分析可以转化为 Adopt / Adapt / Reject / Defer 决策。
- [ ] 产品定义、应用全景、功能取舍和 MVP 范围有独立产物。
- [ ] 原型和评审结束后有产品基线冻结。

### UI 层

- [ ] UX 问题和视觉问题分流。
- [ ] 页面状态、组件状态和交互闭环完整。
- [ ] 设计系统和组件映射可以被开发消费。
- [ ] UI 变更不会静默改产品需求。

### DEV 层

- [ ] 开发前会检索已有资产和组件。
- [ ] 新建组件有明确差异说明和测试要求。
- [ ] 技术方案、代码和评审共享追踪关系。
- [ ] 代码问题可以回退到正确阶段。

### Testing 层

- [ ] 测试从产品和工程基线生成。
- [ ] 关键需求有测试覆盖或明确豁免。
- [ ] 测试结果有可复核证据。
- [ ] 缺陷有分类、修复、回归和发布 Gate。

### 工程层

- [ ] 旧项目仍可续跑。
- [ ] 新项目可以从模糊想法跑到发布 Gate。
- [ ] 静态验证和黄金场景验证可重复运行。
- [ ] 所有重大决策、未决问题和风险都有留痕。

---

## 12. 下一步执行顺序

计划确认后，严格按以下顺序开始：

```text
Step 1  完成 Phase 0 基线盘点
Step 2  评审并定稿公共契约、状态和产物格式
Step 3  只实现 PRD-Workflow 试点
Step 4  用模糊想法黄金场景运行并修正
Step 5  在 PRD 试点稳定后迁移 UI-Workflow
Step 6  再迁移 DEV-Workflow
Step 7  最后迁移 Testing-Workflow
Step 8  整合总 Workflow、兼容旧项目并完成回归
```

第一阶段不直接大规模改写业务 Skill，而是先完成现状盘点、映射和公共契约，确保后续每一步都有明确边界和可验证结果。


---

## 13. 迭代开发与 Bug 修复适配

### 13.1 结论

本架构适用于新产品 0→1、功能迭代和 Bug 修复，但三者不能机械地运行同一条完整链路。总 `Workflow` 需要支持三种运行模式：

```text
CREATE     新产品或新应用，从产品发现开始
CHANGE     已有产品的功能迭代，从变更影响到的最早阶段开始
DEFECT     已有行为偏离基线，从缺陷分诊和根因归属开始
```

无论哪一种模式，最终都使用同一套产品、设计、工程和测试基线；区别只在于起点、受影响范围和必须重跑的 Gate。

### 13.2 功能迭代流程

```text
变更请求
→ Change-Intake
→ Impact-Analysis
→ 确定最早受影响基线
→ 进入对应领域 Workflow
→ 更新受影响产物
→ 下游影响传播
→ Regression-Testing
→ 新基线版本冻结
```

迭代不默认重跑全链：

| 变更类型 | 默认起点 | 必须经过 |
|---|---|---|
| 文案、静态配置，不改变业务语义 | UI 或 DEV | 受影响实现 + 定向测试 |
| 页面布局、交互反馈、状态补全 | UI-Workflow | UI 评审 + 前端实现 + 还原/回归 |
| 新增局部功能，产品定位不变 | PRD-Workflow 的 Feature Decision / PRD 阶段 | PRD、受影响设计、开发、测试 |
| 修改业务规则、权限、状态机、数据契约 | PRD-Workflow 的 Blueprint / PRD 阶段 | 产品、技术方案、开发、契约/回归测试 |
| 修改目标用户、核心价值、商业模式或核心闭环 | PRD-Workflow 的 Product Discovery / Definition 阶段 | 受影响的完整下游链 |
| 纯重构，无外部行为变化 | DEV-Workflow | 工程方案、代码评审、回归测试 |
| 架构、依赖、安全或基础设施升级 | DEV-Workflow 的 Technical Discovery / Tech Design 阶段 | 方案评审、开发、非功能测试、回归 |

迭代的核心不是“这是小需求还是大需求”，而是：**最早被改变的事实源是什么，以及哪些下游产物因此失效。**

### 13.3 Bug 修复流程

```text
问题报告
→ Defect-Triage（复现、证据、严重度、预期/实际）
→ Bug-Fix（根因定位与归属）
→ 路由到正确 Workflow / Skill
→ 最小正确修复
→ Regression-Testing
→ 缺陷关闭
→ 必要时沉淀 bug-pattern / skill 防复发规则
```

根因路由：

| 根因 | 回退位置 |
|---|---|
| 需求没有定义、业务规则矛盾 | PRD-Workflow |
| 原型流程、页面结构或交互状态错误 | PRD-Workflow 原型阶段或 UI-Workflow |
| 技术方案、接口契约、数据设计错误 | DEV-Workflow 技术设计阶段 |
| 代码没有按正确方案实现 | Backend-Dev / Frontend-Dev |
| 测试用例、测试数据或测试环境错误 | Testing-Workflow |
| 线上配置、部署或依赖异常 | DEV-Workflow 的工程/运行修复路径 |

Bug 修复不默认重跑竞品分析、产品发现和全部设计流程；如果预期行为已经由已批准基线明确，只需修复实现并执行受影响回归。如果无法回答“正确行为应该是什么”，它就不再是纯代码 Bug，必须回到上游基线澄清。

### 13.4 紧急 Hotfix

紧急问题允许走缩短路径，但不能无记录跳过全部门禁：

```text
快速分诊
→ 最小修复
→ 最小强制门禁（构建/类型/关键测试/主链冒烟）
→ 发布
→ 补充完整根因分析、回归、文档和沉淀
```

Hotfix 必须记录：

- 为什么需要紧急通道
- 跳过了哪些检查
- 当前残留风险
- 回滚方法
- 补做任务和截止状态

### 13.5 变更规模分级

| 等级 | 典型范围 | 默认策略 |
|---|---|---|
| C0 | 文案、注释、非语义配置 | 定向修改 + 最小验证 |
| C1 | 单页面、单组件、单接口实现问题 | DEV/UI 局部路径 + 定向回归 |
| C2 | 跨模块功能或业务规则变化 | PRD 受影响部分 + UI/DEV/Testing |
| C3 | 核心流程、权限、数据模型、接口契约变化 | 从 Application Blueprint / Tech Design 重跑 |
| C4 | 产品定位、目标用户、核心价值、重大合规/架构变化 | 从 Product Discovery / Definition 重跑完整受影响链 |

`Impact-Analysis` 负责给出建议等级、受影响产物和推荐路径；用户或授权角色对高影响变更进行最终确认。

---

## 14. 重构后的目标 Skill 清单

> 这是目标架构清单，不代表第一批一次性创建全部目录。采用“先建立 Workflow 和契约、再按真实场景逐步拆分”的方式。标记：`保留改造` = 现有 Skill 继续存在但收窄职责；`新增` = 需要创建；`兼容迁移` = 新名称/新职责稳定前保留旧入口。

### 14.1 编排层（5 个）

| # | Skill | 状态 | 单一职责 |
|---|---|---|---|
| 1 | `Workflow` | 保留重构 | 识别 CREATE/CHANGE/DEFECT 模式，调度四大 Workflow，维护全局状态、门禁和跨阶段回退 |
| 2 | `PRD-Workflow` | 新增 | 编排从模糊想法到产品基线冻结的完整产品流程 |
| 3 | `UI-Workflow` | 新增 | 编排从产品结构基线到设计基线冻结的 UX/UI 流程 |
| 4 | `DEV-Workflow` | 新增 | 编排技术调研、技术方案、资产决策、开发和代码评审 |
| 5 | `Testing-Workflow` | 新增 | 编排测试策略、执行、缺陷分流、回归和发布门禁 |

### 14.2 迭代与缺陷横向 Skill（4 个）

| # | Skill | 状态 | 单一职责 |
|---|---|---|---|
| 6 | `Change-Intake` | 新增 | 将自然语言迭代诉求整理成明确的变更请求，不直接设计解决方案 |
| 7 | `Impact-Analysis` | 新增 | 基于追踪关系计算受影响的产品、页面、组件、接口、代码和测试产物 |
| 8 | `Defect-Triage` | 新增 | 收集复现步骤、预期/实际、环境、证据、严重度和影响范围 |
| 9 | `Bug-Fix` | 保留改造 | 基于证据定位根因、判定归属并委托正确的方案/开发/回归 Skill；自身不越权包办全部修复 |

### 14.3 PRD-Workflow 原子 Skill（10 个）

| # | Skill | 状态 | 单一职责 |
|---|---|---|---|
| 10 | `Idea-Intake` | 新增 | 保留用户原始想法，识别已知、未知、假设和需要研究的问题 |
| 11 | `Product-Discovery` | 新增 | 推演目标用户、用户问题、场景、替代方案、旅程和待验证假设 |
| 12 | `Competitive-Analysis` | 保留改造 | 研究竞品、市场和用户证据，并形成可供产品决策消费的结构化输入 |
| 13 | `Product-Definition` | 新增 | 明确为谁解决什么问题、核心价值、产品边界、差异化和成功判断 |
| 14 | `Application-Blueprint` | 新增 | 规划角色、全链路流程、模块、页面、对象、状态、异常和数据生命周期 |
| 15 | `Feature-Decision` | 新增 | 将候选功能转化为 Adopt/Adapt/Reject/Defer 和 Must/Should/Could/Won’t 决策 |
| 16 | `PRD-Design` | 保留改造 | 只基于已确认产品定义、蓝图和范围编写可测试 PRD |
| 17 | `PRD-Review` | 保留改造 | 独立检查产品逻辑、完整性、冲突、可测试性和基线偏差 |
| 18 | `Prototype-Design` | 保留改造 | 将已确认需求转为低保真可交互结构，用于验证流程而非视觉 |
| 19 | `Prototype-Review` | 保留改造 | 检查页面完整性、文案、状态、入口出口和业务闭环 |

产品基线冻结由 `PRD-Workflow` 执行，不单独创建只负责“改状态”的空壳 Skill。

### 14.4 UI-Workflow 原子 Skill（6 个）

| # | Skill | 状态 | 单一职责 |
|---|---|---|---|
| 20 | `UX-Architecture` | 新增 | 检查和设计信息架构、导航、页面层级和任务路径；发现产品问题时发起回退 |
| 21 | `Interaction-State-Design` | 新增 | 补全 loading/empty/error/success/permission/long-content 等交互和页面状态 |
| 22 | `Design-System` | 新增 | 定义设计 token、字体、颜色、间距、层级、组件状态和使用边界 |
| 23 | `Component-Mapping` | 新增 | 将页面设计元素映射到已有 UI 组件/设计资产，记录缺口，不负责写业务代码 |
| 24 | `UI-UX-Design` | 保留改造 | 基于已确认 UX 和设计系统生成页面设计稿，不静默修改产品结构 |
| 25 | `UI-UX-Review` | 保留改造 | 检查设计稿完整性、规范一致性、交互状态、可访问性和可实现性 |

设计基线冻结由 `UI-Workflow` 执行。

### 14.5 DEV-Workflow 原子 Skill（10 个）

| # | Skill | 状态 | 单一职责 |
|---|---|---|---|
| 26 | `Technical-Discovery` | 新增 | 阅读现有代码、架构、依赖、约束、技术债和运行环境，建立技术现状基线 |
| 27 | `OSS-Radar` | 保留改造 | 调研同域开源项目和可复用实现，只提供外部技术情报和证据 |
| 28 | `Backend-Tech-Design` | 保留改造 | 设计后端架构、数据、接口、业务边界、可观测性和迁移方案 |
| 29 | `Frontend-Tech-Design` | 保留改造 | 设计前端架构、状态、路由、接口消费、组件组织和页面实现方案 |
| 30 | `Tech-Review` | 保留改造 | 独立评审 TDD/FTDD 的正确性、契约一致性、风险和可实施性 |
| 31 | `Component-Decision` | 新增 | 按精确复用→组合→扩展→新建的顺序决定工程组件/模块资产方案 |
| 32 | `Implementation-Planning` | 新增 | 将已批准方案拆成有依赖、有验收、有批次的实现计划 |
| 33 | `Backend-Dev` | 保留改造 | 按批准方案和计划实现后端代码、迁移、测试和运行证据 |
| 34 | `Frontend-Dev` | 保留改造 | 按批准设计和方案实现前端页面、交互、组件和测试 |
| 35 | `Code-Review` | 保留改造 | 检查契约、架构、质量、安全、可维护性和实现偏差，并按根因分流 |

工程基线冻结由 `DEV-Workflow` 执行。

### 14.6 Testing-Workflow 原子 Skill（9 个）

| # | Skill | 状态 | 单一职责 |
|---|---|---|---|
| 36 | `Test-Planning` | 新增 | 根据需求、状态、设计、接口和风险生成测试策略、矩阵与追踪关系 |
| 37 | `Quality-Gate` | 新增 | 执行 install/typecheck/lint/unit/build 等确定性工程门禁并保存证据 |
| 38 | `Contract-Testing` | 新增 | 验证 API、schema、共享类型、错误码、事件和数据契约一致性 |
| 39 | `Integration-Testing` | 新增 | 验证模块、服务、数据库、队列和外部依赖集成行为 |
| 40 | `E2E-Testing` | 从 `auto-test` 收窄/兼容迁移 | 运行用户主链、页面状态和跨端端到端自动化验收 |
| 41 | `Fidelity-Review` | 保留改造 | 对照设计基线检查实现页视觉与交互还原度并截图存证 |
| 42 | `Exploratory-Testing` | 从 `Testing` 收窄/兼容迁移 | 执行人工/AI 探索式走查，发现脚本化用例未覆盖的问题 |
| 43 | `Nonfunctional-Testing` | 新增 | 按风险触发性能、安全、可访问性、兼容性和稳定性专项测试 |
| 44 | `Regression-Testing` | 新增 | 根据变更影响清单执行定向或完整回归并判定缺陷是否关闭 |

发布 Gate 由 `Testing-Workflow` 汇总执行；`auto-test` 和 `Testing` 在迁移期保留兼容入口，稳定后再决定是否改名或归档。

### 14.7 链外研究、核验与 Skill 治理（5 个）

| # | Skill | 状态 | 单一职责 |
|---|---|---|---|
| 45 | `Fact-Check` | 保留 | 对重要事实和技术断言做独立取证与判定 |
| 46 | `Source-Reading` | 保留 | 阅读外部源码仓库并输出可追踪的结构和关键实现说明 |
| 47 | `Skill-Optimizer` | 保留改造 | 根据真实问题、评测和运行记录优化现有 Skill |
| 48 | `Skill-Evolver` | 保留改造 | 从长期信号中发现需要演进的模式，提出演进建议和触发条件 |
| 49 | `Essence-Distill` | 保留 | 将书籍、仓库和学习资料蒸馏为可溯源的高密度知识资产 |

### 14.8 不应被创建为独立 Skill 的内容

以下内容属于 Workflow 职责、模板、脚本或产物，不为它们单独创建空壳 Skill：

- `Product-Baseline`：由 `PRD-Workflow` 冻结。
- `UI-Baseline`：由 `UI-Workflow` 冻结。
- `Engineering-Baseline`：由 `DEV-Workflow` 冻结。
- `Release-Gate`：由 `Testing-Workflow` 汇总判定。
- `Artifact-Manifest`：是产物和 schema。
- `Traceability`：是公共契约和映射产物。
- `Asset-Registry`：是机器可读注册表和校验脚本。
- 单纯的文档格式转换、目录创建和状态改写：优先用模板/脚本完成。

### 14.9 总量与实施原则

目标清单共 49 个 Skill：

```text
编排层                 5
迭代与缺陷横向         4
PRD 原子 Skill         10
UI 原子 Skill           6
DEV 原子 Skill         10
Testing 原子 Skill      9
链外研究与治理          5
合计                   49
```

这 49 个是目标职责地图，不是要求立即生成 49 份大而全的 `SKILL.md`。实施时遵循：

1. 现有 Skill 优先收窄和复用。
2. 新 Skill 必须有独立触发条件、输入、输出和完成 Gate。
3. 如果两个步骤总是一起触发、共享全部上下文且无法独立验收，则保留为一个 Skill 的内部模式。
4. 如果真实运行证明某个新 Skill 只是空壳，则合并回所属 Workflow 或相邻 Skill。
5. 优先完成 CREATE/CHANGE/DEFECT 三个黄金场景，不以目录数量作为重构完成标准。

---

## 15. 从“交付流水线”升级为“持续运行与进化闭环”

> 本节是对前述目标架构的重要升级：四个研发 Workflow 只能覆盖“做出来并测完”，不足以覆盖发布、运行、观测、学习和持续优化。目标架构调整为六个领域 Workflow，并增加运行期闭环。第 16 节的 60 个 Skill 清单取代第 14 节的 49 个初版职责清单，作为后续实施基线。

### 15.1 最终目标

本系统不是一次性把应用开发完成，而是让应用持续经历：

```text
发现问题 / 机会
→ 做出产品与技术决策
→ 设计与开发
→ 测试验证
→ 安全发布
→ 运行观测
→ 分析真实结果
→ 产生下一轮迭代 / 缺陷 / 优化
→ 再次验证和发布
```

最终主循环：

```text
PRD-Workflow
→ UI-Workflow
→ DEV-Workflow
→ Testing-Workflow
→ Release-Workflow
→ Operations-Workflow
→ Change / Defect / Incident / Optimization
→ Impact-Analysis
→ 路由回最早受影响的 Workflow
→ Testing
→ Release
→ Operations
```

这是一条有证据、有基线、有回滚、有前后对比的正向循环，而不是“看到报错就让 AI 自动改代码”的无控制循环。

### 15.2 六个领域 Workflow

```text
Workflow
├── PRD-Workflow
├── UI-Workflow
├── DEV-Workflow
├── Testing-Workflow
├── Release-Workflow
└── Operations-Workflow
```

| Workflow | 负责的生命周期阶段 |
|---|---|
| `PRD-Workflow` | 明确问题、产品目标、范围、验收标准和产品基线 |
| `UI-Workflow` | 建立 UX、视觉、交互状态和设计基线 |
| `DEV-Workflow` | 技术设计、可观测性设计、实现和工程基线 |
| `Testing-Workflow` | 验证需求、设计、代码、非功能质量和回归 |
| `Release-Workflow` | 发布计划、部署、灰度、回滚准备和发布后验证 |
| `Operations-Workflow` | 运行观测、信号分诊、事故响应、产品分析和优化回流 |

### 15.3 运行期不是只收集错误日志

正向循环需要采集六类信号：

| 信号类型 | 示例 | 主要用途 |
|---|---|---|
| 技术错误 | 异常、5xx、崩溃、任务失败、前端白屏 | Defect / Incident |
| 可靠性与性能 | 可用性、错误率、p95/p99、超时、资源饱和 | 性能优化、容量和稳定性治理 |
| 用户体验 | Web Vitals、页面加载、交互失败、关键路径中断 | UI/前端优化 |
| 产品行为 | 激活、转化、留存、功能使用、流程流失 | 产品迭代和功能取舍 |
| 用户反馈 | 客诉、工单、建议、评分、访谈 | 产品问题与机会发现 |
| 安全、合规与成本 | 异常访问、权限风险、敏感数据、调用成本 | 安全修复、合规治理、成本优化 |

仅接日志无法判断应用是不是“更高质量”。必须同时观测：

```text
系统是否稳定
+ 用户是否能完成任务
+ 产品目标是否改善
+ 变更是否产生副作用
+ 成本是否可接受
```

### 15.4 可观测性必须前置设计

监控和日志不是项目做完后临时安装。它们需要进入各阶段：

#### PRD 阶段

- 定义产品目标及可观测的成功指标。
- 定义关键用户旅程和失败终点。
- 定义重要业务事件和禁止采集的敏感信息。
- 每个关键功能说明“上线后怎样判断有效”。

#### UI 阶段

- 定义关键交互事件、失败反馈和页面性能关注点。
- 定义用户旅程中允许观测的步骤，不采集密码、令牌和敏感正文。
- 保证埋点不改变交互行为。

#### DEV 阶段

- 设计结构化日志、错误分类、trace/correlation ID。
- 定义指标、追踪、审计日志、健康检查和运行环境信息。
- 定义 SLI/SLO、告警阈值、去重、降噪和采样策略。
- 接入 `server-log`、`server-monitor`、`web-monitor` 或目标项目的等价能力。
- 将可观测性作为功能完成定义的一部分，不允许只留 TODO。

#### Testing 阶段

- 验证关键错误是否能被记录和关联。
- 验证日志不会泄露密钥、密码、令牌和隐私数据。
- 验证告警能触发、恢复后能关闭、相同事件不会形成告警风暴。
- 验证 trace 可以串起前端、网关、后端、数据库和外部依赖的关键链路。

#### Release 阶段

- 保存 release ID、版本、commit、配置和迁移版本。
- 让运行信号可以关联到具体发布批次。
- 发布后执行健康检查、关键主链冒烟和指标基线对比。
- 指标越过回滚阈值时停止灰度或执行回滚。

#### Operations 阶段

- 持续聚合、去重、关联和分级运行信号。
- 区分事故、缺陷、优化机会、产品机会和无行动噪声。
- 观察发布前后指标变化。
- 将确认后的信号转成标准 Change / Defect / Incident / Optimization 输入。

### 15.5 运行期信号处理状态机

```text
DETECTED
→ NORMALIZED
→ DEDUPLICATED
→ CORRELATED
→ TRIAGED
→ CLASSIFIED
→ PRIORITIZED
→ ROUTED
→ FIXED / IMPROVED
→ VERIFIED
→ RELEASED
→ OBSERVED
→ CLOSED 或 REOPENED
```

每个运行信号至少记录：

- signal ID
- 来源和环境
- 首次/最近发生时间
- 影响版本和 release ID
- 用户/请求/trace 关联信息（脱敏）
- 发生次数和影响范围
- 严重度和置信度
- 预期行为与实际行为
- 关联产品目标、需求、页面、接口和代码模块
- 当前分类和处理状态
- 修复/优化版本
- 发布后验证结果

### 15.6 信号分类与路由

| 分类 | 判定 | 路由 |
|---|---|---|
| `INCIDENT` | 正在造成严重业务影响，需要先止损 | `Incident-Response` → 缓解/回滚 → `Bug-Fix` |
| `DEFECT` | 实际行为偏离已批准基线 | `Defect-Triage` → `Bug-Fix` |
| `PRODUCT-GAP` | 正确行为没有被定义或产品链路缺失 | `PRD-Workflow` |
| `UX-GAP` | 用户完成任务困难，设计/交互基线需调整 | `UI-Workflow` |
| `PERFORMANCE` | 功能正确但时延、吞吐、资源或稳定性不达标 | DEV 技术设计 + Nonfunctional Testing |
| `SECURITY` | 权限、注入、泄露、滥用等风险 | Incident/DEV 安全修复 + 安全回归 |
| `OPTIMIZATION` | 没有明确错误，但真实数据表明存在改进机会 | `Optimization-Planning` → CHANGE |
| `FEATURE-REQUEST` | 用户或业务提出的新能力 | `Change-Intake` → `Impact-Analysis` |
| `NO-ACTION` | 重复、误报、低价值或证据不足 | 关闭并记录理由，必要时调告警规则 |

### 15.7 六种运行模式

总 `Workflow` 最终支持：

```text
CREATE       新产品、新应用或重大产品方向
CHANGE       已有产品的明确功能迭代
DEFECT       实际行为偏离已批准基线
REFACTOR     旧项目接管、技术债治理和行为保持型架构重构
INCIDENT     生产环境正在造成高影响，需要先止损
OPTIMIZE     基于真实运行数据和用户行为持续优化
```

#### INCIDENT 与 DEFECT 的区别

- Incident 首先保护用户和业务：降级、隔离、停止发布、回滚、切流或临时关闭高风险功能。
- Defect 首先定位根因并修复正确行为。
- 事故缓解不等于根因修复；事故关闭前仍要建立后续 Bug-Fix、回归和复盘任务。

#### OPTIMIZE 与 CHANGE 的区别

- OPTIMIZE 从运行证据中发现机会，例如转化下降、功能使用率低、关键流程耗时高。
- CHANGE 是已经明确要实施的变更请求。
- Optimization 需要先证明问题、建立基线和预期收益，再转为 Change，不能根据单次波动自动改产品。

### 15.8 反馈闭环的三个层次

#### 层次 A：修复应用

```text
信号 → 根因 → 修复 → 回归 → 发布 → 观测
```

目标：让当前问题不再发生。

#### 层次 B：改进工程与产品基线

```text
问题 → 更新 PRD/UI/TDD/测试/运行手册 → 新基线
```

目标：让同类问题在当前项目中更难再次出现。

#### 层次 C：改进 Skill 系统

```text
重复问题模式
→ bug-patterns / issue
→ Skill-Optimizer / Skill-Evolver
→ 更新生成 Skill 和 Review Skill
→ 黄金场景回归
```

目标：让未来项目和未来迭代不再重复犯同类错误。

只有 A/B/C 三层都具备，才是真正的正向循环。

### 15.9 发布前后结果对比

每个发布必须带有假设和观测窗口：

```text
变更前基线
→ 预期改善
→ 保护性指标（不能变坏的指标）
→ 发布时间和 release ID
→ 发布后观测窗口
→ 实际结果
→ 继续 / 扩大 / 回滚 / 再迭代
```

示例：

| 项目 | 内容 |
|---|---|
| 目标 | 降低注册流程流失 |
| 主指标 | 注册完成率 |
| 保护指标 | 错误率、p95、客诉率 |
| 变更前 | 58% |
| 预期 | 提升到 ≥65% |
| 发布方式 | 10% → 50% → 100% 灰度 |
| 观察窗口 | 7 天或达到约定样本量 |
| 判定 | 达标扩量；保护指标恶化则停止或回滚 |

### 15.10 自动化边界

允许自动化：

- 采集、标准化、去重和聚类信号。
- 关联 release、trace、需求、页面、接口和代码模块。
- 生成初步问题卡、影响分析和推荐路由。
- 运行只读诊断、测试和回归。
- 在明确策略内执行低风险告警降噪和任务创建。

默认禁止无确认自动执行：

- 根据单一日志直接修改代码。
- 未经过测试自动发布生产。
- 自动改变产品规则、权限、计费或数据语义。
- 自动执行不可逆数据迁移。
- 自动扩大灰度或忽略保护指标。
- 未具备回滚能力时自动部署高风险变更。

### 15.11 新增运行期产物

```text
.spec/
├── observability/
│   ├── observability-plan.md
│   ├── telemetry-catalog.yaml
│   ├── sli-slo.yaml
│   ├── alert-rules.yaml
│   └── privacy-redaction.md
├── releases/
│   ├── release-plan.md
│   ├── release-manifest.yaml
│   ├── deployment-record.md
│   ├── rollback-plan.md
│   └── post-release-verification.md
├── operations/
│   ├── runtime-signal-ledger.yaml
│   ├── incidents/
│   ├── optimization-backlog.md
│   ├── product-metrics.md
│   └── outcome-reviews/
└── runbooks/
```

追踪链扩展为：

```text
产品目标
→ 成功指标
→ 需求 / 验收标准
→ 页面 / 接口 / 代码 / 测试
→ release ID
→ runtime signal
→ incident / defect / optimization
→ change request
→ 新 release
→ 实际结果
```

建议新增 ID：

```text
METRIC-xxx   产品或质量指标
SLI-xxx      服务水平指标
SLO-xxx      服务水平目标
TEL-xxx      遥测事件
REL-xxx      发布
SIG-xxx      运行信号
INC-xxx      事故
DEF-xxx      缺陷
OPT-xxx      优化机会
EXP-xxx      实验或效果验证
```

---

## 15.12 新建、接管、迭代与应用重构：统一生命周期入口

本体系不只服务“从零开发”。所有项目都先进入同一个 `Workflow`，再根据项目状态和用户目标选择生命周期模式。新项目、旧项目和正在运行的项目使用同一套产物契约、门禁和运行反馈，只是入口与需要重建的基线不同。

### 15.12.1 六种模式的边界

| 模式 | 适用对象 | 起点 | 核心目标 | 默认是否改变外部行为 |
|---|---|---|---|---|
| `CREATE` | 新产品、新应用、新平台 | Idea-Intake / Product-Discovery | 从模糊想法建立完整产品与工程基线 | 是 |
| `CHANGE` | 已有应用的新功能、业务规则、体验升级 | Change-Intake / Impact-Analysis | 在现有基线上完成可追踪的产品变更 | 是，按批准范围 |
| `DEFECT` | 已有行为偏离批准基线的问题 | Defect-Triage / Bug-Fix | 恢复正确行为并防止复发 | 否，除非确认基线本身错误 |
| `REFACTOR` | 旧项目治理、模块拆分、技术债清理、架构升级 | Project-Onboarding / Refactor-Planning | 在可回滚、可验证的前提下改善内部质量 | 默认否 |
| `INCIDENT` | 生产中正在造成高影响的事故 | Runtime-Signal-Triage / Incident-Response | 先止损、恢复服务，再转永久修复 | 允许临时改变，必须补齐基线 |
| `OPTIMIZE` | 指标、用户行为或成本显示出的改进机会 | Product-Analytics / Optimization-Planning | 以基线和实验验证收益，转成受控变更 | 是，按验证计划 |

必须区分：

- **REFACTOR 不是 CHANGE 的别名**：重构的默认验收条件是外部行为保持不变；如果重构过程中发现需要改变产品行为，应拆出一个 `CHANGE`，分别维护产品决策和技术重构证据。
- **INCIDENT 不是 DEFECT 的替代品**：Incident 负责恢复和止损，永久根因仍然要进入 Defect 或 Refactor。
- **OPTIMIZE 不是“看到一个波动就改代码”**：必须有足够样本、变更前基线、预期收益、保护指标和观察窗口。
- **旧项目不能直接从 Backend-Dev 开始**：缺少可靠基线时，先走 `Project-Onboarding`，否则 AI 会把旧代码的偶然行为误当成正确需求。

### 15.12.2 旧项目接管流程

旧项目可能没有完整 PRD、设计稿、技术方案、测试和监控。接管阶段的任务不是立即重写，而是把“未知”显式化：

```text
项目识别与平台判定
→ Project-Onboarding
→ 代码 / 依赖 / 构建 / 部署 / 数据 / 接口盘点
→ 现有行为采样与关键路径走查
→ 现有测试、日志、监控、告警盘点
→ 反向生成 Baseline Pack
→ 标记 FACT / INFERENCE / ASSUMPTION / OPEN
→ 用户确认接管范围与风险
→ 进入 CHANGE / DEFECT / REFACTOR / OPTIMIZE
```

`Baseline Pack` 至少包括：

```text
.spec/baseline/
├── project-profile.yaml       # 项目类型、平台、技术栈、运行环境、构建/发布入口
├── architecture-map.md        # 模块、服务、数据流、外部依赖
├── behavior-baseline.md       # 可观察行为、关键用户旅程、兼容约束
├── api-and-data-inventory.md  # API、事件、表、消息、外部契约
├── test-baseline.md           # 当前可运行测试与缺口
├── observability-baseline.md  # server-log/web-monitor/server-monitor 接入现状与缺口
├── release-baseline.md        # 版本、构建、部署、回滚和配置事实
└── unknowns-and-risks.md      # 未知项、假设、风险和建议验证顺序
```

接管完成的标准不是“文档写得很漂亮”，而是：

1. 能够在干净环境中构建，或记录清晰的阻塞原因；
2. 能够运行至少一条真实关键路径，或记录无法运行的证据；
3. 能够说清楚当前版本如何发布、如何回滚、如何判断是否健康；
4. 能够识别核心用户流程、核心接口、关键依赖和高风险模块；
5. 能够把未知项列入后续任务，而不是用 AI 推测填平；
6. 能够建立最小日志、错误和运行监控闭环。

### 15.12.3 应用重构流程

应用重构采用“可运行切片 + 行为保护 + 逐步替换”，禁止没有基线的大爆炸重写：

```text
REFACTOR 请求
→ Project-Onboarding（若尚未完成）
→ Refactor-Planning
→ 选择一个重构目标与边界
→ 建立 characterization / contract / smoke tests
→ 设计兼容层、迁移顺序和回滚点
→ 小切片实施
→ Code-Review
→ Regression-Testing + Nonfunctional-Testing
→ Release-Planning / Release-Verification
→ 对比行为、性能、错误率和资源指标
→ 继续下一切片或关闭重构项
```

重构计划必须回答：

- 要消除的具体问题是什么：耦合、重复、不可测试、性能、依赖风险、部署风险还是可观测缺口；
- 哪些外部行为、接口、数据格式和用户流程必须保持不变；
- 哪些内部边界将改变，如何判断边界已经真正建立；
- 每个切片如何独立编译、测试、发布或回滚；
- 重构前后比较哪些指标：构建时间、测试稳定性、错误率、p95、资源消耗、变更交付周期等；
- 如果发现需求或行为本身有问题，如何转出 `CHANGE` / `DEFECT`，而不是在重构分支里偷偷改语义。

### 15.12.4 统一路由算法

`Impact-Analysis` 不仅判断“改动大小”，还要判断“最早失效的事实源”：

```text
用户请求 / 运行信号
→ 判断项目是否已有可信 Baseline Pack
→ 判断外部行为是否变化
→ 判断影响的事实源
→ 判断平台与运行形态
→ 选择模式 + 起始 Workflow + 必须重跑的 Gate
→ 生成影响清单和回滚策略
```

| 判断结果 | 推荐路由 |
|---|---|
| 没有可信项目基线 | `Project-Onboarding` |
| 外部行为变化且产品规则未定义 | `CHANGE` → PRD-Workflow |
| 外部行为变化但仅设计/交互变化 | `CHANGE` → UI-Workflow |
| 外部行为不变，内部结构或工程质量变化 | `REFACTOR` → DEV-Workflow |
| 行为偏离已批准基线 | `DEFECT` → Defect-Triage |
| 生产影响正在扩大 | `INCIDENT` → Incident-Response |
| 运行数据证明存在改进机会 | `OPTIMIZE` → Product-Analytics |

## 15.13 全平台工程体系：统一领域流程，平台配置化扩展

目标是覆盖 Web、后端、小程序、桌面端、iOS、Android、鸿蒙等形态，但不为每个平台复制一套 PRD/UI/DEV/Testing 流程。正确的扩展方式是：

```text
统一 Workflow / Skill 契约
        +
平台 Profile（平台约束、生命周期、发布渠道、权限、测试矩阵）
        +
平台 Adapter（构建、运行、观测、打包、发布的落地实现）
        +
平台专属质量与合规门禁
```

### 15.13.1 平台分层

| 平台族 | 当前策略 | 后续接入重点 |
|---|---|---|
| Web 前端 | 第一阶段直接支持 | `web-monitor`、浏览器兼容性、性能/可访问性、SourceMap |
| 后端服务 | 第一阶段直接支持 | `server-log`、`server-monitor`、API/数据库/部署回归 |
| 小程序 | 第二阶段扩展 | 页面生命周期、分包、审核、端能力和小程序监控适配 |
| 桌面端 | 第二阶段扩展 | Electron/Tauri/原生进程、自动更新、崩溃与设备信息 |
| iOS | 后续扩展 | Swift/原生生命周期、签名、TestFlight/App Store、崩溃分析 |
| Android | 后续扩展 | Kotlin/原生生命周期、签名、渠道包、ANR/崩溃分析 |
| 鸿蒙 | 后续扩展 | ArkTS/Stage 模型、签名、分发、设备兼容与运行观测 |

### 15.13.2 平台 Profile 的内容

每个平台 Profile 由 `skills-knowledge` 管理，至少包含：

- 项目形态与技术栈识别规则；
- 目录和模块约定；
- UI/交互可用能力与平台限制；
- 构建、类型检查、测试、打包和发布命令；
- 权限、隐私、合规和敏感数据规则；
- 平台特有的错误、性能、生命周期和用户行为信号；
- `releaseId`、版本、构建号、commit 与渠道的关联方式；
- 平台专属的回滚、灰度、审核和恢复策略；
- 推荐的能力卡、Pattern、Composite、Adapter 及其版本。

平台 Profile 不是把平台代码复制进 Skill，而是告诉 Workflow：同一个职责在该平台如何落地、使用什么资产和如何验收。

### 15.13.3 当前仓库边界与目标集成

```text
tenger-skills
├── Workflow 编排、Skill 契约、门禁、状态机、产物模板和跨平台路由
skills-knowledge
├── 平台 Profile、能力卡、Pattern、Composite、Adapter、版本与证据
web-monitor
├── Web 前端错误 / 性能 / 行为 / 回放遥测及服务端看板
server-log
├── 后端结构化日志、请求上下文、脱敏和多目的地输出
server-monitor
├── 主机/服务运行采集、心跳/拨测、告警、通知、事件和状态页
```

当前已确认的事实与目标集成要分开：

- `web-monitor` 服务端当前已经接入 `server-log`；
- `web-monitor` 协议当前已有 `appVersion`、`env`、`sessionId`、`anonymousId`、`pageId` 和可选 `traceId`；
- `server-log` 当前上下文支持 `reqId`、`traceId`、`userId` 和扩展字段；
- `server-monitor` 当前已落地 Agent 快照、心跳/拨测、告警和事件等后端监控能力；
- 三个项目之间的统一信号关联、发布关联和跨平台统一看板属于下一步建设目标，不能在尚未实现时当作现成能力宣称。

### 15.13.4 跨仓库运行信号关联

在不破坏各仓库现有协议的前提下，新增兼容映射层，逐步补齐以下公共关联字段：

```yaml
signalId: SIG-xxx
releaseId: REL-xxx
service: web-app | api | worker | agent
environment: production | staging | development
version: 1.4.2
commitSha: <optional>
reqId: <server-log request id>
traceId: <cross-service trace id>
sessionId: <web-monitor session id, optional>
source: web-monitor | server-log | server-monitor | user-feedback
severity: info | warning | error | critical
privacyClass: public | internal | sensitive-redacted
```

兼容原则：

1. 现有 `reqId`、`traceId`、`sessionId`、`appVersion` 和 Agent 字段不立即重命名，由 Adapter 做规范化映射；
2. 不把 `sessionId` 当作后端请求链路 ID，也不把 `reqId` 当作跨天的业务实体 ID；
3. `releaseId` 是发布关联键，`traceId` 是请求/事件关联键，`signalId` 是运行信号自身的唯一键，三者不能混用；
4. 跨仓契约升级先在 `skills-knowledge` 记录版本和迁移说明，再由对应项目实现和验证；
5. 没有真实证据的字段标为 `optional` 或 `OPEN`，不能为了“统一”伪造数据。

### 15.13.5 完整团队式工程循环

```text
Project-Onboarding / Idea-Intake
→ PRD-Workflow
→ UI-Workflow
→ DEV-Workflow
   ├─ 选择 skills-knowledge 资产
   ├─ 设计 Observability
   ├─ 接入 server-log / web-monitor / server-monitor
   └─ 生成平台 Adapter 实现计划
→ Testing-Workflow
→ Release-Workflow
→ Operations-Workflow
   ├─ web-monitor：前端错误、性能、行为、回放
   ├─ server-log：后端日志与请求上下文
   └─ server-monitor：运行指标、心跳、拨测、告警与事件
→ Change / Defect / Refactor / Incident / Optimize
→ Impact-Analysis
→ 回到最早受影响的 Workflow
```

这套流程等价于一个可持续运行的“虚拟工程团队”：产品、设计、技术、开发、测试、发布/运维和架构治理各自有清晰职责；AI 负责执行和协作，人负责关键产品、风险和不可逆决策。

### 15.14 分阶段落地顺序（补充）

不要先为 iOS、Android、桌面端和鸿蒙创建大量空 Skill。推荐按真实闭环逐步建设：

1. **阶段 A：统一模式和接管能力**：增加 `Project-Onboarding`、`REFACTOR` 模式和 `Refactor-Planning` 契约，为旧项目生成 Baseline Pack。
2. **阶段 B：Web + 后端黄金场景**：以现有 Web + NestJS 项目验证完整链路，接入三项观测资产，建立 `releaseId → signalId → change` 追踪样例。
3. **阶段 C：运行闭环**：完成信号归一、分诊、缺陷/事故/优化路由，验证修复、回归、发布、再观测。
4. **阶段 D：小程序 Profile + Adapter**：先扩展平台 Profile、监控适配、构建/测试/发布门禁，不复制领域 Workflow。
5. **阶段 E：桌面端、iOS、Android、鸿蒙**：每个平台先做 Profile，再做最小 Adapter 和一条黄金场景；只有出现独立触发、产物和 Gate 时，才新增平台专属 Skill。

---
## 16. 重构后的最终目标 Skill 清单 v3（62 个）

> 本节取代第 14 节的 49 个初版清单。62 个仍是职责地图，不要求一次性创建 60 个目录；真实运行中没有独立触发、独立产物和独立 Gate 的职责，应合并为 Workflow 内部步骤或脚本。

### 16.1 编排层（7 个）

1. `Workflow`
2. `PRD-Workflow`
3. `UI-Workflow`
4. `DEV-Workflow`
5. `Testing-Workflow`
6. `Release-Workflow`
7. `Operations-Workflow`

### 16.2 项目接管、迭代与缺陷横向 Skill（6 个）
8. `Project-Onboarding`
9. `Refactor-Planning`


10. `Change-Intake`
11. `Impact-Analysis`
12. `Defect-Triage`
13. `Bug-Fix`

### 16.3 PRD-Workflow 原子 Skill（10 个）

14. `Idea-Intake`
15. `Product-Discovery`
16. `Competitive-Analysis`
17. `Product-Definition`
18. `Application-Blueprint`
19. `Feature-Decision`
20. `PRD-Design`
21. `PRD-Review`
22. `Prototype-Design`
23. `Prototype-Review`

### 16.4 UI-Workflow 原子 Skill（6 个）

24. `UX-Architecture`
25. `Interaction-State-Design`
26. `Design-System`
27. `Component-Mapping`
28. `UI-UX-Design`
29. `UI-UX-Review`

### 16.5 DEV-Workflow 原子 Skill（11 个）

30. `Technical-Discovery`
31. `OSS-Radar`
32. `Backend-Tech-Design`
33. `Frontend-Tech-Design`
34. `Observability-Design`
35. `Tech-Review`
36. `Component-Decision`
37. `Implementation-Planning`
38. `Backend-Dev`
39. `Frontend-Dev`
40. `Code-Review`

`Observability-Design` 负责把产品指标、关键旅程、错误分类、日志、指标、追踪、审计、SLI/SLO、告警和隐私要求转成可实施契约；具体埋点和监控代码仍由 Backend/Frontend-Dev 实现。

### 16.6 Testing-Workflow 原子 Skill（9 个）

41. `Test-Planning`
42. `Quality-Gate`
43. `Contract-Testing`
44. `Integration-Testing`
45. `E2E-Testing`
46. `Fidelity-Review`
47. `Exploratory-Testing`
48. `Nonfunctional-Testing`
49. `Regression-Testing`

### 16.7 Release-Workflow 原子 Skill（3 个）

50. `Release-Planning`
51. `Deployment-Execution`
52. `Release-Verification`

职责边界：

- `Release-Planning`：版本范围、迁移顺序、灰度、回滚、审批、观察窗口和保护指标。
- `Deployment-Execution`：按批准计划执行部署并保存可审计记录；生产变更遵守用户授权和环境权限。
- `Release-Verification`：发布后健康检查、关键主链冒烟、遥测有效性、基线对比和继续/暂停/回滚建议。

### 16.8 Operations-Workflow 原子 Skill（6 个）

53. `Runtime-Signal-Triage`
54. `Incident-Response`
55. `Product-Analytics`
56. `Optimization-Planning`
57. `Post-Release-Review`
58. `Quality-Inspection`

职责边界：

- `Runtime-Signal-Triage`：标准化、去重、关联、分级并路由日志、监控、告警、反馈和安全信号。
- `Incident-Response`：事故期间止损、协同、时间线、恢复验证和后续行动；不替代永久根因修复。
- `Product-Analytics`：分析产品目标、用户旅程、功能使用和流失数据，区分趋势、异常和证据不足。
- `Optimization-Planning`：把可信运行证据转成带基线、预期收益、保护指标和验证计划的优化候选。
- `Post-Release-Review`：比较发布前假设与发布后结果，决定继续、扩大、回滚、再迭代或关闭。
- `Quality-Inspection`：按周期或用户要求巡检代码、依赖、测试、架构漂移、可观测性、运行质量和维护风险；只产出带证据的问题与建议，不未经 Gate 直接改码或上线。

### 16.9 链外研究、核验与 Skill 治理（5 个）

59. `Fact-Check`
60. `Source-Reading`
61. `Skill-Optimizer`
62. `Skill-Evolver`
63. `Essence-Distill`

### 16.10 总量

```text
编排层                    7
项目接管、迭代与缺陷横向  6
PRD 原子 Skill            10
UI 原子 Skill              6
DEV 原子 Skill            11
Testing 原子 Skill         9
Release 原子 Skill         3
Operations 原子 Skill      6
链外研究与治理             5
────────────────────────────
合计                      63
```

### 16.11 实施顺序调整

原 Phase 6 后新增：

```text
Phase 6  Release-Workflow
Phase 7  Operations-Workflow 与运行信号闭环
Phase 8  总 Workflow 整合、旧项目兼容和全循环回归
```

最终黄金场景增加两类：

```text
场景 D：发布后监控发现错误
SIG → TRIAGE → INCIDENT/DEFECT → FIX → REGRESSION → RELEASE → OBSERVE

场景 E：发布后数据发现优化机会
METRIC → ANALYSIS → OPTIMIZATION → CHANGE → IMPACT → 实施 → 发布前后效果对比
```

最终完成标准增加：

- [ ] 每个新应用在技术方案阶段定义可观测性，而不是上线后补日志。
- [ ] 每次发布可以关联版本、commit、配置、迁移和运行信号。
- [ ] 日志/监控问题可以自动归一和推荐路由，但不会未经 Gate 自动改码上线。
- [ ] 事故、缺陷、功能请求和优化机会使用不同处理路径。
- [ ] 修复后不仅测试通过，还经过发布后观测确认没有复发。
- [ ] 优化项有变更前基线、预期收益、保护指标和发布后结果。
- [ ] 重复问题可以反哺项目基线、bug-patterns 和 Skill 系统。
- [ ] 任意模型更换后仍必须通过同一套确定性质量门禁、可维护性审查和发布后验证。
- [ ] 项目支持周期性 `Quality-Inspection`，巡检问题可以回流到 CHANGE / DEFECT / REFACTOR / OPTIMIZE。


