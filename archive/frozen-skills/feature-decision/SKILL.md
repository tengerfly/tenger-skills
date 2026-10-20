---
name: feature-decision
description: 向用户解释功能全景并逐模块确认 MVP/Later/Reject/Defer、依赖和范围边界；不做竞品研究、不设计业务状态或编写 PRD。触发：功能取舍、MVP 范围、优先级、做什么不做什么、版本范围确认。
metadata:
  short-description: 基于产品蓝图对候选功能做价值、成本、风险和依赖取舍，冻结 MVP 与行为边界。
---

# feature-decision

本 Skill 是 PRD Workflow 的原子节点。公共边界见 `../../shared/product-workflow-contract.md`。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
把候选能力转成可追踪的 MVP/Later/Reject/Defer 决策，明确 MVP、后续范围、不可变行为和验收边界。若用 Adopt/Adapt 或 MoSCoW 讨论，落入决策表前统一映射为 MVP/Later/Reject/Defer（Adopt→MVP、Adapt→MVP/Later、Defer→Defer、Reject→Reject；Must→MVP、Should→MVP/Later、Could→Later、Won’t→Reject）。

## Trigger
`application-blueprint` 已准备，或 CHANGE/OPTIMIZE 调整功能范围、MVP、优先级、依赖或保护指标时触发。

## Inputs
- `application-blueprint`；
- `product-definition` 和研究证据；
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
- 产出 MVP/Later/Reject/Defer（Adopt/Adapt、MoSCoW 等框架结论先按 Purpose 的映射表归一到该枚举）；
- 引用蓝图中的规则，确认选入范围的不可变行为、验收边界、保护指标和不做项；
- 生成用户确认的 Feature Decision Record。

## Non-goals
- 不替用户决定商业优先级、预算或重大取舍；
- 不把技术研究直接当产品授权；
- 不写完整 PRD、视觉或代码。

## Procedure
1. 引用 research 的模块全景/功能 ID 与蓝图映射，合并有来源的补充候选；不从用户随口提到的单点反推整个产品范围。
2. 先展示整个能力地图，再逐模块解释“做什么、解决什么、依赖什么、不做会怎样”；给出范围建议及理由，不能只问“还有什么需求”。
3. 用决策表记录：功能 ID、用户场景/价值、候选实现边界、依赖、成本/风险（估算注明）、AI 建议、用户选择、确认引用。选择统一用 MVP/Later/Reject/Defer；未答复为 OPEN，不默认同意。
4. 每轮聚焦少量有关联的决策，按用户理解程度深入；用户不知道时给案例、差异和可选方案。用户可一次确认一组明确列出的功能及版本，不必逐条点头。
5. 引用蓝图的规则，只确认本次纳入哪些行为/权限/异常边界；发现规则不清回 application-blueprint，不在这里重复设计状态机。检查选入功能的依赖与主链，删减导致断链则提出选择，不能自动扩大范围。
6. 展示最终 MVP/Later/Reject/Defer 表、未决项、范围外内容及验收边界，请用户或授权负责人明确确认版本；沉默、“继续研究”或同意竞品名单不等于范围批准。
7. 只有已批准范围可交 `prd-design`。尚未决定的模块继续探索或由用户明确延期；缺关键确认即停，不用评审轮次上限强行定稿。

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

同一阻塞点反复 3 轮未收敛则请求裁决；新场景、新证据和不同问题可继续探索，不把三轮理解为整个 PRD 的访谈上限。不得为结束对话把 OPEN 改为已确认。

## Downstream Contract
`prd-design` 只能写 APPROVED 的范围、行为、验收边界和不做项；`prototype-design` 不能超出批准范围。

下游必须消费 artifact 和 decisionRefs，不得从聊天上下文补齐未确认结论。

## State Changes
`APPLICATION_BLUEPRINT_READY → FEATURE_DECISION_IN_PROGRESS → FEATURE_DECISION_READY | WORKFLOW_BLOCKED`
