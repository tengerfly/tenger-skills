---
name: signal-triage
description: 对运行信号去重、分级和路由到事故、缺陷、变更或优化。
metadata:
  short-description: 对运行信号去重、分级和路由到事故、缺陷、变更或优化。
---

# signal-triage

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
将运行信号转成正确的工程入口，避免所有问题都变成 Bug 或所有异常都被当成噪声。

## Trigger
收到 signal-collection 信号包、告警、用户反馈或发布验证异常。

## Inputs
信号包、发布版本、基线、影响指标、已知事件和运行上下文。

## Preconditions
信号来源和时间窗口明确；先判断 P0/P1；保护敏感数据和生产权限。

## Responsibilities
聚合、影响评估、分类 INCIDENT/DEFECT/CHANGE/OPTIMIZE/NOISE/OBSERVABILITY_GAP，建立路由和证据。

## Non-goals
不直接修复、不未经批准调整告警阈值、不用相关性宣称根因。

## Procedure
1. 关联 releaseId/commit/trace/request/session 并去重。
2. 对比发布前基线和保护指标，估计影响范围。
3. 分级 P0-P3，优先事故止损。
4. 输出候选原因、最小下一步、负责人和验证条件。
5. 更新 traceability，把信号路由至 incident/defect/change/optimization。

## Outputs
`.spec/triage/<id>.md`、信号分组、分级、路由任务、证据和后续观察条件。

## Evidence
信号原始引用、基线对比、版本关联、告警/日志/指标和用户影响。

## Gate
PASS：分级和路由有证据；CONDITIONAL：关联或采样有明确限制；BLOCKED：无法判断影响或关键生产信号不可信。

## Failure Route
P0/P1 转 incident-response；行为偏差转 defect-triage；指标机会转 product-analytics 或 optimization-planning；关联缺失转 `signal-collection` 补采集并登记 `OBSERVABILITY_GAP`。

## Downstream Contract
下游收到信号、影响、优先级、路由、不可作出的结论和验证条件。

## State Changes
`SIGNALS_COLLECTED → SIGNAL_TRIAGE_IN_PROGRESS → SIGNAL_ROUTED | INCIDENT_ROUTED | WORKFLOW_BLOCKED`