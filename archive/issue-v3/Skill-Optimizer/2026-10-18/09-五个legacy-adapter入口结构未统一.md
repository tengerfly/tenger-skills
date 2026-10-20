# 5 个 legacy-adapter skill 结构未统一到 v2 入口（registry 允许但风格不一致）

> 归属 skill：`Skill-Optimizer`（体系一致性） ｜ 日期：2026-10-18 ｜ 来源：体检

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P2 |
| 标签 | `流程缺陷` / `产物格式` |
| 优化状态 | 待处理（需评估工作量后决定是否本轮修） |

## 现象

45 个 SKILL.md 中 5 个（`DEV/tech-review`、`Other/essence-distill`、`Other/fact-check`、`Other/source-reading`、`UI/fidelity-review`）为 `legacy-adapter`：frontmatter 无 `metadata.contract-level`，正文为旧式 `一、…七、运行问题埋点` 结构，缺 `Purpose/Trigger/…/State Changes` 等 v2 必备章节。其余 40 个入口（v1/v2/legacy-wrapper）均含这些章节。

## 跟踪与证据

- 证据：本轮脚本核对 45 个 SKILL.md 的章节集合；`shared/legacy-skill-adapter.md` 定义该级别；`validate_core.py skill-contract` 放行 legacy-adapter。
- 影响：同一套体系出现两种入口结构；跨应用安装后，宿主侧展示/解析风格不一致；模型首次读到的结构也不同。
- 根因与归属：已确认——registry 显式允许 legacy-adapter 渐进迁移，但未在 README/手册声明该例外，也未排期统一。

## 期望 vs 实际

- **期望**：所有可安装入口至少统一暴露 common sections（或文档明确声明 legacy-adapter 例外与迁移计划）。
- **实际**：5 个入口静默例外，使用者无法从文档得知。

## 修复方向

1. 低风险选项：在 README/说明书中声明「5 个 legacy-adapter 为兼容入口，结构暂不统一，迁移另排期」。
2. 彻底选项：为 5 个 skill 增补 v2 必备章节（保留旧正文），并改为 legacy-wrapper/v2；工作量大，需单独一轮 + eval 重锚。
3. 本轮先做 1，2 记入 backlog。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（待处理） |
| 沉淀位置 | — |
| 忽略理由 | — |