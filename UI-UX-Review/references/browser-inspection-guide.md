# 浏览器渲染与点击验证指引

> 环境预检 → 工具选择 → 无工具不工作。

## 一、检测顺序
1. Playwright：起静态服务/打开 HTML，渲染 + 点击验证。
2. browser-use：不可用时替代。
3. 其他浏览器工具（agent-browser 等）：可用即用。
4. 全不可用 → ⛔ 报错停止，不产出评审文档。

## 二、渲染
- 首选本地静态服务（npx serve / python -m http.server）；资源全内联/https 时可用 file://。
- 逐页记录可否打开、控制台报错、关键视觉是否符合 design-system。

## 三、截图与点击
- P0/P1 缺陷才截图，存 `.spec/设计评审/screenshots/ISSUE-[编号]-[页面]-[问题].png`。
- 逐入口点击：入口 → 是否真实可点 → 去向是否与站点地图一致。
- 死元素：视觉呈现为按钮/链接（样式/下划线/cursor/hover）但点击无反应且无 href。

## 四、静态审查定位
静态分析（DOM/grep token/href/CSS）与截图互证；不是无浏览器时的替代。