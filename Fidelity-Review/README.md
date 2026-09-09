# Fidelity-Review —— 页面还原度评审 Skill

> 状态：✅ 定稿
> 定位：只审不改；截图必证、成因必写、每条附修改建议。对照 UI 设计稿逐页评前端实现页的视觉/交互/超长文案问题。

## 一、三大评审面

1. 视觉还原：布局/层级/颜色/字号/间距/圆角/阴影/图标/状态（含 10 大 UI 状态）/暗色/窄屏与设计稿一致；数值项用 axe-core。
2. 交互还原：可点元素能点、反馈正确、方式一致、普适交互正常；不含业务逻辑正确性。
3. 超长文案专项：真实/极端长文案下不溢出、遮挡、换行错乱、布局崩坏。

## 二、核心

| 项 | 内容 |
|---|---|
| 输入 | 前端页面 + 设计稿基准（A：`.spec/设计稿/`；B：外部稿，需标注目测）+ 可选 PRD/原型辅助 |
| 输出 | 独立：报告 + 任务清单 + screenshots；Testing 场景：轻量 mini-issue |
| 边界 | 只评实现页 vs 设计稿；业务逻辑归 Testing、契约/架构归 Code-Review、设计稿本身归 UI-UX-Review |
| 浏览器 | 硬依赖，全无报错停 |

## 三、流程

```
输入解析 → 浏览器预检 → 页面×基准映射（用户确认）→ 双开截图+点击验证 → 视觉+交互走查
→ 长文案专项 → 分级报告 → 独立（任务清单）或 Testing（mini-issue）
```

P0/P1 阻断、P2 用户裁决；复核只验本轮，轮次上限 3。

## 四、目录与产出

```
Fidelity-Review/
├── SKILL.md / README.md / CONTEXT.md
├── references/（visual / interaction / overflow / design-source / browser / decision-rules / case-library）
├── assets/（review-report / issue-list / mini-issue 模板）
└── .spec/页面还原评审/
```