# prd-workflow State Changes 6 条转移不在 state-registry（P0）

> 归属 skill：`prd-workflow` ｜ 日期：2026-10-18 ｜ 来源：评审（A-02）

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P0 |
| 标签 | `流程缺陷` / `接口契约` |
| 优化状态 | 处理中（fixer 修复中） |

## 现象

- `PRD/prd-workflow/SKILL.md` State Changes 声明 13 段链，跳过 6 个 `*_READY`：IDEA_INTAKE_IN_PROGRESS→DISCOVERY_IN_PROGRESS 等 6 条在 `governance/state-registry.yaml` 126 条边中不存在。
- 其余 12 个原子 skill 的 State Changes 逐边机检全部合法，仅 prd-workflow 失配。

## 跟踪与证据

- .spec/体系评审/2026-10-18/A-prd-workflow.md A-02
- 机检：126 条注册边，prd-workflow 6 条非法

## 期望 vs 实际

- **期望**：见「修复方向」中的验收判据。
- **实际**：见「现象」。

## 修复方向

1. 状态链补全 6 个 `*_READY`（合法链见报告/Lead 已机检），并注明实际转换以 registry 为准；补 CHANGE/OPTIMIZE 口径。
2. 验收：按新链逐边机检全部命中 registry；三定向校验 PASS。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 本轮修复中；见对应审计报告 |
| 忽略理由 | — |
