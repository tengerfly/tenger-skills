---
name: defect-triage
description: 依据复现、日志和批准基线判断缺陷、事故、环境问题或需求变化，并路由到修复闭环。
metadata:
  short-description: 依据复现、日志和批准基线判断缺陷、事故、环境问题或需求变化，并路由到修复闭环。
---

# defect-triage

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
把异常信号变成可复现、可分级、可追踪的缺陷/事故任务，避免修症状、误把需求变化当 Bug 或让事故进入普通排期。

## Trigger
Bug、报错、线上告警、测试失败、用户反馈、巡检发现行为偏差或需要判断“这是 Bug 还是需求”时触发。

## Inputs
- 原始报告、时间、环境、版本、commit、请求/追踪标识；
- 批准需求/验收标准和当前行为；
- 前后端日志、监控、截图、复现步骤和最近变更；
- 数据敏感性、影响范围和当前止损措施。

## Preconditions
- 先保护凭证和个人/客户数据；
- 不把完整生产日志复制进公共仓库；
- 高影响信号先判断 Incident，不等待完整根因；
- 复现前不输出确定根因，只输出候选和证据。

## Responsibilities
- 去重和标准化信号；
- 复现并建立最小证据链；
- 分级 P0/P1/P2/P3，判断 DEFECT/INCIDENT/CHANGE/环境问题；
- 委托技术方案、修复、回归、发布和后观测。

## Non-goals
- 不直接改码；
- 不在未止损的事故中做大范围重构；
- 不把猜测根因、一次成功复现或测试失败直接当永久结论。

## Procedure
1. 为信号生成 `DEF-*`，脱敏并关联版本/commit/trace/request/session；按 `../../shared/problem-recording.md` 在下一安全节点将已知事实写入 `.spec/defects/<id>.md` 并更新项目 `.spec/问题日志.md`。根因未知仍记录，重复信号沿用原 ID。分诊记录按 `../../shared/templates/defect-triage.md` 落盘，ID 前缀统一 `DEF-`。
2. 去重相关日志、告警、用户报告和测试失败，建立时间线。
3. 按批准基线对比当前行为；缺基线则标 `OPEN`。
4. 尝试最小复现，记录命令、输入、结果和环境差异。
5. 评估影响、可恢复性、安全/数据风险和是否需要立即止损。
6. 输出缺陷分诊：优先级、候选根因、修复委托、回归保护、发布和复发观测。
7. 关闭前必须有修复证据、回归证据和发布后观察计划；同步问题索引。转 Incident/Change 保留原 ID 与目标引用，分诊完成不等于缺陷修复闭环。

## Outputs
- `.spec/defects/<id>.md`（按 `../../shared/templates/defect-triage.md`，Triage ID 统一 `DEF-*`）；
- 时间线、复现记录、证据索引和分级；
- 根因候选与修复任务委托；
- 回归/发布/后观测要求；
- bug-pattern 沉淀候选（去敏）。

## Evidence
脱敏日志、代码/配置定位、复现命令、测试输出、版本与关联 ID、用户确认的影响。生产敏感证据只引用授权位置。

## Gate
`PASS`：分级和路由有证据；`CONDITIONAL`：无法完全复现但有明确止损和补证计划；`BLOCKED`：关键版本/授权/证据缺失或存在未处理 P0 风险。

## Failure Route
P0/P1 转 Incident-Response；缺少批准基线转 Project-Onboarding/Impact-Analysis；行为是新需求转 Change；环境问题转运行/基础设施负责人；复现失败不等于关闭。

## Downstream Contract
下游收到缺陷 ID、影响、优先级、复现/证据、版本关联、不可改变行为、修复边界、回归保护、发布策略和后观测条件；修复 Skill 不得重新定义问题。

## State Changes
`SIGNAL_RECEIVED → TRIAGE_IN_PROGRESS → DEFECT_ROUTED | INCIDENT_ROUTED | CHANGE_ROUTED | OBSERVABILITY_GAP | WORKFLOW_BLOCKED`