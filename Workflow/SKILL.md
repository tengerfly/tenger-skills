---
name: workflow
description: 自然语言任务入口：按范围和风险选择轻量、标准或完整流程，复用已有基线，调用必要的产品/UI/开发/测试 Skill；低风险任务直接实现并验证，正式交接遵守产物、状态和 Gate 契约，研究与发布仅按需启动。
metadata:
  short-description: PEOS 总编排器
---

# PEOS Workflow

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose

把任意软件任务从入口路由到正确的领域 Workflow，并确保每次交接都有可消费的产物、证据、决策、状态和失败路线。成功标准是：下游不需要猜测上游意图，未通过 Gate 的结果不会伪装成完成。

## Trigger

当用户提出新建、迭代、Bug、事故、重构、性能/成本优化、发布、上线后问题或项目巡检时触发。先判断目标、范围与风险，不要求用户选择 Skill 或理解流程字段；信息缺失只澄清影响验收/安全的关键问题。明确的独立任务可直接调用原子 Skill，不强制经过本编排器。

## Inputs

- 项目路径、工作区状态、分支和用户授权；
- 需求、现有 `.spec/` 产物、项目基线和运行信号；
- 生命周期模式或待判定的原始请求；
- 可用 Skill、外部仓库集成、验证命令和用户决策。

## Preconditions

1. 检查当前目录、分支和未提交变更，不重置、不覆盖；
2. 先读 `shared/execution-profiles.md` 判执行强度；正式交接再加载 Skill/artifact/Gate/lifecycle 契约与相关注册项，不默认通读全部注册表；
3. 轻量任务只盘点相关代码、规则和测试；标准/完整缺少必要基线时调用 `project-onboarding`，不因少一份形式文档强迫小任务全量接管项目；
4. 所有事实、推断、假设和未知项带统一证据标签；
5. 消费 PRD 时按 `shared/requirements-context.md` 固定版本、先索引后读相关原文/依赖；新增选型或高风险技术设计按 `shared/oss-research-policy.md` 研究，既有栈局部修改不强制研究。

## Responsibilities

- 识别生命周期并建立执行记录；
- 从已有产物推断可跳过的阶段，但只在证据和 Gate 足够时跳过；
- 调度原子 Skill 和领域 Workflow；
- 验证产物元数据、追踪关系、状态转移和 Gate；
- 在失败时按问题归属回退到正确上游；
- 保留旧 `PIPELINE.md`/线性 15 节点链路的兼容读取能力。

## Non-goals

- 不代替产品、技术、测试或发布 Skill 生成其领域产物；
- 不绕过用户确认、授权、生产安全或发布 Gate；
- 不把 GitHub 研究结论、现有代码行为或模型推断当成已批准需求；
- 不自动修改外部 `web-monitor`、`server-log`、`server-monitor` 仓库。

## Procedure

### 1. 判断强度与终点

按 `shared/execution-profiles.md` 选择轻量/标准/完整；对用户只简述拟走路径、复用基线、修改边界和验收终点。默认完成用户要求的可验收结果，不默认执行发布/运维，也不每完成一小步都等待“继续”。用户只要分析/计划时不修改实现。

- **轻量**：记录最小任务摘要，直接进入“确认验收点 → 相关实现/审查 → 针对性验证 → 结果说明”，复用同一摘要，不执行下面的正式阶段建档。发现风险或需要正式交接时按共享规则升级，保留实际工作与证据。
- **标准/完整**：创建或更新 `.spec/workflow.yaml` 和执行记录，写明 `executionId`、项目、生命周期、状态、证据、产物和下一动作，再执行下面相关阶段。强度只记在任务说明/决策中，不新增状态或未注册 schema 字段。

### 2. 选择正式流程入口与基线（标准/完整）

- 新项目或陌生旧项目：`project-onboarding`；
- 模式不明：`change-intake`；
- 运行信号/缺陷：`defect-triage`；
- 内部结构治理：`refactor-planning`；
- 已有批准产物：读取其 manifest 和 Gate，跳到第一个缺失或已失效的阶段。

### 3. 路由领域 Workflow（标准/完整）

```text
CREATE  -> PRD -> UI -> Tech Design -> DEV -> Testing -> Release -> Operations
CHANGE  -> Intake -> Impact -> affected domain -> Tech Design -> DEV -> Testing -> Release -> Operations
DEFECT  -> Triage -> Tech Design (when needed) -> DEV -> Testing -> Release -> Operations
REFACTOR -> Refactor -> Tech Design -> DEV -> Testing -> Release -> Operations
INCIDENT -> Triage -> Incident Response -> Tech Design (when needed) -> DEV -> Testing -> Release -> Operations
OPTIMIZE -> Intake -> Impact -> experiment/Tech Design/DEV -> Testing -> Release -> Analytics
```

以上为可选领域路线，不是每次必跑清单。标准迭代只处理受影响领域；完整新项目才按所需阶段建立产物。已有批准产物通过证据复用，正式状态转换仍须沿注册合法边，不可伪造跳跃；没有合法边时说明缺口并停下，不手工宣称通过。

### 4. 守门与交接

正式交接的每个 Skill 必须输出 `PASS`、`CONDITIONAL` 或 `BLOCKED`，并声明 `allowDownstream`。轻量仅报告完成内容、真实验证和剩余限制，不输出正式 Gate/状态，也不授予下游自动执行权限。只允许 `PASS` 或显式允许下游的 `CONDITIONAL` 交接；任何 P0/P1 未处理、证据缺失、未授权或产物不完整均停止推进。

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
- **Compatibility entry points**: The numbered legacy pipeline, legacy `.spec/PIPELINE.md`, `Bug-Fix`, `Testing`, and `Fidelity-Review` remain callable as compatibility entries, wrapped by the current contracts. This Workflow wraps them with lifecycle, artifact, Gate, and traceability contracts instead of requiring a one-shot migration.


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

详细旧版节点与脚本兼容规则见 `references/legacy-pipeline.md`；通用契约见仓库根目录 `shared/`。
## Execution Envelope（正式交接 required）

标准/完整流程中的 Skill 调用及任何正式状态转换前必须创建或更新 `task-envelope.yaml` 的实例。低风险独立调用按 `shared/execution-profiles.md` 使用任务摘要，不要求 Envelope，也不能写入正式批准或状态。Envelope 是执行边界，不是普通说明文档；至少声明 `taskId`、`projectId`、`executionId`、`lifecycle`、`currentState`、允许/禁止路径、输入/产物/证据/决策引用、授权、期望输出、Gate 和 `nextAction`。正式执行缺少 Envelope、授权或路径范围时，必须停在 `WORKFLOW_BLOCKED`，不能以轻量名义继续正式转换或下游执行。

正式流程的 Skill 完成后只允许通过 Envelope 交接：写入实际产物引用、证据引用、决策引用、Gate outcome 和下一状态。`PASS` / `CONDITIONAL` / `BLOCKED` 是 Gate outcome；`PRD_APPROVED`、`TEST_PASSED` 等是状态/里程碑，不能混用。

### 可执行校验边界

`scripts/task_preflight.py` 是 **落盘状态转换前的只读就绪检查**，不是执行器。执行前确认 Envelope 输入、范围和真实授权；执行后归档证据、绑定 executionId/revision 和文件摘要，再调用预检。预检拒绝缺少完成证据不代表必须伪造证据才能开始工作；不得提前记录完成状态。它不会调用 Skill、写入状态或部署。批准策略与记录须由外部可信审批流程维护，格式和边界见 `docs/validation-toolchain.md`。
