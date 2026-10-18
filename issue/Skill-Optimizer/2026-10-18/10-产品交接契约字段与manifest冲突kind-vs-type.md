# 产品交接契约 §4 与产物 manifest 契约字段冲突（kind vs type）

> 归属 skill：`product-workflow-contract` ｜ 日期：2026-10-18 ｜ 来源：评审（A-01）

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P0 |
| 标签 | `接口契约` / `产物格式` |
| 优化状态 | 处理中（本轮已改 shared/product-workflow-contract §4，待校验） |

## 现象

- `shared/product-workflow-contract.md` §4 用 `kind` 且只列 artifactId/kind/projectId/lifecycle/status/sourceRefs/evidenceRefs/decisionRefs/openItems/gate/allowDownstream；`shared/artifact-contract.md` §2 与 `governance/schemas/artifact-manifest.schema.yaml:3` 要求必填 `artifactId,type,path,lifecycle,owner,status,producedBy,producedAt`。
- kind 枚举缺 `journey-map`、`scope-decision`（artifact-registry 已登记、application-blueprint/feature-decision 实际产出）；gate/allowDownstream/openItems 不属 manifest 字段。
- 按 §4 写 manifest 会被 `validate_core.py artifact` 拒绝，正式产品交接必踩。

## 跟踪与证据

- .spec/体系评审/2026-10-18/A-prd-workflow.md A-01（含机检与字段对照）
- Lead 已改 shared/product-workflow-contract.md §4 + docs/PRD-Workflow-v2.md

## 期望 vs 实际

- **期望**：见「修复方向」中的验收判据。
- **实际**：见「现象」。

## 修复方向

1. §4 改为与 artifact-contract/schema 同构（type/path/owner/producedBy/producedAt），枚举以 artifact-registry 为唯一源；Gate/放行/开放项移出 manifest 的说明。
2. 同步 `docs/PRD-Workflow-v2.md` 产物类型清单。
3. 验收：按新 §4 写的 manifest 能通过 `python scripts/validate_core.py artifact`。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 本轮修复中；见对应审计报告 |
| 忽略理由 | — |
