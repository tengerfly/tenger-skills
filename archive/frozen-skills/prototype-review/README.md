# Prototype-Review —— 原型评审 Skill

> 产品设计通向技术落地的质量门禁。目标：逻辑闭环、PRD/原型文案一致、内容无遗漏、防加戏。只审不改。

## 一、定位

- 承接 Prototype-Design，位于技术方案/开发之前。
- 只产问题清单、成因、修改方向；P0 经用户确认、P1/P2 由执行方裁决后交 Prototype-Design（原型）/ PRD-Design（PRD）修复，复核放行。

## 二、评审维度

| 维度 | 清单 | 重点 |
|---|---|---|
| 页面与载体完整性 | page-completeness-checklist | 防漏 + 防加戏；载体形式、导航层级 |
| 文案与字段一致性 | copywriting-consistency-checklist | 标题/CTA/提示/列名逐字比对 + 多余文案排查 |
| 交互与流程闭环 | interaction-closure-checklist | 无死胡同；弹框三态；正逆向分支；空载错满状态 |
| 原型实现质量 | prototype-quality-checklist | console 无错、无遮挡、可交互；不查视觉精修 |
| 浏览器工具 | browser-inspection-guide | 硬依赖（检测顺序 / 两级行为 / 报错文案见 `../../shared/browser-policy.md`）；全无报错停 |

## 三、流程与闭环

```
资产解析+预检 → 映射基准 → 截图走查+源码审查（双通道互证）→ 四维对照评审+四份报告
→ 汇总 → 任务清单（P0 须用户确认；P1/P2 执行方裁决）→ 修复回填 → 复核（只验本轮，轮次上限 3：满 3 轮仍未收敛：P0 残留 BLOCKED；P1 残留仅可授权 CONDITIONAL）→ 双向沉淀判定
```

P0 阻断且须用户确认；P1/P2 由执行方按 `../../shared/ruling-policy.md` 裁决；每条附修复判据与建议修改方，裁决记 `.spec/rulings.md`。

> **评审上下文隔离（2026-10-19 起硬性，legacy 保留）**：本 skill 的四维评审（含 `references/legacy-skill.md` 的 legacy 四维流程）只能在隔离评审子代理内执行——四维各 1 个 fresh 评审子代理（互不可见）+ 1 个独立汇总子代理，产出 / 修订原型的上下文不得自审；无隔离能力 ⇒ `BLOCKED`（规则见 `../../shared/review-context-isolation.md`，报告 §0.5 记隔离证据）。

## 四、目录

```
../prototype-review/
├── SKILL.md
├── README.md
├── CONTEXT.md
├── references/   # 四份清单 + browser-inspection-guide + known-issue-patterns（案例库）
├── assets/       # dimension-review / summary / issue-list 模板
└── .spec/原型评审/ # 四维报告 + 汇总 + 任务清单 + screenshots（落被评审项目根，非本 skill 目录）
```