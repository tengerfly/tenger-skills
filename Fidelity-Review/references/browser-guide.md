# 浏览器工具预检与双开截图

## 一、预检
Playwright 可用 → 首选；异常 → browser-use/其他工具；全无 → 报错停止，不产出。

## 二、Playwright 双开
- 装 `pnpm add -D playwright && pnpm exec playwright install chromium`。
- 同视口（如 1440×900）分别截设计稿与实现页并排比对；关键差异用元素级截图。
- 交互/长文案：点击验证按钮、hover 截图、`page.evaluate` 替换 DOM 文本后截图。

## 三、降级
browser-use/其他工具：打开两页截图目测；无法 DOM 注入长文案时用真实长数据页并向用户说明。

## 四、视口
桌面 + 一种窄屏各一轮，同视口对照。

## 五、命名归档
`<页面>_<问题>_<序号>.png` 存 `.spec/页面还原评审/screenshots/`，报告相对路径引用。

## 六、常见错误
无工具硬跑、异视口并排、只截整页、长文案不改 DOM、乱命名 → 均纠正。