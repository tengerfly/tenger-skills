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

## 6. Gate enforcement

A Gate is an execution precondition, not a log entry. Rules 1-3 are enforced before work starts, not after it is delivered.

1. **Read upstream before starting.** Before any Skill runs or any formal state transition, read the manifest entries and Gate records it depends on: `status`, `version`, `gate`, `allowDownstream`, `blockedBy`.
2. **Closed means closed.** If any upstream entry is `SUPERSEDED`, carries a `gate` other than `PASS`, or carries `allowDownstream: false`, the dependent work does not start. Record a block item naming `owner`, `requiredInput`, and `clearCondition`, and point `nextAction` at that owner.
3. **No pointer may sit past a closed upstream.** `currentState` and `nextAction` cannot reference a stage downstream of an open block. Stay at the blocked point using a registered blocked state (for example `WORKFLOW_BLOCKED`); "finish the downstream work while the upstream catches up" is not a valid order, and a new state value is not required to enforce this.
4. **Scope limits live in fields, never in comments.** `gate`, `allowDownstream`, and `blockedBy` carry the decision; prose and YAML comments only explain it. A qualifier written in a comment does not narrow a `PASS`, and `allowDownstream: true` never coexists with a superseded or unapproved baseline. Closing a review round on a retired baseline is `BLOCKED`, recorded as such, with the closed-criteria result kept as a separate fact.
5. **Superseding a baseline triggers a sunk-work inventory.** When a decision retires an approved baseline, the same step lists every downstream artifact built on it and states each one's disposition (rewrite, incremental update, or discard). Discovery is not deferred to the next stage.
6. **Field checks prove authorization, digests prove content.** Rules 1-2 read ledger fields, so an artifact whose body was edited after approval while `status`/`version`/`gate` stayed untouched passes every field check. Every `APPROVED` artifact therefore carries `contentDigest`, and review evidence carries `subjectDigests`; both are written by tooling and recomputed against the bytes on disk by `validate_core.py gate`/`artifact`. A mismatch means the reviewed baseline no longer exists: the round's findings are void for the drifted inputs and must be re-run, and re-signing a digest is only valid with an approval covering that edit. Measured on one real project, field checks alone missed 73% of drifted evidence pairs.
7. **Every formal handoff leaves two run-log events.** Before a Skill starts it records `tsr node-start`, and when it hands off it records `tsr node-end --gate … --allow-downstream … --artifact …`; the tool stamps the clock, the sequence number and the artifact digests, so a hand-off cannot be back-dated or described more favourably than the bytes support. `verify` re-derives these from disk and fails the handoff when an approved body drifted afterwards, when a `node-end` has no matching start, or when a `PASS` with `allowDownstream: true` sits over a closed upstream. Review rounds must carry `round` and `batch` — they are the denominator of every rework metric.
