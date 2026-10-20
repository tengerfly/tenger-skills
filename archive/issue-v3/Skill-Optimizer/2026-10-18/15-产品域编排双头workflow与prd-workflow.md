# 产品域编排双头：workflow 直连 idea-intake 且全文不提 prd-workflow（待裁决）

> 归属 skill：`workflow / prd-workflow` ｜ 日期：2026-10-18 ｜ 来源：评审（A-09）

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P1 |
| 标签 | `流程缺陷` / `边界不清` |
| 优化状态 | 处理中（Lead 按方案①统一路由） |

## 现象

- `workflow/SKILL.md:75`「归 CREATE 并进入需求域（idea-intake）」、:87「CREATE -> PRD -> …」，全文不提 `prd-workflow`；`governance/workflow-registry.yaml:21-22` 却把 prd-workflow 登记为 childWorkflow，根 README 也称 prd-workflow owns product-domain sequence。
- 同一职责双头调度，下游不知道该跟哪个编排。

## 跟踪与证据

- .spec/体系评审/2026-10-18/A-prd-workflow.md A-09
- Lead 已改 workflow/SKILL 路由与 State Changes（方案①）

## 期望 vs 实际

- **期望**：见「修复方向」中的验收判据。
- **实际**：见「现象」。

## 修复方向

1. 二选一：①根 workflow 改为「进入产品域编排 prd-workflow」，删除直连 idea-intake 表述（本轮采用）；②删除 registry 子流程定位并声明 prd-workflow 仅独立进入。
2. 验收：workflow/SKILL 与 registry/README 对产品域编排的描述一致。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 本轮修复中；见对应审计报告 |
| 忽略理由 | — |
