# tenger-skills

## 中文说明书：先从这里看

- **日常怎么用**：[工程体系使用手册](docs/工程体系使用手册.md)——入口、环境准备、常用场景、暂停恢复、Gate、产物与命令。
- **体系是什么、有没有偏离目标**：[当前项目介绍与目标对齐说明书](docs/当前项目介绍与目标对齐说明书.md)——目标复述、整体流程、45 个本地 Skill、模块边界、已实现/待验证能力及待确认取舍。

> 2026-09-22 核对：本地全量校验通过（60 项测试：59 通过、1 因符号链接权限不足跳过；外部知识库未配置，属降级），不等于体系已验收。当前自举 Gate 仍为 `BLOCKED`，真实项目试跑与独立验收待完成。日常无需逐一阅读所有 Skill，先按手册给出项目、目标、范围和终点。

A modular Skill repository for product discovery, PRD, UI, development, testing, release, operations, and Skill optimization.

## 流程可见、需求先研究、测试单入口

- 2026-09-22 修订：开工/恢复、阶段交接、阻塞与收尾展示当前步骤、Skill、产物、待决定事项和下一步；规则见 `shared/workflow-visibility.md`。
- 对标应用或明确要求竞品时，先给带来源的模块/功能全景，再由用户逐模块选择范围；PRD 原子职责见 `shared/product-workflow-contract.md`。
- 旧项目接入称“存量项目接管与工程流程补齐”：先 project-onboarding 盘点缺口，不默认重构或只跑测试。
- 测试唯一入口是 auto-test；Testing 已归档，不再作为备用 Skill 被发现。
- 状态快照：`python scripts/workflow_status.py --project-root <项目路径>`（只读，不调度、不审批）。

## 直接聊天，流程按任务大小选择

“做个 Demo，不部署”“给现有列表加筛选，改完验证”“只优化这一页的视觉”都可以直接作为请求。AI 按范围和风险选择轻量、标准或完整流程，不要求用户掌握内部字段和 Skill 顺序。

- **轻量**：低风险独立任务只保留目标/验收点、必要上下文、实现与验证摘要，不强制全套 PRD、技术设计或 Envelope。
- **标准/完整**：复用有效基线，仅按需进入正式交接；权限、资金、迁移、生产等风险控制不能省。
- **需求按需读取**：现有 PRD 速查表作为 Wiki 导航，固定版本后读取相关原文/AC/依赖，不维护第二套需求摘要。
- **UI 自写 B**：新设计/延展/局部修改分流，继承现有风格；检查通过的首版可交付。Superdesign A 保持原流程。

运行规则：`shared/execution-profiles.md`、`shared/requirements-context.md`。规则由 Agent 执行，现有脚本只校验正式契约，不是自动路由器；轻量不会赋予正式状态、绕过相关阻塞或发布授权。

## 可独立复制的 Skill 维护闭环

[Skill/README.md](Skill/README.md)：把 `Skill/` 整个目录发给别人，或只复制完整的 `Skill/skill-lifecycle/`。接收方可从创建 Skill 开始，记录实际问题、确认个人偏好、小步迭代与验证；无需本工程的共享规则、注册表或问题池。运行数据独立保存，不随工具包分享。原体系内部维护仍用 Skill-Optimizer / Skill-Evolver，独立包不自动接管原流程。

## Repository layout

```text
PRD/       product discovery, decisions, PRD, and prototype workflow
UI/        prototype, UI/UX, and fidelity work
DEV/       technical design, implementation, and code review
Test/      auto-test only; retired Testing resources are read-only
Other/     defects, OSS research, release/operations, and Skill meta-work
Skill/     portable skill-lifecycle package; copy independently
workflow/  root-level orchestration only
shared/    common contracts, templates, and evidence rules
governance/ registries and schemas
```

Every Skill entry point is named `SKILL.md`. Folder names identify the domain; compatibility aliases remain in registries and frontmatter where needed.

## Current product workflow

The following is the formal product workflow, not a mandatory checklist for low-risk standalone tasks. Select execution scope first.

```text
Idea Intake
 -> Product Discovery
 -> Competitive Research
 -> Product Definition
 -> Application Blueprint
 -> Feature Decision
 -> PRD Design
 -> PRD Review
 -> Prototype Design
 -> Prototype Review
```

`change-intake` and `impact-analysis` are cross-domain Workflow entry points. `prd-workflow` owns only the product-domain sequence. `WorkFlow/` routes work, records state, enforces Gates, and manages handoffs; domain Skills produce the domain artifacts.

## Common contracts

All Skills share the safety and evidence rules. The Gate/state/artifact requirements below apply to formal execution and handoffs; lightweight standalone tasks use a scoped result summary without claiming formal approval:

- Gate values are exactly `PASS`, `CONDITIONAL`, or `BLOCKED`.
- `PASS` requires no unresolved P0/P1 in scope.
- Residual P0 is always `BLOCKED`.
- Residual P1 may be `CONDITIONAL` only with an authorized exception containing `exceptionId`, `risk`, `owner`, `dueAt`, `remediation`, `allowDownstream`, and `approvalRef`.
- Review-fix-review is limited to three rounds; there is no automatic fourth round and no force-pass rule.
- Current state is written to `.spec/workflow.yaml`.
- `.spec/PIPELINE.md` and `.spec/WORKFLOW.yaml` are read-only legacy inputs.
- Claims use the shared labels `FACT`, `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, `RECOMMENDATION`, `DECISION`, and `OPEN`.
- `RECOMMENDATION` is not approval; `DECISION` requires the user or an authorized owner.

Read the contracts before changing a Skill:

- `shared/execution-profiles.md`
- `shared/requirements-context.md`
- `shared/skill-contract.md`
- `shared/gate-policy.md`
- `shared/anti-deadloop.md`
- `shared/artifact-contract.md`
- `shared/lifecycle-contract.md`
- `shared/product-workflow-contract.md`

## Compatibility policy

Old Skills, references, assets, aliases, and the numbered pipeline are retained as compatibility material. They are not deleted, but they cannot override the current shared contracts. Historical files are marked with a legacy notice where their old wording could be misleading.

## Validation

Run from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate.ps1 -ProjectRoot (Get-Location).Path
```

The validators check frontmatter, required Skill sections, registry paths, workflow transitions, artifact manifests, and traceability fixtures.

## Execution status

The repository self-spec is intentionally recorded as BLOCKED while remediation and independent acceptance are pending. A passing local validator means the checks ran successfully; it is not a human approval or production-release decision.

The executable validation path is:

1. scripts/bootstrap.ps1 creates/uses .venv and installs the pinned dependency.
2. scripts/run-tests.ps1 runs positive and negative validator tests.
3. scripts/validate.ps1 runs regression tests and validates registries, contracts, the envelope template, graph semantics, references, Gates, fixtures, and knowledge dependency policy.
4. Set SKILLS_KNOWLEDGE_ROOT to enable the external knowledge checks; otherwise validation reports explicit degraded mode.

Actual task transition readiness is checked with `python scripts/task_preflight.py --project-root <project> --task-file .spec/tasks/TASK-001.yaml`. It emits a read-only plan; it does not execute Skills, change state, or deploy. See `docs/validation-toolchain.md` for authorization records, evidence digests, migration notes, and remaining manual controls.
