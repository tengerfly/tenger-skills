# Skill 体系优化路线图——基于 Anthropic Agent Skills 规范

> 文档目的：把前一轮讨论形成的体系化优化路线，与当前仓库对 Anthropic Agent Skills 开发规范的差距分析合并，形成一份可执行、可验收、可逐步迁移的路线图。
>
> 适用范围：当前仓库中的产品、设计、技术方案、开发、评审、测试、BugFix、Workflow 与 Skill-Optimizer 等 Skill。
>
> 本文不是一次性重构方案。原则是：先建立契约和验证，再选择少量 Skill 试点，最后渐进式迁移；不直接批量修改全部现有 Skill。

---

## 1. 先给结论

你的方向是可行的，而且当前仓库已经具备了一个重要的雏形：不是单个“会写代码的超级提示词”，而是由多个专业 Skill、评审门禁、持久化产物和 Workflow 组成的工程系统。

但目前它更接近：

```text
一套内容丰富的 Skill 文档集合
        +
一套以自然语言描述的工作流协议
```

距离企业级、可持续运行的 AI Engineering System 还差三类基础设施：

1. **统一 Skill 契约**：每个 Skill 的输入、输出、前置条件、门禁、停止条件和失败处理方式必须结构化。
2. **统一产物契约**：PRD、原型、TDD、代码评审、测试报告和 PIPELINE 不能只靠文件名和自然语言传递，必须可追踪、可校验、可版本化。
3. **真实运行验证**：不能只检查 SKILL.md 是否存在、章节是否齐全；必须用真实项目场景验证 Skill 能否正确触发、读取资源、产出结果并通过下游门禁。

Anthropic Agent Skills 规范主要解决“Skill 如何被发现、加载和执行”的问题；你的方法论进一步解决“多个 Skill 如何组成企业级开发流程、资产如何沉淀和复用、AI 生成结果如何可控”的问题。二者是上下层关系，不是互相替代的关系。

---

## 2. 当前仓库概况

### 2.1 已盘点的 Skill

当前仓库共有 18 个包含 `SKILL.md` 的 Skill：

| 类别 | Skill |
|---|---|
| 产品与调研 | `Competitive-Analysis`、`PRD-Design`、`PRD-Review` |
| 原型与设计 | `Prototype-Design`、`Prototype-Review`、`UI-UX-Design`、`UI-UX-Review`、`Fidelity-Review` |
| 技术方案 | `Backend-Tech-Design`、`Frontend-Tech-Design`、`Tech-Review` |
| 开发与质量 | `Backend-Dev`、`Frontend-Dev`、`Code-Review`、`Testing` |
| 运行与治理 | `Bug-Fix`、`Workflow`、`Skill-Optimizer` |

当前主链大致为：

```text
竞品分析
→ PRD 设计 ⇄ PRD 评审
→ 原型设计 ⇄ 原型评审
→ UI/UX 设计 ⇄ UI/UX 评审
→ 后端/前端技术方案 ⇄ 技术方案评审
→ 后端/前端开发 ⇄ 代码评审
→ Fidelity-Review（前端并行）
→ Testing
```

此外，仓库已经存在：

```text
shared/
issue/
bug-patterns/
chats/
```

以及各 Skill 下的 `references/` 和部分 `assets/`。这说明你已经在实践“公共规则、案例、模板和工程资产分离”，方向是正确的。

### 2.2 当前已有优势

- Skill 已经普遍具备 YAML frontmatter。
- Skill 不是只描述代码生成，而是覆盖需求、设计、方案、开发、评审、测试和 BugFix。
- 已经有 P0/P1 门禁、证据链、评审回合上限、暂停等待用户等工程约束。
- 已经有 `shared/anti-deadloop.md`、`shared/browser-policy.md`、`shared/evidence-before-claims.md` 等公共规则。
- 产物大多要求落到项目 `.spec/` 目录，具备 Artifact First 的雏形。
- `Workflow` 已经承担编排、记账和门禁职责；`Bug-Fix` 已经有日志、复现、根因、修复委托、回归和沉淀闭环。
- 你已经意识到 Pattern、Template、Adapter、Evidence 与具体项目代码应当分层，这是解决资产冗余和跨语言复用的关键。

### 2.3 当前不能过度宣称的内容

截至本次静态盘点，不能把仓库描述为已经具备以下能力：

- 已经有可执行的 Skill dispatcher；
- 已经有完整的 Skill registry；
- 已经有自动化 artifact validator；
- 已经通过从零项目、遗留项目和线上 BugFix 的真实运行验证；
- 已经证明所有 Skill 在不同 Agent 宿主中行为一致。

后续需要把这些能力列入建设目标，并区分以下状态：

```text
文档完成
结构校验通过
冒烟验证通过
真实场景验证通过
持续稳定运行
```

---

## 3. Anthropic Agent Skills 规范要点

以下结论依据 Anthropic 对 Agent Skills 的公开介绍，以及当前 Agent Skills 开放规范的 `SKILL.md` 约定整理。具体字段和限制应以实际使用的宿主版本为准。

### 3.1 Skill 的最小入口是 `SKILL.md`

Skill 应以目录为边界，并在目录根部提供 `SKILL.md`。Agent 首先读取 frontmatter，用于判断是否需要加载该 Skill；真正执行时再读取正文和所需资源。

因此：

- `SKILL.md` 必须是可执行入口；
- `README.md` 可以服务人类阅读，但不能承载唯一的执行规则；
- `CONTEXT.md` 可以保存背景和决策历史，但不能成为隐式必读前置；
- references、scripts、assets 应由 `SKILL.md` 按需引导加载。

### 3.2 Frontmatter 是发现和路由信息

典型结构：

```yaml
---
name: example-skill
description: What the skill does and when to use it.
compatibility: Optional real runtime requirements.
metadata:
  owner: team-name
  version: 0.1.0
---
```

需要重点遵守：

- `name` 使用小写字母、数字和连字符；
- `name` 应与 Skill 目录和稳定 ID 保持一致；
- `description` 用于“做什么”和“什么时候使用”的发现，不应塞入全部流程；
- `compatibility` 只声明真实的运行时依赖，不要把 Agent 名称列表当作兼容性证明；
- 版本、owner、分类、验证状态等治理信息放入结构化 metadata 或外部 registry，而不是堆到 description 中。

### 3.3 渐进式披露

建议把 Skill 设计成三层加载模型：

```text
Level 1：frontmatter
  只负责发现和路由

Level 2：SKILL.md 正文
  核心行为、边界、输入、输出、关键流程、门禁

Level 3：references / scripts / assets
  只有在具体模式或具体工具需要时才加载
```

这不是单纯的“少写文档”，而是为了减少上下文占用、避免规则互相冲突，并让 Agent 在正确的时机拿到正确的细节。

### 3.4 资源应该服务于执行

- `references/` 适合放详细规范、检查清单、案例、技术决策资料；
- `scripts/` 适合放确定性、重复性、适合程序校验的逻辑；
- `assets/` 适合放模板、样例工程、静态资源和可复制的工程骨架；
- 生成物、缓存、依赖安装目录和临时运行结果不应混入核心 Skill 资产。

### 3.5 复杂 Skill 需要真实场景验证

复杂 Skill 的质量不能用“文件存在”“标题齐全”“正则匹配通过”替代。至少要验证：

1. Agent 是否能发现并触发正确 Skill；
2. 是否能从 `SKILL.md` 找到正确的 references、scripts 和 assets；
3. 输入不完整时是否会澄清或安全停止；
4. 是否能产出约定格式的产物；
5. 下游 Skill 是否能消费该产物；
6. 失败、重试、评审和回退是否能留下证据。

---

## 4. 基于规范的差距分析

以下按优先级分为 P0、P1、P2。这里的 P0 表示会破坏可发现性、可执行性或资产安全的基础问题，不等同于业务线上事故等级。

### 4.1 P0：名称不符合规范，需设计兼容迁移

当前名称是：

```text
PRD-Design
Backend-Dev
UI-UX-Review
Skill-Optimizer
```

建议 canonical ID 改为：

```text
prd-design
backend-dev
ui-ux-review
skill-optimizer
```

不要一次性直接重命名并破坏旧路径。推荐迁移方式：

1. 先建立 `governance/skill-registry.yaml`；
2. 为每个 Skill 记录 `legacy_name`、`canonical_name`、旧目录和新目录；
3. 先让 Workflow 和新文档使用 canonical ID；
4. 保留旧目录兼容映射一段时间；
5. 更新链接、脚本和引用后，再决定是否真正移动目录。

### 4.2 P1：description 过重，路由信息和执行规则混在一起

当前 description 长度大约为 100～400 字符，虽然没有明显超限，但普遍包含：

- 详细流程；
- 内部节点编号；
- 评审轮次和门禁细则；
- 输出路径；
- 技术栈细节；
- 其他 Skill 的调度信息。

建议统一为四段信息：

```text
能力：这个 Skill 做什么
触发：什么场景应该调用
输入：至少需要什么输入
边界：明确不负责什么
```

例如：

```yaml
name: backend-dev
description: Implements backend features from an approved backend technical design. Use when a project has an accepted backend design and needs production code, tests, and verification. Do not use for architecture decisions, product requirements, or root-cause diagnosis without an approved repair plan.
```

具体流程、门禁和文件路径放到正文及 references 中。

### 4.3 P1：compatibility 声明过于笼统

当前所有 Skill 基本都写成：

```yaml
compatibility: Claude Code / Agent SDK / OpenCode
```

这只能说明“希望在这些宿主中使用”，不能说明真实运行条件。应改为按 Skill 真实依赖声明，例如：

```yaml
compatibility: Requires Node.js, pnpm, browser automation, and a project-local dev server.
```

若没有特殊依赖，可以删除该字段；不要制造“已经在所有宿主验证通过”的暗示。

### 4.4 P1：SKILL.md 入口还不够轻，存在重复规则

当前 Skill 正文已经较丰富，单个文件约 3～11 KB，且普遍同时包含规则、案例、资源清单、流程、错误处理和埋点要求。

重点抽离对象：

- 多个 Skill 重复出现的 P0/P1 规则；
- 浏览器策略；
- 证据优先规则；
- 评审接收和回填规则；
- 大段案例；
- 详细检查清单；
- 只在特定技术栈下适用的内容。

建议公共规则集中到 `shared/`，详细内容放 `references/`，但必须在具体 Skill 的 `SKILL.md` 中明确“何时读取哪个文件”，不能只依赖 README 或 CONTEXT。

### 4.5 P1：README、CONTEXT 与执行入口职责不清

建议明确职责：

| 文件 | 责任 |
|---|---|
| `SKILL.md` | Agent 执行入口，必须足以启动任务 |
| `README.md` | 面向人的说明、安装、示例、状态 |
| `CONTEXT.md` | 背景、设计决策、迁移记录、已知限制 |
| `references/` | 需要时加载的详细知识和检查表 |
| `scripts/` | 可重复、可验证的机械操作 |
| `assets/` | 模板和可复制工程资产 |

若某条规则会影响 Agent 的下一步决策，就不能只放在 README 或 CONTEXT。

### 4.6 P1：确定性检查还没有形成 scripts 层

当前已经有大量规则，但不少机械检查仍可能由 Agent 通过自然语言完成。以下任务应逐步脚本化：

```text
validate_skill_frontmatter
validate_skill_name
validate_resource_links
validate_required_sections
validate_artifact_manifest
validate_pipeline_state
scan_generated_files
build_skill_registry
```

脚本只负责确定性检查，不负责替代需要判断、取舍和沟通的专家工作。

### 4.7 P1：真实评测体系尚未形成

当前有 Skill 文档和案例目录，但还需要建立独立的运行验证结构：

```text
verification/
├── scenarios/
├── runs/
└── reports/
```

至少覆盖：

- 从零新项目；
- 接手十年以上的遗留项目；
- 纯前端项目；
- 线上 Bug 修复；
- 输入缺失、资源缺失、工具不可用、评审反复不通过等异常场景。

### 4.8 P1：资产中混入生成物和运行环境

已发现 `Frontend-Dev/assets/frontend-template-vue3/` 下存在：

```text
node_modules/
coverage/
dist/
```

这些目录应从核心 Skill 资产中清理，改为：

- 锁定依赖版本的清单；
- 可重复执行的安装命令；
- CI 或验证脚本产生的运行结果；
- 单独的验证产物目录。

### 4.9 P2：状态和生命周期标记不统一

当前 README 中存在“完成”“定稿”“初版定稿”和没有状态行等不同表达。建议把状态拆成正交维度：

```yaml
lifecycle: active
maturity: experimental
verification: not-run
runtime: available
owner: team-name
last_verified: null
```

“文档写完”不等于“真实运行通过”，更不等于“稳定可复用”。

### 4.10 P2：复杂职责需要按模式拆分，而不是继续堆进主 Skill

`Workflow`、`Testing`、`Bug-Fix`、`Skill-Optimizer`、`Frontend-Dev` 都承担较多模式。优先采用：

```text
主 Skill：负责路由和共同流程
references：承载模式细节
scripts：承载确定性检查
独立 Skill：只拆出真正独立、具有不同触发条件和生命周期的职责
```

不要因为某个 Skill 文件变长就机械拆分；拆分的依据应是职责、触发条件、输入输出和生命周期是否真正不同。

---

## 5. 之前讨论形成的体系性优化方向

### 5.1 从 Skill 列表升级为 Skill Graph

Skill 不是孤立的清单，而是有输入输出关系的节点。每个节点至少要声明：

```yaml
id:
type:
trigger:
inputs:
outputs:
dependencies:
review:
gate:
stop_conditions:
evidence:
```

Workflow 负责调度和状态推进，Skill 负责完成专业工作，二者不能混为一谈。

### 5.2 从聊天上下文升级为 Artifact First

阶段之间不能只传“上一轮聊天记录”，而应传递可持久化产物：

```text
PRD → 原型 → 设计稿 → TDD/FTDD → 代码 → 评审报告 → 测试报告 → 发布/回滚证据
```

每个产物都应该可定位、可版本化、可审计，并能被下游 Skill 消费。

### 5.3 建立 Skill 契约矩阵和产物矩阵

建议新增：

```text
governance/SKILL-STATUS-MATRIX.md
governance/SKILL-CONTRACT-MATRIX.md
governance/ARTIFACT-MATRIX.md
governance/WORKFLOW-GAP-LIST.md
```

至少记录：

```text
Skill / 产物名称
触发条件
输入
输出
前置依赖
评审者
门禁
停止条件
回退方式
证据位置
已知风险
验证状态
```

### 5.4 建立稳定节点 ID 和状态机

Workflow 不应只依赖“⑧、⑨、⑩”等编号。推荐使用稳定 ID：

```text
prd-design
prd-review
prototype-design
ui-ux-design
backend-tech-design
frontend-tech-design
backend-dev
frontend-dev
code-review
testing
```

统一状态建议：

```text
NOT_STARTED
BLOCKED
READY
RUNNING
WAITING_REVIEW
CHANGES_REQUESTED
RECHECKING
APPROVED
RELEASED
SKIPPED
WAIVED
FAILED
ABORTED
```

当前 `Workflow` 是文本式编排 Skill，不应描述成已经存在的程序化工作流引擎。后续可在它之上增加 registry、dispatcher、artifact validator 和状态机执行器。

### 5.5 建立产物 manifest

建议所有关键产物逐步附带 `manifest.yaml`：

```yaml
artifact:
  id: project.feature.prd
  type: prd
  version: 1.2.0
  path: .spec/prd/PRD.md

lifecycle:
  status: approved
  created_by: prd-design
  created_at: 2026-09-16T00:00:00+08:00

review:
  skill: prd-review
  status: approved
  rounds: 1
  p0: 0
  p1: 0
  p2: 2

downstream:
  allowed:
    - prototype-design
    - backend-tech-design
    - frontend-tech-design
```

第一版不必立刻覆盖所有文件，先覆盖 PRD、TDD/FTDD、代码评审、测试报告和 PIPELINE。

### 5.6 建立资产分层，避免相似资产无限复制

推荐使用五类资产：

```text
Method       方法：解决什么问题、适用条件、决策原则
Pattern      模式：可重复的解决结构
Template     模板：可复制的文档或工程骨架
Adapter      适配层：绑定语言、框架、基础设施
Evidence     证据：测试、线上数据、评审记录、事故复盘
```

以“登录”为例，不要把手机号登录、账号登录、微信登录分别复制成十个完整资产。可以拆成：

```text
认证能力
├── Method: authentication-method
├── Pattern: password-login
├── Pattern: phone-otp-login
├── Pattern: oauth-login
├── Adapter: nestjs-auth
├── Adapter: spring-security-auth
├── Adapter: express-auth
├── Template: auth-module-template
└── Evidence: 项目/版本/验证结果
```

差异足以改变输入输出、威胁模型或生命周期时，才升级为独立 Pattern；只是语言、框架或 SDK 差异，优先放入 Adapter。Pattern 的版本与项目使用版本分离，项目可以锁定 `pattern@1.x + adapter@2.x`。

### 5.7 契约决定哪些资产可以组合以及组合顺序

“可组合”不是任意拼接，而是满足前置条件和接口契约：

```yaml
pattern: oauth-login
requires:
  - identity-provider
  - callback-endpoint
provides:
  - authenticated-session
conflicts_with:
  - password-login-only
ordering:
  before:
    - protected-resource-access
  after:
    - user-identity-model
```

组合规则至少包括：

- 输入输出类型是否兼容；
- 前置条件是否满足；
- 是否存在互斥模式；
- 组合顺序是否正确；
- 安全、事务、幂等、权限等横切约束是否覆盖；
- 是否有可验证的验收标准。

因此，AI 不是自由发明方案，而是在候选资产、约束和证据范围内完成选择、组合、适配和落地。

---

## 6. 遗留项目的落地路线

对于已经运行十几年、代码杂乱的项目，不应先试图把全部旧代码“资产化”或重写。建议采用“先建立事实，再建立边界，最后提炼模式”的路线。

### 6.1 遗留项目五步法

```text
1. Baseline：建立现状基线
2. Characterize：用测试、日志和运行行为描述现状
3. Boundary：划定新增代码和改造代码的边界
4. Golden Slice：选择一条真实业务链做规范化样板
5. Extract：从已验证改动中提炼 Pattern / Adapter / Evidence
```

具体执行：

1. 盘点入口、服务、数据库、外部依赖、部署方式和高风险模块；
2. 不先判断“代码是否优雅”，先记录当前真实行为；
3. 用 characterization tests、接口快照、日志样本和回归用例保护旧行为；
4. 新需求优先走新的 Skill 流程，旧代码通过 Adapter 或 Anti-Corruption Layer 接入；
5. 只把已经在线上或真实环境验证过的方案沉淀为资产；
6. 用新模块的质量门禁逐步包围旧模块，而不是一次性重构整个系统。

### 6.2 遗留项目中的资产分级

```text
L0：观察记录——只描述现状，不推荐复用
L1：项目局部方案——只能在本项目复用
L2：经过一次真实验证的候选模式
L3：跨项目验证的稳定模式
L4：带多语言/多框架 Adapter 的组织级资产
```

旧代码本身通常不是 Pattern；它最多是 Case 或 Evidence。只有抽象出适用条件、约束、接口、验证结果和失败边界后，才升级为可复用资产。

---

## 7. 统一优化路线图

### Phase 0：建立基线（第 1 周）

目标：知道每个 Skill 当前“写了什么、能不能跑、谁依赖谁”。

任务：

- 建立 Skill 清单和 canonical ID 映射；
- 建立状态矩阵、契约矩阵、产物矩阵；
- 标记 `documentation / structure / smoke / real-run` 四种验证状态；
- 记录现有 references、assets、scripts 和外部依赖；
- 清理或隔离 `node_modules`、`coverage`、`dist` 等生成物。

验收：任何人可以通过矩阵回答一个 Skill 的触发条件、输入、输出、门禁和当前验证状态。

### Phase 1：统一 Skill 契约（第 2～3 周）

新增建议结构：

```text
shared/contracts/
├── skill-contract.schema.yaml
├── artifact-contract.schema.yaml
├── workflow-node.schema.yaml
└── skills/
```

先选 `Workflow`、`Backend-Dev`、`Testing` 三个 Skill 试点，不要一开始修改全部 Skill。

验收：三者都能明确说明输入、输出、前置、停止条件、失败处理和证据位置。

### Phase 2：统一产物契约（第 3～4 周）

为 PRD、TDD/FTDD、评审报告、测试报告和 PIPELINE 增加 manifest。统一版本、状态、来源、评审结果和下游允许节点。

验收：下游 Skill 不需要阅读完整聊天历史，仅通过产物和 manifest 就能判断能否开始。

### Phase 3：建立真实运行验证（第 5～6 周）

新增：

```text
verification/scenarios/
verification/runs/
verification/reports/
```

建立四个 Golden Scenarios：

1. 从零构建一个小型全栈功能；
2. 接手一个已有项目并新增一个功能；
3. 只修改前端并通过视觉和功能检查；
4. 从线上日志定位并修复一个 Bug。

验收：每个场景都有输入、运行记录、产物、评审结果、失败点和改进结论。

### Phase 4：强化 Workflow（第 7～8 周）

- 引入稳定节点 ID；
- 把自然语言状态统一为状态机；
- 明确人工决策点和自动校验点；
- 将 PIPELINE 作为项目状态源；
- 增加“暂停、跳过、豁免、失败、回滚”的记录方式；
- 先做 validator，再考虑 dispatcher，不要先做复杂平台。

验收：同一个项目中断后，可以仅依据 PIPELINE 和产物 manifest 恢复工作。

### Phase 5：资产分层与检索（第 9～10 周）

- 建立 Method / Pattern / Template / Adapter / Evidence 目录；
- 给 Pattern 增加适用条件、前置、提供能力、冲突和组合顺序；
- 给 Adapter 增加语言、框架、版本和运行依赖；
- 给每个资产增加生命周期：Draft、Experimental、Validated、Stable、Deprecated、Retired；
- 优先沉淀 10～20 个高频、跨项目、已验证资产，不追求一次建大库。

验收：AI 能先检索候选资产，再说明选择理由；没有候选资产时必须显式标记“需要新方案”，不能把临时代码伪装成稳定资产。

### Phase 6：补齐 BugFix 与运维闭环（第 11 周）

在现有日志、复现、根因、修复、回归和沉淀之外，增加：

```text
版本
部署环境
变更记录
发布批次
回滚方案
监控指标
影响范围
观察窗口
事故复盘
```

验收：一个线上问题可以追溯到受影响版本、修复提交、验证结果和后续 Pattern/Anti-Pattern。

### Phase 7：持续运行与 Skill 演进（第 12 周及以后）

每次真实项目结束后执行：

```text
更新 PIPELINE
保存运行证据
记录失败与返工
判断是否产生 Case
判断是否产生 Pattern / Anti-Pattern
判断是否需要更新 Skill
运行回归场景
发布新版本
```

验收：Skill 的每次重要修改都有变更原因、影响范围、验证场景和回滚方案。

---

## 8. 建议的 Skill 标准模板

```markdown
---
name: canonical-skill-name
description: What this skill does, when to use it, and its boundary.
compatibility: Only real runtime requirements, if any.
metadata:
  version: 0.1.0
  lifecycle: experimental
  verification: not-run
---

# Skill 名称

## Purpose
本 Skill 解决什么问题。

## When to use
什么输入和场景下触发。

## When not to use
哪些问题应交给其他 Skill。

## Inputs
必需输入、可选输入、输入缺失时的处理。

## Outputs
文件、目录、manifest、证据和状态更新。

## Preconditions
开始前必须满足的条件。

## Workflow
最小可执行流程和关键决策点。

## Pattern selection
如何检索和选择已有资产；没有资产时如何标记。

## Quality gate
通过条件、P0/P1 规则和人工确认点。

## Stop conditions
何时必须暂停、阻断、请求用户决策或回滚。

## Evidence
验证命令、截图、日志、测试报告和引用位置。

## References
只列出本次任务可能需要读取的参考文件，并说明触发条件。
```

注意：这不是要求每个 Skill 机械复制全部章节；应保留真正影响执行的部分，避免模板化造成更多噪声。

---

## 9. 第一批执行清单

建议按以下顺序执行：

### A. 先做治理文件，不先批量改 Skill

```text
governance/skill-registry.yaml
governance/SKILL-STATUS-MATRIX.md
governance/SKILL-CONTRACT-MATRIX.md
governance/ARTIFACT-MATRIX.md
governance/WORKFLOW-GAP-LIST.md
```

### B. 选择三个试点 Skill

推荐：

```text
Workflow      验证调度、状态和交接
Backend-Dev   验证输入输出、资产选择和代码落地
Testing       验证真实运行、证据和质量门禁
```

### C. 先增加校验，再做迁移

优先建立：

```text
frontmatter 校验
canonical name 校验
引用路径校验
manifest 校验
PIPELINE 状态校验
生成物扫描
```

### D. 先做四个 Golden Scenario

不要先建几十个 Pattern。先用真实场景暴露契约问题，再决定哪些规则值得进入 Skill 和资产库。

### E. 每次只迁移一个闭环

推荐第一个闭环：

```text
Backend-Tech-Design
→ Backend-Dev
→ Code-Review
→ Testing
```

完成后再扩展到前端、设计和 BugFix。

---

## 10. 验证指标

### 10.1 结构指标

- 所有 Skill 都有合法 frontmatter；
- canonical name 唯一且可映射；
- 资源引用无死链；
- 核心规则不依赖 README/CONTEXT 的隐式加载；
- 生成物不在核心资产中。

### 10.2 执行指标

- 正确 Skill 触发率；
- 输入缺失时安全停止率；
- 产物 manifest 完整率；
- 下游 Skill 首次消费成功率；
- PIPELINE 中断恢复成功率；
- 评审返工轮次和 P0/P1 重复率。

### 10.3 工程指标

- AI 生成代码的构建、测试、Lint 通过率；
- 相似功能重复造轮子的比例；
- Pattern 被跨项目复用的次数；
- Pattern 复用后产生的回滚或缺陷数量；
- BugFix 从日志到根因确认的平均时间；
- 线上问题是否能回溯至对应 Skill、Pattern、Adapter 和 Evidence。

不建议一开始追求“AI 生成代码行数”或“单次对话完成率”。这些指标容易鼓励短期能跑、长期难维护的实现。

---

## 11. 暂时不要做的事情

1. 不要一次性重命名、重写全部 18 个 Skill；
2. 不要把所有历史代码直接纳入资产库；
3. 不要把每个项目差异都复制成一个新 Pattern；
4. 不要让 AI 在没有候选资产和验证证据时自动宣称“已沉淀”；
5. 不要先做复杂 Web 管理平台、向量数据库或自动 dispatcher；
6. 不要把 README、CONTEXT、聊天记录和运行日志全部塞进 SKILL.md；
7. 不要把规则越写越绝对，凡是不能改变模型决策或提升质量的规则都应删除；
8. 不要用“文档完成”替代“真实项目验证通过”。

---

## 12. 最终验收标准

当下面条件同时满足时，才可以认为第一阶段完成：

- 每个 Skill 有稳定 ID、清晰 description 和真实 compatibility；
- `SKILL.md` 是自包含执行入口，详细内容按需加载；
- Skill 的输入、输出、门禁、停止条件和证据位置可查；
- 关键产物有 manifest 和版本；
- Workflow 使用稳定节点 ID 和明确状态机；
- 至少四个真实场景完成 forward testing；
- 至少一条后端或前端闭环可以中断后恢复；
- 至少 10 个资产完成 Method/Pattern/Template/Adapter/Evidence 分层；
- 遗留项目有基线、特征测试、边界和 Golden Slice；
- BugFix 可以追踪到发布、回滚、监控和复盘；
- Skill 或 Pattern 的更新能够通过回归场景验证。

---

## 13. 参考资料

- Anthropic：Equipping agents for the real world with Agent Skills
- Agent Skills Specification：`https://agentskills.io/specification`
- Agent Skills 官方示例与工具生态：`https://github.com/anthropics/skills`
- 本仓库内部设计依据：
  - `案例库体系方案-草案.md`
  - `personal-ai-engineering-skill-system.md`
  - `Workflow/SKILL.md`
  - `shared/anti-deadloop.md`
  - `shared/evidence-before-claims.md`

---

## 附录：一句话执行原则

```text
先用契约把 Skill 变得可发现、可执行、可验证；
再用产物和证据把流程串起来；
最后从真实项目中提炼可组合、可跨技术栈适配、可持续演进的工程资产。
```

