# 【前端技术方案总文档】{{PRODUCT_NAME}} 前端 FTDD

> **文档状态**：`[草稿] / [待评审] / [已定稿]`
> **责任前端架构师**：{{AUTHOR_NAME}}　|　**创建/更新**：{{DATE}}
> **实现档位**：`[企业级生产] / [demo 快速实现]`
> 📐 本文件是前端技术方案 **L1 总文档**：定选型、画架构、列页面与组件、划模块边界、定全局规范；模块细节在 `NN_xxx.md`。

---

## 1. 文档元数据

| 字段 | 内容 |
|------|------|
| 项目名称 | {{PRODUCT_NAME}} |
| 需求来源 | PRD `{{PRD_PATH}}` / 原型 `{{PROTO_PATH}}` / 后端 TDD `{{TDD_PATH}}` |
| 实现档位 | {{企业级生产 / demo 快速实现}} |
| 固定技术栈 | pnpm + Vite + TypeScript + React（hooks）+ 原生 fetch + Sass |

---

## 2. 技术选型总览

| 组件 | 选型 | 档位 | 理由 | 备选 |
|------|------|------|------|------|
| 框架 | React 18 | {{TIER}} | hooks 为主 | Vue 3 |
| 构建 | Vite + pnpm + TS | {{TIER}} | 开发快、类型强 | — |
| 组件库 | {{UI_LIB / 自研}} | {{TIER}} | {{REASON}} | {{ALT}} |
| 状态管理 | {{Zustand / Redux Toolkit / TanStack Query}} | {{TIER}} | {{REASON}} | {{ALT}} |
| 路由 | React Router v6 | {{TIER}} | 数据路由 + 懒加载 | — |
| CSS | Sass + CSS Modules | {{TIER}} | 模块化 + 变量 | Less |
| 请求 | 原生 fetch 封装 | {{TIER}} | 无依赖 | — |
| 测试 | Vitest + React Testing Library | {{TIER}} | Vite 原生 | Jest |
| 暗黑模式/主题 | {{开启 / 不开}} | {{TIER}} | {{REASON}} | — |
| 国际化 i18n | {{开启 / 不开}} | {{TIER}} | {{REASON}} | — |
| 浏览器兼容性 | {{Vite 默认 / 用户指定}} | {{TIER}} | {{REASON}} | — |

> 选型规则见 `references/tech-stack-guide.md`。

---

## 3. 前端架构图（Mermaid，强制）

```mermaid
flowchart TB
    subgraph 用户层
        U[用户浏览器]
    end
    subgraph 前端应用
        Router[路由层 React Router]
        Pages[页面容器层]
        Components[组件层 基础/业务组件]
        Hooks[hooks 逻辑层]
        Store[全局状态 Store]
        Api[请求层 fetch 封装]
        Styles[样式层 Sass + CSS Modules]
    end
    subgraph 后端
        GW[API 网关]
        SVC[后端服务 TDD]
    end

    U --> Router
    Router --> Pages
    Pages --> Components
    Pages --> Hooks
    Components --> Hooks
    Hooks --> Api
    Hooks --> Store
    Api --> GW --> SVC
    Components --> Styles
    Pages --> Styles
```

> 架构图按实际选型绘制分层，标注数据流方向。

---

## 4. 页面清单（页面 = 路由）

| 序号 | 路由 | 页面名称 | 所属模块 | 职责 | 对应原型文件 |
|------|------|---------|---------|------|-------------|
| 01 | {{/path}} | {{PAGE_A}} | {{MODULE_A}} | {{DUTY}} | {{proto.html}} |
| 02 | {{/path/:id}} | {{PAGE_B}} | {{MODULE_B}} | {{DUTY}} | {{proto.html}} |

---

## 5. 组件清单

### 5.1 基础组件（跨项目复用）

| 组件 | 职责 | 来源 |
|------|------|------|
| {{Button / Modal / Table ...}} | {{DUTY}} | {{组件库 / 自研}} |

### 5.2 业务组件（模块内复用）

| 组件 | 分层 | 职责 | 复用范围 |
|------|------|------|---------|
| {{UserTable}} | 业务组件 | {{DUTY}} | 模块内 / 全局 |

### 5.3 基础支持（横切关注点）

| 支持项 | 方案 | 说明 |
|--------|------|------|
| 路由守卫 | {{ProtectedRoute + useAuth}} | 登录/权限拦截 |
| 错误边界 | {{ErrorBoundary}} | 渲染异常兜底 |
| 请求层 | {{request.ts fetch 封装}} | 见 §8.1 |
| 主题切换 | {{useTheme + CSS 变量}} | 可选 |
| 国际化 | {{react-i18next}} | 可选 |

---

## 6. 工程目录结构

```
{{PROJECT_NAME}}/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── vitest.config.ts
├── .env.development
├── .env.production
└── src/
    ├── api/                 # fetch 请求封装 + 按域拆分
    ├── components/          # 基础组件 + 跨模块业务组件
    ├── hooks/               # 通用 hooks
    ├── pages/               # 页面容器
    ├── styles/              # 全局样式（variables/mixins/global/theme）
    ├── features/            # 业务模块（模块化开发）
    ├── router/              # 路由配置
    ├── store/               # 全局状态
    ├── locales/             # 国际化语言包（可选）
    ├── utils/               # 工具函数
    ├── types/               # 全局类型
    └── Test/                # 测试 setup
```

---

## 7. 模块清单与边界（应做 / 不应做）

| 序号 | 文件名 | 模块名称 | 应做（前端技术职责） | 不应做（负向边界） | 关键产出 |
|------|--------|---------|--------------------|-------------------|---------|
| 01 | `01_xxx.md` | {{MODULE_A}} | 承载哪些页面/提供哪些 hooks/消费哪些接口 | {{明确排除}} | {{页面+组件+hooks}} |
| 02 | `02_xxx.md` | {{MODULE_B}} | {{B_DO}} | {{B_DONT}} | {{B_OUTPUT}} |

---

## 8. 全局技术规范

### 8.1 fetch 请求封装（实例）

> 完整可运行实例见 `references/fetch-guide.md`；此处贴核心骨架。

```ts
// src/api/request.ts（核心）
export class ApiError extends Error {
  constructor(public status: number, message: string, public code?: string) {
    super(message);
  }
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  // baseURL + 超时(AbortController) + token 注入 + 统一错误处理
  // 详见 references/fetch-guide.md 完整实现
}
```

### 8.2 全局命名规范

- 文件/目录：组件与 hooks 用 PascalCase（`UserTable.tsx` / `useUserList.ts`），工具/配置用 camelCase；
- 接口方法：`getXxx / createXxx / updateXxx / deleteXxx`；
- hooks：一律 `use` 前缀；
- CSS：CSS Modules（`*.module.scss`），类名语义化。

### 8.3 环境变量规范

| 变量 | 说明 |
|------|------|
| `VITE_API_BASE_URL` | 后端接口 baseURL |
| `VITE_APP_TITLE` | 应用标题 |
| {{其它}} | {{说明}} |

### 8.4 错误处理规范

- 请求错误统一由 `ApiError` 承载，UI 按 code 分类提示（HTTP 错误 / 超时 / 网络异常）；
- 渲染异常由 `ErrorBoundary` 兜底；
- 401 统一跳登录。

### 8.5 权限规范（企业级档）

- 路由级：`ProtectedRoute` + `useAuth`；
- 按钮级：`usePermission` 控制显隐。

---

## 9. 测试策略

| 项 | 说明 |
|----|------|
| 测试框架 | Vitest + React Testing Library |
| 测试对象 | 页面 / 组件 / hooks |
| 覆盖要求 | 渲染 / 交互 / 数据流 / 边界 / 异常 |
| AC 追溯 | 测试用例承接 PRD 的 AC 编号 |

---

## 10. 模块关联关系图（Mermaid + 关联表）

```mermaid
flowchart LR
    M01[01 用户模块] -- 路由跳转 --> M02[02 订单模块]
    M01 -- 共享用户态 --> M02
```

### 关联表（逐条验证闭环）

| 关联边 | 输出方提供什么 | 承接方如何消费 | 方式（路由跳转/共享组件/共享状态/接口依赖） |
|--------|---------------|---------------|------------------------------------------|
| 01 → 02 | {{用户态/组件/路由}} | {{如何消费}} | {{方式}} |
