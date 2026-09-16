# frontend-template-react React 前端工程模板

从「学径 LearnPath」项目沉淀的可复用前端工程模板：技术栈、目录骨架、请求层、页面三态、SSE 流式、设计 token、测试与提交规范开箱即用。业务代码已全部剥离，`src/api/demo.ts` + 首页是可运行的活示例。

## 技术栈

| 类别 | 选型 |
| --- | --- |
| 构建 | Vite 5 |
| 框架 | React 18 + TypeScript（strict） |
| 组件库 | Ant Design 5（zh_CN locale + ConfigProvider 主题 token） |
| 路由 | React Router v6（`createBrowserRouter` + 布局路由） |
| 服务端状态 | TanStack Query v5 |
| 样式 | Sass + CSS 设计 token（`variables.scss`，含暗色主题钩子） |
| 测试 | Vitest 2 + Testing Library（jsdom + matchMedia polyfill） |
| 规范 | ESLint（@typescript-eslint + react-hooks）+ Commitlint（conventional） |

## 目录结构

```
frontend-template-react/
├── index.html               # 入口 HTML（新项目改 title）
├── pnpm-workspace.yaml      # pnpm 11+ 依赖构建脚本白名单（allowBuilds）
├── vite.config.ts           # dev 代理 + 分包/缓存/去 console 等工程优化（新项目改代理端口）
├── postcss.config.cjs       # CSS 兼容后处理：autoprefixer 按 browserslist 加厂商前缀
├── vitest.config.ts         # jsdom + globals + setup + 覆盖率门禁（thresholds）
├── Dockerfile               # 多阶段构建：Node 构建 → nginx 静态托管（配 deploy/nginx.conf）
├── .github/workflows/ci.yml # CI 门禁：lint + 覆盖率测试 + 构建（其他平台等价迁移）
├── .editorconfig            # 编辑器格式基准（缩进/换行/编码）
├── tsconfig.json            # strict 全开
├── .eslintrc.cjs            # TS + react-hooks 规则
├── .stylelintrc.cjs         # 样式检查：禁写死色值（token 单一源）+ BEM 命名约定
├── commitlint.config.js     # 提交信息 conventional 规范
├── .husky/                  # 提交钩子：pre-commit=lint-staged，commit-msg=commitlint
├── deploy/nginx.conf        # SPA 静态托管配置（Dockerfile 直接使用，与下方部署节一致）
├── .env.example             # VITE_API_BASE_URL 示例
└── src/
    ├── main.tsx             # Providers 组装：ConfigProvider(主题) + QueryClient（换组件库的触点之一）
    ├── App.tsx              # 路由表：页面全部 React.lazy 懒加载，AppLayout 包裹
    ├── vite-env.d.ts        # 环境变量类型声明（新增 VITE_ 变量在此同步）
    ├── api/                 # 请求层：一个业务域一个文件
    │   ├── request.ts       # 统一 fetch 封装（解包 {code,message,data}、超时、ApiError）
    │   ├── stream.ts        # SSE 流式封装（AI 增量输出场景，可中断）
    │   ├── demo.ts          # 示例模块（新项目删除）
    │   └── request.test.ts 等 # request/stream/guard/ErrorBoundary/Markdown 均带测试（标准写法参考件）
    ├── components/          # 跨页面通用组件
    │   ├── ui/              # ★ 组件库统一出口（当前 AntD 5）：业务代码禁止直接 import 'antd'
    │   │   ├── index.ts     #    组件与类型 re-export；换库后 API 有差异的组件在此做适配包装
    │   │   └── icons.ts     #    图标 re-export（当前 @ant-design/icons）
    │   ├── AppLayout.tsx    # 顶栏 + ErrorBoundary + Suspense(懒加载 fallback) + Outlet 布局
    │   ├── ErrorBoundary.tsx # 全局错误边界：渲染异常降级为可重试错误页，防白屏（含监控上报埋点位）
    │   ├── TopNav.tsx       # 品牌与导航数组驱动（改常量即可）
    │   └── Markdown.tsx     # 零依赖 Markdown 渲染（AI 回复场景，免 XSS，不依赖组件库）
    ├── metrics/
    │   └── webVitals.ts     # Web Vitals 性能采集（CLS/INP/LCP），生产环境启用，上报实现待接监控 SDK
    ├── router/
    │   └── guard.tsx        # ★ 路由守卫单文件收口：默认全放行，接入权限只改此文件
    ├── features/            # 复杂功能域（hooks + 组件），约定见其 README
    ├── pages/               # 页面组件 + 同目录 .test.tsx
    │   ├── HomePage.tsx     # 活示例：三态 + useQuery（新项目整页替换）
    │   └── HomePage.test.tsx
    ├── styles/
    │   ├── variables.scss    # 设计 token（颜色/字号/间距/圆角/阴影 + 暗色钩子；值由 UI 设计稿回填）
    │   ├── _mixins.scss      # SCSS 工具层：additionalData 全量注入，所有 scss 直接用 @mixin 无需引入
    │   └── global.scss      # 全局基础样式（顶栏/内容列/标题层级）
    └── test/setup.ts        # vitest 全局 setup（matchMedia polyfill）
```

## 内置约定

### 请求层（api/request.ts）

- 后端统一响应 `{ code, message, data }`，`code=0` 视为成功，`request<T>()` 直接返回 `data`；
- HTTP 非 2xx、业务码非 0、超时（默认 15s）、网络异常统一抛 `ApiError`（含 status/code），页面层只管捕获展示；
- 需要 FormData/文件下载时用导出的 `API_BASE_URL` 自行拼路径，不走 JSON 封装。

### API 模块

- 一个业务域一个文件（如 `api/plans.ts`），出参类型与请求函数同文件，类型加注释与后端字段对齐；
- 路径不含 BASE_URL；分页/检索参数用 `URLSearchParams` 拼查询串。

### 路由懒加载与守卫

- 页面组件一律 `React.lazy(() => import('./pages/XxxPage'))` 后注册进路由表，`Suspense` fallback 统一在 `AppLayout` 里（`PageLoading`），路由处不用重复包。效果：路由级代码分割，首屏只加载布局 + 当前页面 chunk。
- **守卫单文件收口**（`src/router/guard.tsx`）：路由表用 `guard(<Page />, { requiresAuth: true })` 包装即挂守卫。模板无登录体系默认全放行（`isLoggedIn` 恒真）；接入权限时只改这一个文件——替换 `isLoggedIn` 实现 + 在 `RouteMeta` 扩展 roles/permissions 字段，路由表与页面零改动。

### 错误边界

`ErrorBoundary` 在 `AppLayout` 包裹内容区（以 pathname 为 key，切路由自动复位），渲染异常降级为可重试错误页防白屏；`componentDidCatch` 内留有监控上报埋点位（如 Sentry）。

### 组件库隔离（为换库预留）

- **按需引入零配置**：AntD 5 为 ESM + CSS-in-JS，Vite 生产构建自动 tree-shaking，**不需要** v4 时代的 `babel-plugin-import` / `vite-plugin-style-import`。
- **铁律：业务代码（pages / features）禁止直接 `import 'antd'` 与图标包**，一律从 `components/ui` 出口引入。这是为「后续换组件库」预留的隔离层：
  - 现状是纯 re-export，零包装成本，写法与直接用 antd 完全一致；
  - 换库时改 `components/ui/index.ts`（+ `icons.ts`）一处出口；API 有差异的组件在出口内做适配包装，差异不外溢到页面代码。
- 换库另需同步两处：`src/main.tsx`（Providers/主题/locale）与 `src/styles/variables.scss`（视觉 token）。

### 页面三态

所有列表/详情页按「加载 Skeleton / 错误 Alert+重新加载 / 成功渲染」三态渲染，参考 `HomePage.tsx`；数据用 `useQuery`，`queryKey` 数组带上全部筛选条件。

### SSE 流式（api/stream.ts）

AI 增量输出场景用 `streamRequest(path, { body, onToken, signal })`；帧契约：`data:{"token":"..."}` 增量、`[DONE]` 结束、`event:error` 失败。配合 `AbortController` 实现停止按钮，参考源项目 `useChatStream` 的「增量聚合成一条消息」写法。

### 样式

- 一切颜色/字号/间距从 `variables.scss` token 取，不写魔法值；**stylelint 强制色值走 token**（`color-no-hex`，variables.scss 唯一豁免）+ BEM 命名检查，`pnpm lint` 同时跑 eslint + stylelint；
- **CSS 自定义属性 `var(--token)` 全局直接可用**：variables.scss 在 main.tsx 引入一次即运行时级联，任何 scss/组件无需引入；`@/` 别名（vite + tsconfig 已配）在新代码中按需使用；
- **SCSS 编译期工具（@mixin/$var）全量注入**：`styles/_mixins.scss` 经 vite `additionalData` 注入所有 scss 文件，直接写 mixin 即可；该文件只准放编译期工具，禁放 CSS 规则（会被每个文件重复输出）；
- **CSS 兼容**：autoprefixer（postcss）按 package.json `browserslist` 自动加厂商前缀，样式源码不手写前缀。
- 全局只放基础规则与通用类（`.page-col` 内容列等），页面私有样式用 BEM 命名就近写在页面/组件的样式块或全局文件的语义化段落里，不用 CSS Modules；
- 主色改动要同步两处：`variables.scss` 的 `--color-primary` 系列 + `main.tsx` 的 `ConfigProvider theme`。

### 测试

- mock 边界固定在 **api 层**（`vi.mock('../api/xxx')`），不 mock 组件与网络；
- 页面测试用 `renderPage` helper 注入 `MemoryRouter + QueryClientProvider`；
- 请求层/SSE/守卫/错误边界/Markdown 都有现成测试（`*.test.tsx`），写法即参考件：mock 全局 fetch、构造 SSE ReadableStream、fake timers 测超时等；
- **覆盖率门禁**：`pnpm test:coverage` 跑覆盖率并校验阈值（当前实测 75%，阈值 70/70/70/75 留回归缓冲），CI 同跑；新项目按需上调；
- 已知坑：AntD 在 jsdom 缺 `matchMedia` 会抛异常（setup.ts 已兜底）；AntD 两字中文按钮会自动插空格（`重 试`），断言用 `/重\s*试/` 类正则。

### 提交规范

- Commitlint（conventional）：`feat/fix/docs/refactor/test/chore...`；
- **husky + lint-staged 已实配**：`pre-commit` 对暂存文件跑 `lint-staged`（eslint --fix / stylelint --fix，秒级反馈），`commit-msg` 跑 commitlint；全量门禁（lint + coverage + build）走 CI；
- 钩子在 `git init` 后首次 `pnpm install` 自动激活（`prepare` 脚本）；未 init git 时 install 不报错，钩子不生效而已。

### 工程优化（构建产物）

已内置，无需配置：

- **分包与缓存**：页面路由级 `React.lazy` 分包；`manualChunks` 把依赖抽为 `vendor-antd`（组件库）/`vendor-react`（框架运行时）/`vendor`（其余）——全部带内容 hash，库不升级则 vendor hash 不变，**业务改动时用户浏览器/CDN 直接命中旧缓存，等效增量加载**；
- **生产安全**：`sourcemap: false` 显式声明（防源码映射泄露线上）；构建期移除 `console.log/info/debug` 与 `debugger`（`warn/error` 保留，便于线上排障；仅生产，dev 不受影响）；
- **目标环境**：`build.target: 'es2020'` 显式锁定 + autoprefixer 按 browserslist 出兼容前缀；
- **体积观测**：`chunkSizeWarningLimit` 上调到 1000 消除分包后的预期告警；包体异常增长时临时接 `rollup-plugin-visualizer` 分析。

## 部署（SPA + 静态托管）

**缓存策略与分包配合**：入口不缓存保证发版生效，hash 资源长缓存保证命中率。完整配置在 `deploy/nginx.conf`（Dockerfile 直接使用），要点：

- `try_files $uri $uri/ /index.html`——SPA history 回退（不配刷新/直链 404）；
- `/assets/` → `Cache-Control: public, max-age=31536000, immutable`（文件名带 hash，天然失效）；
- `/index.html` → `no-cache`（发版即时生效）；
- `gzip on` 动态压缩足够（流量大再考虑构建期预压缩）。

**Docker**：`docker build -t app .` → `docker run -p 8080:80 app`（多阶段构建，Node 出产物、nginx 托管）。

**CI**：`.github/workflows/ci.yml` 为 GitHub Actions 参考（lint → test:coverage → build），其他平台按步骤等价迁移。

## 用模板开新项目（5 分钟改造清单）

1. 复制目录，改 `package.json` 的 `name`/`description`；
2. 改 `index.html` 的 `title`；
3. 改 `src/components/TopNav.tsx` 的 `BRAND` 与 `NAV_ITEMS`，在 `App.tsx` 注册新页面路由；
4. 换主题色（两处同步）：`src/styles/variables.scss` + `src/main.tsx` THEME；
5. 改 `vite.config.ts` 代理端口指向本项目后端；复制 `.env.example` 为 `.env` 按需调整；
6. 删除示例：`src/api/demo.ts`、`HomePage.tsx` 换成真实首页、`HomePage.test.tsx` 随之改造；
7. 有登录态时改 `src/router/guard.tsx`（替换 `isLoggedIn` 实现，公开页不用动），需登录的页面在路由表传 `{ requiresAuth: true }`；接入监控时在 `ErrorBoundary.componentDidCatch` 埋点；
8. `pnpm install && pnpm dev` 起步，`pnpm lint && pnpm test:run && pnpm build` 验证。

## 换组件库操作指南（如 AntD → Arco/semi/MUI 等）

1. `components/ui/index.ts` + `icons.ts`：替换 re-export 来源为新城库名；逐个组件核对 props，有差异的在此包一层适配组件（项目内用法不变）；
2. `src/main.tsx`：替换 `ConfigProvider`（主题 token 结构按新城库改）、locale；
3. `src/styles/variables.scss`：视觉 token 按新城库设计变量对齐（AntD token 里的 borderRadius/fontSize 对应项找平）；
4. 全局 grep `from 'antd'` 应只命中 `components/ui/`（这是隔离层的验收标准）；`theme.ts` 级联改动不涉及业务代码；
5. 特殊 API（如 message/Modal 静态方法、Form 表单系统）差异最大，优先在 ui 出口内封装成项目自有 hook/组件（如 `ui/useMessage`），不要让页面直接碰库 API。

## 可选扩展（按需，模板默认未含）

- **Monorepo + 共享契约包**：源项目为 pnpm workspace（`web` + `server` + `libs/shared`），前后端枚举/DTO/响应类型单一源。需要时把本目录并入 workspace，`request.ts` 无需改动，api 模块的类型从 `@xxx/shared` 导入即可（注意给共享包配 ESM 产物 + `optimizeDeps.include` 兜底，见源项目 `web/vite.config.ts` 注释）。
- **zustand**：源项目声明了但实际零使用（服务端状态 React Query + 局部 useState 已覆盖）。确有跨页面客户端状态再加。
- **业务组件库**：AntV G6（图谱）、react-markdown 等按需添加，模板刻意保持最小依赖。

## 与源项目的差异

- 剥离全部业务：页面（学习/知识库/图谱等）、全部业务 API 模块、features 业务域、G6/共享包依赖；
- 新增：`api/stream.ts`（从源项目 `streamChat` 提炼的通用 SSE 封装）、`components/ui/` 组件库隔离出口（源项目直接 import antd，模板改为统一出口以支持换库）、路由懒加载、`router/guard.tsx` 路由守卫（源项目无守卫）、`ErrorBoundary`（源项目无）、stylelint 门禁（源项目未配，`color-no-hex` 强制 token 单一源）、环境变量类型（`vite-env.d.ts`）、Web Vitals 采集位、SCSS mixin 全量注入（`_mixins.scss` + additionalData）、autoprefixer 兼容、vendor 分包与生产构建优化、覆盖率门禁（核心模块带真实测试，实测 75%）、husky + lint-staged 提交钩子、Docker/CI/nginx 部署套件、`.gitignore`/`.env.example` 等独立仓库所需文件；
- TopNav 改为常量数组驱动，品牌/导航不动 JSX。
