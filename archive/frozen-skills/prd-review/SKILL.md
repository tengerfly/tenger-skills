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

## 评审上下文隔离（执行必需）

强制适用 `../../shared/review-context-isolation.md`（优先级高于本正文）：参与过被评 PRD 产出、修订、内部自检或评审调度的会话/子代理，不得作为该 PRD 的评审者；同一会话里换一个「评审角色」不算隔离。评审判断只发生在隔离上下文，评审者只拿评审包，不继承产出会话历史、草稿与自检结论；只审不改。

- **A 编排形态**（产出上下文 / Workflow）：只做固定版本、上游闸门核对、建评审包、派发、收产物核验、按规则落 Gate，不做评审判断。
- **B 评审形态**（fresh 子代理，首选）：收到评审包后执行本 Skill 原步骤 2–4 的评审；不读产出会话记录，不改被评 PRD。
- **C 汇总形态**（多角色拆分时）：由产品专家总审子代理只读 PRD 原文 + 各角色报告，出汇总、任务清单与 Gate 建议；汇总者同样不得是产出方。

派发计划：默认派 1 个 fresh 评审子代理，覆盖 `references/product-checklist.md`、`references/frontend-checklist.md`、`references/backend-checklist.md`、`references/test-checklist.md` 四份清单，由该评审者直接出汇总；若按角色拆分，则前端 / 后端 / 测试各 1 个独立子代理（互不可见）+ 产品专家总审 1 个（只读 PRD + 三份角色报告）。派发口径见 `../../shared/review-context-isolation.md` §4；编排方必须核验报告文件与证据产物，不采信子代理口头「已完成」。

无子代理能力时：按 `../../shared/review-context-isolation.md` §4 写评审包（`../../shared/templates/review-package.md`）+ `dispatch-prompt.md`，交新会话执行并停住主会话；仍无隔离能力 ⇒ `BLOCKED`（缺评审隔离能力；owner=宿主/用户，requiredInput=隔离执行能力，clearCondition=具备后重跑）。可先出「自查（非评审）」，但不得自查冒充评审、不得产出评审报告 / 任务清单 / Gate 建议。

报告必须含 `assets/summary-template.md` §0.5 隔离记录（`isolationMode` / `reviewerRef` / `packageDigest` / `parentExecution` / `producedByContextInvolved: false` / `verifiedArtifacts`）；缺记录或 `producedByContextInvolved` 非 false ⇒ Gate 只能 `BLOCKED`（缺评审隔离证据）。

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
不修改 PRD、补写业务规则、做竞品调研或批准新的 MVP；不以“我已修正”代替退回修订；不把自己的偏好当产品缺陷；不在产出 PRD 的同一会话自审；不以自查代替评审（自查只能标注「自查（非评审）」，不得产出评审报告、任务清单或 Gate 建议）；不采信子代理口头「已评审通过」，以报告 §0.5 与证据产物核验为准。

## Procedure

**〔REQUIRED · 隔离核对〕** 开工前按「评审上下文隔离」节先判形态：本上下文参与过本 PRD 的产出 / 修订 / 自检 / 评审调度 ⇒ 只能作编排形态（固定版本、闸门核对、建包、派发、收产物核验、落 Gate），不得执行步骤 2–4 的评审；已派发时由 fresh 子代理只拿评审包执行步骤 2–4，三角色拆分时由产品专家总审子代理（形态 C）出汇总。形态判定、`reviewerRef` 与 `packageDigest` 记入报告 §0.5；无隔离能力 ⇒ `BLOCKED`（缺评审隔离能力）。

1. 固定被审版本及输入版本，读取上轮未决问题。**〔REQUIRED · 开工前闸门核对〕**逐条读 `.spec/manifest.yaml` 中本批上游条目（功能范围确认、蓝图、产品定义等）的 `status`、`version`、`gate`、`allowDownstream`：任一 `SUPERSEDED`／非 `PASS`／`false` ⇒ 本批只能 `BLOCKED`（命名缺失输入 + owner + 清除条件）；「本轮判据全闭」只作事实记录，限定条件只能落 `gate`/`allowDownstream`/`blockedBy` 字段、不得写进注释或正文（`../../shared/gate-policy.md` §6）；`APPROVED_SUPERSEDED` 这类枚举外状态词不得当作批准依据（`../../shared/artifact-contract.md` §2）；汇总报告须含公共基线 §0「上游闸门核对与本轮 Gate」与时序核查（`../../shared/templates/review-summary-template.md`），缺该节则本轮 Gate 只能记 `BLOCKED`（缺上游闸门核对证据），不得 `PASS` / `CONDITIONAL`。
2. 逐项对照范围表与需求 ID，检查漏项、越界、无来源规则与依赖断裂；竞品功能不等于必做项。
3. 检查用户角色、主链、边界、异常/恢复、数据/权限、指标口径和验收标准。只有两问摘要、没有功能范围确认不能过正式 PRD Gate。
4. 问题写证据位置、影响、归属节点、清除条件与复核方法；不直接编辑被审规格。按审查对象加载 `references/product-checklist.md`、`references/frontend-checklist.md`、`references/backend-checklist.md`、`references/test-checklist.md`；问题用 `assets/issue-list-template.md`，总结用 `assets/summary-template.md`。当前职责优先于 legacy-skill。
5. 按共享 Gate 规则给出结论，缺关键用户确认不得以评审替代批准；修订后核对新版本及受影响项。相同问题三轮未收敛则请求裁决，不自动放行。**〔REQUIRED · 隔离证据核对〕** 汇总报告缺 §0.5 隔离记录，或 `isolationMode` / `reviewerRef` / `packageDigest` 任一为空、`producedByContextInvolved` 非 false ⇒ 本轮 Gate 只能 `BLOCKED`（缺评审隔离证据），不得 `PASS` / `CONDITIONAL`。

## Outputs
review artifact、分级问题清单、覆盖检查结果、Gate 与下一路由；评审包（`.spec/需求评审/评审包-REV-*.md`，按 `../../shared/templates/review-package.md`）、§0.5 隔离记录、派发与核验证据（reviewerRef / packageDigest / 报告与证据文件核验）；正式执行记录 executionId、status、gate、artifactRefs、evidenceRefs、decisionRefs、nextAction。

## Evidence
PRD 原文位置、批准范围和规则引用、实际版本、上轮复核记录；评审者引用（reviewerRef / isolationMode）与评审包摘要（packageDigest）；派发与收产物核验记录；禁止以文件存在、子代理口头「已完成/通过」或模型自评作为完整性证据。

## Gate
PASS：批准范围完整覆盖、无阻塞问题、关键确认齐全。P0/P1 按共享 Gate 契约处理；缺失确认/证据为 BLOCKED。CONDITIONAL 需授权例外与明确下游限制，不能自行批准重大产品取舍。

## Failure Route
规格表达回 prd-design；研究缺口回 competitive-analysis/product-discovery；定位回 product-definition；规则回 application-blueprint；范围决策回 feature-decision。复核只验证修复，不代替修复。

## Downstream Contract
下游消费被评审的精确版本、review、批准/例外引用；不得把被改动后失效的通过结论继续使用。

## State Changes
`PRD_REVIEW_IN_PROGRESS → PRD_APPROVED | WORKFLOW_BLOCKED`；沿注册合法边与授权证据推进，不因写了评审报告直接改为批准。
