# Lifecycle Contract v2

> 适用范围：以下正式产物/Gate/状态契约用于标准、完整及正式交接。低风险独立任务按 `shared/execution-profiles.md` 留最小摘要，不写正式状态、不授予下游权限；已有相关阻塞与安全要求不因轻量而失效。

## 1. Supported lifecycles

| Lifecycle | Entry | Typical route |
|---|---|---|
| `CREATE` | project-onboarding or change-intake | product -> UI/DEV -> Test -> Release -> Operations |
| `CHANGE` | change-intake | impact-analysis -> affected domain Skills -> verification |
| `DEFECT` | defect-triage | Bug-Fix or DEV -> Test -> Release; escalate to Incident when needed |
| `REFACTOR` | refactor-planning | impact-analysis -> DEV -> Test -> Release |
| `INCIDENT` | incident-response | containment -> recovery -> verification -> post-release review |
| `OPTIMIZE` | optimization-planning | impact-analysis -> Skill optimization -> verification |

## 2. Boundaries

`change-intake` and `impact-analysis` are cross-domain Workflow entry points. `prd-workflow` owns only the internal product sequence. UI, DEV, Test, Release, and Operations Skills own their domain work.

## 3. State ownership

The current lifecycle and state are written to `.spec/workflow.yaml`. Every transition records the old state, new state, actor, timestamp, reason, evidence references, and Gate. A Skill may not silently change lifecycle or bypass an upstream block.

## 4. Open work

An unresolved `OPEN` item must have an owner, a next action, and a Failure Route. If it affects delivery safety or scope, the Gate is `BLOCKED` or an authorized `CONDITIONAL`; it is never silently treated as complete.
