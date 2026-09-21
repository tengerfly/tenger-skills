---
name: deployment-execution
description: 按批准的发布计划执行部署并保存可审计结果，不擅自改变生产范围。
metadata:
  short-description: 按批准的发布计划执行部署并保存可审计结果，不擅自改变生产范围。
---

# deployment-execution

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
在明确授权和批准计划下执行部署、迁移、灰度和回滚，保存版本、环境、命令、结果和异常。

## Trigger
release-planning 通过并获得执行授权。

## Inputs
批准的 release plan、目标环境、凭证引用、部署命令、窗口、回滚步骤和观察责任人。

## Preconditions
- 计划 Gate 为 PASS 或允许执行的 CONDITIONAL；
- 授权人、目标环境、版本和回滚责任人已确认；
- 凭证从安全系统读取，不写入日志；
- 变更前健康检查通过。

## Responsibilities
执行计划、记录时间线和命令结果、按条件暂停/回滚、将异常路由给 ../release-verification/incident-response。

## Non-goals
不改代码、不临时加未批准变更、不跳过迁移检查、不将命令成功当成业务健康。

## Procedure
1. 再核对计划摘要、环境、版本和授权。
2. 执行 preflight 并记录结果。
3. 按批次部署/迁移/灰度，每批次完成健康检查后才继续。
4. 触发保护指标或命令失败时立即暂停并按计划回滚。
5. 输出执行记录，交给 release-verification。

## Outputs
`.spec/release/<release-id>/deployment-report.md`、命令/时间线摘要、版本和环境绑定、异常与回滚记录。

## Evidence
脱敏命令输出、部署系统记录、commit/tag、迁移结果、健康检查、操作者和授权记录。

## Gate
PASS：计划步骤完整执行且无未解释异常；CONDITIONAL：已暂停并有明确验证/负责人；BLOCKED：授权、环境、版本或安全前置条件缺失。

## Failure Route
任何高影响异常转 incident-response；验证未通过转 release-verification；计划与现实不一致返回 release-planning。

## Downstream Contract
release-verification 收到实际执行差异，不得假设计划等于实际。

## State Changes
`RELEASE_PLAN_READY → DEPLOYMENT_IN_PROGRESS → DEPLOYMENT_EXECUTED | DEPLOYMENT_ROLLED_BACK | WORKFLOW_BLOCKED`