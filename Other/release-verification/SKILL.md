---
name: release-verification
description: 验证发布后的健康、关键旅程、遥测和版本关联，并给出继续、暂停或回滚建议。
metadata:
  short-description: 验证发布后的健康、关键旅程、遥测和版本关联，并给出继续、暂停或回滚建议。
---

# release-verification

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
确认发布不是“命令成功”而是用户主链、接口、数据、错误率、延迟和遥测均在保护范围内。

## Trigger
部署/迁移完成、回滚完成或观察窗口结束。

## Inputs
发布计划、实际执行报告、关键旅程、健康检查、日志/指标/告警和上一版本基线。

## Preconditions
版本、commit、环境、releaseId 和观察窗口可关联；缺失关联必须标为 OPEN。

## Responsibilities
执行发布后检查、比较前后基线、验证遥测、判断继续/暂停/回滚并建立运行信号追踪。

## Non-goals
不在验证时临时修代码；不以单个请求成功代替趋势；不静默忽略遥测缺失。

## Procedure
1. 校验版本/commit/配置/迁移实际状态。
2. 运行关键主链冒烟和接口/数据一致性检查。
3. 在观察窗口内比较错误率、延迟、资源、关键旅程和告警。
4. 检查前端、后端和服务器信号是否能用关联 ID 对齐。
5. 输出继续、暂停、回滚或转事故的结论；更新 traceability。

## Outputs
`.spec/release/<release-id>/verification-report.md`、指标对比、冒烟证据、遥测缺口和继续/暂停/回滚建议。

## Evidence
真实环境健康检查、测试/冒烟结果、脱敏日志和指标、告警记录、版本关联和前后基线。

## Gate
PASS：保护指标和主链通过，遥测可用；CONDITIONAL：低风险缺口已限制并登记；BLOCKED：主链失败、保护指标越阈值、版本无法关联或无法回滚。

## Failure Route
信号异常转 `signal-triage` / `incident-response`；测试回归转 defect-triage；计划执行差异转 release-planning。

## Downstream Contract
operations 收到版本、commit、观察窗口、信号和已知缺口；不得把验证报告当作永久健康保证。

## State Changes
`DEPLOYMENT_EXECUTED → RELEASE_VERIFICATION_IN_PROGRESS → RELEASE_VERIFIED | RELEASE_PAUSED | INCIDENT_ROUTED`