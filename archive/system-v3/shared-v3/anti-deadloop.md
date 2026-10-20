# Anti-Deadloop v2

This contract prevents endless review-fix-review loops while preserving safety and user control.

## 1. Required issue fields

Every review or verification issue must have:

- a stable `issueId`;
- severity `P0`, `P1`, `P2`, or `P3`;
- source location and evidence references;
- a concrete repair criterion;
- an accountable owner;
- a state such as `OPEN`, `CONFIRMED`, `FIXED`, `WAIVED`, or `REJECTED`;
- the round in which it was found and the round in which it was verified.

A verbal statement such as "fixed" is not evidence.

## 2. Review round protocol

1. Freeze the current issue list before repair.
2. Ask the user or authorized owner to confirm, waive, or reject each actionable issue.
3. The responsible Skill repairs only confirmed items and records the change.
4. Re-review only the current round's confirmed items; new findings are recorded separately.
5. Record evidence, Gate, residual issues, and the next action in `.spec/workflow.yaml` and the execution record.

## 3. Maximum rounds and residual issues

The same issue batch has a maximum of three repair-review rounds. After round 3:

- residual P0 => `BLOCKED`;
- residual P1 => never `PASS`; it may become `CONDITIONAL` only with the complete authorized exception record from `shared/gate-policy.md`;
- residual P2/P3 => may remain open if impact and owner are recorded;
- no automatic fourth round;
- never use "force pass", "clear P0 then pass", or "leave P1 as legacy" as a Gate rule.

A new scope, new evidence, or a changed decision starts a new execution rather than silently extending the old loop.

## 4. Bidirectional learning

When an issue is confirmed as a repeatable pattern:

- add a prevention rule to the producing Skill;
- add a detection rule to the reviewing Skill's known-issue pattern library;
- link both changes to the original `issueId` and evidence.

Learning changes the Skills, not the current Gate outcome.

## 5. Source of truth

Use `shared/gate-policy.md` for Gate meaning, this file for loop control, and `.spec/workflow.yaml` for current execution state. Legacy pipeline files are read-only compatibility inputs.
