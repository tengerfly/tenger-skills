# tenger-skills

A modular Skill repository for product discovery, PRD, UI, development, testing, release, operations, and Skill optimization.

## Repository layout

```text
PRD/       product discovery, decisions, PRD, and prototype workflow
UI/        prototype, UI/UX, and fidelity work
DEV/       technical design, implementation, and code review
Test/      automated and manual testing
Other/     defects, OSS research, release/operations, and Skill meta-work
WorkFlow/  root-level orchestration only
shared/    common contracts, templates, and evidence rules
governance/ registries and schemas
```

Every Skill entry point is named `SKILL.md`. Folder names identify the domain; compatibility aliases remain in registries and frontmatter where needed.

## Current product workflow

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

All Skills and Workflows use the same rules:

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
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-skill-contract.ps1 -IncludeLegacy
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-system.ps1
```

The validators check frontmatter, required Skill sections, registry paths, workflow transitions, artifact manifests, and traceability fixtures.
