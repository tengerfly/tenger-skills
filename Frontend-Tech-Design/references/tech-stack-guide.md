# 前端技术选型指南

> 用途：为技术选型澄清阶段提供推荐规则。所有选型必须给「选型 + 理由 + 备选」，禁止拍脑袋。

---

## 一、档位决策（每次必问，推荐企业级）

| 档位 | 特征 | 典型选择 |
|------|------|---------|
| **企业级生产**（默认） | 工程质量优先：完整测试、错误边界、权限路由、监控埋点、性能优化、ESLint/Prettier/Husky、CI/CD | 组件库 + 状态管理 + 路由 + i18n + 主题 + 测试全覆盖 |
| **demo 快速实现** | 以实现为主：最小可用、快速跑通、够用即可 | 精简配置、少量公共组件、测试只覆盖核心路径 |

> 判定口径：用户明确要「demo / 快速 / MVP / 先跑通」才走 demo 档；其余一律企业级。

---

## 二、框架（固定 React，hooks 为主）

| 项 | 选型 | 理由 |
|----|------|------|
| 框架 | React 18+ | 与「hooks 为主」的模块化开发约束一致，函数组件 + 自定义 hooks |
| 组件范式 | 函数组件 + hooks | 逻辑复用、可测试性强 |
| 类型 | TypeScript 严格模式 | 全量类型约束，props/状态/接口契约 |

> 固定技术栈不询问；仅当用户团队明确偏好 Vue 时才切换（Vue 3 组合式 API），并同步调整组件库/状态管理/测试框架的推荐。

---

## 三、组件库选型（每次必问，让用户决定）

先探索 PRD/原型得出产品形态（表单密集型 / 数据展示型 / 中后台 / C 端营销），再推荐：

| 形态 | 推荐组件库 | 理由 | 备选 |
|------|-----------|------|------|
| 中后台管理系统 | Ant Design | 生态最成熟、组件最全、表单表格强 | Arco Design |
| 中后台（字节系） | Arco Design | 设计规范清晰、TS 友好 | Ant Design |
| TS 友好 / 轻量 | Naive UI | 全量 TS、主题定制灵活、体积可控 | — |
| C 端营销 / 高度定制 | 自研组件 | 视觉与交互完全可控 | — |

**决策要点**：
- 用户选「不用组件库」→ 走自研路线，总文档 §5 补「基础组件自研清单」（Button/Modal/Table/Form 等逐项列）；
- 用户选「用组件库」→ 确认该库是否支持主题定制与国际化（与暗黑模式/i18n 决策联动）。

---

## 四、状态管理选型（推荐默认，按复杂度取舍）

| 场景 | 推荐 | 理由 |
|------|------|------|
| 轻量全局态（用户态/主题/侧边栏） | Zustand | API 极简、无模板代码、支持中间件 |
| 复杂全局态（多模块联动/异步编排） | Redux Toolkit | 规范化、DevTools 强、适合大团队 |
| 服务端数据（接口缓存/请求状态） | TanStack Query | 缓存、重试、请求状态内建，替代手写数据层 |
| 局部状态 | React 内置 useState/useReducer | 不引入额外依赖 |

> 原则：优先局部状态 + hooks；只有跨模块共享的全局态才上状态库。服务端数据优先用 TanStack Query，避免手写重复的 loading/error 逻辑。

---

## 五、路由（推荐默认 React Router v6）

| 能力 | 方案 |
|------|------|
| 基础路由 | React Router v6（`createBrowserRouter` 数据路由） |
| 懒加载 | `React.lazy` + `Suspense` 按路由分包 |
| 权限守卫 | 自定义 `ProtectedRoute` + `useAuth` hook |
| 布局嵌套 | 嵌套路由 + `Outlet`（侧边栏/顶部导航布局复用） |

---

## 六、CSS 方案（固定预编译 + 模块化 + 全局抽离）

| 项 | 选型 | 说明 |
|----|------|------|
| 预编译 | Sass（SCSS） | 变量/mixin/嵌套 |
| 组件样式 | CSS Modules（`*.module.scss`） | 组件级隔离 |
| 全局样式 | `src/styles/` 抽离 | variables/mixins/global/theme |
| 设计 token | CSS 变量 | 支持暗黑模式/主题切换 |

> 详见 `css-guide.md`。

---

## 七、请求（固定原生 fetch）

| 项 | 选型 | 说明 |
|----|------|------|
| 请求库 | 原生 fetch（不引入 axios） | 现代浏览器原生支持 |
| 封装 | `src/api/request.ts` 统一封装 | baseURL/超时/错误/token/取消 |
| 业务接口 | `src/api/<模块>.ts` 按域拆分 | 与后端 TDD 接口一一对应 |

> 详见 `fetch-guide.md`。

---

## 八、测试框架（固定 Vitest + RTL）

| 项 | 选型 | 说明 |
|----|------|------|
| 单测框架 | Vitest | 与 Vite 无缝、快 |
| 组件测试 | React Testing Library | 以用户视角测试 |
| hooks 测试 | `renderHook` | 独立测试 hooks 逻辑 |
| 覆盖率 | `@vitest/coverage-v8` | 企业级档要求 |

> 详见 `test-guide.md`。

---

## 九、浏览器兼容性（每次必问）

| 用户意图 | 方案 |
|---------|------|
| 指定目标浏览器（如兼容 IE11 / 老安卓） | Vite `build.target` + `@vitejs/plugin-legacy`；CSS 加 `autoprefixer` 前缀 |
| 不指定 | **以 Vite 默认浏览器目标为准**（现代浏览器：ES2020+），总文档显式声明 |

> 企业级档若需兼容旧浏览器，需额外评估 polyfill 体积与构建产物。

---

## 十、工程规范（企业级档）

| 项 | 选型 |
|----|------|
| 代码规范 | ESLint + Prettier |
| 提交规范 | Husky + lint-staged + commitlint |
| 类型检查 | `tsc --noEmit` 纳入 CI |
| 环境变量 | Vite `import.meta.env`，`.env.development` / `.env.production` |

---

## 十一、选型决策表模板（总文档用）

| 组件 | 选型 | 档位 | 理由 | 备选 |
|------|------|------|------|------|
| 框架 | React 18 | 企业级 | hooks 为主 | Vue 3 |
| 构建 | Vite + pnpm + TS | 企业级 | 开发快、类型强 | — |
| 组件库 | Ant Design | 企业级 | 中后台生态 | Arco / 自研 |
| 状态管理 | Zustand + TanStack Query | 企业级 | 轻量 + 服务端缓存 | Redux Toolkit |
| 路由 | React Router v6 | 企业级 | 数据路由 + 懒加载 | — |
| CSS | Sass + CSS Modules | 企业级 | 模块化 + 变量 | Less |
| 请求 | 原生 fetch 封装 | 企业级 | 无依赖 | — |
| 测试 | Vitest + RTL | 企业级 | Vite 原生 | Jest |
| 主题 | CSS 变量 + data-theme | 企业级 | 暗黑模式 | — |
| i18n | react-i18next | 企业级 | 生态成熟 | — |
| 浏览器兼容 | Vite 默认（现代浏览器） | 企业级 | 用户未指定 | — |
