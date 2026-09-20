# 同类视觉审查 Skill 结构样本（Agent Skill Samples）

> 用途：优化本 Skill 结构时的借鉴范本（只借鉴组织方式，不搬运内容）。

---

## 一、colbymchenry/frontend-audit-skill（gate 机制范本）

- measured visual-regression gate：拿 design PNGs 和 live renders 比对。
- OmniParser（ML 区域检测器）识别页面区块，递归走查 `design/` 文件夹；`/frontend-audit` 命令自动修 CSS 直到匹配。
- 借鉴点：「gate」概念（不达标不让过）+ ML 区域检测替代纯像素 diff。

## 二、draz26648/flutter-design-fidelity（token 强制范本）

- design-tokens / figma-to-widget / visual-verification；禁止硬编码视觉值，所有视觉属性走 token。
- 借鉴点：token 强制约束（已融入 decision-rules §五）。

## 三、KirillBaranov/figma-map（is/should diff 范本）

- ground-truth layer：每个元素记录 `is`（现状）→ `should`（应然）的 diff，闭环验证。
- 借鉴点：`is` vs `should` 的 diff 结构，天然适配「差异分级响应」。

## 四、robukh/figma-suite（0-100 评分范本）

- token sync / 组件库 / design system audits（评分 0–100）。
- 借鉴点：设计系统审计评分 0–100 量化输出，可作报告模板。

> 出处：github.com/colbymchenry/frontend-audit-skill、github.com/KirillBaranov/figma-map、github.com/robukh/figma-suite。
