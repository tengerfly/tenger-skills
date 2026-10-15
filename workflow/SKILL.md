---
name: workflow
description: 任何软件任务的统一入口（PEOS 编排器）。只要用户描述「期望存在的软件能力」（要一个还不存在的东西，而非改已有代码），就先加载本 skill 判定范围/风险/路径再调度专业 skill——无论被称作应用、Agent、知识库等任意形态，未列举同判；也覆盖功能迭代、Bug、事故、重构、优化、发布、巡检及「按体系重跑旧项目」。不代做需求澄清/竞品研究/PRD/代码实现。
metadata:
  short-description: PEOS 总编排器
---

# PEOS Workflow

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose

把任意软件任务从入口路由到正确的领域 Workflow，并确保每次交接都有可消费的产物、证据、决策、状态和失败路线。成功标准是：下游不需要猜测上游意图，未通过 Gate 的结果不会伪装成完成。

## Trigger

当用户提出新建、迭代、Bug、事故、重构、性能/成本优化、发布、上线后问题或项目巡检时触发。**「新建」按类别判，不按形态名词判**：用户描述的是「期望存在的软件能力」即属新建，无论称它应用、系统、平台、服务、后台、小程序、Agent、智能体、知识库、RAG、图谱还是别的说法，未列举的同判；请求听起来模糊也不是拒绝理由，模糊正是入口。先判断目标、范围与风险，不要求用户选择 Skill 或理解流程字段。明确的独立任务可直接调用原子 Skill，不强制经过本编排器。

**澄清分层（硬约束）**：需求方向确认阶段的澄清只允许落在业务范围、目标用户、使用场景、数据语义与验收预期层；语言、框架、数据库、存储真相源、渲染库、部署形态等技术决策不得在此阶段提问，须留到 Tech Design 节点按 `../shared/oss-research-policy.md` 展开。不得用「只澄清关键问题」为由把选型问题充当需求澄清，也不得把 AI 自己可查证、可推断的认知转成用户的填空题（判据见 `../shared/product-workflow-contract.md` §2.2）。

## Inputs

- 项目路径、工作区状态、分支和用户授权；
- 需求、现有 `.spec/` 产物、项目基线和运行信号；
- 生命周期模式或待判定的原始请求；
- 可用 Skill、外部仓库集成、验证命令和用户决策。

## Preconditions

1. 检查当前目录、分支和未提交变更，不重置、不覆盖；
2. 先读 `../shared/execution-profiles.md` 判执行强度；正式交接再加载 Skill/artifact/Gate/lifecycle 契约与相关注册项，不默认通读全部注册表；
3. 轻量任务只盘点相关代码、规则和测试；标准/完整缺少必要基线时调用 `project-onboarding`，不因少一份形式文档强迫小任务全量接管项目；
4. 所有事实、推断、假设和未知项带统一证据标签；
5. 消费 PRD 时按 `../shared/requirements-context.md` 固定版本、先索引后读相关原文/依赖；新增选型或高风险技术设计按 `../shared/oss-research-policy.md` 研究，既有栈局部修改不强制研究。

## Responsibilities

- 识别生命周期并建立执行记录；
- 从已有产物推断可跳过的阶段，但只在证据和 Gate 足够时跳过；
- 调度原子 Skill 和领域 Workflow，并在调度前执行上游闸门核对（`../shared/gate-policy.md` §6）；
- 验证产物元数据、追踪关系、状态转移和 Gate；
- 在失败时按问题归属回退到正确上游；
- 保留旧 `PIPELINE.md`/线性 15 节点链路的兼容读取能力。

## Non-goals

- 不代替产品、技术、测试或发布 Skill 生成其领域产物；
- 不绕过用户确认、授权、生产安全或发布 Gate；
- 不把 GitHub 研究结论、现有代码行为或模型推断当成已批准需求；
- 不在上游 `gate` 非 `PASS` 或 `allowDownstream: false`、或基线作废未清点时，把下游节点排进 `nextAction`；
- 不自动修改外部 `web-monitor`、`server-log`、`server-monitor` 仓库。

## Procedure

### 0. 公开路径与当前位置

按 `../shared/workflow-visibility.md` 展示阶段路线与状态卡；开工/恢复、阶段切换、等待决策、阻塞和收尾都要更新。先说明当前 skill、正在做什么、产物、下一步与需用户决定的事项，再执行。用户查询状态先回应；要求暂停即保存并停止。

### 1. 判断强度与终点

按 `../shared/execution-profiles.md` 选择轻量/标准/完整（输出强度须附命中判据条目，缺引用视为未判定；单次会话跨 3 模块/供应商替换/新增外部服务至少标准）；对用户只简述拟走路径、复用基线、修改边界和验收终点。默认完成用户要求的可验收结果，不默认执行发布/运维，也不每完成一小步都等待“继续”。「按你推荐的来 / 继续」只代理已摆出的选项之选择，不豁免阶段可见性、影响分析与 Gate 交接，也不扩大修改范围。用户只要分析/计划时不修改实现。

- **轻量**：记录最小任务摘要，直接进入“确认验收点 → 相关实现/审查 → 针对性验证 → 结果说明”，复用同一摘要，不执行下面的正式阶段建档。发现风险或需要正式交接时按共享规则升级，保留实际工作与证据。
- **标准/完整**：创建或更新 `.spec/workflow.yaml` 和执行记录，写明 `executionId`、项目、生命周期、状态、证据、产物和下一动作，再执行下面相关阶段。强度只记在任务说明/决策中，不新增状态或未注册 schema 字段。**〔REQUIRED · 建档结构与量具可达〕**两份控制文件的根结构与字段名以 `../shared/templates/workflow.yaml`、`../shared/templates/project-manifest.yaml` 为准，`status`／`state` 取值以 `governance/` 注册表与 `../shared/artifact-contract.md` §2 为准（业务口径词如 `REGISTERED`／`READY`／`APPROVED_SUPERSEDED` 不得写入 `status`）；首次建档或改动后各跑一次 `python scripts/validate_core.py gate --project-root <项目>` 与 `artifact --project-root <项目>`（**业务项目用这两条**；`system` 需项目内另有 `governance/` 与 `traceability.yaml`，对本仓之外的项目会报一堆无关红，只在本仓自检时用）——**解析失败或字段非法即停 `WORKFLOW_BLOCKED` 并如实报告，不得在「校验器读不通」的状态下继续正式交接**：闸门字段的机械检出者就是这个校验器，它不通则 §6 全部规则只剩执行方自觉（成因见仓库根 `issue/WorkFlow/2026-10-10/02`）。

### 2. 选择正式流程入口与基线（标准/完整）

- **先判产品意图（最高优先）**：目标目录为空、无 `.spec/`、无已有实现，且请求含产品意图（目标用户、功能、形态）⇒ 归 CREATE 并进入需求域（`idea-intake`），强度按 `../shared/execution-profiles.md` 落到标准/完整档。此时禁止从探查兄弟项目工程栈、盘点技术栈或抛技术选型问题开始；起点由该判据决定，不由执行方自行发挥。对标应用与从零新应用共用本判据；
- 新项目或陌生旧项目：`project-onboarding`；
- “旧项目按现在体系重跑/接入新流程/工程流程补齐”：先 `project-onboarding` 产出阶段缺口矩阵，再让用户确认补齐范围；不是自动 REFACTOR，也不是只跑测试。仅补工程基线按 CHANGE 记录，若实际目标是重构/缺陷/优化则按相应生命周期；不新增迁移状态、不重写旧 PIPELINE、不默认改代码或发布；
- “全流程测试/全量回归”仅测试已有实现：直接 `auto-test`，缺失基准如实列出，不扩成需求重做；
- 模式不明：`change-intake`；
- 运行信号/缺陷：`defect-triage`；
- 内部结构治理：`refactor-planning`；
- 已有批准产物：读取其 manifest 和 Gate，跳到第一个缺失或已失效的阶段。

### 3. 路由领域 Workflow（标准/完整）

```text
CREATE  -> PRD -> Prototype -> UI Design -> UI Review -> Tech Design -> DEV -> auto-test -> Release -> Operations
CHANGE  -> Intake -> Impact -> affected domain -> Tech Design -> DEV -> auto-test -> Release -> Operations
DEFECT  -> Triage -> Tech Design (when needed) -> DEV -> auto-test -> Release -> Operations
REFACTOR -> Refactor -> Tech Design -> DEV -> auto-test -> Release -> Operations
INCIDENT -> Triage -> Incident Response -> Tech Design (when needed) -> DEV -> auto-test -> Release -> Operations
OPTIMIZE -> Intake -> Impact -> experiment/Tech Design/DEV -> auto-test -> Release -> Analytics
```

CREATE 行的 `UI Design -> UI Review` 是**必经节点**（`ui-ux-design` → `ui-ux-review`，产物 `.spec/设计稿/`），不是可选领域名：`PROTOTYPE_APPROVED → TECH_DESIGN_IN_PROGRESS` 不是合法边，进入技术设计的 CREATE 合法前驱是 `UI_APPROVED`。需求阶段亦不得提前抛出技术选型问题（见 `Trigger` 澄清分层与 §3.1）。以上仅对 CREATE 强制；CHANGE/DEFECT 等复用已批准视觉基线，局部改动不重做设计稿。

以上为可选领域路线，不是每次必跑清单。标准迭代只处理受影响领域；完整新项目才按所需阶段建立产物。已有批准产物通过证据复用，正式状态转换仍须沿注册合法边，不可伪造跳跃；没有合法边时说明缺口并停下，不手工宣称通过。

测试执行唯一入口为 `auto-test`，`testing-workflow` 只是领域路由 ID，不是第二套测试流程。旧 Testing 请求重定向 auto-test，不启动历史人工测试流程。

### 3.1 资源投入门禁与等待态（标准/完整）

高成本动作——调度研究类 Skill、大范围检索、竞品或源码调研、技术选型展开、代码实现——的准入前提是**存在用户已确认并登记的需求方向**（decision 或 artifact 状态 `ACCEPTED`，或用户在本会话内明确复述确认过的事实）。未确认时只允许零成本的意图澄清。

- 禁止以「并行不空等／利用等待时间／先把能做的做了」为理由启动上述动作：研究范围本身取决于需求方向，方向未定即开跑属资源浪费，且该浪费由用户买单；
- 启动前向用户简述「查什么范围、大概什么代价、回来后给你什么」，由用户决定是否现在投入——用户是资源裁决者；
- 与用户确定需求的正确抓手，是先陈述 AI 理解的需求方向供其改写，而不是抛选择题、或自行调研代替这一步。

后台研究未回传期间，本轮交付物只能是「已登记事实 + 当前在等什么 + 回来后给你什么」，不得同时向用户追加索取答案依赖该研究的题目；用户可见的交付顺序必须与研究的交付顺序一致。提问本身的合法性判据（只问只有用户能回答的题）见 `../shared/product-workflow-contract.md` §2.2，本处不另立规则。

### 4. 守门与交接

正式交接的每个 Skill 必须输出 `PASS`、`CONDITIONAL` 或 `BLOCKED`，并声明 `allowDownstream`。**〔REQUIRED · 交接留轨〕**标准/完整流程每个节点开工前跑 `python scripts/tsr.py --project-root <项目> --execution-id <E> --node <节点> --skill <skill> --role <produce|fix|review|recheck> [--round n --batch n] node-start`，交接时同参数跑 `node-end --gate … --allow-downstream … --artifact <产物路径> [--upstream <id>:<gate>]`；时钟、序号、产物摘要由脚本生成，不得手写（口径 `../shared/gate-policy.md` §6 第 7 条，`verify` 复算不过即视同交接未完成）。轻量任务不要求正式 Envelope，但同样不因此获得下游执行权限。轻量仅报告完成内容、真实验证和剩余限制，不输出正式 Gate/状态，也不授予下游自动执行权限。只允许 `PASS` 或显式允许下游的 `CONDITIONAL` 交接；任何 P0/P1 未处理、证据缺失、未授权或产物不完整均停止推进。

**开工前闸门核对（REQUIRED，先于任何节点调度与状态前移）**：调度任一专业 Skill 之前，先读该节点所依赖的上游 artifact 在 `.spec/manifest.yaml` / `.spec/gates/` 的 `status`、`version`、`gate`、`allowDownstream`、`blockedBy`（口径见 `../shared/gate-policy.md` §6）。任一上游为 `SUPERSEDED`、`gate` 非 `PASS`、或 `allowDownstream: false` ⇒ ① 不启动该节点；② `currentState` 与 `nextAction` 不得指向关闸上游的下游，状态停在阻塞点并用已注册状态（如 `WORKFLOW_BLOCKED`），不为此新增状态名；③ 在 `workflow.yaml.blockedItems` 记 `BLK-*`（含 `owner`、`requiredInput`、`clearCondition`），`nextAction` 指回上游 owner。**禁止**以「下游先往前赶、上游慢慢补」「并行不空等」「先把能做的做了」越过未清阻塞：闸门既是数据也是检查点，不靠执行方自觉。

**基线作废即清点沉没产出（REQUIRED）**：方向 / 基线类 DEC（如 `DEC-*-PRODUCT-DIRECTION`）把已批准基线转为 `SUPERSEDED` 的同一轮，必须输出「引用该基线的下游产物清单 + 逐项处置（回炉重写／增量更新／作废）」并登记，不得留到下游节点自己发现；清单靠下游产物按 `../shared/artifact-contract.md` §2 登记的 `sourceRefs` 反查得到。

**视觉基线准入**：CREATE 流程进入技术设计或前端开发前，须存在设计稿批准记录（`UI_APPROVED`，或已批准的 `.spec/设计稿/` + `design-system.md`）。缺失时只有经用户显式批准的例外（EXC）可放行；凡输入基线自称「设计稿：无」「本批不涉及视觉」「缺省回退低保真原型」而无 EXC 引用，判 `BLOCKED` 并停下报告，不得把缺失写成批次说明后继续推进（规则见 `../shared/product-workflow-contract.md` §5.1）。

### 5. 失败回退

- 产品范围/验收失败 → PRD；
- 原型/交互失败 → Prototype/UI；
- 技术契约/架构失败 → Backend/Frontend Tech Design；
- 代码实现失败 → Backend/Frontend Dev；
- 测试失败 → Defect-Triage 或对应实现；
- 发布/运行信号异常 → Release / Operations / Incident；
- 流程自身问题 → `Skill-Optimizer` / `Skill-Evolver`。

### 6. 收尾

Record the handoff summary, commands, evidence, Gate, user decision, change scope, and next action. After release, associate runtime signals with version, commit, request/trace/session identifiers and enter the observability loop.

## Compatibility & Retained Controls

PEOS v2 is an incremental refactor. It preserves the proven controls from the previous Workflow:

- **Any start, explicit stop**: Apply execution profiles first. In formal workflows, read the relevant manifest/state and reuse only proven coverage. Legacy `.spec/PIPELINE.md` is read-only. Stop at the requested verifiable result; never infer permission for release or operations. A request explicitly limited to an entry stage stops there.
- **Gate loop (formal artifacts)**: Every required formal artifact goes through its corresponding review; low-risk standalone tasks use scoped self-checks without manufacturing formal approvals. Unresolved P0 findings remain BLOCKED. Unresolved P1 findings never become PASS; after three rounds they require an authorized CONDITIONAL with exceptionId, risk, owner, dueAt, remediation, allowDownstream, and approvalRef.
- **Ordering and parallel boundaries**: Technical design remains "write one, review one". Frontend and backend may run in parallel only after dependencies are satisfied; merge parallel findings, check conflicts, run the full validation, and sample-review the result. Frontend code review and Fidelity Review share one issue list.
- **Runtime feedback**: `web-monitor`, `server-log`, and `server-monitor` are controlled inputs only. Signals flow through `signal-collection`, `signal-triage`, and `incident-response`, then return to defect remediation, testing, release, and review. No external repository or production action is changed automatically.
- **Learning loop**: Gate and runtime findings keep the existing paths into project issues, `bug-patterns/`, and `issue/`; `Skill-Optimizer` and `Skill-Evolver` may distill them later. Every learning entry records evidence, destination, and rollback information.
- **Compatibility entry points**: The numbered legacy pipeline, legacy `.spec/PIPELINE.md`, `Bug-Fix` and `Fidelity-Review` remain callable as compatibility entries, wrapped by the current contracts. This Workflow wraps them with lifecycle, artifact, Gate, and traceability contracts instead of requiring a one-shot migration.


## Outputs

轻量：目标/范围/验收点、实际改动、验证证据、未验证项和下一步；暂停/交接时持久化同一任务摘要。以下为正式流程产物，不为轻量任务全套创建：

- `.spec/workflow.yaml`：当前状态、模式、Gate、产物引用和下一动作；
- `.spec/manifest.yaml`：项目产物索引；
- `.spec/traceability.yaml`：需求、实现、测试、发布和运行信号之间的关系；
- `.spec/decisions/`：关键决策和例外；
- `.spec/<domain>/`：各领域产物；
- `execution` 摘要：状态、证据、Gate、失败路线和下游契约。

## Evidence

有效证据包括文件/行号、执行命令及退出码、测试报告、真实渲染截图、脱敏日志/指标、已核验 GitHub 源码位置、用户确认和发布记录。不能用“看起来完成”“模型说可以”替代证据。

## Gate

仅正式交接使用以下 Gate；轻量结果描述不等于任何正式里程碑。

- `PASS`：模式、范围、产物、证据、状态和下一步均清楚，阻塞项为零；
- `CONDITIONAL`：例外已登记负责人、截止时间、补证动作和 `allowDownstream`；
- `BLOCKED`：模式/范围/授权/关键输入不明，或存在未处理的 P0/P1。

## Failure Route

轻量缺少关键规则时定向澄清，风险扩大则升级；正式流程缺少必要基线转 `project-onboarding`；模式不明转 `change-intake`；线上高影响转 `defect-triage`/Incident；结构治理转 `refactor-planning`；链路无法验证转相应领域评审。任何脚本发现注册表、产物或追踪关系非法时，停止自动推进并修复契约，不手工宣称通过。

## Downstream Contract

轻量协作复用同一任务摘要与需求上下文，不假装完成正式状态转换。正式下游必须收到：生命周期模式、范围、已批准输入、不可改变行为、产物 manifest、证据索引、决策引用、当前 Gate、允许动作和回退路径。下游不得假设未列出的行为、环境或权限。

## State Changes

轻量独立任务不写入正式状态。以下仅描述正式生命周期，实际转换以注册图与预检为准：

```text
ONBOARDING_REQUESTED | INTAKE_REQUESTED -> DISCOVERY_IN_PROGRESS
-> ONBOARDING_BASELINE_READY | INTAKE_READY
-> PRD_IN_PROGRESS -> PRD_APPROVED -> UI_IN_PROGRESS -> UI_APPROVED
-> TECH_DESIGN_IN_PROGRESS -> TECH_DESIGN_APPROVED -> DEV_IN_PROGRESS
-> CODE_REVIEW_PASSED -> TEST_IN_PROGRESS -> TEST_PASSED
-> RELEASE_PLANNING_IN_PROGRESS -> RELEASE_PLAN_READY
-> DEPLOYMENT_IN_PROGRESS -> DEPLOYMENT_EXECUTED
-> RELEASE_VERIFICATION_IN_PROGRESS -> RELEASE_VERIFIED
-> OPERATIONS_OBSERVED -> SIGNAL_COLLECTION_IN_PROGRESS -> SIGNALS_COLLECTED
-> SIGNAL_TRIAGE_IN_PROGRESS -> SIGNAL_ROUTED
-> DEV_IN_PROGRESS | INCIDENT_ROUTED | INSPECTION_RECORDED | COMPLETED
```

详细旧版节点与脚本兼容规则见 `references/legacy-pipeline.md`；通用契约见仓库根目录 `../shared/`。
## Execution Envelope（正式交接 required）

标准/完整流程中的 Skill 调用及任何正式状态转换前必须创建或更新 `task-envelope.yaml` 的实例。低风险独立调用按 `../shared/execution-profiles.md` 使用任务摘要，不要求 Envelope，也不能写入正式批准或状态。Envelope 是执行边界，不是普通说明文档；至少声明 `taskId`、`projectId`、`executionId`、`lifecycle`、`currentState`、允许/禁止路径、输入/产物/证据/决策引用、授权、期望输出、Gate 和 `nextAction`。正式执行缺少 Envelope、授权或路径范围时，必须停在 `WORKFLOW_BLOCKED`，不能以轻量名义继续正式转换或下游执行。

正式流程的 Skill 完成后只允许通过 Envelope 交接：写入实际产物引用、证据引用、决策引用、Gate outcome 和下一状态。`PASS` / `CONDITIONAL` / `BLOCKED` 是 Gate outcome；`PRD_APPROVED`、`TEST_PASSED` 等是状态/里程碑，不能混用。

### 可执行校验边界

`scripts/task_preflight.py` 是 **落盘状态转换前的只读就绪检查**，不是执行器。执行前确认 Envelope 输入、范围和真实授权；执行后归档证据、绑定 executionId/revision 和文件摘要，再调用预检。预检拒绝缺少完成证据不代表必须伪造证据才能开始工作；不得提前记录完成状态。它不会调用 Skill、写入状态或部署。批准策略与记录须由外部可信审批流程维护，格式和边界见 `docs/validation-toolchain.md`。
