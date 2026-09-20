---
name: refactor-planning
description: 在默认外部行为不变的前提下规划可验证、可回退的应用重构和工程治理。
metadata:
  short-description: 在默认外部行为不变的前提下规划可验证、可回退的应用重构和工程治理。
---

# refactor-planning

## Purpose
把“代码太乱/想重构”转成有行为基线、拆分批次、保护测试、风险和回滚的工程任务。

## Trigger
结构治理、模块拆分、依赖替换、测试补强、可观测性补齐、架构漂移或质量巡检建议触发；若要改变外部行为，改走 Change。

## Inputs
- Project Onboarding 基线；
- 当前结构、依赖、构建/测试、性能和运行证据；
- 已批准行为、API/数据兼容约束；
- 目标质量指标、允许的停机/发布窗口和回滚能力。

## Preconditions
- 明确“行为不变”的边界；
- 先有 characterization/contract/regression 保护或登记缺口；
- 读取 `../../shared/traceability.md` 和 `../../shared/oss-research-policy.md`；
- 不把未测行为承诺为不变。

## Responsibilities
- 定义重构目标和非目标；
- 建立拆分批次、依赖顺序、保护测试、观测和回滚；
- 判断是否实际包含 Change/Defect；
- 产出可交给技术设计和开发的计划。

## Non-goals
- 不直接改码或大范围替换技术栈；
- 不因“清理代码”扩大产品范围；
- 不用静态风格偏好证明重构收益。

## Procedure
1. 对比基线与目标，列出结构问题、证据和外部行为边界。
2. 先把缺少的行为保护转成最小测试/观测任务。
3. 画依赖图，选择可独立验证、可回滚的小批次。
4. 对数据库、接口、鉴权、缓存、消息和部署逐项检查兼容性。
5. 对新工具/框架执行 OSS/GitHub 研究并登记许可证和适用范围。
6. 定义每批次的通过条件、停止条件、回滚和发布后观察。
7. 建立 REFACTOR 到代码、测试、发布和基线的追踪链。

## Outputs
- `.spec/refactor/<id>.md`；
- 行为保护清单、拆分批次和风险矩阵；
- 技术方案委托与回滚方案；
- manifest、decision 和 traceability 更新。

## Evidence
基线命令、架构/依赖定位、测试和指标、兼容性证据、GitHub 源码研究和人工确认。只凭“代码更干净”不足以通过。

## Gate
`PASS`：行为边界、批次、保护、回滚和收益可验证；`CONDITIONAL`：缺口有负责人和截止时间；`BLOCKED`：行为基线不存在、风险不可接受或重构实际是未批准变更。

## Failure Route
识别到外部行为变化转 Change/Impact；发现行为偏差转 Defect；缺少基线转 Onboarding；技术方案风险转 Tech-Review。

## Downstream Contract
下游收到重构目标、不可变行为、批次、依赖、测试/观测、回滚、发布窗口和停止条件；开发不得将计划外清理混入本轮。

## State Changes
`INTAKE_READY → REFACTOR_PLANNING_IN_PROGRESS → DEV_IN_PROGRESS | CHANGE_ROUTED | DEFECT_ROUTED | WORKFLOW_BLOCKED`