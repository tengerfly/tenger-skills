---
name: change-intake
description: 把模糊请求登记为可追踪的生命周期任务并完成初步分类。
metadata:
  short-description: 把模糊请求登记为可追踪的生命周期任务并完成初步分类。
---

# change-intake

## Purpose
Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.

把用户请求从自然语言转成有范围、有成功标准、有证据边界的任务入口。它不替用户批准产品或架构决策，只负责让后续决策可以被正确承接。

## Trigger
用户说“做一个”“改一下”“优化”“修复”“重构”、提出新需求，或运行反馈需要形成工程任务时触发。

## Inputs
- 原始请求与用户目标；
- 项目基线、当前版本和未提交变更；
- 相关 `.spec/` 产物、反馈、日志或指标；
- 用户已明确的范围、限制、截止时间和授权。

## Preconditions
- 先检查项目路径、分支和工作区，不覆盖未提交变更；
- 读取 `../../shared/lifecycle-contract.md` 和 `../../shared/evidence-before-claims.md`；
- 不确定的模式、规则或成功指标标记 `OPEN`；
- 不把现有代码行为自动当成批准需求。

## Responsibilities
- 原始请求登记；
- 识别 `CREATE/CHANGE/DEFECT/REFACTOR/INCIDENT/OPTIMIZE`；
- 记录范围、非目标、成功标准、风险和下一步；
- 判断是否需要 Project Onboarding、Impact Analysis 或 Defect Triage。

## Non-goals
- 不分析完整技术方案；
- 不修复代码、不改产品范围、不替用户做高风险确认；
- 不把“模型建议”写成用户决策。

## Procedure
1. 为任务生成唯一 `INTAKE-*`，原文逐字保存并标注来源。
2. 把目标、问题、期望结果、不可改变行为、约束和未知项拆成表格。
3. 用生命周期契约逐项判断；无法区分时保留多个候选并列出最小澄清问题。
4. 估算影响领域和风险等级，列出需要的证据，不提前假设实现。
5. 写入 manifest、workflow 和 traceability；给出下一 Skill、Gate 和停止条件。

## Outputs
- `.spec/intake/<id>.md`；
- `.spec/manifest.yaml` 增加 intake artifact；
- `.spec/workflow.yaml` 写入模式、状态、Gate、nextAction；
- `.spec/traceability.yaml` 建立原始请求到任务的关系；
- 一份不超过三个关键问题的确认清单。

## Evidence
原始用户消息、文件/版本定位、基线命令输出、已存在产物和用户确认。所有推断必须写出推理链；没有证据的内容为 `OPEN`。

## Gate
`PASS`：模式、范围、成功标准和下一动作清楚；`CONDITIONAL`：存在已登记的未知项且明确允许下游；`BLOCKED`：模式或授权无法确定，或关键基线缺失。

## Failure Route
缺少项目上下文转 `project-onboarding`；疑似线上故障转 `defect-triage`；外部行为变更转 `impact-analysis`；纯内部结构问题转 `refactor-planning`；用户决策冲突时暂停并请求确认。

## Downstream Contract
下游收到原始请求、生命周期候选/结论、范围、成功标准、非目标、证据索引、未知项、风险、用户决策和下一步，不得自行补齐未声明的业务规则。

## State Changes
`INTAKE_REQUESTED → DISCOVERY_IN_PROGRESS → INTAKE_READY | WORKFLOW_BLOCKED`
