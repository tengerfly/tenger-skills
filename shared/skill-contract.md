# Skill Contract v2

This is the common execution contract for every active Skill and legacy wrapper.

## 1. Precedence

When instructions conflict, apply this order:

1. `shared/` contracts;
2. `governance/` registries and schemas;
3. the current Skill `SKILL.md`;
4. the Skill's references and assets;
5. historical or legacy material, which is read-only compatibility input.

A local Skill must not redefine Gate values, lifecycle states, evidence labels, or the current state source.

## 2. SKILL.md frontmatter

```yaml
---
name: example-skill
description: One sentence describing the trigger and responsibility.
metadata:
  contract-level: v2 | legacy-wrapper
  legacy-alias: null
---
```

`name` is lowercase kebab-case. The entry file is always named `SKILL.md`. Historical names belong in `metadata.legacy-alias`, not in the active `name`.

## 3. Required sections

Every entry Skill contains these headings:

`Purpose`, `Trigger`, `Inputs`, `Preconditions`, `Responsibilities`, `Non-goals`, `Procedure`, `Outputs`, `Evidence`, `Gate`, `Failure Route`, `Downstream Contract`, `State Changes`.

`Procedure` must describe one deterministic path. If an input is missing, route to `Failure Route`; do not invent a second, incompatible process.

## 4. Evidence labels

Use the following labels consistently:

| Label | Meaning | Rule |
|---|---|---|
| `FACT` | Directly observed or explicitly supplied | Preserve source location |
| `EVIDENCE` | A verifiable observation or test result | Link `evidenceRef` |
| `INFERENCE` | Reasoned conclusion from evidence | Show the reasoning boundary |
| `ASSUMPTION` | Temporary premise not yet verified | Mark as open |
| `RECOMMENDATION` | Suggested option | Not an approval |
| `DECISION` | Accepted direction by the user or authorized owner | Link `decisionRef` |
| `OPEN` | Unresolved question or missing input | Must have an owner or Failure Route |

## 5. Execution record

Use `projectId`, never a new local alias such as `project`:

```yaml
execution:
  executionId: EXE-YYYYMMDD-001
  skill: <governance skill id>
  lifecycle: CREATE | CHANGE | DEFECT | REFACTOR | INCIDENT | OPTIMIZE
  projectId: <project-id>
  status: COMPLETED | PARTIAL | BLOCKED
  gate: PASS | CONDITIONAL | BLOCKED
  evidenceRefs: []
  artifactRefs: []
  decisionRefs: []
  nextAction: <explicit action or NONE>
```

## 6. Gate and state rules

Use only `PASS`, `CONDITIONAL`, and `BLOCKED`. Follow `shared/gate-policy.md` and `shared/anti-deadloop.md`; do not create local exceptions. The current state source is `.spec/workflow.yaml`. `.spec/PIPELINE.md` and `.spec/WORKFLOW.yaml` are read-only legacy inputs.

## 7. Wrapper compatibility

A `legacy-wrapper` may retain old references and assets, but it must:

- expose the common sections and contract;
- translate old outputs into the current artifact, evidence, and Gate vocabulary;
- prevent legacy text from overriding the shared contracts;
- keep historical material clearly marked as legacy.
