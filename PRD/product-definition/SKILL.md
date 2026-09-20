---
name: product-definition
description: 把发现证据转成待用户确认的产品问题、定位、价值、非目标和成功指标。
metadata:
  short-description: 把发现证据转成待用户确认的产品问题、定位、价值、非目标和成功指标。
---

# product-definition

本 Skill 是 PRD Workflow 的原子节点。公共边界见 `../../shared/product-workflow-contract.md`。

## Purpose
在证据基础上提出并记录产品定义候选，明确为谁解决什么问题、为什么现在解决、什么不做以及如何判断成功。

## Trigger
Discovery Brief 和竞争研究可用，或 CHANGE/OPTIMIZE 影响目标用户、核心价值、业务规则或成功指标时触发。

## Inputs
- Discovery Brief；
- Competitive-Analysis research artifact；
- 现有基线、运行数据、约束和技术可行性提示。

## Preconditions
- 核心问题有证据或登记假设；
- 来源和冲突可回溯；
- 候选和确认点分开；
- 技术未知不能写成已实现能力。

## Responsibilities
- 形成问题陈述、目标用户、核心价值和定位候选；
- 明确非目标、成功指标、风险和依赖；
- 将竞品观察转成 Adopt/Adapt/Reject 候选；
- 生成 Definition Decision Record 和确认清单。

## Non-goals
- 不确定功能明细、页面结构或最终技术架构；
- 不把竞品能力自动列为本产品需求；
- 不在无确认时输出 ACCEPTED。

## Procedure
1. 建立证据—推理—候选定义链。
2. 写问题陈述和目标用户，检查能否被场景复述。
3. 写定位、价值、非目标、指标、风险和依赖。
4. 比较产品选项，记录收益、成本、风险和可逆性。
5. 等待责任人确认，批准后才进入 Blueprint。

## Outputs
- `product-definition` artifact；
- 定位/用户/价值/非目标/指标的 decision records；
- 风险、假设和确认记录。

每次执行都必须记录 `executionId`、`skill`、`lifecycle`、`project`、`status`、`gate`、`evidenceRefs`、`artifactRefs`、`decisionRefs` 和 `nextAction`。

## Evidence
Discovery/Research、用户确认、产品指标、约束和技术可行性输入。指标必须有口径、窗口和基线。

## Gate
PASS：关键定义已确认；CONDITIONAL：仅非关键项开放并有期限；BLOCKED：定位、用户、核心价值、非目标或重大风险未确认。

`CONDITIONAL` 必须记录例外、风险、责任人、截止时间、补证动作和 `allowDownstream`。AI 只能提出 Gate，不能替用户批准关键产品决策。

## Failure Route
回 product-discovery 补证；冲突回用户决策；技术问题交 DEV Workflow 的技术发现和 OSS 研究。

评审或澄清最多 3 轮；仍未收敛时保留问题并请求人工裁决，不无限生成。

## Downstream Contract
Application Blueprint 只消费已确认的用户、问题、价值、非目标和约束，不得假设未确认功能或技术方案。

下游必须消费 artifact 和 decisionRefs，不得从聊天上下文补齐未确认结论。

## State Changes
`COMPETITIVE_RESEARCH_READY → PRODUCT_DEFINITION_IN_PROGRESS → PRODUCT_DEFINITION_READY | WORKFLOW_BLOCKED`
