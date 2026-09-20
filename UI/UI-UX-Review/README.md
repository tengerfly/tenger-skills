# UI-UX-Review —— UI/UX 设计稿评审 Skill

> 视觉稿产出到技术落地间的质量门禁：对照 PRD + 布局清单 + design-system 三源，独立第三方复审 UI-UX-Design 产出的设计稿。只查问题、找成因、给方向，不改稿。

## 一、定位

- 承接 UI-UX-Design（`.spec/设计稿/`），位于技术方案/开发前；Workflow 第⑦节点。
- 不信任生成方门禁结论；以对照源 + 真实渲染独立复核。
- 四维评审：结构零改动 / 文案一致 / 规范一致 / 渲染质量+可点击。
- 防死循环：修复判据 + 分级冻结 + 轮次上限 3。

## 二、评审维度

| 维度 | 清单 | 重点 |
|---|---|---|
| 载体与结构零改动 | layout-freeze-checklist | 防漏 + 防加戏 |
| 文案与字段一致性 | copywriting-consistency-checklist | 逐字比对 + 多余文案排查 |
| 视觉规范一致性 | visual-spec-consistency-checklist | 视觉值出 token；反 AI 味 |
| 视觉呈现与可交付 | rendered-quality-checklist | 渲染/死链/遮挡/资源 404 + 结构级可点击 + Nielsen 启发式 |
| 浏览器工具 | browser-inspection-guide | 全无报错停 |

## 三、闭环

问题 → 任务清单（待确认）→ 用户逐条裁决 → UI-UX-Design / Prototype-Design / PRD-Design 修复 → 复核只验本轮，轮次上限 3。

## 四、目录与产出

```
../UI-UX-Review/
├── SKILL.md / README.md / CONTEXT.md
├── references/（四清单 + browser-inspection-guide + known-issue-patterns 案例库）
├── assets/（dimension-review / summary / issue-list 模板）
└── .spec/设计评审/（四份报告 + 汇总 + 任务清单 + screenshots）
```