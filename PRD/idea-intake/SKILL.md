---
name: idea-intake
description: 登记原始产品想法、约束、歧义与研究问题，形成 intake；只做入口澄清，不研究竞品、不完成范围确认或编写 PRD。
metadata:
  short-description: 把模糊产品想法登记为带证据边界、未知项和确认问题的产品入口。
---

# idea-intake

本 Skill 是 PRD Workflow 的原子节点。公共边界见 `../../shared/product-workflow-contract.md`。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
将用户原始表达结构化为可研究的产品入口，保留原意、上下文和生命周期，不把一句话直接升级为确定需求。

## Trigger
新想法、新机会、用户反馈进入产品流程，或 CHANGE/OPTIMIZE 需要重新澄清目标时触发。已有批准 PRD 的纯实现或视觉修复不触发。

## Inputs
- 用户原始表达和附件；
- 项目基线、已有 PRD、决策和运行信号；
- 生命周期、范围、约束和授权人。

## Preconditions
- 检查项目 `.spec/`、分支和未提交内容；
- 读取产品契约和生命周期契约；
- 原始表达必须可回放，不能只保留摘要。

## Responsibilities
- 保存问题、目标、初始场景、约束和非目标；
- 区分 FACT、INFERENCE、ASSUMPTION、OPEN；
- 识别 CREATE/CHANGE/OPTIMIZE；
- 每轮生成不超过三个的入口确认问题；这是本节点的认知负担限制，不是整个 PRD 探索只问三题或三轮；
- 保存用户明确要求的研究/确认顺序及产品歧义，把“我不知道整体功能”交给后续研究，不要求用户凭空列完需求；
- 建立 intake、manifest 和 traceability 起点。

## Non-goals
- 不做竞品结论、定位、功能清单或 MVP 决策；
- 不替用户确认预算、商业模式或目标用户；
- 不直接创建正式 PRD。

## Procedure
1. 记录原始输入并生成 Intake ID。
2. 拆分问题、目标、角色/场景、约束、不可改变行为和未知项。
3. 给判断加证据标签，冲突并列呈现。
4. 选择生命周期并列研究命题。
5. 生成确认清单，写入 `.spec/intake/`、manifest、workflow 和 traceability。

## Outputs
- `intake` artifact；
- 证据索引、确认清单和 execution record；
- 供 Product Discovery 消费的未知项与研究问题。

每次执行都必须记录 `executionId`、`skill`、`lifecycle`、`project`、`status`、`gate`、`evidenceRefs`、`artifactRefs`、`decisionRefs` 和 `nextAction`。

## Evidence
原始用户消息、项目文件、批准决策、运行信号和用户确认。无证据的业务结论只能为 OPEN。

## Gate
PASS：原始意图、生命周期、边界和研究问题清晰；CONDITIONAL：未知项已登记且不阻塞；BLOCKED：意图、授权或项目基线无法确定。

`CONDITIONAL` 必须记录例外、风险、责任人、截止时间、补证动作和 `allowDownstream`。AI 只能提出 Gate，不能替用户批准关键产品决策。

## Failure Route
语义冲突回用户确认；上下文缺失回 project-onboarding；变化交 ../change-intake/impact-analysis；故障交 defect-triage。

同一阻塞问题最多重复澄清 3 轮，仍未收敛则保留缺口并请求裁决；不限制后续节点对新主题继续探索。入口完成不等于需求已明确。

## Downstream Contract
Product Discovery 可消费原始意图、候选问题、场景、约束和未知项，不得假设定位、功能范围或 MVP 已批准。

下游必须消费 artifact 和 decisionRefs，不得从聊天上下文补齐未确认结论。

## State Changes
`INTAKE_READY → IDEA_INTAKE_IN_PROGRESS → IDEA_INTAKE_READY | WORKFLOW_BLOCKED`
