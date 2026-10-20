# Web 界面质量规则集（Web Interface Quality）

> 用途：Frontend-Dev S9 验收与日常开发自检；Fidelity-Review / Code-Review 的检出子集引用本文件（来源：Vercel Web Interface Guidelines，消化整理）。
> 口径：本集管**实现质量**（a11y / 表单 / 排版细节 / 性能 / i18n 等），不替代设计还原判定（视觉应然仍以设计稿为准）。

## 目录

- [一、可访问性（a11y）](#一可访问性a11y)
- [二、焦点](#二焦点)
- [三、表单](#三表单)
- [四、排版细节](#四排版细节)
- [五、内容健壮性](#五内容健壮性)
- [六、图片](#六图片)
- [七、性能](#七性能)
- [八、导航与状态](#八导航与状态)
- [九、触控](#九触控)
- [十、安全区与布局](#十安全区与布局)
- [十一、暗色与主题](#十一暗色与主题)
- [十二、国际化](#十二国际化)
- [十三、水合安全](#十三水合安全)
- [十四、悬停与交互态](#十四悬停与交互态)
- [十五、界面文案（实现期产生部分）](#十五界面文案实现期产生部分)
- [十六、反模式速查（命中即问题）](#十六反模式速查命中即问题)

## 一、可访问性（a11y）

- 纯图标按钮必须有 `aria-label`；
- 表单控件必须有 `<label>` 或 `aria-label`；
- 交互元素有键盘处理（`onKeyDown` / `onKeyUp`）；
- 动作类用 `<button>`、导航类用 `<a>` / `<Link>`，禁 `<div onClick>`；
- 图片有 `alt`（装饰性用 `alt=""`）；装饰图标加 `aria-hidden="true"`；
- 异步更新（Toast、校验结果）用 `aria-live="polite"`；
- 语义 HTML 优先于 ARIA 堆砌（先 `<button>` / `<a>` / `<label>` / `<table>`，不足再加 ARIA）；
- 标题层级递进（h1-h6）；主内容提供 skip link；
- 锚点标题设 `scroll-margin-top`（防被吸顶导航遮住）。

## 二、焦点

- 交互元素必须有可见焦点（`focus-visible:ring-*` 或等价样式）；
- 禁 `outline: none` 且无替代；
- 用 `:focus-visible` 而非 `:focus`（避免鼠标点击也出焦点环）；
- 复合控件用 `:focus-within` 分组聚焦；
- 吸顶头部 / 浮层不得覆盖当前聚焦元素。

## 三、表单

- 输入必带 `autocomplete` 与有意义的 `name`；
- 用正确 `type`（`email` / `tel` / `url` / `number`）与 `inputmode`；
- 禁阻止粘贴（`onPaste` + `preventDefault`）；
- 标签可点（`htmlFor` 或包裹控件）；
- 邮箱 / 验证码 / 用户名关闭拼写检查；
- 勾选类控件：label 与控件共享同一命中区（无死区）；
- 提交按钮在请求开始前保持可用，请求中显示 spinner；
- 错误内联在字段旁；提交时聚焦第一个错误字段；
- placeholder 以 `…` 结尾并给示例格式；非认证字段设 `autocomplete="off"`（防密码管理器误触发）；
- 有未保存修改时离开前提醒（`beforeunload` 或路由守卫）。

## 四、排版细节

- 省略号用 `…` 不用 `...`；引号用弯引号 `“”`；
- 数字与单位 / 快捷键之间用不换行空格（`10&nbsp;MB`、`⌘&nbsp;K`）；
- 加载态文案以 `…` 结尾（「加载中…」）；
- 数字列 / 可对比数值用 `font-variant-numeric: tabular-nums`；
- 标题用 `text-wrap: balance` 或 `text-pretty`（防孤行）。

## 五、内容健壮性

- 文本容器防超长：`truncate` / `line-clamp-*` / `break-words`；
- flex 子项加 `min-w-0` 才允许文本截断生效；
- 空态处理：空串 / 空数组不渲染出破 UI；
- 用户生成内容按「短 / 中 / 极长」三档预想（与超长文案专项呼应）。

## 六、图片

- `<img>` 显式 `width` / `height`（防 CLS）；
- 首屏外图片 `loading="lazy"`；首屏关键图 `priority` 或 `fetchpriority="high"`。

## 七、性能

- 大列表（>50 项）虚拟化（`virtua`、`content-visibility: auto`）；
- 渲染过程不做布局读取（`getBoundingClientRect` / `offsetHeight` / `offsetWidth` / `scrollTop`）；
- DOM 读写批处理，避免交织；非受控输入优先，受控输入保证每次击键开销低；
- CDN / 资源域加 `<link rel="preconnect">`；关键字体 `preload` + `font-display: swap`；
- 动图用 `<video autoplay muted loop playsinline>` 替代 GIF，并提供静帧替代。

## 八、导航与状态

- URL 反映状态（筛选 / Tab / 分页 / 展开面板进 query 参数）；
- 链接用 `<a>` / `<Link>`（支持 Cmd/Ctrl 点击、中键新开）；
- 有状态 UI 尽量可深链（URL 同步）；
- 破坏性操作必须有确认弹窗或撤销窗口，禁止点下即执行。

## 九、触控

- `touch-action: manipulation`（去掉双击缩放的点击延迟）；
- `-webkit-tap-highlight-color` 有意设置（不裸留默认）；
- 弹层 / 抽屉内 `overscroll-behavior: contain`（防滚动穿透）；
- 拖拽期间禁文本选择；拖拽 / 手势操作必须有 tap / 键盘替代（除非本质必需）；
- `autoFocus` 节制：仅桌面、单一主输入；移动端避免。

## 十、安全区与布局

- 全出血布局用 `env(safe-area-inset-*)` 适配刘海屏；
- 容器 `overflow-x-hidden` 防意外横向滚动条，同时修内容溢出的根因；
- 布局用 flex / grid 而非 JS 测量。

## 十一、暗色与主题

- 暗色主题在 `<html>` 设 `color-scheme: dark`（修正滚动条 / 原生输入框）；
- `<meta name="theme-color">` 与页面背景一致；
- 原生 `<select>` 显式设 `background-color` 与 `color`（Windows 暗色模式适配）。

## 十二、国际化

- 日期时间用 `Intl.DateTimeFormat`；数字 / 货币用 `Intl.NumberFormat`（禁硬编码格式串）；
- 语言检测用 `Accept-Language` / `navigator.languages`（禁按 IP 判断）；
- 品牌名 / 代码标识用 `translate="no"` 包裹（防浏览器自动翻译走样）。

## 十三、水合安全

- 受控输入有 `value` 必须配 `onChange`（或改 `defaultValue` 走非受控）；
- 日期时间渲染防 SSR / CSR 不一致（水合错配）；
- `suppressHydrationWarning` 只在确实需要处使用。

## 十四、悬停与交互态

- 按钮 / 链接必须有 hover 视觉反馈；
- hover / active / focus 态的对比度强于静止态（交互态可辨认）；
- 触摸设备不依赖 hover（配合 hover 门控，见动效指南）。

## 十五、界面文案（实现期产生部分）

> 业务文案源头是 PRD（以设计稿为准、一字不差）；本节管实现期新产生的文案——错误提示、加载态、aria-label、空态辅助语。

- 主动语态（「安装 CLI」而非「CLI 将被安装」）；
- 计数用数字（「8 个部署」而非「八个」）；
- 按钮标签具体（「保存 API Key」而非「继续」）；
- 错误信息含下一步（不只说问题）；
- 第二人称，避免第一人称；空间紧张用 `&` 代「和」。

## 十六、反模式速查（命中即问题）

| 反模式 | 纠正 |
|---|---|
| `user-scalable=no` / `maximum-scale=1` | 放开缩放（可访问性硬伤） |
| `onPaste` + `preventDefault` | 允许粘贴 |
| `transition: all` | 列明具体属性 |
| `outline: none` 无替代 | 补 `:focus-visible` 焦点样式 |
| `<div onClick>` 当按钮 / 链接 | 换 `<button>` / `<a>` |
| 图片无尺寸 | 显式 width/height |
| 大数组 `.map()` 无虚拟化 | >50 项虚拟化 |
| 表单输入无 label | 补 label / aria-label |
| 图标按钮无 `aria-label` | 补 aria-label |
| 硬编码日期 / 数字格式 | 用 `Intl.*` |
| 无理由 `autoFocus` | 去掉或仅桌面主输入 |
| 可用视频时用 GIF | `<video>` + 静帧替代 |
| 纯手势操作无替代 | 补 tap / 键盘通路 |
