---
name: incident-response
description: 在运行事故期间止损、恢复、记录时间线并验证恢复，不替代永久修复。
metadata:
  short-description: 在运行事故期间止损、恢复、记录时间线并验证恢复，不替代永久修复。
---

# incident-response

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
降低事故影响并恢复服务，同时保留可审计时间线、临时措施、恢复证据和后续修复委托。

## Trigger
P0/P1 信号、服务不可用、数据/安全风险或发布保护指标越阈值。

## Inputs
signal-triage、告警、运行手册、发布/回滚计划、权限、影响范围和沟通边界。

## Preconditions
事故负责人和环境明确；不扩大敏感数据读取；优先安全和止损；每个动作可回滚或可解释。

## Responsibilities
确认事故、分工、止损、回滚/降级、时间线、恢复验证和后续任务。

## Non-goals
不在事故中做无关重构；不隐藏影响；不以恢复服务等同于根因修复。

## Procedure
1. 建立 incident ID（`INC-*`）、严重级别、影响范围和负责人。
2. 记录每个假设、命令、结果和时间，不把猜测写成根因。
3. 执行批准的降级/回滚/隔离措施。
4. 通过主链、错误率、延迟、数据一致性和告警验证恢复。
5. 关闭临时措施，委托 defect/change/refactor 和 post-release-review。

## Outputs
`.spec/incidents/<id>/timeline.md`、影响/恢复报告（按 `../../shared/templates/incident-report.yaml`，`incidentId` 统一 `INC-*`）、临时措施、根因候选和后续任务。

## Evidence
时间线、部署/回滚记录、健康检查、指标、日志引用、授权和恢复确认。

## Gate
PASS：影响受控且恢复证据充分；CONDITIONAL：服务恢复但永久修复/数据核验未完成；BLOCKED：无法止损、权限不足或存在持续数据/安全风险。

## Failure Route
无法恢复升级负责人/基础设施；疑似安全事件走安全响应；恢复后转 defect-triage 和 post-release-review。

## Downstream Contract
后续修复必须引用 incident、影响、时间线、临时措施和复现/回归要求，不得只接收一句“线上已恢复”。

## State Changes
`INCIDENT_ROUTED → INCIDENT_ACTIVE → SERVICE_RECOVERED → DEFECT_ROUTED | POST_RELEASE_REVIEW`