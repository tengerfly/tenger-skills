# 像素级对比方法学（Pixel Methods）

> 用途：视觉还原走查时的量化方法参考。阈值见 `decision-rules.md`。

---

## 一、半透明叠加对比

- Figma overlay：把设计稿以 50% 透明度盖在实现页上，2x 分辨率下肉眼/算法找偏移。
- 断点至少覆盖 375 / 768 / 1024 / 1280 / 1440。

## 二、5-attempts 闭环（lobehub visual-pixel-perfect）

1. **implement**：按设计稿写 HTML/CSS。
2. **render**：Puppeteer/Playwright 无头渲染到指定视口。
3. **snapshot**：截设计稿 + 实现图，统一 2x 分辨率。
4. **compare**：pixelmatch 逐像素比对，输出 diff 图 + 偏差百分比（Web 0.5% / PDF 1.0%）。
5. **fix**：按 diff 改 CSS，最多 5 次 attempts，超次报告未达标区域并暂停。
- 目录约定：`.claude/visual/` 下放 `design/`、`render/`、`diff/`、`report.md`。

## 三、设计 token 绑定（治本）

- 视觉偏差根因常是硬编码魔法值；把颜色/间距/字号/圆角抽象成 Design Token（CSS 变量 / Style Dictionary），实现只引用 token。
- 三阶校验（hbddjk）：① Puppeteer + Resemble.js 像素偏差 ≤0.3% → ② Style Dictionary token 一致性 → ③ Cypress 交互保真。

## 四、交互还原量化（双轨）

- 视觉回归：Figma API + 前端实现 → 像素 Diff。
- 微交互量化：采集 hover/点击/过渡时长、缓动曲线 → 评分（过渡时长误差 ≤50ms、缓动函数匹配）。

## 五、反模式

- 只比对首屏，不扫断点。
- 容忍度一刀切（文本和纯色块用同一阈值）。
- 纯人工肉眼对，无 diff 图无量化。
- 修 CSS 无限循环（必须设 max attempts）。
- 只评静态，不评交互（按钮点了没反应也算还原失败）。

> 出处：lobehub visual-pixel-perfect、hbddjk 三阶校验、CSDN「像素之眼的自动化」。
