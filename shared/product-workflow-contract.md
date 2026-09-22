# Product Workflow Contract v2

This contract defines the product-domain sequence. It uses the common Skill, artifact, lifecycle, Gate, and anti-deadloop contracts.

## 0. Task scope

先按 `shared/execution-profiles.md` 判定强度。以下为正式产品流程；轻量 Demo/局部需求只确认目标、边界与验收点，不为进入开发重做产品发现、竞品与完整 PRD。轻量摘要不是下列阶段的 APPROVED 产物，也不能解锁已阻塞阶段。标准变更只更新受影响需求与依赖，复用有效基线。所有需求读写遵循 `shared/requirements-context.md`，索引不是第二需求源。

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

## 2.1 单一职责与路由边界

| Skill | 唯一主责 / 产物 | 不在此做 |
|---|---|---|
| prd-workflow | 选阶段、调度、状态展示与 Gate 交接 | 代写任何领域产物 |
| idea-intake | 保存意图、约束、歧义与研究任务 / intake | 用入口两三问完成整个需求确认 |
| product-discovery | 用户任务、问题与使用证据 / discovery-brief | 竞品功能盘点、冻结定位 |
| competitive-analysis | 外部来源、模块全景和功能对比 / research | 选择本产品 MVP、实现路线 |
| product-definition | 用户定位、价值、目标和非目标 | 功能级 Adopt/Reject |
| application-blueprint | 将候选映射成旅程、业务对象、权限和状态规则 | 重新研究竞品、决定功能优先级 |
| feature-decision | 基于候选和蓝图确认功能范围、依赖及取舍 | 重写研究或业务规则 |
| prd-design | 把批准范围/规则写成可测试规格 | 研究、范围批准、独立评审 |
| prd-review | 固定版本只读评审 / 问题与 Gate | 改 PRD、重新定范围 |

同一事实只在所属产物维护，下游引用 ID/版本；缺口回责任节点，不在多个 Skill 重做。change-intake 负责已有项目请求分类，impact-analysis 负责变更影响传播，product-analytics 负责运行指标分析，不替代上表任何产品决策节点。原型负责交互表达，不改变批准范围。

## 2.2 先有全景，再做范围决策

“做一个像某成熟产品一样的应用”、用户不知道整体功能或明确要求找竞品时，不能按两问入口直接写 PRD。产品形态有歧义先澄清；用户不了解功能时由 AI 调研补齐认知，不反复把“还要哪些功能”抛回用户。

研究阶段必须交模块全景与带来源的功能清单（日期、版本/套餐、限制、未知项）；范围阶段先展示全貌，再按模块解释场景、依赖、成本/风险与不做的影响，提供建议，由用户决定 MVP/Later/Reject/Defer。研究事实、AI 建议和用户批准分开记录。

若 Discovery 尚缺信息，可先执行独立竞品补证草稿再回填；不能为了研究伪造上游通过或沿非法边推进正式状态。用户明确要求先研究再深入提问时尊重该次序。

确认深度取决于是否形成可验收的角色、任务主链、数据/权限、正常与异常行为、范围及非目标，而不是问了几题。每轮少量问题只是降低认知负担，不是全流程问题总额；同一问题三轮升级裁决不限制正常模块探索。

正式 PRD 交接须有明确版本的范围表与用户/授权负责人确认引用；默认同意、沉默、只同意研究对象均不算批准。已批准局部迭代可复用相关证据，不重复强制全量研究；任何跳过须展示覆盖依据与失效检查。

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
