---
name: product-discovery
description: 验证目标用户、问题场景、替代方案和证据强度，形成产品发现简报。
metadata:
  short-description: 验证目标用户、问题场景、替代方案和证据强度，形成产品发现简报。
---

# product-discovery

本 Skill 是 PRD Workflow 的原子节点。公共边界见 `../../shared/product-workflow-contract.md`。

## Purpose
回答“谁在什么场景遇到什么问题，现有替代方案为何不足”，把事实、证据、推断和待验证假设分开。

## Trigger
Intake 已准备，产品方向不清，或 CHANGE/OPTIMIZE 需要重新验证用户问题时触发。

## Inputs
- 已通过 Gate 的 intake；
- 访谈、反馈、行为数据、客服/工单；
- 可核验的市场和社区资料；
- 用户可确认的假设。

## Preconditions
- Intake 含原始表达和边界；
- 证据有来源和时间；
- 不能把宣传文案、搜索摘要或模型记忆当用户事实。

## Responsibilities
- 定义角色、场景、任务、痛点、频率、影响和替代方案；
- 组织证据并记录强度、样本和偏差；
- 识别冲突说法；
- 生成待验证假设和成功信号；
- 将外部竞争研究路由到 Competitive-Analysis。

## Non-goals
- 不冻结定位、商业模式、MVP 或最终功能；
- 不把少量反馈外推成全体用户事实；
- 不用“用户可能喜欢”替代证据。

## Procedure
1. 校验 Intake 并建立 Discovery ID。
2. 建立角色—场景—任务—问题—影响—替代方案表。
3. 记录资料原文位置、时间、样本和口径。
4. 把推断拆成可证伪假设，写验证动作、责任人和截止点。
5. 输出 Discovery Brief；核心问题无证据时保持 OPEN 并阻塞。

## Outputs
- `discovery-brief` artifact；
- 证据矩阵、假设清单和研究缺口；
- 竞争研究引用与确认清单。

每次执行都必须记录 `executionId`、`skill`、`lifecycle`、`project`、`status`、`gate`、`evidenceRefs`、`artifactRefs`、`decisionRefs` 和 `nextAction`。

## Evidence
用户原话、访谈、产品数据、客服/工单、公开来源和现有基线。每个 INFERENCE 必须指向 EVIDENCE。

## Gate
PASS：核心问题和人群有足够直接证据；CONDITIONAL：假设有责任人和期限；BLOCKED：核心问题无证据或样本冲突未裁决。

`CONDITIONAL` 必须记录例外、风险、责任人、截止时间、补证动作和 `allowDownstream`。AI 只能提出 Gate，不能替用户批准关键产品决策。

## Failure Route
证据缺失回补研究；外部问题交 Competitive-Analysis；运行信号不明交 ../../Other/signal-triage/product-analytics。

评审或澄清最多 3 轮；仍未收敛时保留问题并请求人工裁决，不无限生成。

## Downstream Contract
Product Definition 可消费问题、用户、场景、替代方案、证据和假设，不得将假设当事实。

下游必须消费 artifact 和 decisionRefs，不得从聊天上下文补齐未确认结论。

## State Changes
`IDEA_INTAKE_READY → DISCOVERY_IN_PROGRESS → DISCOVERY_READY | WORKFLOW_BLOCKED`
