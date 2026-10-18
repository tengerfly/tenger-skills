# UI

UI/UX 设计域。承接 PRD 域已批准的产品结构和原型，产出可交付的设计稿与视觉/交互验收结果。

## 主流程

`Prototype-Design`（兼容入口，由 `prd-workflow` 调度）→ `Prototype-Review`（兼容入口，同上）→ `UI-UX-Design` → `UI-UX-Review`；实现完成后可独立调用 `Fidelity-Review` 做页面还原度验收。

## 边界

- 原型负责结构与交互闭环，UI 设计稿负责视觉唯一应然；两者不能互相替代。
- 设计评审与还原度评审只审不改，产出带证据的问题清单和回退方向。
- 设计稿生成前必须冻结载体、布局清单和 design system；不在 UI 阶段擅自增加 PRD 未批准的功能。
