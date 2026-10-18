---
name: prd-review
description: 只读评审指定版本 PRD 的完整性、一致性、范围追踪和可测试性，输出分级问题与 Gate 建议；不改 PRD、不做研究或重新决定功能范围。触发：评审 PRD、需求评审、查 PRD 问题、PRD 走查、需求文档检测。
metadata:
  legacy-alias: PRD-Review
  migration-target: prd-review
---

# PRD Review

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Task scope & context

按 `../../shared/execution-profiles.md` 判强度，按 `../../shared/requirements-context.md` 固定需求版本，按 `../../shared/product-workflow-contract.md` 守职责边界。轻量只处理已确认的局部范围；正式交接遵守 manifest、Gate、决策与状态契约。旧 references/assets 按需复用，不执行旧版跨域流程。

## Purpose
判断指定版本规格是否忠实覆盖批准范围且足够可实现、可测试，发现问题交原责任节点修订。

## Trigger
PRD 已形成并请求评审，或修订后需要复核；不是模糊想法的访谈或撰写入口。

## Inputs
固定版本 PRD、批准范围表、业务蓝图、产品定义、研究来源及上轮问题/例外。

## Preconditions
评审对象与批准输入可定位，采用 `../../shared/requirements-context.md` 读取原文，不只读摘要；保持只审不改。

## Responsibilities
核对范围完整性、需求来源、规则一致性、权限/状态/异常闭环、验收可测性；输出问题严重度、证据、归属、清除条件与复核结论。

## Non-goals
不修改 PRD、补写业务规则、做竞品调研或批准新的 MVP；不以“我已修正”代替退回修订；不把自己的偏好当产品缺陷。

## Procedure
1. 固定被审版本及输入版本，读取上轮未决问题。**〔REQUIRED · 开工前闸门核对〕**逐条读 `.spec/manifest.yaml` 中本批上游条目（功能范围确认、蓝图、产品定义等）的 `status`、`version`、`gate`、`allowDownstream`：任一 `SUPERSEDED`／非 `PASS`／`false` ⇒ 本批只能 `BLOCKED`（命名缺失输入 + owner + 清除条件）；「本轮判据全闭」只作事实记录，限定条件只能落 `gate`/`allowDownstream`/`blockedBy` 字段、不得写进注释或正文（`../../shared/gate-policy.md` §6）；`APPROVED_SUPERSEDED` 这类枚举外状态词不得当作批准依据（`../../shared/artifact-contract.md` §2）；汇总报告须含公共基线 §0「上游闸门核对与本轮 Gate」与时序核查（`../../shared/templates/review-summary-template.md`），缺该节则本轮 Gate 只能记「未验证」，不得 `PASS`。
2. 逐项对照范围表与需求 ID，检查漏项、越界、无来源规则与依赖断裂；竞品功能不等于必做项。
3. 检查用户角色、主链、边界、异常/恢复、数据/权限、指标口径和验收标准。只有两问摘要、没有功能范围确认不能过正式 PRD Gate。
4. 问题写证据位置、影响、归属节点、清除条件与复核方法；不直接编辑被审规格。按审查对象加载 `references/product-checklist.md`、`references/frontend-checklist.md`、`references/backend-checklist.md`、`references/test-checklist.md`；问题用 `assets/issue-list-template.md`，总结用 `assets/summary-template.md`。当前职责优先于 legacy-skill。
5. 按共享 Gate 规则给出结论，缺关键用户确认不得以评审替代批准；修订后核对新版本及受影响项。相同问题三轮未收敛则请求裁决，不自动放行。

## Outputs
review artifact、分级问题清单、覆盖检查结果、Gate 与下一路由；正式执行记录 executionId、status、gate、artifactRefs、evidenceRefs、decisionRefs、nextAction。

## Evidence
PRD 原文位置、批准范围和规则引用、实际版本、上轮复核记录；禁止以文件存在或模型自评作为完整性证据。

## Gate
PASS：批准范围完整覆盖、无阻塞问题、关键确认齐全。P0/P1 按共享 Gate 契约处理；缺失确认/证据为 BLOCKED。CONDITIONAL 需授权例外与明确下游限制，不能自行批准重大产品取舍。

## Failure Route
规格表达回 prd-design；研究缺口回 competitive-analysis/product-discovery；定位回 product-definition；规则回 application-blueprint；范围决策回 feature-decision。复核只验证修复，不代替修复。

## Downstream Contract
下游消费被评审的精确版本、review、批准/例外引用；不得把被改动后失效的通过结论继续使用。

## State Changes
`PRD_REVIEW_IN_PROGRESS → PRD_APPROVED | WORKFLOW_BLOCKED`；沿注册合法边与授权证据推进，不因写了评审报告直接改为批准。
