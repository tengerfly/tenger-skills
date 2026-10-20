# UI-UX-Review —— UI/UX 设计稿评审 Skill

> 视觉稿产出到技术落地间的质量门禁：对照 PRD + 布局清单 + design-system 三源，独立第三方复审 UI-UX-Design 产出的设计稿。只查问题、找成因、给方向，不改稿。

## 一、定位

- 承接 UI-UX-Design（`.spec/设计稿/`），位于技术方案/开发前；Workflow 第⑦节点。
- 不信任生成方门禁结论；以对照源 + 真实渲染独立复核。
- 四维评审：结构零改动 / 文案一致 / 规范一致 / 渲染质量+可点击。评审判断只在隔离上下文：四维各派 1 个独立 fresh 评审子代理（互不可见）+ 1 个独立汇总子代理，产出/修订/自检上下文只编排不自审。
- 防死循环：修复判据 + 分级冻结 + 轮次上限 3。

## 二、评审维度

| 维度 | 清单 | 重点 |
|---|---|---|
| 载体与结构零改动 | layout-freeze-checklist | 防漏 + 防加戏 |
| 文案与字段一致性 | copywriting-consistency-checklist | 逐字比对 + 多余文案排查 |
| 视觉规范一致性 | visual-spec-consistency-checklist | 视觉值出 token；反 AI 味 |
| 视觉呈现与可交付 | rendered-quality-checklist | 渲染/死链/遮挡/资源 404 + 结构级可点击 + 跨页不变量（§七 导航外壳跨页全等与页内标题栏对齐实测表）+ 可见层内部语扫描（§八）+ Nielsen 启发式 |
| 浏览器工具 | browser-inspection-guide | 全无报错停 |

## 三、闭环

问题 → 任务清单（P0 须用户确认；P1/P2 由执行方按 `../../shared/ruling-policy.md` 裁决并记 `.spec/rulings.md`）→ UI-UX-Design / Prototype-Design / PRD-Design 修复 → 复核只验本轮，轮次上限 3。

**评审隔离（硬性）**：评审判断必须由隔离上下文作出——四维各派 1 个独立 fresh 评审子代理（互不可见），汇总由独立汇总子代理完成；评审者只拿评审包（`../../shared/templates/review-package.md`），不继承产出会话历史、草稿或自检结论；产出/修订/自检上下文只做编排（解析、闸门核对、建包、派发、收产物核验、落 Gate），不得做成维度判断。无隔离能力 ⇒ 写评审包 + `dispatch-prompt.md` 交新会话，仍无 ⇒ `BLOCKED`；报告须含 §0.5 隔离记录（缺记录或 `producedByContextInvolved` 非 false ⇒ Gate 只能 `BLOCKED`）。口径 `../../shared/review-context-isolation.md`。

## 四、目录与产出

```
../ui-ux-review/
├── SKILL.md / README.md / CONTEXT.md
├── references/（四清单 + browser-inspection-guide + known-issue-patterns 案例库）
├── assets/（dimension-review / summary / issue-list 模板）
└── .spec/设计评审/（评审包 + dispatch-prompt + 四份报告 + 汇总 + 任务清单 + screenshots；落被评审项目根，非本 skill 目录）
```