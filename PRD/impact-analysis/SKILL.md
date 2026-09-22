---
name: impact-analysis
description: 分析已登记变更对产品行为、接口、数据、权限、测试、发布和运行指标的影响。
metadata:
  short-description: 分析已登记变更对产品行为、接口、数据、权限、测试、发布和运行指标的影响。
---

# impact-analysis

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## Purpose
Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.

在改变外部行为前形成影响面和交付策略，防止下游只改一个文件而遗漏契约、迁移、回滚和监控。

## Trigger
`CHANGE` 或 `OPTIMIZE` 任务已通过 Intake；巡检/评审发现需要改变行为时也可触发。

## Inputs
- 已批准或待确认的 intake；
- 项目基线、PRD/原型/技术方案、接口与数据清单；
- 相关组件知识、OSS 研究和运行指标；
- 不可改变行为、兼容性和发布约束。

## Preconditions
- Intake Gate 通过；
- 基线可追踪；
- 读取 `../../shared/traceability.md`、`../../shared/gate-policy.md`；
- 技术选型问题须遵守 `../../shared/oss-research-policy.md`，不能只引用模型记忆。

## Responsibilities
- 列出受影响产物、模块、用户旅程、接口、数据、权限、测试、发布和可观测性；
- 区分事实影响、推断影响和待验证影响；
- 给出最小变更路径、风险、回滚和需要确认的决策；
- 将任务路由到 PRD/UI/DEV/auto-test/Release。

## Non-goals
- 不写最终技术实现；
- 不直接改数据库、代码或生产配置；
- 不把“可能受影响”伪装成已确认影响。

## Procedure
1. 读取基线和 intake，建立影响对象清单。
2. 对每个对象检查外部行为、接口/数据、权限、安全、性能、测试、发布、监控和资产授权。
3. 检查现有组件和 GitHub 同域实现；若证据不足记录 `OPEN`。
4. 生成变更切片：必须同步改变、可以延后、明确不改变。
5. 为每个高风险项定义验证、保护指标、回滚和确认人。
6. 更新 traceability 和 workflow，只有 Gate 通过才能进入实现。

## Outputs
- `.spec/impact/<id>.md`；
- 影响矩阵和变更切片；
- 风险/回滚/验证清单；
- 决策记录与下游任务委托；
- manifest 与 traceability 更新。

## Evidence
基线文件、接口/迁移定位、测试结果、运行指标、已核验 OSS 源码位置和用户决策。没有运行数据时明确 `OBSERVABILITY_GAP`。

## Gate
`PASS`：影响面、验证和回滚清楚；`CONDITIONAL`：可控缺口已登记且允许下游；`BLOCKED`：关键影响未知、存在不可接受风险或需要的用户决策未确认。

## Failure Route
产品规则冲突转 PRD；接口/数据不一致转技术方案；高影响线上变化转 Incident/Release；证据无法取得则停止，不用猜测推进。

## Downstream Contract
下游收到受影响对象、批准范围、不可改变行为、变更切片、风险、验证、回滚、研究证据、保护指标和 Gate；不得把未影响对象当作无需检查。

## State Changes
`INTAKE_READY → IMPACT_ANALYSIS_IN_PROGRESS → PRD_IN_PROGRESS | UI_IN_PROGRESS | DEV_IN_PROGRESS | WORKFLOW_BLOCKED`
