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
 -> UI_UX_DESIGN
 -> UI_UX_REVIEW
```

A stage may be skipped only when an existing manifest artifact, evidence, decision, and upstream Gate prove equivalent coverage. Chat context alone is not coverage.

`UI_UX_DESIGN`/`UI_UX_REVIEW` 由 `ui-workflow`（`ui-ux-design` → `ui-ux-review`）承担，列在本序列是因为它们是该序列的**必经后置**，不是因为产品 Skill 代做视觉稿：设计稿是 `frontend-tech-design` 的视觉基准输入，也是 `fidelity-review` 的唯一比对源。

**禁止的直连边**：`PROTOTYPE_REVIEW → TECH_DESIGN`、`PRD_APPROVED → TECH_DESIGN`、`INTAKE_READY → TECH_DESIGN`（CREATE 生命周期）都不是合法推进路线。注册状态图中进入 `TECH_DESIGN_IN_PROGRESS` 的 CREATE 合法前驱是 `UI_APPROVED`；确有理由不出视觉稿时，只能作为**经用户批准的例外**登记（见 §5.1），不得由执行方以「本批不涉及视觉」「缺省回退原型」自行降级。

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
- `UI_UX_DESIGN`: 把批准的原型转成视觉与交互设计稿（`.spec/设计稿/` + `design-system.md` token 源）。
- `UI_UX_REVIEW`: 对设计稿做独立四维复审（载体结构零改动、文案字段一致、视觉规范出处、真实渲染可交付）。

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
| ui-ux-design | 把批准原型转成视觉与交互设计稿 / `.spec/设计稿/` + design-system | 改批准范围或原型结构、定技术选型、替用户批准风格方案 |
| ui-ux-review | 设计稿独立四维复审 / 问题与 Gate | 改稿、补画缺失页面、重新定视觉规范 |

同一事实只在所属产物维护，下游引用 ID/版本；缺口回责任节点，不在多个 Skill 重做。change-intake 负责已有项目请求分类，impact-analysis 负责变更影响传播，product-analytics 负责运行指标分析，不替代上表任何产品决策节点。原型负责交互表达，不改变批准范围。

## 2.2 先有全景，再做范围决策

“做一个像某成熟产品一样的应用”、用户不知道整体功能或明确要求找竞品时，不能按两问入口直接写 PRD。产品形态有歧义先澄清；用户不了解功能时由 AI 调研补齐认知，不反复把“还要哪些功能”抛回用户。

研究阶段必须交模块全景与带来源的功能清单（日期、版本/套餐、限制、未知项）；范围阶段先展示全貌，再按模块解释场景、依赖、成本/风险与不做的影响，提供建议，由用户决定 MVP/Later/Reject/Defer。研究事实、AI 建议和用户批准分开记录。全景与功能清单的**裁剪依据必须声明**来自哪一条用户确认（需求方向、指定竞品、限定形态或明示授权），否则不得自行划定研究范围并投入资源。

三条硬门禁（可执行判据，非叙述性要求）：

1. **确认先于投入**：大范围研究、选型展开与代码实现属高成本动作，准入前提是被用户确认并登记为 `ACCEPTED` 的需求方向；该方向未确认前只允许零成本意图澄清，不得以「并行不空等」为由提前开跑。次序是「陈述 AI 理解的需求方向 → 用户改写确认 → 决定是否调研」。
2. **提问合法性**：只允许提出**只有用户能回答**的题——意图、偏好、优先级、不可逆约束与内部事实。凡可通过公开资料、竞品现状、既有代码或常识推断得到答案的题，一律转为研究任务，不得提问；每轮题数上限只是降低认知负担的附带约束，不构成合规证明。
3. **研究未回传即冻结其下游题目**：处于 `RESEARCH_RUNNING`/`OPEN` 且答案依赖该研究的条目，在其回传并整理成用户可见产物之前，不得作为向用户提问的内容；等待期间本轮只交付「已登记事实 + 当前在等什么 + 回来后给你什么」，不追加索取。用户可见顺序须与研究交付顺序一致。

若 Discovery 尚缺信息，可先执行独立竞品补证草稿再回填；不能为了研究伪造上游通过或沿非法边推进正式状态。用户明确要求先研究再深入提问时尊重该次序。

确认深度取决于是否形成可验收的角色、任务主链、数据/权限、正常与异常行为、范围及非目标，而不是问了几题。每轮少量问题只是降低认知负担，不是全流程问题总额；同一问题三轮升级裁决不限制正常模块探索。

正式 PRD 交接须有明确版本的范围表与用户/授权负责人确认引用；默认同意、沉默、只同意研究对象均不算批准。已批准局部迭代可复用相关证据，不重复强制全量研究；任何跳过须展示覆盖依据与失效检查。

## 3. Decision boundary

Research can produce `EVIDENCE` and `RECOMMENDATION`; it cannot create a product `DECISION`. Only the user or an authorized owner can approve positioning, scope, MVP, risk acceptance, or exceptions.

## 4. Product artifact contract

产品产物的 manifest 条目与 `shared/artifact-contract.md` §2、`governance/schemas/artifact-manifest.schema.yaml` 完全同构（字段名与必填项以那两个文件为准，本节只说明产品域用法）：

```yaml
artifactId: ART-YYYYMMDD-001          # 产品域常用 PROD- 前缀，但登记键名固定为 artifactId
type: discovery-brief | research | product-definition | application-blueprint | journey-map | feature-decision | scope-decision | prd | prototype | prototype-review
path: .spec/<阶段目录>/<文件>
lifecycle: CREATE | CHANGE | OPTIMIZE   # 产品阶段常用值；完整枚举见 artifact-contract
owner: <user-or-agent>
status: DRAFT | REVIEW | APPROVED | SUPERSEDED
sourceRefs: []
evidenceRefs: []
decisionRefs: []
producedBy: <registry-skill-id>
producedAt: <ISO-8601-with-offset>
supersedes: null
```

- `type` 的完整枚举与逐型 required 以 `governance/artifact-registry.yaml` 为唯一源（含 `journey-map`、`scope-decision`）；表中未列的产品域新类型必须先登记注册表再使用。
- `gate` / `allowDownstream` / `openItems` 不写进 manifest：Gate 与放行记在 `.spec/workflow.yaml` 与 `.spec/gates/`；开放项记 workflow.yaml 或 `.spec/decisions/`。把 Gate 写进产物条目会让下游把「文件存在」误读成「已放行」。

## 5. Handoff rule

The next stage consumes only manifest entries whose status and Gate allow downstream use. Missing or conflicting input routes to the named upstream stage; it does not get filled by an unstated assumption.

## 5.1 视觉基线缺失须登记例外（禁止静默降级）

任何下游产物（FTDD、代码评审、还原度评审、测试报告）的输入基线里出现「设计稿：无」「本批不涉及视觉」「缺省回退低保真原型」「视觉基准回退原型」等字样时，必须同时具备一条已登记的例外（EXC）：例外 ID、用户批准出处、缺失原因、影响范围与补偿验证方式，并写入 `.spec/decisions/` 与 manifest 引用。

没有该例外时，Gate 只能是 `BLOCKED`——不得以 `PASS`/`CONDITIONAL` 放行，也不得把缺失写成批次说明（如「⑩-前 未产出」）后继续推进。静默回退是让上游漏点无感传到开发期的通道。
