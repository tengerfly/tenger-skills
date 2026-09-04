# Prototype-Review —— 原型评审 Skill

> 原型评审是产品设计阶段通向技术落地的关键质量门禁。通过将已生成的原型工程与 PRD 需求文档做全量双向对齐，保证页面无遗漏、文案无偏差、链路全闭环、质量无硬伤。

---

## 一、核心定位与价值

- **承前启后**：接在 `Prototype-Design` 产出高保真原型之后，位于 `Backend-Tech-Design` 与 `Frontend-Tech-Design` 之前。
- **守门把关**：避免前端/后端工程师依照有遗漏、有歧义或未闭环的原型进行架构设计与编码，大幅降低后续返工成本。
- **闭环机制**：只产出问题清单、成因剖析与修改方向，经用户裁决确认为 `已确认` 后，交由 `Prototype-Design` 或 `PRD-Design` 精准修复并回填状态，最终复核放行。

---

## 二、评审维度与职责划分

| 维度 | 参考规范清单 | 重点检查内容 |
|---|---|---|
| **页面与载体完整性** | `references/page-completeness-checklist.md` | PRD 功能点与原型页面的映射覆盖（防漏）+ 无依据的冗余按钮/区块/装饰排查（防加戏）；独立页、弹框、抽屉的载体形式是否合规；导航层级与面包屑。 |
| **文案与字段一致性** | `references/copywriting-consistency-checklist.md` | 标题、CTA 按钮、Toast 提示、表格列名与 PRD 原文逐字比对 + PRD 未要求的多余文案排查；表单 Label、必填星号、占位符对齐。 |
| **交互与流程闭环** | `references/interaction-closure-checklist.md` | 页面无死胡同；弹框打开/关闭/确认三态闭环；全流程正向与逆向分支畅通；空/载/错/满全状态覆盖。 |
| **原型自身质量** | `references/prototype-quality-checklist.md` | 浏览器控制台无报错；无布局错位与层级遮挡；拒绝廉价 AI 模板感；组件可正常交互。 |
| **浏览器工具硬门禁** | `references/browser-inspection-guide.md` | 开工预检 Playwright → browser-use → 其他浏览器工具（如 agent-browser），任一可用即截图存证；全无则报错提醒安装，不工作。 |

---

## 三、目录结构

```
Prototype-Review/
├── SKILL.md                                 # 主流程、严重度定义与五大铁律
├── README.md                                # 模块定位与使用指引
├── references/                              # 标准化检查清单与操作指引
│   ├── page-completeness-checklist.md       # 页面与载体完整性清单
│   ├── copywriting-consistency-checklist.md # 文案与字段一致性清单
│   ├── interaction-closure-checklist.md     # 交互与流程闭环清单
│   ├── prototype-quality-checklist.md       # 原型自身实现质量清单
│   └── browser-inspection-guide.md          # 浏览器检测与截图指引
└── assets/                                  # 产出文档标准化模板
    ├── dimension-review-template.md         # 维度评审报告模板
    ├── summary-template.md                  # 评审汇总报告模板
    └── issue-list-template.md               # 评审任务清单模板
```

---

## 四、产出物落位约定

所有评审产出物统一落盘在被开发项目的 `.spec/原型评审/` 目录下：

```
.spec/原型评审/
├── 页面与载体完整性评审.md
├── 文案与字段一致性评审.md
├── 交互与流程闭环评审.md
├── 原型自身质量评审.md
├── 原型评审汇总报告.md
├── 任务清单.md                              # 状态：待确认 -> 已确认 -> 已修复/已忽略
└── screenshots/                            # 截图存证目录（仅在工具可用时生成）
    └── ISSUE-xxx-xxx.png
```
