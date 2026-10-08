# frontend-template-vue3 Vue3 前端工程模板

与 `frontend-template-react`（React 版）**功能点一一对应**的 Vue3 同构模板：技术栈、目录骨架、请求层、页面三态、SSE 流式、Pinia 状态、设计 token、测试与提交规范开箱即用。业务代码已全部剥离，`src/api/demo.ts` + 首页是可运行的活示例。全部门禁实测通过：lint / test（18 例）/ coverage / build 全绿。

## 技术栈

| 类别 | 选型 |
| --- | --- |
| 构建 | Vite 5 |
| 框架 | Vue 3.5 + TypeScript（strict），`<script setup>` 单文件组件 |
| 组件库 | Element Plus（全量注册 + zh_CN locale；暗色经 `html.dark` css-vars） |
| 路由 | Vue Router 4（`createRouter` + 布局路由 + meta 驱动守卫） |
| 服务端状态 | TanStack Vue Query v5（与 React 版同一套 TanStack Query） |
| 客户端全局状态 | Pinia（options 式 store；示例 `stores/app.ts` 驱动暗色主题） |
| 样式 | Sass + CSS 设计 token（`variables.scss`，含 `html.dark` 暗色段与 Element Plus 主题映射） |
| 测试 | Vitest 2 + Vue Test Utils（jsdom；覆盖率门禁阈值与 React 版一致） |
| 规范 | ESLint 9 flat config（eslint-plugin-vue + typescript-eslint）+ Stylelint + Commitlint（conventional） |

## 目录结构

```
frontend-template-vue3/
├── index.html               # 入口 HTML（<div id="app"> 挂载点；新项目改 title）
├── pnpm-workspace.yaml      # pnpm 11+ 依赖构建脚本白名单（allowBuilds）
├── vite.config.ts           # dev 代理 + 分包/缓存/去 console 等工程优化（新项目改代理端口）
├── postcss.config.cjs       # CSS 兼容后处理：autoprefixer 按 browserslist 加厂商前缀
├── vitest.config.ts         # jsdom + globals + setup + 覆盖率门禁（thresholds；需带 vue 插件编译 SFC）
├── eslint.config.js         # ESLint 9 flat config：TS + Vue SFC
├── Dockerfile               # 多阶段构建：Node 构建 → nginx 静态托管（配 deploy/nginx.conf）
├── .github/workflows/ci.yml # CI 门禁：lint + 覆盖率测试 + 构建（其他平台等价迁移）
├── .editorconfig            # 编辑器格式基准（缩进/换行/编码）
├── tsconfig.json            # strict 全开（build 走 vue-tsc，.vue 类型一起查）
├── .stylelintrc.cjs         # 样式检查：禁写死色值（token 单一源）+ BEM 命名约定
├── commitlint.config.js     # 提交信息 conventional 规范
├── .husky/                  # 提交钩子：pre-commit=lint-staged，commit-msg=commitlint
├── deploy/nginx.conf        # SPA 静态托管配置（Dockerfile 直接使用）
├── .env.example             # VITE_API_BASE_URL 示例
└── src/
    ├── main.ts              # createApp 组装：Pinia + Router + VueQueryPlugin + ElementPlus(全量/locale/dark css)
    ├── App.vue              # 挂载根：仅 <RouterView/>（布局与路由表分别在 AppLayout 与 router/）
    ├── vite-env.d.ts        # 环境变量类型声明（新增 VITE_ 变量在此同步）
    ├── api/                 # 请求层：一个业务域一个文件（与 React 版逐字同构，框架无关）
    │   ├── request.ts       # 统一 fetch 封装（解包 {code,message,data}、超时、ApiError）
    │   ├── stream.ts        # SSE 流式封装（AI 增量输出场景，可中断）
    │   ├── demo.ts          # 示例模块（新项目删除）
    │   └── request.test.ts 等 # request/stream/guard/ErrorBoundary/Markdown/HomePage/store 均带测试（参考件）
    ├── components/          # 跨页面通用组件
    │   ├── ui/              # ★ 组件库统一出口：模板 <el-xxx> 靠 main.ts 全局注册；script 侧命令式 API/类型/图标一律从出口引入
    │   │   ├── index.ts     #    ElMessage/ElMessageBox 等命令式 API + FormInstance 等类型 re-export
    │   │    └── icons.ts    #    图标 re-export（当前 @element-plus/icons-vue；先登记再使用）
    │   ├── AppLayout.vue    # 顶栏 + ErrorBoundary + Suspense(懒加载 fallback) + RouterView 布局路由
    │   ├── ErrorBoundary.vue # 全局错误边界：onErrorCaptured 捕获（渲染/事件/watch 全覆盖）降级可重试错误页
    │   ├── TopNav.vue       # 品牌与导航数组驱动（改常量即可）+ 暗色切换入口
    │   └── Markdown.vue     # 零依赖 Markdown 渲染（AI 回复场景，h() 产出 VNode 免 XSS）
    ├── router/
    │   ├── index.ts         # createRouter + 路由表：页面全部 () => import() 懒加载，AppLayout 作布局路由
    │   └── guard.ts         # ★ 守卫单文件收口：beforeEach 默认全放行 + afterEach 写标题；接权限只改此文件
    ├── stores/              # ★ Pinia 全局状态（跨页面客户端状态才进 store，服务端数据走 vue-query）
    │   ├── index.ts         #    createPinia 出口 + 状态分层约定
    │   ├── app.ts           #    示例 store：暗色主题切换（驱动 html.dark 钩子）
    │   └── app.test.ts
    ├── features/            # 复杂功能域（composables + 组件），约定见其 README
    ├── pages/               # 页面组件 + 同目录 .test.ts
    │   ├── HomePage.vue     # 活示例：三态 + useQuery（新项目整页替换）
    │   └── HomePage.test.ts
    ├── metrics/
    │   └── webVitals.ts     # Web Vitals 性能采集（生产环境启用，上报实现待接监控 SDK）
    ├── styles/
    │   ├── variables.scss   # 设计 token（含 html.dark 暗色段 + Element Plus 主题映射段；值由 UI 设计稿回填）
    │   ├── _mixins.scss     # SCSS 工具层：additionalData 全量注入（SFC 的 <style> 同样生效）
    │   └── global.scss      # 全局基础样式（顶栏/内容列/标题层级）
    └── test/setup.ts        # vitest 全局 setup（matchMedia + ResizeObserver polyfill）
```

## 内置约定

### 请求层（api/request.ts）——与 React 版逐字同构

- 后端统一响应 `{ code, message, data }`，`code=0` 视为成功，`request<T>()` 直接返回 `data`；
- HTTP 非 2xx、业务码非 0、超时（默认 15s）、网络异常统一抛 `ApiError`（含 status/code），页面层只管捕获展示；
- 需要 FormData/文件下载时用导出的 `API_BASE_URL` 自行拼路径，不走 JSON 封装。

### API 模块

- 一个业务域一个文件（如 `api/plans.ts`），出参类型与请求函数同文件，类型加注释与后端字段对齐；
- 路径不含 BASE_URL；分页/检索参数用 `URLSearchParams` 拼查询串。

### 路由懒加载与守卫

- 页面组件一律 `() => import('./pages/XxxPage.vue')` 注册进路由表，懒加载 fallback（Suspense）统一在 `AppLayout` 里，路由处不用重复包。效果：路由级代码分割，首屏只加载布局 + 当前页面 chunk；
- **守卫单文件收口**（`src/router/guard.ts`）：Vue Router 的全局 `beforeEach` 天然单点，比 React 版更简——路由表 `meta: { requiresAuth: true }` 即挂守卫，`meta.title` 自动写 `document.title`。模板无登录体系默认全放行（`isLoggedIn` 恒真）；接入权限时只改这一个文件——替换 `isLoggedIn` 实现 + 在 `RouteMeta` 声明合并处扩展 roles/permissions 字段，路由表与页面零改动。

### 错误边界

`ErrorBoundary.vue` 在 `AppLayout` 包裹内容区（以 `route.path` 为 key，切路由自动复位），`onErrorCaptured` 捕获异常降级为可重试错误页防白屏；捕获范围比 React 版更广（渲染、生命周期、watch、事件处理器全覆盖）；埋点位留有 TODO（如 Sentry）。

### 组件库隔离（为换库预留）

- **全量注册**：`main.ts` 里 `app.use(ElementPlus, { locale: zhCn })`，模板直接写 `<el-xxx>`，无需逐个 import；
- **铁律：业务代码（pages / features）禁止直接 import 'element-plus' 与图标包**。模板组件靠全局注册不需要 import；script 侧需要命令式 API（`ElMessage`/`ElMessageBox`）、类型（`FormInstance` 等）、图标时，**一律从 `components/ui` 出口引入**，图标先在 `ui/icons.ts` 登记再使用；
- 换库同步三处：`components/ui/`（出口）、`src/main.ts`（全局注册/locale/dark css）、`src/styles/variables.scss`（视觉 token 映射段）。

### 页面三态

所有列表/详情页按「加载 Skeleton / 错误 Alert+重新加载 / 成功渲染」三态渲染，参考 `HomePage.vue`；数据用 `useQuery`，`queryKey` 数组带上全部筛选条件。

### 状态管理（Pinia）——Vue 版新增功能点

状态分三层，避免滥用全局状态：

| 状态类型 | 去处 |
| --- | --- |
| 服务端数据（列表/详情/轮询） | `@tanstack/vue-query`，**不进 store** |
| 跨页面客户端状态（主题/登录用户/全局开关） | `stores/<domain>.ts`（Pinia） |
| 页面局部状态 | 组件内 `ref`/`reactive`，不外提 |

- store 用 options 式（`state`/`getters`/`actions`）定义，示例 `stores/app.ts`：`toggleTheme()` 切 `html.dark`，同时驱动 `variables.scss` 的 token 覆盖段与 Element Plus dark css-vars，一处切换全站生效；
- 新业务域在 `stores/` 加一个文件即可，`stores/index.ts` 统一 re-export。

### SSE 流式（api/stream.ts）——与 React 版逐字同构

AI 增量输出场景用 `streamRequest(path, { body, onToken, signal })`；帧契约：`data:{"token":"..."}` 增量、`[DONE]` 结束、`event:error` 失败。配合 `AbortController` 实现停止按钮；对话流 composable 参照 `features/` README 的 `useXxx` 约定写。

### 样式

- 一切颜色/字号/间距从 `variables.scss` token 取，不写魔法值；**stylelint 强制色值走 token**（`color-no-hex`，variables.scss 唯一豁免）+ BEM 命名检查，`pnpm lint` 同时跑 eslint + stylelint；
- **CSS 自定义属性 `var(--token)` 全局直接可用**：variables.scss 在 main.ts 引入一次即运行时级联，任何 scss/SFC `<style>` 无需引入；
- **SCSS 编译期工具（@mixin/$var）全量注入**：`styles/_mixins.scss` 经 vite `additionalData` 注入所有 scss（含 SFC style 块），直接写 mixin 即可；该文件只准放编译期工具，禁放 CSS 规则；
- **组件库主色同源**：`variables.scss` 的「Element Plus 主题映射」段把 `--el-color-primary` 系列对齐 token，组件库与自定义样式视觉一致，改主色两处同步；
- **CSS 兼容**：autoprefixer（postcss）按 `browserslist` 自动加厂商前缀，样式源码不手写前缀；
- 全局只放基础规则与通用类（`.page-col` 内容列等），页面私有样式用 BEM 命名就近写在 SFC 的 `<style lang="scss">`（模板默认不用 scoped，靠 BEM 隔离；需要时加 scoped）；
- 暗色主题：`html.dark` 一个钩子驱动 token 覆盖 + Element Plus dark css-vars，入口在 TopNav 下拉（`stores/app.ts`）。

### 测试

- mock 边界固定在 **api 层**（`vi.mock('../api/xxx')`），不 mock 组件与网络；
- 经 main.ts 全局注册的组件库/插件，单测挂载时显式装插件：`mount(X, { global: { plugins: [ElementPlus, [VueQueryPlugin, { queryClient }]] } })`（参考 `HomePage.test.ts`）；
- 请求层/SSE/守卫/错误边界/Markdown/store 都有现成测试（写法即参考件）：mock 全局 fetch、构造 SSE ReadableStream、fake timers 测超时等；
- **覆盖率门禁**：`pnpm test:coverage` 校验阈值（实测 73%，阈值 70/70/70/75 留回归缓冲），CI 同跑；
- 已知坑：jsdom 缺 `matchMedia`/`ResizeObserver`，Element Plus 挂载会抛异常（setup.ts 已兜底）；未装 ElementPlus 插件时 `<el-xxx>` 会按自定义元素渲染——slot 内容可见但 **props（如 el-alert 的 title）不渲染**，断言会假失败。

### 提交规范

- Commitlint（conventional）：`feat/fix/docs/refactor/test/chore...`；
- **husky + lint-staged 已实配**：`pre-commit` 对暂存文件跑 lint-staged（eslint --fix / stylelint --fix），`commit-msg` 跑 commitlint；全量门禁走 CI；
- 钩子在 `git init` 后首次 `pnpm install` 自动激活（`prepare` 脚本）。

### 工程优化（构建产物）——与 React 版同构

- **分包与缓存**：页面路由级懒加载分包；`manualChunks` 抽 `vendor-element`（组件库）/`vendor-vue`（框架运行时）/`vendor`（其余），全部内容 hash，业务改动时浏览器/CDN 直接命中旧缓存；
- **生产安全**：`sourcemap: false` + 构建期移除 `console.log/info/debug` 与 `debugger`（`warn/error` 保留）；
- **目标环境**：`build.target: 'es2020'` + autoprefixer；
- **类型门禁**：build 前置 `vue-tsc --noEmit`，`.vue` 的模板表达式一起做类型检查；
- **体积观测**：`chunkSizeWarningLimit: 1000`；包体异常增长时临时接 `rollup-plugin-visualizer`。

## 部署（SPA + 静态托管）

与 React 版完全一致：`deploy/nginx.conf`（SPA 回退 / hash 资源长缓存 / 入口 no-cache / gzip）+ Docker 多阶段构建 + GitHub Actions CI。`docker build -t app . && docker run -p 8080:80 app`。

## 用模板开新项目（5 分钟改造清单）

1. 复制目录，改 `package.json` 的 `name`/`description`；
2. 改 `index.html` 的 `title` 与 `src/router/guard.ts` afterEach 里的品牌名；
3. 改 `src/components/TopNav.vue` 的 `BRAND` 与 `NAV_ITEMS`，在 `src/router/index.ts` 注册新页面路由；
4. 换主题色（两处同步）：`src/styles/variables.scss` 的 `--color-primary` 系列 + 同文件「Element Plus 主题映射」段；
5. 改 `vite.config.ts` 代理端口指向本项目后端；复制 `.env.example` 为 `.env` 按需调整；
6. 删除示例：`src/api/demo.ts`、`stores/app.ts`（或改造）、`HomePage.vue` 换成真实首页、`HomePage.test.ts` 随之改造；
7. 有登录态时改 `src/router/guard.ts`（替换 `isLoggedIn` 实现），需登录页面在路由表 meta 传 `{ requiresAuth: true }`；接入监控时在 `ErrorBoundary.vue` 埋点、`metrics/webVitals.ts` 换上报 SDK；
8. `pnpm install && pnpm dev` 起步，`pnpm lint && pnpm test:run && pnpm build` 验证。

## 换组件库操作指南（如 Element Plus → Naive UI/Ant Design Vue 等）

1. `components/ui/index.ts` + `icons.ts`：替换出口来源为新城库；模板全局标签从 `<el-xxx>` 改为新标签（或在此包一层适配组件保持用法不变）；
2. `src/main.ts`：替换全局注册与 locale、暗色 css 引入；
3. `src/styles/variables.scss`：「Element Plus 主题映射」段换成新城库的设计变量对齐；
4. 全局 grep `from 'element-plus'` 应只命中 `components/ui/`（隔离层验收标准）；差异最大的命令式 API（Message/MessageBox）与表单系统优先在 ui 出口封装成项目自有 hook，不要让页面直接碰库 API。

## 与 frontend-template-react 的功能点对应

| 功能点 | React 版 | Vue3 版 |
| --- | --- | --- |
| 框架运行时 | React 18 | Vue 3.5（`<script setup>`） |
| 组件库 | AntD 5（ui 出口 + 手动 import） | Element Plus（全局注册 + ui 出口管 script 侧） |
| 路由 | React Router v6（`guard()` 包装组件） | Vue Router 4（`beforeEach` 全局守卫 + meta） |
| 服务端状态 | TanStack Query v5 | TanStack Vue Query v5（同一套库） |
| 客户端全局状态 | 无（刻意最小依赖） | **Pinia**（Vue 版唯一新增功能点） |
| 错误边界 | 类组件 getDerivedStateFromError | `onErrorCaptured`（捕获范围更广） |
| 请求层 / SSE / Markdown / WebVitals / token / 门禁 / CI·Docker | — | 逐字或近逐字同构 |
| 暗色主题 | token 钩子（无切换入口） | token + Element Plus 共用 `html.dark`，TopNav 可切换 |

## 可选扩展（按需，模板默认未含）

- **Monorepo + 共享契约包**：与 React 版相同（pnpm workspace + `libs/shared`），request.ts 无需改动；
- **unplugin-vue-components 按需加载**：替换全量注册以减小包体；注意其自动导入会绕过 ui 隔离出口，需配置 resolvers 约束；
- **业务组件库**（echarts 等）按需添加，模板刻意保持最小依赖。
