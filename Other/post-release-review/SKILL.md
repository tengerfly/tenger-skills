---
name: post-release-review
description: 比较发布前假设与发布后结果，决定继续、扩大、回滚、再迭代或关闭。
metadata:
  short-description: 比较发布前假设与发布后结果，决定继续、扩大、回滚、再迭代或关闭。
---

# post-release-review

## Purpose
把发布结果和原始目标、保护指标、用户行为、事故与缺陷证据闭环，形成下一轮决策。

## Trigger
发布观察窗口结束、事故恢复、实验结束或用户要求复盘。

## Inputs
release-verification、产品/技术目标、前后基线、运行信号、缺陷/事故、用户反馈和决策记录。

## Preconditions
版本、时间窗口和指标口径可关联；未关联的结论必须标 OPEN。

## Responsibilities
比较假设与结果、判断偏差、登记未关闭风险、推荐继续/扩大/回滚/再迭代/关闭并回写知识资产。

## Non-goals
不在复盘中直接改生产；不把单次成功/失败夸大为长期结论；不沉淀客户机密。

## Procedure
1. 复核发布范围、目标、保护指标和观察窗口。
2. 对比结果、异常、事故、缺陷、用户行为和成本。
3. 区分已证实结果、推断、替代解释和数据缺口。
4. 输出决策与下一任务；将重复问题去敏后写入项目基线/bug-patterns/Skill 优化。
5. 更新 traceability 和 release 状态。

## Outputs
`.spec/release/<release-id>/post-release-review.md`、前后对比、结论、未关闭风险和下一步。

## Evidence
版本/commit、指标/日志、关键旅程、事故时间线、用户反馈、测试与发布记录。

## Gate
PASS：结果和后续决策有证据；CONDITIONAL：关键数据延迟/缺失但限制已写明；BLOCKED：无法关联版本、指标或影响。

## Failure Route
新事故转 incident-response；功能偏差转 defect-triage；优化机会转 optimization-planning；过程缺陷转 Skill-Optimizer。

## Downstream Contract
下一轮任务收到结果、证据、未决风险、假设修正和资产沉淀建议。

## State Changes
`RELEASE_VERIFIED → OPERATIONS_OBSERVED → POST_RELEASE_REVIEWED → COMPLETED | CHANGE_ROUTED | DEFECT_ROUTED | OPTIMIZATION_PLANNING_IN_PROGRESS`