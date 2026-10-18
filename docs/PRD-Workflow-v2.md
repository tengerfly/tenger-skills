# PRD Workflow v2

> 更新时间：2026-09-20

## 目标

产品设计域已从“竞品分析 → PRD → 原型”的大而全线性逻辑，重构为证据、决策和用户确认驱动的产品阶段图：

```text
Idea-Intake
→ Product-Discovery
→ Competitive-Analysis
→ Product-Definition
→ Application-Blueprint
→ Feature-Decision
→ PRD-Design
→ PRD-Review
→ Prototype-Design
→ Prototype-Review
```

## 核心边界

- 模糊想法不再直接进入 PRD；
- `FACT / EVIDENCE / INFERENCE / ASSUMPTION / RECOMMENDATION / DECISION / OPEN` 分开记录；
- 产品定位、目标用户、非目标、MVP、预算、外部依赖、关键业务规则和重大取舍必须等待用户/授权责任人确认；
- 产品定义层负责问题、用户、价值和范围；应用蓝图负责旅程、业务流程、异常、权限、状态和能力地图；Prototype 只承接已批准的产品结构；
- PRD/原型评审只审不改，问题回退到正确的上游 Skill，不允许下游用补丁掩盖上游定义缺口。

## 兼容迁移

`Competitive-Analysis`、`PRD-Design`、`PRD-Review`、`Prototype-Design`、`Prototype-Review` 仍可用，但已成为受契约治理的兼容入口。旧版成熟逻辑完整保存在各目录的 `references/legacy-skill.md`，原有 references/assets 保留；新的职责边界由各目录 `SKILL.md` 和五个新原子 Skill 执行。

## 产物和追踪

新阶段产物使用 `.spec/manifest.yaml` 登记，字段名与必填项以 `shared/artifact-contract.md` §2 与 `governance/schemas/artifact-manifest.schema.yaml` 为准（即 `type`/`path`/`owner`/`producedBy`/`producedAt` 等，不使用 `kind`）。产品域常用类型：

- `intake` / `discovery-brief` / `research`
- `product-definition` / `application-blueprint`
- `journey-map`
- `feature-decision` / `scope-decision`
- `prd` / `prototype` / `prototype-review`

完整枚举与逐型 required 以 `governance/artifact-registry.yaml` 为唯一源。每个阶段必须登记 `sourceRefs`、`evidenceRefs`、`decisionRefs`；`gate`/`allowDownstream` 记在 `.spec/workflow.yaml` 与 `.spec/gates/`，不写进 manifest。只有 `APPROVED` artifact 才能驱动下游；OPEN 和 ASSUMPTION 不得伪装成需求事实。

## 研究逻辑保留

竞品分析继续保留多来源证据、数据禁编造、预测标注、多方口径并列、独立画像和横向比较。技术方案阶段继续强制执行 `shared/oss-research-policy.md`，先查 GitHub/官方源码、测试、许可证和版本，再形成采用/借鉴/不采用决策。

## 验证

```powershell
.\scripts\validate-system.ps1
```

黄金场景覆盖：完整 CREATE 产品路径、CHANGE 受影响阶段重做，以及核心问题无证据时阻塞正式 PRD。