---
name: prd-design
description: 根据已确认产品定义、应用蓝图和功能决策编写可执行 PRD 的兼容入口。
metadata:
  legacy-alias: PRD-Design
  migration-target: prd-workflow
---

# PRD-Design 兼容入口

本目录保留旧版成熟逻辑和资源；旧版完整说明已归档到 `references/legacy-skill.md`，原有 references/assets 不删除。新流程通过本入口承接，但职责和 Gate 受 `../../shared/product-workflow-contract.md` 约束。

## Purpose
平滑接入新的 PRD Workflow，同时保留已经验证过的领域规则和模板。

## Trigger
用户明确要求执行本领域动作，或 `prd-workflow` 在对应阶段调度时触发。请求属于上游研究、定位、蓝图或范围决策时先路由上游。

## Inputs
- 上游 artifact、manifest、决策记录和 traceability；
- 用户确认、研究证据、PRD/原型原文；
- 本目录 legacy-skill、references、assets 和既有脚本。

## Preconditions
- 上游输入可定位，OPEN/ASSUMPTION 不能被当作批准结论；
- 工作区边界已检查，不覆盖未提交内容；
- 读取产品契约和 Gate 规则；
- 评审类入口必须只审不改。

## Responsibilities
- 校验输入 artifact、证据和用户确认；
- 在职责边界内复用旧版成熟规则；
- 产出带 artifactId、sourceRefs、evidenceRefs、decisionRefs 的结果；
- 失败时回退到正确上游；
- 将 execution、Gate 和问题写入项目 `.spec/`。

## Non-goals
- 不替用户决定产品定位、MVP、范围或重大取舍；
- 不删除旧版 references/assets；
- 不把竞品存在、模型推荐或原型表现升级为产品事实。

## Procedure
1. 阅读本目录 legacy-skill 和资源，识别要复用的成熟规则。
2. 校验生命周期、上游状态、证据和开放项。
3. 执行本领域动作，只生成职责范围内的草案、报告或结果。
4. 使用旧模板、清单、脚本和案例库做自检。
5. 写入 manifest、traceability、decision/execution record 并输出 Gate。
6. 评审最多 3 轮，问题路由到产品定义、蓝图、范围、原型或 UI/DEV。

## Outputs
- 本领域 artifact、问题清单或评审报告；
- 证据、决策、开放项和下游接口；
- executionId、status、gate、evidenceRefs、artifactRefs、decisionRefs、nextAction。

## Evidence
使用上游 artifact、用户确认、文件/源码/截图、可核验外部来源和确定性命令结果。无来源数据标 OPEN；预测/估算显式标注；多方口径并列保留。

## Gate
PASS：输入、产物、证据和关键确认齐全；CONDITIONAL：风险、责任人、期限、补证动作和 allowDownstream 已登记；BLOCKED：关键证据、授权、范围或上游 Gate 缺失。文件存在不等于 Gate 通过。

## Failure Route
证据/用户问题不足回 `feature-decision`；产品定位/核心价值回 `product-definition`；业务流程/状态回 `application-blueprint`；MVP/功能范围回 `feature-decision`；技术未知交 DEV Workflow；页面/视觉问题交 `prd-review`。

## Downstream Contract
下游只能消费 manifest 中状态明确的 artifact，必须读取 sourceRefs、evidenceRefs、decisionRefs 和 openItems，不得从聊天上下文补齐未确认结论。

## State Changes
`WORKFLOW_BLOCKED → INTAKE_REQUESTED → DISCOVERY_IN_PROGRESS → INTAKE_READY`。
