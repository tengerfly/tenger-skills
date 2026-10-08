# WORKFLOW

`WorkFlow/` is the root-level orchestrator. It does not replace domain Skills and does not create product, UI, code, or test artifacts on their behalf.

## Responsibilities

1. identify lifecycle, scope, entry point, and authorized owner;
2. read `.spec/manifest.yaml` and `.spec/workflow.yaml` before routing;
3. select the next domain Skill from the registries;
4. record artifacts, evidence, decisions, Gate, and next action;
5. stop at an explicit boundary and route missing inputs to the named owner.

## Current product route

```text
IDEA_INTAKE
 -> PRODUCT_DISCOVERY
 -> COMPETITIVE_RESEARCH
 -> PRODUCT_DEFINITION
 -> APPLICATION_BLUEPRINT
 -> FEATURE_DECISION
 -> PRD_DESIGN
 -> PRD_REVIEW
 -> PROTOTYPE_DESIGN
 -> PROTOTYPE_REVIEW
```

The numbered legacy pipeline and old `PIPELINE.md` state file remain callable as read-only compatibility inputs. They are wrapped by the current artifact, lifecycle, Gate, and traceability contracts.

## Gate policy

Use only `PASS`, `CONDITIONAL`, and `BLOCKED`.

- `PASS`: required inputs, evidence, decisions, artifacts, and acceptance checks are complete; no unresolved P0/P1 remains.
- `CONDITIONAL`: an authorized exception record is complete and explicitly sets `allowDownstream`.
- `BLOCKED`: required evidence, authorization, upstream Gate, artifact, or safe handoff is missing; residual P0 is always blocked.

After three review-fix-review rounds, do not start a fourth round automatically. Residual P0 is `BLOCKED`; residual P1 is never `PASS` and requires an authorized `CONDITIONAL` if downstream use is approved.

## State and artifacts

The current project state is `.spec/workflow.yaml`. The manifest is `.spec/manifest.yaml`, and traceability is `.spec/traceability.yaml`. Every handoff must include `projectId`, `executionId`, `artifactRefs`, `evidenceRefs`, `decisionRefs`, `gate`, `allowDownstream`, and `nextAction`.

See `SKILL.md` and the contracts in `../shared/` for the complete routing procedure.
