---
name: prd-workflow
description: 编排从模糊产品想法到已确认 PRD 与原型基线的产品需求流程。
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
CREATE、CHANGE、OPTIMIZE 进入产品域，或运行反馈被判断为产品问题/优化机会时触发。不接收没有项目标识和生命周期的孤立“写个 PRD”命令。

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
- 顺序调度 `idea-intake`、`product-discovery`、`Competitive-Analysis`、`product-definition`、`application-blueprint`、`feature-decision`、`PRD-Design`、`PRD-Review`、`Prototype-Design`、`Prototype-Review`；
- 校验证据、产物、决策和回退路径；
- 将产品问题路由回正确上游，不让下游补猜；
- 形成 UI/DEV/Testing 可消费的产品基线。

## Non-goals
- 不替原子 Skill 生成领域产物；
- 不替用户做定位、MVP、商业模式或重大架构取舍；
- 不把文件存在、模型自评或评审完成当作 Gate。

## Procedure
1. 读取 lifecycle 和现有基线；CREATE 走完整路径，CHANGE/OPTIMIZE 由 impact analysis 定位受影响阶段。
2. 执行 Intake、Discovery 和 Competitive Research；证据不足即阻塞。
3. 执行 Product Definition，等待目标用户、定位、非目标和成功指标确认。
4. 执行 Application Blueprint，冻结旅程、流程、异常、权限、状态和能力地图。
5. 执行 Feature Decision，等待 MVP、Later、Reject、Defer 和行为边界确认。
6. 将批准范围交 PRD-Design；PRD-Review 只审不改，问题回正确上游。
7. PRD 通过后交 ../../UI/Prototype-Design/Review；原型不得改变产品范围。
8. 输出 execution summary、manifest、decision、traceability 和下一 Workflow。

## Outputs
- intake、discovery-brief、research、product-definition、application-blueprint、feature-decision、prd、prototype artifact；
- 产品基线和决策链；
- `PASS`、`CONDITIONAL` 或 `BLOCKED` Gate。

## Evidence
PRD/原型必须能回链原始请求、研究证据、产品决策、蓝图和范围确认。技术实现问题交 DEV Workflow，并沿用 GitHub/OSS 研究策略。

## Gate
PASS：产品基线和原型批准，关键开放项为零；CONDITIONAL：例外已登记且有下游限制；BLOCKED：关键确认、证据、业务状态或范围决策缺失。

## Failure Route
研究不足回 Product Discovery/Competitive Analysis；定位冲突回 Product Definition；流程/状态缺口回 Application Blueprint；MVP/范围冲突回 Feature Decision；PRD 结构问题回 PRD-Design；原型问题回 Prototype-Design；技术未知交 DEV Workflow。

## Downstream Contract
UI/DEV/Testing 只消费 manifest 中 APPROVED 的产品 artifact；OPEN、ASSUMPTION、RECOMMENDATION 不得作为批准需求实现。

## State Changes
`INTAKE_READY → IDEA_INTAKE_IN_PROGRESS → DISCOVERY_IN_PROGRESS → COMPETITIVE_RESEARCH_IN_PROGRESS → PRODUCT_DEFINITION_IN_PROGRESS → APPLICATION_BLUEPRINT_IN_PROGRESS → FEATURE_DECISION_IN_PROGRESS → PRD_IN_PROGRESS → PRD_REVIEW_IN_PROGRESS → PRD_APPROVED → PROTOTYPE_IN_PROGRESS → PROTOTYPE_REVIEW_IN_PROGRESS → PROTOTYPE_APPROVED`。
