---
name: feature-decision
description: 基于产品蓝图对候选功能做价值、成本、风险和依赖取舍，冻结 MVP 与行为边界。
metadata:
  short-description: 基于产品蓝图对候选功能做价值、成本、风险和依赖取舍，冻结 MVP 与行为边界。
---

# feature-decision

本 Skill 是 PRD Workflow 的原子节点。公共边界见 `../../shared/product-workflow-contract.md`。

## Purpose
把候选能力转成可追踪的 Adopt/Adapt/Reject/Defer 与 Must/Should/Could/Won’t 决策，明确 MVP、后续范围、不可变行为和验收边界。

## Trigger
Application Blueprint 已准备，或 CHANGE/OPTIMIZE 调整功能范围、MVP、优先级、依赖或保护指标时触发。

## Inputs
- Application Blueprint；
- Product Definition 和研究证据；
- 候选功能、价值、成本、风险、依赖估计；
- 预算、时间、合规和发布约束。

## Preconditions
- 候选功能有问题/旅程来源；
- 成本和技术未知标估算或 OPEN；
- 重大架构问题先执行 GitHub/OSS 研究；
- 决策人明确。

## Responsibilities
- 建立功能卡和评价维度；
- 比较价值、频率、成本、风险、依赖、可逆性和验证成本；
- 产出 MVP/Later/Reject/Defer 与 Must/Should/Could/Won’t；
- 记录不可变行为、验收边界、保护指标和不做项；
- 生成用户确认的 Feature Decision Record。

## Non-goals
- 不替用户决定商业优先级、预算或重大取舍；
- 不把技术研究直接当产品授权；
- 不写完整 PRD、视觉或代码。

## Procedure
1. 从蓝图生成并去重候选功能。
2. 记录价值、证据、成本/风险/依赖、可逆性和验证方式。
3. 比较范围方案，明确 MVP 与 Later 边界。
4. 写关键行为、权限、状态、异常和验收边界。
5. 等待确认，未确认项保持 PROPOSED/OPEN。
6. 通过 Gate 后交 PRD-Design。

## Outputs
- `feature-decision` artifact；
- `scope-decision` 和 decision records；
- MVP/Later/Reject/Defer 表、行为边界和验收边界。

每次执行都必须记录 `executionId`、`skill`、`lifecycle`、`project`、`status`、`gate`、`evidenceRefs`、`artifactRefs`、`decisionRefs` 和 `nextAction`。

## Evidence
问题/旅程证据、产品定义、蓝图、用户确认、成本估算、依赖和 GitHub/OSS 研究记录。

## Gate
PASS：MVP、范围、关键行为和不做项已确认；CONDITIONAL：低风险项开放且不影响下游；BLOCKED：关键范围、预算、商业或架构取舍未确认。

`CONDITIONAL` 必须记录例外、风险、责任人、截止时间、补证动作和 `allowDownstream`。AI 只能提出 Gate，不能替用户批准关键产品决策。

## Failure Route
来源不足回 Blueprint/Discovery；定位变化回 product-definition；技术不确定交 DEV Workflow；评审发现范围问题回本 Skill。

评审或澄清最多 3 轮；仍未收敛时保留问题并请求人工裁决，不无限生成。

## Downstream Contract
PRD-Design 只能写 APPROVED 的范围、行为、验收边界和不做项；Prototype 不能超出批准范围。

下游必须消费 artifact 和 decisionRefs，不得从聊天上下文补齐未确认结论。

## State Changes
`APPLICATION_BLUEPRINT_READY → FEATURE_DECISION_IN_PROGRESS → FEATURE_DECISION_READY | WORKFLOW_BLOCKED`
