---
name: signal-collection
description: 从前端监控、服务日志、服务监控和产品数据收集可关联、可脱敏的运行信号。
metadata:
  short-description: 从前端监控、服务日志、服务监控和产品数据收集可关联、可脱敏的运行信号。
---

# signal-collection

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
把运行信号标准化为带版本、环境和关联 ID 的证据，为分诊和产品分析提供可靠输入。

## Trigger
发布后观察、定时采集、告警/用户反馈或优化分析请求。

## Inputs
web-monitor、server-log、server-monitor、产品分析导出及其接口/权限说明。

## Preconditions
只读取授权范围；敏感数据脱敏；无法关联的信号标 OPEN；不伪造缺失指标。

## Responsibilities
采集、标准化、去重、时间对齐、关联 projectId/environment/appVersion/releaseId/commitSha/traceId/requestId/sessionId/eventId，记录来源和缺口。

## Non-goals
不分诊根因、不改生产、不将采样数据外推为全量事实。

## Procedure
1. 记录采集窗口、来源、查询条件和权限。
2. 按统一关联键归一字段和时间。
3. 去重相同事件并保留原始引用。
4. 分为错误、性能、可用性、用户行为、安全和资源信号。
5. 输出信号包和质量说明，交给 `signal-triage` / `product-analytics`（按用途择一）。

## Outputs
`.spec/signals/<window>/signal-pack.md`、脱敏索引、关联质量和采集缺口。

## Evidence
来源查询、导出摘要、字段映射、时间窗口、采样说明和权限记录。

## Gate
PASS：来源、窗口、关联和脱敏可复核；CONDITIONAL：已声明采样/关联缺口；BLOCKED：无权限、数据不可解读或敏感信息无法安全处理。

## Failure Route
安全/权限问题转 incident-response；关联缺失：在信号包登记 `OBSERVABILITY_GAP`，转 `quality-inspection` 补埋点巡检；高影响信号直接转 signal-triage。

## Downstream Contract
下游收到原始引用、规范化字段、窗口、版本关联、质量限制，不得丢失不确定性。

## State Changes
`OPERATIONS_OBSERVED → SIGNAL_COLLECTION_IN_PROGRESS → SIGNALS_COLLECTED | WORKFLOW_BLOCKED`