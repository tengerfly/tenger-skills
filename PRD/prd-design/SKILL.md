---
name: prd-design
description: 将已批准的产品定义、业务蓝图与功能范围编写为带验收标准的 PRD。用于需求规格撰写或更新；不做竞品研究、范围决策或 PRD 评审。
metadata:
  legacy-alias: PRD-Design
  migration-target: prd-design
---

# PRD Design

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Task scope & context

按 `../../shared/execution-profiles.md` 判强度，按 `../../shared/requirements-context.md` 固定需求版本，按 `../../shared/product-workflow-contract.md` 守职责边界。轻量只处理已确认的局部范围；正式交接遵守 manifest、Gate、决策与状态契约。旧 references/assets 按需复用，不执行旧版跨域流程。

## Purpose
把批准输入转成清晰、可实现、可测试的需求规格；不重新发现或批准产品需求。

## Trigger
feature-decision 已批准范围，需要编写/更新 PRD，或 prd-review 将规格表达问题退回。模糊想法先交 prd-workflow，不直接生成正式全量 PRD。

## Inputs
批准的 product-definition、application-blueprint、feature-decision 及其版本/decisionRefs；research 功能 ID、现有需求与影响分析。

## Preconditions
输入可定位且正式 Gate 允许交接；范围确认可追踪，关键规则无 OPEN。用户明确限定的局部任务可用已确认验收点，但不能冒充整套产品基线。

## Responsibilities
组织规格结构与稳定 REQ ID；把批准规则写成前置条件、行为、权限、数据、异常、恢复和可验证验收标准；建立需求—功能决策—蓝图追踪。只编写规格，不批准自己的产物。

## Non-goals
不重做研究或定位；不增删批准范围；不代写业务规则和商业取舍；不执行 PRD 评审、原型、技术选型或代码开发。

## Procedure
1. 固定输入版本并核查功能 ID、范围决策与关键规则。缺失就退回对应节点，不凭竞品清单直接写实现需求。
2. 按批准范围编写 PRD；结构用 `references/prd-structure.md`，验收语法用 `references/gherkin-guide.md`，按需使用 `assets/overview-template.md`、`assets/module-template.md`、`assets/quickref-template.md`。若旧模板要求顺带研究/定范围/自批 Gate，忽略该越界部分。
3. 每项需求写可测试的正常、失败、权限与恢复结果及来源，引用蓝图而非建立互相冲突的规则副本。
4. 检查批准范围覆盖和双向追踪，标出排除项与非阻塞开放项。自检不等于独立评审。
5. 输出 DRAFT/REVIEW 版本交 prd-review；评审修改后产生新版本并标明受影响条目，不能继续沿用失效批准。

## Outputs
prd artifact、需求索引/验收标准、来源与范围覆盖表。正式执行记录 executionId、status、gate、artifactRefs、evidenceRefs、decisionRefs、nextAction。

## Evidence
已批准输入与用户确认引用；估算注明来源和假设，不把未知约束编成事实。

## Gate
PASS 仅表示本节点规格编写满足交接要求，PRD_APPROVED 必须经 prd-review 与授权确认。关键范围/规则/验收标准缺失为 BLOCKED；CONDITIONAL 按共享契约记录例外与限制。

## Failure Route
来源不足回 competitive-analysis/product-discovery；定位回 product-definition；流程/权限/状态回 application-blueprint；取舍回 feature-decision；纯表达遗漏由本节点修订；技术未知交 DEV。

## Downstream Contract
prd-review 消费固定版本、确认引用和范围覆盖表。未评审批准的 PRD 不作为正式实现授权。

## State Changes
`FEATURE_DECISION_READY → PRD_IN_PROGRESS → PRD_REVIEW_IN_PROGRESS`；正式推进由编排器按注册合法边完成，编写者不能自行设置 PRD_APPROVED。
