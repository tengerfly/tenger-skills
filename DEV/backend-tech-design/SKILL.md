---
name: backend-tech-design
description: "后端技术方案（TDD）编写。依据 PRD 与原型先定全技术选型（语言/DB/缓存/检索/消息队列/Docker/服务形态/ORM 等，企业级或快速档），产出总文档（架构图+模块边界+关联+全部表结构）与各模块方案（流程+图+TDD 测试用例，先写测试再写代码）。开发期零技术决策。触发：编写后端技术文档/技术方案/技术设计/架构设计/TDD 文档。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: "Backend-Tech-Design"
  compatibility: "Claude Code / Agent SDK / OpenCode"
---


> **增量设计入口**：先按 `../../shared/execution-profiles.md` 判断是否需要本 Skill。低风险已有栈局部修改可直接由开发做局部计划，不为了补形式文档强制调用技术设计。确需技术方案时按 `../../shared/requirements-context.md` 固定相关需求/AC 与依赖；已有框架和选型未变化则复用，不重复询问、不重做全套方案。新增架构/关键基础设施/不熟悉依赖仍按 OSS 研究策略核验，专业工具与安全要求不降级。

# 后端技术方案文档（TDD）编写 Skill

> IRON LAW：**开发期零技术决策**——所有选型必须在方案阶段一次定全并过收敛证明。
> TDD = Technical Design Document；全程测试驱动：先写测试用例，后写实现方案。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

**闭环回流（L2）**：P0/P1 条目要标「已沉淀」前，必须先回流 1 条评测用例，并在该用例声明里用 `issueRef` 指回本条问题（值＝本条问题的仓库相对路径，形如 issue/<skill>/<日期>/<NN>-<标题>.md）；没有这条用例就按「未验证」处理，优化状态停在待处理/处理中，不得写「已沉淀」。
判据与字段口径的单一来源是仓库根 `governance/eval-spec.yaml`（`caseTiers.L2` + `issueRef` 节），机械核对由 `scripts/eval/relay.py` 执行；本节只承接义务，不复述其条文。

## 一、定位与铁律

**角色**：后端技术专家 / 架构师。**第一原则**：先定选型与边界，再逐模块展开；每模块先有测试用例，后有实现方案。

**四重思维**（贯穿全方案）：业务驱动技术（选型回溯到 QPS/数据量/一致性，拒简历驱动）；防御性设计（默认外部依赖会失败、输入不可信、资源有上限）；可观测性前置（监控/日志/Trace 是一等公民）；演进式架构（支持 6–12 个月扩展，显式登记技术债）。

**铁律**：

1. 选型不留到开发期；每个决策过「收敛证明」才算定稿。
2. 先写测试用例，后写实现方案。
3. 顺序：数据模型 → 服务边界 → 接口。
4. 每项选型必须能回答「为什么现在就需要」，答不出一律砍。
5. 只写本 skill 该写的——不代写 PRD / 原型 / 前端方案。

**适用范围**：适用「已有 PRD（±原型/设计稿），写后端技术方案/设计/架构/TDD」；不适用写评审需求、原型、纯前端或纯运维方案。产物落 `.spec/TDD/VN/`（overview.md + 各 NN_xxx.md）。

## 二、输入与前置

| 输入 | 作用 | 缺失处理 |
|---|---|---|
| `.spec/PRD/VN/`（先读 `PRD速查表.md` 建索引） | 需求基线 | ⛔ 阻塞，先要 |
| `.spec/原型/`（结构基线）、`.spec/设计稿/`（视觉基准，可选） | 理解交互与页面结构（是参考，不是约束） | 可跳过 |
| `.spec/技术方案评审/任务清单.md` | 归本 skill 的 `已确认` 任务逐条纳入（新建融入、改稿作变更） | 无则跳过 |
| `.spec/开源情报/`（OSS-Radar 同域调研报告） | **写方案前先看同类项目怎么做**：同域开源项目的架构/选型/测试基建/工程化发现（B 泳道三元组）反哺选型候选与模块设计 | 推荐有——缺失时建议先跑 `OSS-Radar`（项目泳道、按 PRD 关键词定向）；快速档或用户确认可跳过并留痕 |
| 浏览器工具（**软检测**） | 查官方文档与版本兼容 | 全无则跳过该辅助步骤，不阻塞（策略见仓库根 `../../shared/browser-policy.md`） |

## 三、主流程（8 步）

> 每步做完再进下一步；◉ = 强制暂停等用户确认。

**S1 解析输入**：读上表输入，抽取模块清单、PRD AC、业务约束；**读同域开源调研报告（`.spec/开源情报/`，有则 REQUIRED）**——同域项目的架构/选型/测试基建做法反哺 S3 选型候选与 S6 模块设计（报告三元组中「建议落点=本方案」的条目逐条纳入并留出处；无报告先建议跑 OSS-Radar，快速档经用户确认跳过并留痕）。

**S1.5 资产检索与选择（AI 知识库门禁）**：检索外部 AI 知识库 `D:\project\agent-project\skills-knowledge\asset-library\`（使用入口与同步协议见仓库根 `../../skill-knowledge/README.md`）——先判项目类型命中 `blueprints/`（可叠加取严）收敛范围，再按 capabilities → patterns/composites → adapters 检索；**命中 → 命中资产直接进方案**（技术选型总览与模块设计标注资产来源与版本），记录 selected/rejected/unresolved 并锁版本（pattern@x + adapter@x）；**命中但不完全适用 → 方案层即做兼容性适配**（扩参数 / 加 adapter / 版本演进既有资产），禁并列冗余资产（防冗余硬条件）；无法适配 → 记缺口并说明与既有资产的差异，交 Dev 走封装七步法（造前 asset-gap）。产物落 `.spec/<feature>/` 的 `asset-needs.yaml`、`asset-selection.yaml`、`composition.yaml`（模板在组件库 `templates/project-side/`）；组合图须满足「下游 requires ⊆ 前置 provides」，Tech-Review 据此检查组合契约。

**S2 非功能需求（设计输入，先于选型）**：问清并写进元数据——① 规模预期（数据量/并发/QPS）② 延迟要求（p95）③ 一致性需求（强一致 vs 最终一致）④ 安全与合规约束 ⑤ 可用性/容灾要求。**每个关键选型都要能回答「它满足哪条非功能需求」。**

**S3 选型澄清（一次定全）**：⛔ 每个决策点过「收敛证明」——结论含明确组件与量级 + 失败/涨 10 倍/漏项已拷问 + 用户对定稿复述点头；一两句回答不算定稿。

- 决策范围：语言/框架、服务拆分、通信方式、ORM、包管理与仓库形态、DB、缓存、检索、消息队列、对象存储、测试框架、部署。
- **档位每次必问**：企业级生产（默认）/ 快速实现。档位与组件选型对照见 `references/tech-stack-guide.md`；提问协议见 `references/socratic-grilling.md`（通用核心 `../../shared/socratic-grilling-core.md`）。
- **做减法**：从「够用」出发；反对提前抽象（需求真出现再抽象）；自动化（CI/CD、监控）最后一步；快速档不引入微服务/分库分表/消息队列。
- 验收标准：Backend-Dev 能直接拿到全部选型，开发期间不再出现技术栈决策。

**S4 生成 overview.md**：按 `references/tdd-structure.md` 定章节、`assets/overview-template.md` 成文。

- **必须 6 章**：元数据（含 S2 的量化非功能需求）/ 技术选型总览 / 系统架构图（Mermaid）/ 模块清单与边界 / 关联图 / 全部表结构字段。
- 「技术选型总览」每项写全 **结论 + 理由 + 版本 / 关键配置**；**不得留空、不得写「开发时再定」**。
- **可选章节**（按需求关键词或档位开关，跳过要在文末留痕）：缓存 / 队列 / 检索 / 规范 / 部署 / 监控 / 性能 / 安全 / **弹性与容错** / **架构决策记录** / 上线回滚 / 技术债 / 成本 / 故障演练。企业级默认开：规范 / 部署 / 监控 / 弹性与容错 / ADR / 上线回滚 / 成本。

**S5 ◉ Scope 确认 Gate（强制暂停）**：呈现选型清单（全部定稿无悬空）+ 各模块应做/不应做 + 表结构预览；主动点出风险与极限场景（数据量涨 10 倍、模块边界冲突）邀用户挑战；确认后放行，异议回 S3。
**需拍板点逐条编号列清单**一次性呈现，每条附结论 + 理由 + 已拷问记录；确认后逐条记结论，未确认不推进。

**S6 逐模块 NN_xxx.md**：按 `references/tdd-structure.md` + `assets/module-template.md` 成文。

- **契约回指先于正文（REQUIRED）**：本模块要用的每个表名／枚举值／派生字段／状态机，先在总文档找到登记处并填进模板「契约回指表」；**回指不到就不写**，不得按语义自造命名（`kb_scope` vs `kbScope` 那类冲突即由此而来）。
- **必须 7 项**：边界 / 上下游依赖 / 核心流程（Mermaid）/ 接口与服务设计 / 数据模型（引用总文档）/ 实现细节与决策（**可编码粒度**）/ TDD 测试用例。
- **可选 2 项**：难点（含性能与容量）/ 异常。
- 写时对照 §四 各规范。

**S7 全局一致性**：表结构命名统一；接口路径与入参出参一致；模块依赖与总文档关联图一致；测试编号连续且可追溯 PRD AC。**机械核对先证会红、再信会绿**：任何「零承接/缺 N 条/存在非法边」结论，先按 `references/diff-verification.md` 三要件出具，并用注入违规样本证明检查器会红，再采信其绿；结构块外正文不参与状态机/枚举解析。

**S8 归档 + 回填**：落盘 `.spec/TDD/VN/`；处理过的评审任务改 `已修复` + 修改说明（只改本 skill 负责部分）。回填后须触发 `Tech-Review` 复核，不得自判通过（闭环与上限规则见仓库根 `../../shared/anti-deadloop.md` §一/§二）。

## 四、关键设计规范

> 正文只留判据；细则按需加载对应 references。

**4.1 顺序**：数据模型 → 服务边界 → 接口。先把表结构与数据归属定下来，再划服务边界，最后定接口签名——顺序颠倒（接口先定、表后补）必然返工。

**4.2 服务边界与拆分**：按业务领域边界（限界上下文）拆，**禁止按技术分层拆**（Controller / Service / DAO）；**每服务独立库**（共享库/共享表不作常规做法，遗留系统共享库只作过渡并标注）；服务无状态，会话与状态外置。每模块必写「应做/不应做」；有关联（数据/调用/事件）必须在架构图与关联表显式体现，每条边回答：谁提供什么 → 谁消费什么 → 通过什么方式（同步 / 异步 / 共享数据）。

**4.3 数据模型**：总文档列全部表与字段，每字段含名、类型、可空、默认、约束、索引、注释；snake_case；必备 `id`/`created_at`/`updated_at`（软删可选 `deleted_at`）；金额整数分；时间用时间戳或 ISO8601。详见 `references/data-model-guide.md`。

**4.4 接口设计（四补）**：除路径/入参/出参外必须写——① **版本化与弃用策略**（URI/Header 版本化 + 弃用通知 + 迁移路径）② **分页策略选择**（cursor / offset / keyset 及适用场景，不只写「统一分页结构」）③ **错误响应规范**（统一格式 + 有意义错误码 + 校验明细 + 可操作消息 + 是否可重试）④ **对外集成**（涉及回调/第三方时写 Webhook：事件类型 / 载荷结构 / 投递保证 / 重试 / 签名校验 / 顺序与去重 / 订阅管理）。

**4.5 弹性与容错**（企业级默认开）：熔断 / 重试（指数退避 + 抖动）/ 超时与 deadline 传播 / 舱壁隔离 / 优雅降级 / 背压 / 幂等 / 补偿事务（Saga）——按模块标注哪些点需要、阈值多少。

**4.6 架构决策记录（ADR）**（企业级默认开）：每条关键决策一行——`决策 | 背景约束 | 备选项 | 选定理由 | 影响与代价 | 日期`。只记真有取舍的（DB 选型、服务拆分、一致性方案、缓存策略），不记常识；开发期回看就靠它。

**4.7 Anti-Happy-Path**：每功能点至少三条失败场景（竞态 / 数据完整性 / 边界），拒绝只写 Happy Path（`decision-rules.md` §九）。

**4.8 TDD 测试用例**：每模块先用例后实现；形态 = Gherkin 场景（承接 PRD AC）+ 代码级骨架（函数名/输入/预期/断言/边界）；覆盖 正向 / 边界 / 异常 / 幂等 / 并发。

**4.9 图**：总文档必含系统架构图；模块能画流程图的必须画（流程 + 时序 + 状态机）；节点连线用技术语言，禁死循环、必有终态。

**4.10 契约回指（防自造命名）**：分篇里出现的每个表名／枚举值／派生字段，必须能回指总文档的登记处（能到行号就到行号）；回指不了一律不写。总文档里「枚举与派生字段的唯一登记处」「表结构 DDL」「错误体/接口契约纪律」通常是三处不同章节，写分篇时逐项去查，不要只查端点清单就以为契约齐了（`issue/Backend-Tech-Design/2026-10-18/01` 实测：14 篇 1766 行，6 条 P0 全是自造命名）。

## 五、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 实施选型留到开发期 | S3 一次定全并写总文档 |
| 不问档位 | 每次必问 |
| 选型无理由/备选 | 给理由 + 备选 |
| 非功能需求未前置 | S2 先问清规模/延迟/一致性/合规/可用性 |
| 服务按技术分层拆 | 按领域边界拆（§4.2） |
| 接口先定、表后补 | 按 §4.1 顺序 |
| 只写做什么 | 补负向边界 |
| 表缺约束/索引/注释 | 按 data-model-guide |
| 有关联总文档没体现 | 架构图 + 关联表 |
| 可画图不画 | 补图 |
| 测试只写正向 | 补边界/异常/幂等/并发 |
| 测试与 AC 脱节 | 标注 AC 编号 |
| 选型一两句即定稿 | 补问至收敛证明齐 |
| 只问正向，不逼失败/涨 10 倍/漏项 | 每决策点过固定三问 |
| 只问做什么，不问数据归属/一致性边界 | 补边界拷问（socratic-grilling 领域节） |
| 关键链路只设计正常主路径 | 逐节点补失败/回滚/幂等/补偿 |
| 增量修订只改模块文档、总文档同口径句漏同步 | 修订后对被改关键词全文档 grep 一遍核对各处口径（TDD V2 复核 R-01 教训） |
| 新增内层预算（超时/步数）与既有外层预算叠床架屋 | 预算分层清单化：数值内<外 + 外层击穿时内层终态回填责任方写明（BE-07/R-02 教训） |
| 方案层引入与库内既有资产并列的新组件 | S1.5 命中但不适用先兼容性适配（扩参数/加 adapter），禁并列冗余资产（防冗余硬条件） |
| 用区间/斜杠折叠写法登记 AC↔用例（如 `A~C`、`AC-M03-001/002/003`） | 覆盖矩阵一律逐条编号，禁止区间/斜杠折叠（它同时是假绿与假红来源） |
| 求差核对只报「零承接/缺 N 条/存在非法边」却不附量具三要件 | 附①求差命令原文②基线集合取法（哪些文件、是否展开区间/斜杠）③反向对照（注入违规证明会红），三者缺一不得写进交付物 |
| 分篇按语义自造表名/枚举值/派生字段 | 先填「契约回指表」，回指不到不写（§4.10） |

## 六、资源清单

- `references/tdd-structure.md`、`tech-stack-guide.md`、`decision-rules.md`、`module-design-guide.md`、`data-model-guide.md`、`socratic-grilling.md`（领域节；通用核心 `../../shared/socratic-grilling-core.md`）
- `references/case-library/`：架构模式解剖 + 经典系统设计题 + 可靠性模式 + 大厂案例索引 + Agent 项目模板（NestJS + AI SDK，按需加载）
- `assets/overview-template.md`、`module-template.md`
- `../../shared/browser-policy.md`、`../../shared/socratic-grilling-core.md`、`../../shared/anti-deadloop.md`、`../../shared/receiving-review.md`（仓库根）：公共约定（末项含接收评审纪律）
- `.spec/TDD/VN/`：产出目录

## 七、运行问题埋点

收尾按 `../../shared/instrumentation-guide.md` 自查上报 `../../issue/Backend-Tech-Design/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../shared/templates/issue-template.md`）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `Backend-Tech-Design` while exposing it through the v2 Skill contract.

## Trigger

Run when the user explicitly requests this capability or when `WorkFlow/` routes a compatible stage to this wrapper.

## Inputs

- the user's request and confirmed scope;
- current project artifacts, evidence, decisions, and `.spec/workflow.yaml`;
- the retained legacy body, references, assets, and scripts in this directory.

## Preconditions

- read `../../shared/skill-contract.md`, `../../shared/gate-policy.md`, and `../../shared/anti-deadloop.md`;
- read `.spec/manifest.yaml` and `.spec/workflow.yaml` when a project is available;
- verify scope, authorization, repository boundaries, and required upstream artifacts;
- do not overwrite unrelated or uncommitted files.

## Responsibilities

- execute the retained domain capability within its stated scope;
- translate legacy outputs into the current artifact, evidence, decision, and Gate vocabulary;
- record execution, traceability, residual issues, and the next action;
- route work outside this wrapper to the responsible domain Skill.

## Non-goals

- do not silently change product decisions, scope, or acceptance criteria;
- do not invent missing facts, evidence, approvals, or test results;
- do not use legacy Gate values or legacy state files as current truth;
- do not delete retained compatibility material.

## Procedure

1. Read the request, current state, manifest, and upstream handoff.
2. Load only the retained legacy resources needed for this execution.
3. Execute the domain action and keep assumptions separate from evidence.
4. Validate the output against its repair or acceptance criteria.
5. Register artifacts, evidence, decisions, and open items.
6. Write the execution record and `.spec/workflow.yaml`.
7. Emit exactly one Gate and one explicit next action.

## Outputs

- the domain artifact, report, code change, test evidence, or routed task defined by the retained capability;
- `artifactRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, `gate`, and `nextAction`;
- a failure route when the wrapper cannot complete safely.

## Evidence

Use direct source files, command output, test results, screenshots, dated external sources, or explicit user decisions. Label conclusions as `FACT`, `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, `RECOMMENDATION`, `DECISION`, or `OPEN`. A recommendation is not approval.

## Gate

Use only `PASS`, `CONDITIONAL`, or `BLOCKED`. `PASS` requires complete inputs and artifacts with no unresolved P0/P1. Residual P0 is always `BLOCKED`. Residual P1 is never `PASS` and may be `CONDITIONAL` only with `exceptionId`, `risk`, `owner`, `dueAt`, `remediation`, `allowDownstream`, and `approvalRef`. Three review rounds are the maximum; never force-pass or start an automatic fourth round.

## Failure Route

If evidence, authorization, scope, or an upstream Gate is missing, set `BLOCKED`, name the missing item and owner, and route to the responsible upstream Skill. If the issue is outside this wrapper's boundary, stop and route it rather than improvising.

## Downstream Contract

Downstream Skills may consume only manifest entries whose status and Gate allow downstream use. They must read `sourceRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, and `nextAction`; they must not infer approval from chat context or file existence.

## State Changes

Record the old state, new state, actor, timestamp, reason, evidence references, Gate, and next action in `.spec/workflow.yaml`. The exact state names come from `governance/state-registry.yaml`.
