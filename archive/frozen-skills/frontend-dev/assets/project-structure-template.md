# 工程目录结构模板

> 用途：步骤 3「工程初始化」时，把 FTDD 技术选型落成可运行工程。**目录结构以 FTDD overview §6 为准**，本模板给出落地清单与基础设施先行原则。
> 使用时机：步骤 3「工程初始化」。**工程建在用户在步骤 1 给定的目标目录里**（目录名用给定目录名或用户自定义名称，不套用任何按端命名约定），替换 `{{PROJECT_NAME}}`。

---

## 一、工程根目录（web 端示例）

```
{{PROJECT_NAME}}/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── vitest.config.ts
├── eslint.config.js            # ESLint（提交门禁）
├── .stylelintrc.json           # Stylelint（提交门禁）
├── commitlint.config.js        # commitlint（提交门禁）
├── .prettierrc                 # 企业级档
├── .husky/                     # pre-commit（lint-staged）+ commit-msg（commitlint）
├── .env.development
├── .env.production
├── README.md                   # 运行说明（交付必含）
├── PROJECT.md                  # 项目说明与进度（断点续做入口，见 project-status-template.md）
└── src/
    ├── main.tsx                # 入口：挂载 Provider + Router + 全局样式
    ├── App.tsx                 # 根组件（Routes + ErrorBoundary + 布局骨架）
    ├── vite-env.d.ts
    ├── api/
    │   ├── request.ts          # 统一 fetch 封装（ApiError/token/超时/取消）
    │   ├── auth.ts             # 按域拆分……
    │   └── order.ts
    ├── components/             # 基础组件 + 跨模块业务组件（共享层）
    │   ├── Button.tsx
    │   ├── UserSelect.tsx      # 跨模块业务组件
    │   └── index.ts            # 统一出口（按需导出，避免全量 tree-shaking 问题）
    ├── features/               # 业务模块（与 FTDD 模块清单一一对应）
    │   └── orders/
    │       ├── components/     # 模块私有业务组件（模块内 ≥2 次复用）
    │       │   ├── OrderStatusTag.tsx
    │       │   └── OrderStatusTag.module.scss
    │       ├── hooks/          # 模块私有 hooks
    │       │   ├── useOrderList.ts
    │       │   └── useOrderList.test.ts
    │       ├── OrderListPage.tsx        # 模块页面容器（也可集中到 pages/，以 FTDD 为准）
    │       ├── OrderListPage.module.scss
    │       └── OrderListPage.test.tsx
    ├── hooks/                  # 通用 hooks
    │   ├── useFetch.ts
    │   ├── useDebounce.ts
    │   ├── useAuth.ts
    │   └── index.ts
    ├── pages/                  # 页面容器（若 FTDD 用集中式 pages 组织）
    ├── router/
    │   ├── index.tsx           # createBrowserRouter 路由表 + 懒加载
    │   ├── guards.tsx          # 登录/权限守卫
    │   └── routes.ts           # 路由枚举/常量（与页面一一对应）
    ├── store/                  # 全局状态（按 FTDD：zustand / RTK）
    ├── styles/
    │   ├── variables.scss      # 设计 token（色板/间距/字号/圆角/阴影——设计稿 design-system §7 抽取；无设计稿才取原型）
    │   ├── mixins.scss         # 断点/文本溢出等 mixin
    │   ├── global.scss         # reset + 全局样式
    │   └── theme.scss          # 主题覆盖（按需）
    ├── locales/                # i18n（企业级档，按需）
    ├── utils/                  # 纯函数工具
    ├── types/                  # 全局类型
    └── Test/                   # vitest.setup.ts 等
```

> 页面容器归属二选一：集中式 `src/pages/`（FTDD §6 常见）或按模块内聚 `features/<模块>/*Page.tsx`——**以 FTDD overview §6 为准**，本模板两种都给出。

### 1.1 monorepo 落位（前后端同仓库）

> 详见 `references/tech-stack-guide.md` §七。要点：

```
<repo>/                          # 用户给定 git 仓库
├── pnpm-workspace.yaml          # 根级（与后端共享）
├── package.json                 # 根级公共 devDependencies + lint 脚本
├── eslint.config.js             # 根级 ESLint（前端继承 + 最小覆盖）
├── .stylelintrc.json            # 根级 Stylelint
├── commitlint.config.js         # 根级 commitlint
├── tsconfig.base.json           # 根级 TS 基础配置
├── apps/
│   ├── web/                     # 前端子包（本模板 §一 的 src/ 落这里；PROJECT.md 也落这里）
│   └── server/                  # 后端包（Backend-Dev 产出，前端不改）
└── packages/
    └── shared-types/            # 共享类型包（前后端共用，单一来源）
```

- 前端只动 `apps/web/` 内文件；根配置/后端包/共享包结构改动前必问用户；
- 依赖共享类型：`"@repo/shared-types": "workspace:*"`，`import type { Order } from '@repo/shared-types'`。

---

## 二、依赖清单（落地 package.json）

| 类目 | 依赖 | 说明 |
|------|------|------|
| 框架 | `react` `react-dom` | 按 FTDD 版本 |
| 路由 | `react-router-dom` | 路由 + 守卫 + 懒加载 |
| 状态 | 按 FTDD（zustand / RTK） | 仅跨模块共享态 |
| 数据 | 按 FTDD（TanStack Query / 自研 useFetch） | 服务端数据 |
| 样式 | `sass` | CSS Modules + 变量 |
| 测试 | `vitest` `@testing-library/react` `@testing-library/user-event` `@testing-library/jest-dom` | 测试先行 |
| 工程 | `@vitejs/plugin-react` `typescript` `eslint` `prettier` `husky`（企业级） | 规范与类型 |
| 提交门禁 | `eslint` `stylelint` `stylelint-config-standard-scss` `@commitlint/cli` `@commitlint/config-conventional` `husky` `lint-staged` | 每次提交 eslint + stylelint + commitlint（配置见 tech-stack-guide §六） |

> 版本参考 tech-stack-guide §2.2；落地前可用 Playwright/browser-use（若可用）查官方最新稳定版。

---

## 三、基础设施先行清单（步骤 3 落地，模块才可复用）

| 基础设施 | 落地物 | 说明 |
|---------|--------|------|
| 请求封装 | `src/api/request.ts` | fetch + ApiError + token + 超时 + AbortController 取消 |
| 样式 token | `src/styles/variables.scss` 等 | 从设计稿 `design-system.md` §7 抽取的设计 token 先落地并与实现逐条对账；无设计稿才取原型 |
| 路由 | `src/router/`（路由表 + 守卫 + 懒加载） | 页面 = 路由，与 FTDD 页面清单一一对应 |
| 通用 hooks | `src/hooks/useFetch/useDebounce/useAuth` | 供各模块 hooks 复用 |
| 错误兜底 | `src/App.tsx` 挂 ErrorBoundary | 渲染异常兜底 |
| 环境变量 | `.env.development` / `.env.production` | `VITE_API_BASE_URL` 等 |
| 测试环境 | `vitest.config.ts` + `src/test/setup.ts` | jsdom + jest-dom + cleanup |
| 模块目录 | `src/features/<模块>/{components,hooks}` 空壳 | 逐模块填内容 |

---

## 四、运行说明模板（产物 README 必含）

```markdown
# {{需求名}}（web 端）

## 技术栈
React + Vite + TypeScript + React Router + Zustand/TanStack Query + Sass + Vitest

## 快速开始
pnpm install
pnpm dev

## 命令
pnpm build        # 构建（含 tsc --noEmit）
pnpm test         # 单测
pnpm test:coverage

## 目录结构
（见本模板 §一）

## 页面清单
| 路由 | 页面 | 对应 FTDD 模块 | 还原基线 |
|------|------|---------------|---------|
| /orders | 订单列表 | 01 订单模块 | 见基线清单 |

## 还原核对记录
方式：Playwright 自动截图 / browser-use 截图
结论：逐页结论表（见 fidelity-guide §3.3）
```

---

## 五、初始化自检清单

- [ ] 目录结构与 FTDD overview §6 一致？
- [ ] package.json 依赖与选型一致、版本已锁？
- [ ] request.ts / styles token / router / 通用 hooks / ErrorBoundary 已落地？
- [ ] vitest 环境可跑通一个冒烟测试？
- [ ] eslint / stylelint / commitlint 三套配置 + Husky hook 已就位、可跑通？
- [ ] monorepo 场景：子包落位、共享类型引用、根配置继承已按仓库约定接好？
- [ ] `PROJECT.md` 已建（步骤 6 生成）？
- [ ] `pnpm dev` 可启动、`pnpm build`（tsc --noEmit）通过？