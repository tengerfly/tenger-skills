# 埋点规范需落地到各 skill（监听主通道建设）

> 归属 skill：`Skill-Optimizer` ｜ 日期：2026-09-04 ｜ 来源：用户

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P1 |
| 标签 | 流程缺陷 |
| 优化状态 | 已沉淀 |

## 现象

D-03 定了「记录 = 埋点为主 + 兜底」，但埋点规范（`instrumentation-guide.md`）只是文档，12 个专业 skill 的 SKILL.md 里没有埋点节，「监听」主通道实际未接通。

## 期望 vs 实际

- **期望**：各 skill 执行收尾时自查上报问题到 issue 池
- **实际**：各 skill SKILL.md 无埋点职责，主通道空转

## 修复方向

给 12 个专业 skill 的 SKILL.md 各追加「运行问题埋点（收尾自查）」节，引用统一规范。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 12 个专业 skill（Competitive-Analysis / PRD-Design / PRD-Review / Prototype-Design / Prototype-Review / Backend-Tech-Design / Frontend-Tech-Design / Tech-Review / Backend-Dev / Frontend-Dev / Code-Review / Testing） |
| 沉淀位置 | 各 SKILL.md 末尾新增「运行问题埋点（收尾自查）」节；规范源 `../Skill-Optimizer/references/instrumentation-guide.md`；模板 `../Skill-Optimizer/assets/issue-template.md` |
