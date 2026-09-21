---
name: product-analytics
description: 用产品目标、用户旅程和行为数据判断功能效果、异常和证据不足。
metadata:
  short-description: 用产品目标、用户旅程和行为数据判断功能效果、异常和证据不足。
---

# product-analytics

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
把发布后用户行为和业务指标转成可验证的产品结论，不把相关性直接当因果。

## Trigger
发布观察、优化请求、功能复盘、流失/转化异常或用户旅程问题。

## Inputs
产品目标、事件字典、实验/发布版本、用户旅程、指标基线、时间窗口和数据质量说明。

## Preconditions
指标定义、口径、样本、隐私和版本切分明确；没有数据时标 OPEN。

## Responsibilities
检查数据质量、按版本/环境/人群对比、识别趋势/异常/证据不足、提出可验证优化候选。

## Non-goals
不直接改产品、不伪造因果、不将小样本异常当确定趋势。

## Procedure
1. 核对指标定义、事件覆盖、采样和时间窗口。
2. 比较发布前后、版本间和关键旅程漏斗。
3. 区分事实、推断、替代解释和待验证假设。
4. 生成候选优化、保护指标和验证计划。
5. 交给 optimization-planning 或 change/defect 路由。

## Outputs
`.spec/analytics/<id>.md`、指标质量、基线对比、结论标签、优化候选和数据缺口。

## Evidence
查询/报表引用、事件字典、版本切分、样本范围、统计方法和隐私检查。

## Gate
PASS：口径和结论可复核；CONDITIONAL：数据缺口已声明且不影响有限结论；BLOCKED：指标口径不一致、样本不可信或无授权。

## Failure Route
埋点/关联缺失转 Observability-Design；行为偏差转 defect-triage；策略改变转 change-intake；数据风险转 incident-response。

## Downstream Contract
下游收到指标基线、假设、保护指标、样本限制和验证计划，不得把建议当批准需求。

## State Changes
`SIGNALS_COLLECTED → ANALYTICS_IN_PROGRESS → ANALYTICS_READY | WORKFLOW_BLOCKED`