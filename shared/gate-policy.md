# Gate Policy v2

This file is the single source of truth for Gate semantics. Every Skill and Workflow uses the same three outcomes:

```text
PASS | CONDITIONAL | BLOCKED
```

> 适用范围：以下正式产物/Gate/状态契约用于标准、完整及正式交接。低风险独立任务按 `shared/execution-profiles.md` 留最小摘要，不写正式状态、不授予下游权限；已有相关阻塞与安全要求不因轻量而失效。

## 1. Severity and Gate mapping

| Severity | Meaning | Default handling |
|---|---|---|
| P0 | Critical path is unusable, unsafe, contradictory, or impossible to implement | Must be resolved; any residual P0 is `BLOCKED` |
| P1 | Important ambiguity, missing boundary, unverifiable acceptance, or contract inconsistency | Must be resolved for `PASS`; residual P1 requires an authorized `CONDITIONAL` |
| P2 | Non-critical quality or completeness issue | May remain open when risk is recorded |
| P3 | Backlog or polish item | Does not block by itself |

Severity is not the Gate. The Gate is the result of the evidence, authorization, artifact completeness, and unresolved-risk checks below.

## 2. PASS

Use `PASS` only when all of the following are true:

- required inputs and upstream Gates are present;
- required artifacts are complete, traceable, and stored in the manifest;
- no unresolved P0 or P1 remains in the current scope;
- every claim that affects delivery has evidence or a decision reference;
- no OPEN item is being silently treated as a decision;
- downstream is allowed by the lifecycle and workflow rules.

`PASS` is never a synonym for "file exists" or "the agent believes it is good".

## 3. CONDITIONAL

Use `CONDITIONAL` only when the remaining risk is explicitly accepted by an authorized owner. The record must include every field below:

```yaml
gate: CONDITIONAL
exceptionId: EXC-YYYYMMDD-001
risk: <specific residual risk>
owner: <accountable person or role>
dueAt: YYYY-MM-DD
remediation: <concrete action and acceptance condition>
allowDownstream: true | false
approvalRef: <decision or approval record>
```

Rules:

- residual P0 is never eligible for `CONDITIONAL`;
- residual P1 is never an implicit exception;
- `allowDownstream: false` blocks downstream even though the Gate is recorded;
- `allowDownstream: true` is valid only when `approvalRef` and the remediation plan are present.

## 4. BLOCKED

Use `BLOCKED` when a required input, evidence, authorization, artifact, upstream Gate, or acceptance condition is missing, contradictory, or unsafe to waive. Residual P0 after the allowed review rounds is always `BLOCKED`.

The Failure Route must name the next owner, required input, and the exact condition that clears the block.

## 5. Gate record

Every execution record and workflow state record must contain:

```yaml
gate: PASS | CONDITIONAL | BLOCKED
allowDownstream: true | false
reason: <short decision rationale>
evidenceRefs: []
decisionRefs: []
nextAction: <explicit action or NONE>
```

Do not invent `FAIL`, `APPROVED`, `FORCED_PASS`, `RELEASED`, or other local Gate values. They may appear only as historical text in a legacy reference.
