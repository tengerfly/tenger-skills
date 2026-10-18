---
name: prd-workflow
description: 只编排模糊想法到批准 PRD/原型的产品阶段、用户决策与 Gate；不代替竞品研究、产品定义、蓝图、功能取舍、PRD 编写或评审。触发：从想法推进到原型的产品阶段编排、产品流程编排、推进产品阶段、多个产品阶段要串起来时（单点写/改 PRD 交 prd-design，单点评审交 prd-review）。
metadata:
  short-description: 编排产品发现、定义、蓝图、范围、PRD 和原型的阶段门禁。
---

# prd-workflow

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Task scope & context

先按 `../../shared/execution-profiles.md` 判断强度，需求读写按 `../../shared/requirements-context.md`。轻量 Demo/局部任务只保留确认的目标、边界、验收点与本领域必要产物，不要求下文的全套上游正式文档和建档；不得用摘要冒充批准或绕过相关阻塞。标准/完整及正式交接才执行下述 manifest、Gate、状态契约。资源按任务加载，不先通读全部 references。

## Purpose
把产品域原子 Skill 按证据和 Gate 串起来，从模糊入口建立可追踪的产品基线。成功标准是正式 PRD 和原型都建立在已确认的用户、问题、旅程、范围和行为边界上。

## Trigger
CREATE、CHANGE、OPTIMIZE 进入产品域，或运行反馈被判断为产品问题/优化机会时触发。孤立“写个 PRD”请求先识别范围、建立必要项目上下文；不要求用户预先了解项目标识或生命周期术语。

## Inputs
- lifecycle、projectId、用户请求或批准变更；
- `.spec/` 基线、manifest、decisions、traceability；
- 运行信号、研究证据和用户确认。

## Preconditions
- 项目基线已完成；
- 上游 artifact 可定位且状态清晰；
- 未提交变更不被覆盖；
- 产品决策责任人已明确。

## Responsibilities
- CREATE 默认走完整路径，CHANGE/OPTIMIZE 按影响分析选择受影响阶段；
- 顺序调度 `idea-intake`、`product-discovery`、`competitive-analysis`、`product-definition`、`application-blueprint`、`feature-decision`、`prd-design`、`prd-review`、`prototype-design`、`prototype-review`；
- 校验证据、产物、决策和回退路径；
- 将产品问题路由回正确上游，不让下游补猜；
- 形成 UI/DEV/auto-test 可消费的产品基线。

## Non-goals
- 不替原子 Skill 生成领域产物；
- 不替用户做定位、MVP、商业模式或重大架构取舍；
- 不把文件存在、模型自评或评审完成当作 Gate。

## Procedure
1. 〔REQUIRED · 开工前闸门核对〕调度任一原子 Skill 前，先读 `.spec/manifest.yaml` / `.spec/gates/` 中该节点所依赖上游 artifact 的 `status`、`version`、`gate`、`allowDownstream`、`blockedBy`（口径见 `../../shared/gate-policy.md` §6）。任一上游 `SUPERSEDED`、`gate` 非 `PASS`、或 `allowDownstream: false` ⇒ 不启动该节点；`currentState` 与 `nextAction` 不得指向关闸上游的下游，状态停在已注册的 `WORKFLOW_BLOCKED`；在 `.spec/workflow.yaml` 的 `blockedItems` 记 `BLK-*`（含 `owner`、`requiredInput`、`clearCondition`），`nextAction` 指回上游 owner。禁止以「下游先往前赶、上游慢慢补」「并行不空等」越过未清阻塞。
2. 读取 lifecycle 和现有基线；CREATE 走完整路径，CHANGE/OPTIMIZE 由 impact analysis 定位受影响阶段。
3. 按 `../../shared/workflow-visibility.md` 展示阶段、当前 Skill、待用户决策与下一步。执行 `idea-intake`、`product-discovery` 和 `competitive-analysis`；对标应用或用户明确要求竞品时必须交付功能全景，不能用入口问答替代。Discovery 缺口可用独立研究草稿补证后复核，不伪造 Gate。
4. 执行 `product-definition`，等待目标用户、定位、非目标和成功指标确认。
5. 执行 `application-blueprint`，冻结旅程、流程、异常、权限、状态和能力地图。
6. 执行 `feature-decision`：先向用户展示完整模块图，再分模块解释候选及取舍，等待明确版本的 MVP、Later、Reject、Defer 和行为边界确认；用户不清楚时先给调研信息/示例，不要求其自己补全全体系功能。
7. 将批准范围交 `prd-design`；`prd-review` 只审不改，问题回正确上游。
8. PRD 通过后交 `prototype-design`（构建）与 `prototype-review`（评审）；原型不得改变产品范围。
9. 输出 execution summary、manifest、decision、traceability 和下一 Workflow = `ui-workflow`（`PROTOTYPE_APPROVED → UI_IN_PROGRESS`）。

## Outputs
- intake、discovery-brief、research、product-definition、application-blueprint、feature-decision、prd、prototype artifact；
- 产品基线和决策链；
- `PASS`、`CONDITIONAL` 或 `BLOCKED` Gate。

## Evidence
PRD/原型必须能回链原始请求、研究证据、产品决策、蓝图和范围确认。技术实现问题交 DEV Workflow，并沿用 GitHub/OSS 研究策略。

## Gate
PASS：产品基线和原型批准，关键开放项为零；CONDITIONAL：例外已登记且有下游限制；BLOCKED：关键确认、证据、业务状态或范围决策缺失。

## Failure Route
研究不足回 `product-discovery`/`competitive-analysis`；定位冲突回 `product-definition`；流程/状态缺口回 `application-blueprint`；MVP/范围冲突回 `feature-decision`；PRD 结构问题回 `prd-design`；原型问题回 `prototype-design`；技术未知交 DEV Workflow。

## Downstream Contract
UI/DEV/auto-test 只消费 manifest 中 APPROVED 的产品 artifact；OPEN、ASSUMPTION、RECOMMENDATION 不得作为批准需求实现。产品域出口 `PROTOTYPE_APPROVED` 的合法下游 Workflow 是 `ui-workflow`（`PROTOTYPE_APPROVED → UI_IN_PROGRESS`）。

## State Changes
`INTAKE_READY → IDEA_INTAKE_IN_PROGRESS → IDEA_INTAKE_READY → DISCOVERY_IN_PROGRESS → DISCOVERY_READY → COMPETITIVE_RESEARCH_IN_PROGRESS → COMPETITIVE_RESEARCH_READY → PRODUCT_DEFINITION_IN_PROGRESS → PRODUCT_DEFINITION_READY → APPLICATION_BLUEPRINT_IN_PROGRESS → APPLICATION_BLUEPRINT_READY → FEATURE_DECISION_IN_PROGRESS → FEATURE_DECISION_READY → PRD_IN_PROGRESS → PRD_REVIEW_IN_PROGRESS → PRD_APPROVED → PROTOTYPE_IN_PROGRESS → PROTOTYPE_REVIEW_IN_PROGRESS → PROTOTYPE_APPROVED`。实际转换以 `governance/state-registry.yaml` 为准，按注册边核对 `from`/`to`，不自行新增或跳过状态。CHANGE/OPTIMIZE 复用同一阶段图，经 `impact-analysis` 定位起点（`IMPACT_ANALYSIS_IN_PROGRESS` 的出边按注册表选择目标阶段，含 `WORKFLOW_BLOCKED`；不另立第二套状态链）。
