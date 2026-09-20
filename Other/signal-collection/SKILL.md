---
name: signal-collection
description: 从前端监控、服务日志、服务监控和产品数据收集可关联、可脱敏的运行信号。
metadata:
  short-description: 从前端监控、服务日志、服务监控和产品数据收集可关联、可脱敏的运行信号。
---

# signal-collection

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
5. 输出信号包和质量说明，交给 ../signal-triage/product-analytics。

## Outputs
`.spec/signals/<window>/signal-pack.md`、脱敏索引、关联质量和采集缺口。

## Evidence
来源查询、导出摘要、字段映射、时间窗口、采样说明和权限记录。

## Gate
PASS：来源、窗口、关联和脱敏可复核；CONDITIONAL：已声明采样/关联缺口；BLOCKED：无权限、数据不可解读或敏感信息无法安全处理。

## Failure Route
安全/权限问题转 incident-response；关联缺失转 Observability-Design；高影响信号直接转 signal-triage。

## Downstream Contract
下游收到原始引用、规范化字段、窗口、版本关联、质量限制，不得丢失不确定性。

## State Changes
`OPERATIONS_OBSERVED → SIGNAL_COLLECTION_IN_PROGRESS → SIGNALS_COLLECTED | WORKFLOW_BLOCKED`