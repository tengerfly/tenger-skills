# ui-ux-design 质量门禁仍写「3 轮不收敛强制清 P0 后直接放行」（P0）

> 归属 skill：`ui-ux-design` ｜ 日期：2026-10-18 ｜ 来源：评审（UI-01）

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P0 |
| 标签 | `流程缺陷` / `门禁口径` |
| 优化状态 | 处理中（fixer 修复中） |

## 现象

- `UI/ui-ux-design/references/design-review-gate.md:110` 写「同一问题 3 轮不收敛 → 强制清零 P0 后直接放行，残留 P1 记入 PIPELINE 遗留问题」，并引 `shared/anti-deadloop.md §二.3`（现行文件无此节）。
- 该文件是 A 路径每次生成后必读的放行规则，违反 anti-deadloop v2 §3 与根 README「no force-pass rule」。
- 同族残留：prototype-review CONTEXT:23 + legacy-skill:68、prd-review CONTEXT:29/45/47、workflow/CONTEXT:22（已由各自范围修复/注记）。

## 跟踪与证据

- .spec/体系评审/2026-10-18/B-ui.md UI-01
- 机械 grep：force-pass 残留 6 处 + anti-deadloop 旧节号 40+ 处

## 期望 vs 实际

- **期望**：见「修复方向」中的验收判据。
- **实际**：见「现象」。

## 修复方向

1. 改为 v2：残留 P0⇒BLOCKED；残留 P1 不得 PASS、仅完整授权 CONDITIONAL；不自动第 4 轮；删除旧节号引用。
2. CONTEXT 补订正 D-xx；验收：活跃文件中「强制清 P0/直接放行/残留 P1 记遗留」清零（历史日志带「已撤销」注记除外）。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 本轮修复中；见对应审计报告 |
| 忽略理由 | — |
