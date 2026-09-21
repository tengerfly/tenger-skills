# Legacy Skill Adapter Contract

This boundary wraps historical domain instructions without replacing their procedures.

## Purpose
Make a legacy Skill callable through the current lifecycle, evidence and Gate contracts.

## Trigger
The registry selects a Skill with contractLevel: legacy-adapter.

## Inputs
The original Skill inputs plus a task envelope, project manifest and current workflow state.

## Preconditions
Resolve the canonical registry ID, validate the envelope and read the original SKILL.md.
Do not invent authorization, upstream approvals or evidence.

## Responsibilities
Retain domain behavior; normalize the result into manifest artifacts, evidence and Gate records.

## Non-goals
Do not rewrite historical domain rules, grant production access or bypass review/test gates.

## Procedure
1. Before execution, confirm inputs, path scope and real authorization; do not require unproduced completion evidence.
2. Follow the original Skill procedure within the authorized scope.
3. Register actual outputs and execution/revision-bound evidence, then run scripts/task_preflight.py before proposing the completed transition.
4. Hand the validated proposal to the orchestrator; validation does not execute a Skill.

## Outputs
Manifest artifacts and an explicit result Gate; never a fabricated approval.

## Evidence
Record real file paths, commands, exit codes and the execution/revision they verify.

## Gate
Use only PASS, CONDITIONAL or BLOCKED, as defined by shared/gate-policy.md.
Historical APPROVED/PASSED/RELEASED words are not Gate outcomes.

## Failure Route
Stop on missing input, authorization or evidence. Name the owner, required input and clearance condition.

## Downstream Contract
Pass the envelope, artifacts, evidence, scope, Gate and next state; downstream revalidates them.

## State Changes
Only registered transitions may be proposed. The adapter cannot alter registry rules to force a pass.
