# Product Workflow Contract v2

This contract defines the product-domain sequence. It uses the common Skill, artifact, lifecycle, Gate, and anti-deadloop contracts.

## 1. Product sequence

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

A stage may be skipped only when an existing manifest artifact, evidence, decision, and upstream Gate prove equivalent coverage. Chat context alone is not coverage.

## 2. Stage responsibilities

- `IDEA_INTAKE`: normalize the request, actor, scope, and unknowns.
- `PRODUCT_DISCOVERY`: establish user/problem evidence and hypotheses.
- `COMPETITIVE_RESEARCH`: collect dated, source-linked external evidence.
- `PRODUCT_DEFINITION`: define target users, value, goals, and non-goals.
- `APPLICATION_BLUEPRINT`: define business flows, objects, states, permissions, and boundaries.
- `FEATURE_DECISION`: decide MVP scope, priorities, exclusions, and trade-offs.
- `PRD_DESIGN`: write a testable product specification from approved inputs.
- `PRD_REVIEW`: independently check completeness, consistency, and measurability.
- `PROTOTYPE_DESIGN`: turn approved requirements into an interaction prototype.
- `PROTOTYPE_REVIEW`: verify coverage, copy, states, and interaction closure.

## 3. Decision boundary

Research can produce `EVIDENCE` and `RECOMMENDATION`; it cannot create a product `DECISION`. Only the user or an authorized owner can approve positioning, scope, MVP, risk acceptance, or exceptions.

## 4. Product artifact contract

```yaml
artifactId: PROD-YYYYMMDD-001
kind: intake | discovery-brief | research | product-definition | application-blueprint | feature-decision | prd | prototype
projectId: <project-id>
lifecycle: CREATE | CHANGE | OPTIMIZE
status: DRAFT | REVIEW | APPROVED | SUPERSEDED
sourceRefs: []
evidenceRefs: []
decisionRefs: []
openItems: []
gate: PASS | CONDITIONAL | BLOCKED
allowDownstream: true | false
```

## 5. Handoff rule

The next stage consumes only manifest entries whose status and Gate allow downstream use. Missing or conflicting input routes to the named upstream stage; it does not get filled by an unstated assumption.
