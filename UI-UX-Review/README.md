# UI-UX-Review —— UI/UX 设计稿评审 Skill

> UI/UX 设计稿评审是「视觉稿产出 → 技术落地」之间的关键质量门禁：把 UI-UX-Design 产出的视觉稿 HTML 对照 PRD + 布局清单 + design-system 三源做**独立第三方全面复审**，兜底生成方内部门禁的自查盲区。只查问题、找成因、给方向，绝不越界改稿。

---

## 一、核心定位与价值

- **承前启后**：接在 `UI-UX-Design` 产出设计稿（`.spec/设计稿/`）之后，位于 `Backend-Tech-Design` / `Frontend-Tech-Design` 之前；是 Workflow 链上第 ⑦ 节点。
- **独立兜底**：UI-UX-Design 自带内部门禁（布局零改动 / 规范一致 / 反 AI 味 / 文案保真），本 skill 不从其结论出发、以对照源 + 真实渲染为唯一证据独立复核，防自查走过场。
- **四维评审**：① 载体与结构零改动（防漏 + 防加戏）② 文案与字段一致性（逐字比对）③ 视觉规范一致性（token 溯源）④ 视觉呈现与可交付质量（浏览器真实渲染 + 结构级可点击性验证，抓死元素）。
- **防评审死循环三招内建**：修复判据 + 分级冻结 + 轮次上限 3，避免「改完再评又出新问题」无限循环。
- **闭环机制**：只产出问题清单（含修复判据）、成因剖析与修改方向，经用户裁决为 `已确认` 后，交由 `UI-UX-Design`（或 `Prototype-Design` / `PRD-Design`）修复并回填状态，最终复核放行。

---

## 二、评审维度与职责划分

| 维度 | 参考规范清单 | 重点检查内容 |
|---|---|---|
| **载体与结构零改动** | `references/layout-freeze-checklist.md` | 布局清单的页面/弹框/抽屉/区块/元素/跳转在设计稿中一一对应（防漏）+ 无依据新增区块/按钮/装饰排查（防加戏） |
| **文案与字段一致性** | `references/copywriting-consistency-checklist.md` | 标题/CTA/列名/字段标签/提示语与 PRD 逐字比对 + PRD 未要求的多余文案排查；Mock 数据真实自洽 |
| **视觉规范一致性** | `references/visual-spec-consistency-checklist.md` | 页面一切视觉值（色/字号/间距/圆角/阴影/组件样式/图标）出自 design-system token；反 AI 味 12 条 |
| **视觉呈现与可交付质量** | `references/rendered-quality-checklist.md` | 浏览器真实渲染：控制台报错/死链/层级遮挡/资源 404 + **结构级可点击性验证**（该跳转入口真实可点、死元素识别）+ 截图存证 + **Nielsen 十项启发式主观体验交叉核对** |
| **浏览器工具硬门禁** | `references/browser-inspection-guide.md` | 开工预检 Playwright → browser-use → 其他（如 agent-browser），任一可用即渲染走查；全无则报错等安装，不产出文档 |

---

## 三、目录结构

```
UI-UX-Review/
├── SKILL.md                                 # 主流程、严重度定义与六大铁律
├── CONTEXT.md                               # 术语表 + 决策日志（D-01~D-08）
├── README.md                                # 本文档
├── references/                              # 标准化检查清单与操作指引
│   ├── layout-freeze-checklist.md           # ① 载体与结构零改动清单
│   ├── copywriting-consistency-checklist.md # ② 文案与字段一致性清单
│   ├── visual-spec-consistency-checklist.md # ③ 视觉规范一致性清单
│   ├── rendered-quality-checklist.md        # ④ 渲染质量 + 可点击性 + Nielsen 启发式清单
│   └── browser-inspection-guide.md          # 浏览器渲染与点击验证指引
└── assets/                                  # 产出文档标准化模板
    ├── dimension-review-template.md         # 维度评审报告模板
    ├── summary-template.md                  # 评审汇总报告模板
    └── issue-list-template.md               # 评审任务清单模板
```

---

## 四、产出物落位约定

所有评审产出物统一落盘在被开发项目的 `.spec/设计评审/` 目录下：

```
.spec/设计评审/
├── 载体与结构零改动评审.md
├── 文案与字段一致性评审.md
├── 视觉规范一致性评审.md
├── 视觉呈现与可交付质量评审.md
├── 设计稿评审汇总报告.md
├── 任务清单.md                              # 状态：待确认 -> 已确认 -> 已修复/已忽略
└── screenshots/                            # 浏览器截图存证目录（硬性前置产物）
    └── ISSUE-xxx-xxx.png
```

> `.spec/设计评审/任务清单.md` 已被 `UI-UX-Design` SKILL 步骤 2（开工检测）/ 步骤 9（收尾回填）引用——本 skill 落此目录即接上修复闭环，无需改动 UI-UX-Design。
