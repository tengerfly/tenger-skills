# 前端技术选型指南

> 用途：选型澄清阶段的推荐规则。**端形态与技术框架每次必问**（默认 React 但不可自主定死）；框架确认后，组件库/路由/状态/请求/测试按 §三配套清单联动推荐。所有选型必须给「选型 + 理由 + 备选」，禁止拍脑袋。

---

## 一、档位决策（每次必问，推荐企业级）

| 档位 | 特征 | 典型选择 |
|------|------|---------|
| **企业级生产**（默认） | 工程质量优先：完整测试、错误边界、权限路由、监控埋点、性能优化、ESLint/Prettier/Husky、CI/CD | 组件库 + 状态管理 + 路由 + i18n + 主题 + 测试全覆盖 |
| **demo 快速实现** | 以实现为主：最小可用、快速跑通、够用即可 | 精简配置、少量公共组件、测试只覆盖核心路径 |

> 判定口径：用户明确要「demo / 快速 / MVP / 先跑通」才走 demo 档；其余一律企业级。

---

## 二、端形态与技术框架（每次必问，默认 ≠ 定死）

### 2.1 端形态 × 框架候选

| 端/形态 | 框架候选 | 默认/说明 |
|---|---|---|
| Web PC（中后台/官网） | **React 18** / Vue 3 | 默认 React，每次必问用户确认 |
| H5（移动网页） | 跟随 Web 主栈（React / Vue 3）+ 移动端组件库 | 与主栈同框架，避免双栈维护 |
| 小程序 | **Taro（React 语法）** / **uni-app（Vue3）** / 原生小程序 | React 栈→Taro；Vue 栈→uni-app；原生仅简单小程序 |
| App（移动） | **React Native** / Flutter（备选）/ uni-app（App 端） | TS/React 栈→RN 优先 |
| 桌面端 | **Electron**（渲染层复用 Web 栈）/ Tauri | 复用 Web 生态 |
| 多端一套（小程序+H5+App） | Taro（React）/ uni-app（Vue3） | 必问：一码多端 vs 分端独立（维护成本差异大） |

### 2.2 选型规则

- **技术框架每次必问**：默认 React 18，用户可选其他框架；未经用户确认不得写入文档（禁止自主定死）。
- **多端复用**：小程序+H5+App 多端时优先推荐一码多端（React 栈→Taro、Vue 栈→uni-app），并给出与分端独立的成本对比。
- **Flutter 为备选**：跨出 TS 栈（Dart），与共享类型/前后端契约模式不兼容，仅在用户点名时选择，选前提示团队语言成本。
- **复杂度门槛**：复杂交互/重业务的小程序与 App 一律用跨端框架（Taro/uni-app）；原生小程序仅适合简单页面型小程序。

---

## 三、各框架配套生态清单（框架确认后联动取默认）

> 每框架给出「UI 库 / 路由 / 状态 / 请求 / CSS / 测试 / 逻辑复用」默认推荐；用户可逐项替换，替换须记录理由。

### 3.1 React 18（Web PC / H5）

| 项 | 默认推荐 | 备选 |
|----|---------|------|
| 构建 | Vite + pnpm + TS 严格模式 | — |
| UI 库（PC 中后台） | Ant Design | Arco Design / MUI / shadcn/ui+Tailwind |
| UI 库（H5） | Ant Design Mobile | arco-design-mobile |
| 路由 | React Router v6（数据路由+懒加载） | TanStack Router |
| 状态管理 | Zustand（轻）/ Redux Toolkit（复杂）+ TanStack Query（服务端态） | Jotai / MobX |
| 请求 | 原生 fetch 统一封装（禁 axios） | — |
| CSS | Sass/Less（按生态选）+ CSS Modules | Tailwind |
| 测试 | Vitest + React Testing Library + jest-dom | Jest |
| 逻辑复用 | 自定义 hooks（useFetch/useForm/useAuth/useTheme） | — |
| i18n（按需） | react-i18next | — |
| SSR（按需） | Next.js | Remix |

### 3.2 Vue 3（Web PC / H5）

| 项 | 默认推荐 | 备选 |
|----|---------|------|
| 构建 | Vite + pnpm + TS 严格模式 | — |
| UI 库（PC 中后台） | Element Plus | Ant Design Vue / Naive UI / Arco Design Vue |
| UI 库（H5） | Vant 4 | NutUI-Vue |
| 路由 | Vue Router 4 | — |
| 状态管理 | Pinia（官方默认） | TanStack Query Vue（服务端态，可选） |
| 请求 | 原生 fetch 统一封装（禁 axios） | — |
| CSS | Sass + scoped / CSS Modules | Tailwind |
| 测试 | Vitest + Vue Test Utils + jest-dom | — |
| 逻辑复用 | 组合式函数 composables（useXxx 同规范） | — |
| i18n（按需） | vue-i18n | — |
| SSR（按需） | Nuxt 3 | — |

### 3.3 Taro（React 语法，多端：小程序 + H5 + RN）

| 项 | 默认推荐 | 备选 |
|----|---------|------|
| UI 库 | NutUI-React（京东，主流） | Taro UI |
| 路由 | Taro 声明式页面路由（app.config.ts） | — |
| 状态管理 | Zustand / Redux Toolkit | — |
| 请求 | Taro.request / Taro.uploadFile 统一封装（契约对齐 fetch 版） | — |
| CSS | Sass + rpx 适配 | — |
| 测试 | Vitest + Taro 测试库 | — |
| 逻辑复用 | 自定义 hooks | — |

### 3.4 uni-app（Vue3 语法，多端：小程序 + H5 + App）

| 项 | 默认推荐 | 备选 |
|----|---------|------|
| UI 库 | wot-design-uni | uView Plus / uni-ui / NutUI-Vue |
| 路由 | pages.json 声明式路由 | — |
| 状态管理 | Pinia | — |
| 请求 | uni.request / uni.uploadFile 统一封装 | — |
| CSS | Sass + rpx 适配 | — |
| 测试 | Vitest | — |
| 逻辑复用 | 组合式函数 composables | — |
| 工具链 | CLI（Vite）或 HBuilderX | — |

### 3.5 小程序原生（仅简单页面型小程序）

| 项 | 默认推荐 |
|----|---------|
| UI | 原生组件 + WeUI / 自研 |
| 路由 | pages.json |
| 状态 | 自封装全局态（store 模块/事件） |
| 请求 | wx.request 统一封装 |
| CSS | WXSS + rpx |
| 适用 | 页面少、交互简单的轻量小程序；**复杂场景一律上跨端框架** |

### 3.6 React Native（App）

| 项 | 默认推荐 | 备选 |
|----|---------|------|
| 脚手架 | Expo | RN CLI |
| UI 库 | 官方核心组件 + gluestack-ui | NativeBase / React Native Elements / Ant Design Mobile RN |
| 导航 | React Navigation | Expo Router |
| 状态管理 | Zustand / Redux Toolkit | — |
| 请求 | fetch 统一封装 | — |
| 测试 | Jest + React Native Testing Library | — |
| 逻辑复用 | 自定义 hooks | — |

### 3.7 Flutter（App，备选——用户点名才选）

| 项 | 默认推荐 |
|----|---------|
| 语言 | Dart（跨出 TS 栈，选前提示团队成本与契约共享限制） |
| UI | Material / Cupertino 官方 Widget |
| 导航 | Navigator 2.0 / go_router |
| 状态管理 | Riverpod / Bloc |
| 请求 | dio 统一封装 |
| 测试 | flutter_test |

### 3.8 Electron（桌面）

| 项 | 默认推荐 |
|----|---------|
| 架构 | 主进程 Node.js + 渲染进程 React/Vue（Web 栈全套复用 §3.1/§3.2） |
| 构建 | electron-vite + electron-builder |
| 通信 | IPC（contextBridge 预加载隔离） |
| 安全 | 渲染进程基线：contextIsolation: true，禁 nodeIntegration |

---

## 四、通用决策（跨框架不变项）

| 项 | 原则 |
|----|------|
| 请求契约 | 各端载体不同（fetch / Taro.request / uni.request / wx.request / dio），封装原则一致：统一入口、baseURL/超时/取消/错误分类（ApiError）/token 注入；业务接口按域拆分，与后端 TDD 一一对应 |
| CSS / 设计 token | 全部收敛变量（variables）：语义色、字号阶梯、4px 间距栅格、圆角阴影；颜色禁写死；变量载体按平台（Web 用 CSS 变量） |
| 测试策略 | 先写用例后写实现；TC ↔ AC 编号可追溯；覆盖渲染/交互/数据流/边界/异常；逻辑层（hooks/composables）独立测试 |
| 浏览器兼容（每次必问） | 指定→build.target + legacy 插件 + 前缀；未指定→Vite 默认（现代浏览器）并显式声明 |
| 工程规范（企业级档） | ESLint + Prettier、Husky + lint-staged + commitlint、tsc --noEmit 入 CI、环境变量分环境 |

---

## 五、选型决策表模板（总文档 §2 用）

| 组件 | 选型 | 档位 | 理由 | 备选 |
|------|------|------|------|------|
| 端形态 | {{Web PC / H5 / 小程序 / App / 桌面 / 多端一套}} | {{TIER}} | {{REASON}} | — |
| 框架 | {{用户选定：React 18 / Vue 3 / Taro / uni-app / RN / Electron / Flutter}} | {{TIER}} | {{REASON}} | {{备选}} |
| 构建 | {{随框架：Vite / HBuilderX / Expo / electron-vite}} | {{TIER}} | {{REASON}} | — |
| 组件库 | {{随框架联动，见 §三}} | {{TIER}} | {{REASON}} | {{备选}} |
| 状态管理 | {{随框架联动}} | {{TIER}} | {{REASON}} | {{备选}} |
| 路由 | {{随框架联动}} | {{TIER}} | {{REASON}} | — |
| CSS | {{Sass/Less 按生态选}} + 隔离方案（React→CSS Modules / Vue→scoped）+ 全局抽离 | {{TIER}} | 随框架 | Tailwind |
| 请求 | {{随端载体}} 统一封装 | {{TIER}} | 契约对齐 TDD | — |
| 测试 | {{随框架联动}} | {{TIER}} | {{REASON}} | — |
| 主题 | CSS 变量 + data-theme | {{TIER}} | 暗黑模式 | — |
| i18n | {{react-i18next / vue-i18n / 不开}} | {{TIER}} | {{REASON}} | — |
| 浏览器兼容 | {{Vite 默认 / 用户指定}} | {{TIER}} | {{REASON}} | — |
