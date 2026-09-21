---
name: application-blueprint
description: 将已确认的产品定义展开为用户旅程、业务流程、能力地图、状态和异常闭环。
metadata:
  short-description: 将已确认的产品定义展开为用户旅程、业务流程、能力地图、状态和异常闭环。
---

# application-blueprint

本 Skill 是 PRD Workflow 的原子节点。公共边界见 `../../shared/product-workflow-contract.md`。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
把产品定义变成可讨论的应用蓝图，覆盖主流程、分支、权限、空状态、失败、恢复和对象生命周期。

## Trigger
Product Definition 已批准，或 CHANGE 影响核心旅程、规则、权限、状态机或模块边界时触发。

## Inputs
- 已批准 Product Definition；
- 已确认功能候选或现有基线；
- 角色、业务对象、外部依赖和约束。

## Preconditions
- 定位、目标用户、非目标和成功指标已确认；
- 业务术语有单一事实源；
- 主流程节点有来源；
- 页面视觉不是前置。

## Responsibilities
- 绘制角色—旅程—流程和能力地图；
- 定义对象、状态、迁移、权限和生命周期；
- 推演成功、失败、重试、超时、取消、空、无权限和恢复；
- 区分产品规则与技术实现约束。

## Non-goals
- 不设计视觉稿、组件样式或代码；
- 不偷偷增加未决功能；
- 不用“后续技术处理”掩盖产品规则缺口。

## Procedure
1. 列角色、目标和边界。
2. 建立端到端主流程并回链问题/决策。
3. 定义状态机、合法迁移、终态和失败出口。
4. 推演资源不存在、权限不足、空数据、依赖失败、重复、超时、恢复和回滚。
5. 输出蓝图、状态机、异常矩阵和能力地图。
6. 由产品责任人确认规则，未决项路由 Feature Decision 或阻塞。

## Outputs
- `application-blueprint` artifact；
- `journey-map`、业务流程/状态机、异常矩阵和能力地图；
- OPEN 清单和 traceability 更新。

每次执行都必须记录 `executionId`、`skill`、`lifecycle`、`project`、`status`、`gate`、`evidenceRefs`、`artifactRefs`、`decisionRefs` 和 `nextAction`。

## Evidence
Product Definition、用户旅程、批准规则、运行数据和依赖约束。每个状态/迁移有来源或标为候选。

## Gate
PASS：主流程、异常、状态、权限和恢复闭环；CONDITIONAL：非主链缺口有登记且不影响下游；BLOCKED：主流程断头、状态无终态、规则冲突或未确认。

`CONDITIONAL` 必须记录例外、风险、责任人、截止时间、补证动作和 `allowDownstream`。AI 只能提出 Gate，不能替用户批准关键产品决策。

## Failure Route
定位冲突回 product-definition；功能取舍回 feature-decision；技术问题交 DEV Workflow；页面问题交 Prototype/UI。

评审或澄清最多 3 轮；仍未收敛时保留问题并请求人工裁决，不无限生成。

## Downstream Contract
Feature Decision 消费旅程、能力、状态和异常边界；Prototype 消费批准的流程和信息架构。

下游必须消费 artifact 和 decisionRefs，不得从聊天上下文补齐未确认结论。

## State Changes
`PRODUCT_DEFINITION_READY → APPLICATION_BLUEPRINT_IN_PROGRESS → APPLICATION_BLUEPRINT_READY | WORKFLOW_BLOCKED`
