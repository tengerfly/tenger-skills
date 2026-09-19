# UI/UX 设计与前端组件化思考

> 来源：抖音 @全栈道 图文《第 5 章：UI/UX 设计与前端组件化思考》（Design Tokens, Components & 10 UI States，第 15 集）。本文为对原图文内容的提炼整理，供写好前端页面的方法论参考。

## 0. 核心问题：AI 生成前端代码的"拼凑感"

开发者在使用 AI 生成前端代码时，经常遇到界面看起来像"拼凑出的 Demo"的问题：

- 字体字号拉不开层级；
- 边距不一致；
- 交互缺少反馈；
- 遇到网络延迟或错误时，页面直接变为空白。

企业级前端不仅要求"视觉合规"，更要求"状态稳健"。解法 = **Design Tokens 构建视觉体系 + 原型到高内聚组件的拆解 + 覆盖 AI 流式输出在内的 10 大 UI 状态**。

## 1. 现代 Web 界面设计原则与 Design Tokens

一个视觉效果精良的 Web 界面，绝不是靠随机挑选字体颜色和排版拼凑出来的，而是基于一套严格的 **Design System（设计系统）**。

三层结构：

```
Design Tokens（设计变量）      基础组件层（Base Components）    业务页面（Business Views）
├─ Color Tokens               Button / Input / Badge          Task Dashboard
├─ Spacing Tokens                                             AI Chat Portal
└─ Typography Tokens
```

### 1.1 视觉层级拉开（Visual Hierarchy）

- **字体排版**：标题与正文的字号必须建立阶梯式比例（如 24px → 18px → 14px → 12px），搭配合理的字重（Font Weight：600 用于标题，400 用于正文），避免所有文字大小一致。
- **色彩映射（Color Semantics）**：严禁在样式中写死硬编码颜色（如 `#ff0000`）。使用语义化 Token（如 `--color-danger`、`--color-success`），确保黑夜模式（Dark Mode）轻松切换。

### 1.2 栅格与间距系统（Spacing Scale）

- 所有的 Padding、Margin、Height 统一遵守 **4px / 8px 栅格网格系统**（如 4px、8px、12px、16px、24px、32px）。
- 使用统一的变量可以避免界面元素出现参差不齐的视觉细节。

## 2. 从原型到前端组件的高内聚拆解

将 UI 原型或 AI 生成的 HTML 拆解为可复用的 Vue 组件时，应遵循**容器组件（Container/Smart Component）与展示组件（Presentational/Dumb Component）相分离**的工程原则。

三层拆解示例：

| 层级 | 组件 | 职责 |
|---|---|---|
| 页面容器层（Smart Component / Page） | `TaskDashboardView.vue` | 负责调用 Pinia/API，掌控全局数据状态 |
| 业务容器层（Container Component） | `TaskListContainer.vue` | 负责处理筛选、分页，向下派发数据 |
| 展示组件层（Dumb Component / Reusable） | `TaskCard.vue` / `StatusBadge.vue` / `UserAvatar.vue` | 只做 props 渲染（列表项 / 状态到徽章样式映射 / 头像展示） |

### 组件拆解黄金法则

**1. 展示组件（Dumb Components）**

- 只通过 `props` 接收数据，只通过 `emits` 向外派发事件。
- 内部不直接发起 HTTP API 请求，不绑定全局 Pinia Store。
- 优点：高度可复用，极易进行单元测试与 Storybook 原型展示。

**2. 容器组件（Smart Components）**

- 负责连接后端 API、Pinia 状态库与路由控制器。
- 将数据通过 Props 组合后向下传递给展示组件。

## 3. 完整 UI 状态设计：覆盖 10 大关键界面状态

在真实网络环境下，前端页面绝不仅仅只有"正常显示（Success）"这一种状态。缺乏状态设计的代码在遇到网络波动时会导致用户体验极度糟糕。

典型状态流转：

```
Skeleton（结构化加载占位）
  → Loading（异步请求发起）
    → Success（数据成功返回） / Empty（返回但数据为 0）
    / NetworkError（断网/超时） / Error（500 服务器错误） / PermissionDenied（403 无权限）

AI 特有交互状态：Streaming（SSE 流式输出） → PartialData（增量解析 JSON 流） → Success（传输完成）
```

### 10 大 UI 状态矩阵与对应处理策略

| # | 状态维度 | 对应场景 | 用户体验要求与工程实现 |
|---|---|---|---|
| 1 | Skeleton（骨架屏） | 页面首次加载 | 替代转圈 Loading，显示与最终页面结构一致的灰色占位图，减少视觉抖动 |
| 2 | Loading（加载中） | 局部数据提交/刷新 | 按钮显示 Spin 动画并设置 `disabled`，防止重复提交 |
| 3 | Success（成功渲染） | 数据正常返回 | 渲染真实 UI 内容，确保空数据与长文本正常截断显示（Ellipsis） |
| 4 | Empty（空态） | 列表查询结果为 0 | 放置引导插画与"新建条目"行动按钮（CTA），避免用户面对空白页 |
| 5 | Error（业务错误） | 500/502 服务器异常 | 弹出友好的 Toast 或错误 Banner，提供"重新加载"或"联系管理员"按钮 |
| 6 | Disabled（禁用状态） | 缺少操作条件 | 按钮颜色变灰、`cursor: not-allowed`，悬浮给出 Tooltip 提示缺少什么条件 |
| 7 | Permission Denied | 403 无权限访问 | 引导用户向管理员申请权限，展示无权限专属插画 |
| 8 | Network Error | 断网 / 网络超时 | 弹出顶部全局持久的无网提示条（Offline Banner），恢复连接后自动重试 |
| 9 | Streaming（流式打字） | AI 文本生成中（SSE） | 显示光标闪烁（Blinking Cursor）与打字机效果，滚动条自动吸底 |
| 10 | Partial Data（增量数据） | AI 结构化输出生成中 | AI 输出 JSON 时，前端即使只收到前 50% 的字段，也能通过宽松 JSON 解析渐进渲染部分 UI |

## 4. 一句话总结

**视觉合规靠 Design Tokens（字号层级 + 语义色 + 栅格间距），状态稳健靠 10 大 UI 状态全覆盖，工程可维护靠 Smart/Dumb 组件高内聚拆解。**

> 原文结语：通过系统设计 Design Tokens 与 10 大 UI 状态，为后续 Vue 3 前端工程落地打下稳健的交互基础；下一章进入企业级系统架构设计（四层架构与 ADR 架构决策记录）。
