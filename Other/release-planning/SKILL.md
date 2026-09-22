---
name: release-planning
description: 把已通过测试的变更编排为可观察、可回滚、可审批的发布计划。
metadata:
  short-description: 把已通过测试的变更编排为可观察、可回滚、可审批的发布计划。
---

# release-planning

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
将版本范围、迁移、配置、灰度、观察窗口、保护指标和回滚条件写成可执行计划。成功标准是任何执行者都能按计划判断继续、暂停或回滚。

## Trigger
测试 Gate 通过且准备发布；或事故修复/高风险变更需要紧急发布计划。

## Inputs
- 变更 manifest、测试报告、commit 和版本；
- 数据迁移/配置/依赖/基础设施变更；
- 环境、发布权限、灰度能力和历史基线；
- 关键旅程、SLI/SLO、告警、回滚入口和用户影响。

## Preconditions
- TEST_PASSED 或明确的紧急例外；
- 生产授权、发布窗口和回滚责任人明确；
- 不复制密钥和完整生产数据；
- 保护指标和停止条件不能为空。

## Responsibilities
- 定义发布批次、顺序、前置检查、迁移与兼容策略；
- 绑定版本、commit、配置、数据迁移和验证命令；
- 定义灰度、观察窗口、继续/暂停/回滚条件；
- 请求需要的人工审批。

## Non-goals
- 不直接部署、不替用户批准生产例外；
- 不把测试通过等同于生产健康；
- 不临时修改代码掩盖发布风险。

## Procedure
1. 汇总变更、测试和已知风险，核对追踪链完整性。
2. 检查迁移是否前后兼容、配置是否可回退、依赖是否可复现。
3. 写出预发布、灰度、全量、观察和回滚步骤及负责人。
4. 为每个保护指标定义基线、阈值、来源和观察时间。
5. 生成 release plan，等待明确授权后交给 deployment-execution。

## Outputs
- `.spec/release/<release-id>/release-plan.md`；
- 版本/commit/配置/迁移清单；
- 灰度、观察、回滚和审批记录；
- manifest、decision、traceability 更新。

## Evidence
测试报告、commit/tag、构建产物摘要、迁移 dry-run、配置 diff、历史基线和回滚演练/验证记录。

## Gate
PASS：计划、权限、保护指标、回滚和验证齐全；CONDITIONAL：已登记例外且不得越过限制；BLOCKED：无授权、无回滚、P0/P1 未处理或版本范围不清。

## Failure Route
测试失败转 defect-triage/对应开发节点修复，再由 ../../Test/auto-test 复测；迁移不兼容转 Tech-Design；运行高风险转 incident-response；无授权停止等待负责人。

## Downstream Contract
deployment-execution 只可执行计划中列出的版本、环境、命令、观察和回滚，不得自行扩大范围。

## State Changes
`TEST_PASSED → RELEASE_PLANNING_IN_PROGRESS → RELEASE_PLAN_READY | WORKFLOW_BLOCKED`