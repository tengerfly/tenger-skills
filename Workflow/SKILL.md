---
name: workflow
description: 总编排器：识别项目生命周期、加载已验证基线、路由到产品/UI/开发/测试/发布/运行领域，并用统一产物契约、状态机和 Gate 控制交接；保留旧版线性流水线兼容入口，技术方案前仍强制执行 OSS/GitHub 同域研究。
metadata:
  short-description: PEOS 总编排器
---

# PEOS Workflow

## Purpose

把任意软件任务从入口路由到正确的领域 Workflow，并确保每次交接都有可消费的产物、证据、决策、状态和失败路线。成功标准是：下游不需要猜测上游意图，未通过 Gate 的结果不会伪装成完成。

## Trigger

当用户提出新建、迭代、Bug、事故、重构、性能/成本优化、发布、上线后问题或项目巡检时触发。若用户只给出模糊描述，先进入 `change-intake`，不直接启动开发。

## Inputs

- 项目路径、工作区状态、分支和用户授权；
- 需求、现有 `.spec/` 产物、项目基线和运行信号；
- 生命周期模式或待判定的原始请求；
- 可用 Skill、外部仓库集成、验证命令和用户决策。

## Preconditions

1. 检查当前目录、分支和未提交变更，不重置、不覆盖；
2. 读取 `shared/skill-contract.md`、`shared/artifact-contract.md`、`shared/gate-policy.md`、`shared/lifecycle-contract.md`；
3. 若项目缺少基线，先调用 `project-onboarding`；
4. 所有事实、推断、假设和未知项带统一证据标签；
5. 技术方案节点必须先调用 `OSS-Radar` 或按 `shared/oss-research-policy.md` 留下已核验的研究记录。

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

### 1. 建立执行上下文

创建 `.spec/workflow.yaml` 和执行记录，写明 `executionId`、项目、模式、当前状态、证据、产物和下一动作。

### 2. 选择入口与基线

- 新项目或陌生旧项目：`project-onboarding`；
- 模式不明：`change-intake`；
- 运行信号/缺陷：`defect-triage`；
- 内部结构治理：`refactor-planning`；
- 已有批准产物：读取其 manifest 和 Gate，跳到第一个缺失或已失效的阶段。

### 3. 路由领域 Workflow

```text
CREATE  -> PRD -> UI -> Tech Design -> DEV -> Testing -> Release -> Operations
CHANGE  -> Intake -> Impact -> affected domain -> Tech Design -> DEV -> Testing -> Release -> Operations
DEFECT  -> Triage -> Tech Design (when needed) -> DEV -> Testing -> Release -> Operations
REFACTOR -> Refactor -> Tech Design -> DEV -> Testing -> Release -> Operations
INCIDENT -> Triage -> Incident Response -> Tech Design (when needed) -> DEV -> Testing -> Release -> Operations
OPTIMIZE -> Intake -> Impact -> experiment/Tech Design/DEV -> Testing -> Release -> Analytics
```

保留既有的 `Competitive-Analysis → PRD → Prototype → UI/UX → OSS-Radar → TDD/FTDD → Dev → Code-Review → auto-test` 逻辑；变化只是将它们置于领域 Workflow 和状态机之下。

### 4. 守门与交接

每个 Skill 必须输出 `PASS`、`CONDITIONAL` 或 `BLOCKED`，并声明 `allowDownstream`。只允许 `PASS` 或显式允许下游的 `CONDITIONAL` 交接；任何 P0/P1 未处理、证据缺失、未授权或产物不完整均停止推进。

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

- **Any start, explicit stop**: Read `.spec/manifest.yaml` and `.spec/workflow.yaml` first. `.spec/PIPELINE.md` is read-only legacy input only; valid existing artifacts may skip stages only when manifest and Gate prove coverage. If no end point is specified, execute only the current entry stage and stop for `continue`, `skip`, `redo`, or `stop`.
- **Gate loop**: Every produced artifact goes through its corresponding review. Unresolved P0 findings remain BLOCKED. Unresolved P1 findings never become PASS; after three rounds they require an authorized CONDITIONAL with exceptionId, risk, owner, dueAt, remediation, allowDownstream, and approvalRef.
- **Ordering and parallel boundaries**: Technical design remains "write one, review one". Frontend and backend may run in parallel only after dependencies are satisfied; merge parallel findings, check conflicts, run the full validation, and sample-review the result. Frontend code review and Fidelity Review share one issue list.
- **Runtime feedback**: `web-monitor`, `server-log`, and `server-monitor` are controlled inputs only. Signals flow through `signal-collection`, `signal-triage`, and `incident-response`, then return to defect remediation, testing, release, and review. No external repository or production action is changed automatically.
- **Learning loop**: Gate and runtime findings keep the existing paths into project issues, `bug-patterns/`, and `issue/`; `Skill-Optimizer` and `Skill-Evolver` may distill them later. Every learning entry records evidence, destination, and rollback information.
- **Compatibility entry points**: The numbered legacy pipeline, legacy `.spec/PIPELINE.md`, `Bug-Fix`, `Testing`, and `Fidelity-Review` remain callable as compatibility entries, wrapped by the current contracts. This Workflow wraps them with lifecycle, artifact, Gate, and traceability contracts instead of requiring a one-shot migration.


## Outputs

- `.spec/workflow.yaml`：当前状态、模式、Gate、产物引用和下一动作；
- `.spec/manifest.yaml`：项目产物索引；
- `.spec/traceability.yaml`：需求、实现、测试、发布和运行信号之间的关系；
- `.spec/decisions/`：关键决策和例外；
- `.spec/<domain>/`：各领域产物；
- `execution` 摘要：状态、证据、Gate、失败路线和下游契约。

## Evidence

有效证据包括文件/行号、执行命令及退出码、测试报告、真实渲染截图、脱敏日志/指标、已核验 GitHub 源码位置、用户确认和发布记录。不能用“看起来完成”“模型说可以”替代证据。

## Gate

- `PASS`：模式、范围、产物、证据、状态和下一步均清楚，阻塞项为零；
- `CONDITIONAL`：例外已登记负责人、截止时间、补证动作和 `allowDownstream`；
- `BLOCKED`：模式/范围/授权/关键输入不明，或存在未处理的 P0/P1。

## Failure Route

缺少基线转 `project-onboarding`；模式不明转 `change-intake`；线上高影响转 `defect-triage`/Incident；结构治理转 `refactor-planning`；链路无法验证转相应领域评审。任何脚本发现注册表、产物或追踪关系非法时，停止自动推进并修复契约，不手工宣称通过。

## Downstream Contract

下游必须收到：生命周期模式、范围、已批准输入、不可改变行为、产物 manifest、证据索引、决策引用、当前 Gate、允许动作和回退路径。下游不得假设未列出的行为、环境或权限。

## State Changes

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