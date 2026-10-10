# Artifact Contract v2

> 适用范围：以下正式产物/Gate/状态契约用于标准、完整及正式交接。低风险独立任务按 `shared/execution-profiles.md` 留最小摘要，不写正式状态、不授予下游权限；已有相关阻塞与安全要求不因轻量而失效。

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

**Baseline binding.** Every downstream artifact registers the artifacts it is built on in `sourceRefs`, and this must include the governing baseline (PRD, prototype, design baseline, upstream technical design). `sourceRefs` is the only link a `SUPERSEDED` baseline can travel on: when a baseline entry becomes `SUPERSEDED`, every artifact citing it is built on a retired baseline, cannot carry a non-blocked Gate that cites it, and is re-judged before any downstream use. Record the exact baseline identity consumed at production time (`artifactId` + `version` + date) in the artifact header or README; "based on PRD v0.2" as loose prose is not a binding. No new manifest field is introduced for this.

**Status vocabulary.** `status` takes only the registered values (`DRAFT | REVIEW | APPROVED | SUPERSEDED`). Business words found in legacy project files are not status values and must not be written into it: `REGISTERED` (logged, not yet reviewed) → `DRAFT`; `READY` (reviewed, awaiting approval) → `REVIEW`, or `APPROVED` only with a matching decision and Gate record; `APPROVED_SUPERSEDED` (approved, then retired) → `SUPERSEDED`, with the approval history carried by `decisionRefs` and the replacement by `supersedes`. A value that claims "approved" and "retired" at once lets downstream read only the first half. Review round counts (`round: n/3`) belong to the Gate record, never to `status`.

## 3. Traceability

Claims that influence delivery must link to source, evidence, and when applicable a decision. `OPEN` and `ASSUMPTION` items must not be silently promoted to `DECISION`.

## 4. Path and scope safety

Artifact paths are relative to the project root, must stay inside the project, and must not contain `..`. Skills must not overwrite unrelated or uncommitted files without explicit authorization.

## 5. Workflow state

`.spec/workflow.yaml` must record `projectId`, `updatedAt`, `state`, `gate`, `allowDownstream`, `artifactRefs`, `evidenceRefs`, `decisionRefs`, and `nextAction`. The state values must come from `governance/state-registry.yaml`.
