---
name: optimization-planning
description: 把可信的运行/产品证据转成有基线、收益、保护指标和验证计划的优化变更。
metadata:
  short-description: 把可信的运行/产品证据转成有基线、收益、保护指标和验证计划的优化变更。
---

# optimization-planning

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
让性能、成本、转化、可用性或体验优化成为可回滚、可衡量的工程任务。

## Trigger
product-analytics、巡检、运行信号或用户反馈发现优化机会。

## Inputs
指标分析、当前基线、目标、候选方案、成本/风险、实验能力和发布约束。

## Preconditions
优化目标可量化；保护指标和停止条件明确；不把缺陷掩盖成优化；技术方案需做 OSS 研究。

## Responsibilities
排序候选、定义变更边界、收益假设、实验/发布策略、保护指标、回滚和复盘条件。

## Non-goals
不直接实施、不降低安全/正确性换取单一指标、不从无证据的偏好发起大改。

## Procedure
1. 记录当前基线、样本、版本和指标质量。
2. 判断候选是否其实是 defect/incident/change。
3. 生成方案对比，必要时查 GitHub 同域实现并核验许可证。
4. 定义预期收益、保护指标、最小批次、实验/灰度和回滚。
5. 委托 impact-analysis、技术设计、开发及 auto-test，并记录追踪链。
6. 发布后通过 post-release-review 比较实际结果。

## Outputs
`.spec/optimization/<id>.md`、优化任务卡、基线/目标/保护指标、方案决策和验证计划。

## Evidence
指标前后基线、数据质量、成本/性能测量、源码研究、用户/负责人确认和回滚能力。

## Gate
PASS：收益假设、保护指标和验证可执行；CONDITIONAL：小范围试验且风险已限制；BLOCKED：无可信基线、保护指标或授权。

## Failure Route
行为错误转 defect-triage；事故转 incident-response；外部产品改变转 change-intake；技术方案不明转 Tech-Design；数据不足转 product-analytics。

## Downstream Contract
实施方收到目标、基线、保护指标、变更边界、实验/发布、回滚和停止条件，不得以“优化”为由省略测试和发布验证。

## State Changes
`ANALYTICS_READY → OPTIMIZATION_PLANNING_IN_PROGRESS → CHANGE_ROUTED | DEV_IN_PROGRESS | WORKFLOW_BLOCKED`