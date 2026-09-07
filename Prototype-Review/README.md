# Prototype-Review —— 原型评审 Skill

> 产品设计通向技术落地的质量门禁。目标：逻辑闭环、PRD/原型文案一致、内容无遗漏、不防加戏。只审不改。

## 一、定位

- 承接 Prototype-Design，位于技术方案/开发之前。
- 只产问题清单、成因、修改方向；经用户裁决后交 Prototype-Design（原型）/ PRD-Design（PRD）修复，复核放行。

## 二、评审维度

| 维度 | 清单 | 重点 |
|---|---|---|
| 页面与载体完整性 | page-completeness-checklist | 防漏 + 防加戏；载体形式、导航层级 |
| 文案与字段一致性 | copywriting-consistency-checklist | 标题/CTA/提示/列名逐字比对 + 多余文案排查 |
| 交互与流程闭环 | interaction-closure-checklist | 无死胡同；弹框三态；正逆向分支；空载错满状态 |
| 原型实现质量 | prototype-quality-checklist | console 无错、无遮挡、可交互；不查视觉精修 |
| 浏览器工具 | browser-inspection-guide | Playwright → browser-use → 其他；全无报错停 |

## 三、流程与闭环

```
资产解析+预检 → 映射基准 → 截图走查+源码审查（双通道互证）→ 四维评审 → 四份报告
→ 汇总 → 任务清单+逐条确认 → 修复回填 → 复核（只验本轮，轮次上限 3）
```

P0/P1 阻断，P2 由用户裁决；每条附修复判据与建议修改方。

## 四、目录

```
Prototype-Review/
├── SKILL.md
├── README.md
├── CONTEXT.md
├── references/   # 四份清单 + browser-inspection-guide
├── assets/       # dimension-review / summary / issue-list 模板
└── .spec/原型评审/ # 四维报告 + 汇总 + 任务清单 + screenshots
```