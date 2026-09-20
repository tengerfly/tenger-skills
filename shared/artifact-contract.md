# Artifact Contract v2

## 1. Project control files

The current project control directory is:

```text
.spec/
  workflow.yaml       # current lifecycle, state, Gate, next action
  manifest.yaml       # artifact inventory
  traceability.yaml   # source/evidence/decision links
  decisions/          # approved decisions
  evidence/           # verifiable evidence
  gates/              # Gate records
```

`.spec/PIPELINE.md` and `.spec/WORKFLOW.yaml` are read-only legacy inputs. They must not be written as the current state source.

## 2. Manifest entry

Every material artifact has a stable manifest entry:

```yaml
projectId: <project-id>
artifacts:
  - artifactId: ART-YYYYMMDD-001
    type: prd
    path: .spec/PRD/V1/PRD.md
    lifecycle: CREATE
    owner: user-or-agent
    status: DRAFT | REVIEW | APPROVED | SUPERSEDED
    sourceRefs: []
    evidenceRefs: []
    decisionRefs: []
    producedBy: prd-design
    producedAt: 2026-09-20T12:00:00+08:00
    supersedes: null
```

An artifact is not approved merely because its file exists. `APPROVED` requires a matching decision and Gate record.

## 3. Traceability

Claims that influence delivery must link to source, evidence, and when applicable a decision. `OPEN` and `ASSUMPTION` items must not be silently promoted to `DECISION`.

## 4. Path and scope safety

Artifact paths are relative to the project root, must stay inside the project, and must not contain `..`. Skills must not overwrite unrelated or uncommitted files without explicit authorization.

## 5. Workflow state

`.spec/workflow.yaml` must record `projectId`, `updatedAt`, `state`, `gate`, `allowDownstream`, `artifactRefs`, `evidenceRefs`, `decisionRefs`, and `nextAction`. The state values must come from `governance/state-registry.yaml`.
