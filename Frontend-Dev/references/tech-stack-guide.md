# 各端工程落地骨架指南

> 用途：把 FTDD 的技术选型落成「可运行工程骨架」。**技术选型本身来自 FTDD**（不重新选型）；本指南提供 web/app/小程序三端的标准落地骨架、依赖清单、fetch 封装与端差异要点。
> 版本给的是「常用稳定版」，落地时以 FTDD 指定版本或官方稳定版为准（可用 Playwright/browser-use 查最新版本）。

---

## 一、端与选型来源

| 端 | 典型选型（由 FTDD 决定，此处为常用参考） | 工程特征 |
|----|--------------------------------|---------|
| web | React + Vite + pnpm + TS（FTDD 固定栈） | SPA，浏览器运行 |
| app | React Native / Flutter / uni-app | 移动原生/跨端，按团队熟悉度必问 |
| 小程序 | 微信原生 / Taro / uni-app | 微信等平台小程序 |

> 覆盖端判定见 SKILL §三-步骤1；选型冲突时：FTDD 存在→照 FTDD；缺失→补选型（档位 + 组件库 + 端选型必问）；覆盖端不符→阻塞。

---

## 二、web 端工程落地骨架（React + Vite + pnpm + TS）

### 2.1 目录树（对齐 FTDD overview §6）

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
    ├── main.tsx                # 入口：挂载 Router + Provider + global.scss
    ├── api/                    # request.ts + 按域拆分
    ├── components/             # 基础组件 + 跨模块业务组件
    ├── hooks/                  # 通用 hooks
    ├── pages/                  # 页面容器（页面 = 路由）
    ├── styles/                 # variables/mixins/global/theme
    ├── features/               # 业务模块（<模块>/components + hooks）
    ├── router/                 # 路由配置 + 守卫 + 懒加载
    ├── store/                  # 全局状态（按 FTDD）
    ├── locales/                # i18n（按需）
    ├── utils/  ├── types/      # 工具 / 全局类型
    └── Test/                   # 测试 setup
```

### 2.2 关键依赖（参考版本）

| 依赖 | 用途 | 参考版本 |
|------|------|---------|
| `react` / `react-dom` | 框架 | ^18.3.0 |
| `react-router-dom` | 路由 | ^6.26.0 |
| `zustand` 或 `@reduxjs/toolkit` | 全局状态 | 按 FTDD |
| `@tanstack/react-query` | 服务端数据（可选） | ^5.x |
| `sass` | CSS 预编译（Less 生态换 `less`，随 FTDD 选型） | ^1.77.0 |
| `vitest` / `@testing-library/react` / `@testing-library/user-event` / `@testing-library/jest-dom` | 测试 | ^2.x / ^16.x |
| `@vitejs/plugin-react` / `typescript` | 构建/类型 | ^4.x / ^5.5.0 |
| ESLint + Prettier + Husky | 工程规范（企业级档） | 最新稳定 |

### 2.3 fetch 统一封装（模板，直接落地为 src/api/request.ts）

> 与 FTDD `fetch-guide` 约定一致：原生 fetch，不引入 axios。**组件/hooks 不直接用裸 fetch**。

```ts
// src/api/request.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: unknown;
  timeout?: number;
  signal?: AbortSignal;
}

// token 载体按 FTDD 安全规范：Access Token 存内存（setAuthToken 注入）、Refresh Token 存 HttpOnly Cookie；禁 localStorage 明文（见 decision-rules.md §七）
let memoryToken = '';
export const setAuthToken = (token: string) => { memoryToken = token; };

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', headers = {}, body, timeout = 10000, signal } = options;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  const onAbort = () => controller.abort();
  signal?.addEventListener('abort', onAbort);

  // token 载体按 FTDD 安全规范：Access Token 存内存、Refresh Token 存 HttpOnly Cookie；
  // 本封装经 setAuthToken 注入，禁止读写 localStorage 明文 token（见 decision-rules.md §七）。
  const token = memoryToken;
  const config: RequestInit = {
    method,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...headers },
    signal: controller.signal,
  };
  if (body !== undefined) config.body = JSON.stringify(body);

  try {
    const res = await fetch(`${BASE_URL}${path}`, config);
    clearTimeout(timer);
    signal?.removeEventListener('abort', onAbort);
    if (!res.ok) throw new ApiError(res.status, `请求失败：${res.status}`, 'HTTP_ERROR');
    return (await res.json()) as T;
  } catch (err) {
    clearTimeout(timer);
    signal?.removeEventListener('abort', onAbort);
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError(0, '请求超时或已取消', 'TIMEOUT');
    }
    throw new ApiError(0, '网络异常', 'NETWORK_ERROR');
  }
}
```

业务方法按域拆分，签名与后端 TDD 接口一一对应：

```ts
// src/api/order.ts —— 对应 TDD：GET /api/orders、POST /api/orders、PUT /api/orders/:id
export interface Order { id: string; status: 'pending' | 'paid' | 'cancelled'; /* ... */ }
export interface OrderListResult { list: Order[]; total: number; }

export const orderApi = {
  getOrderList: (params: { page: number; pageSize: number }) => {
    const qs = new URLSearchParams({ page: String(params.page), pageSize: String(params.pageSize) });
    return request<OrderListResult>(`/api/orders?${qs}`);
  },
  createOrder: (payload: Omit<Order, 'id'>) => request<Order>('/api/orders', { method: 'POST', body: payload }),
  cancelOrder: (id: string) => request<void>(`/api/orders/${id}/cancel`, { method: 'POST' }),
};
```

### 2.4 运行命令（交付 README 必须含）

```bash
pnpm install
pnpm dev        # 本地开发
pnpm build      # 生产构建（tsc --noEmit && vite build）
pnpm test       # 跑测试（vitest run）
pnpm test:coverage
```

---

## 三、app / 小程序端落地骨架

> 端选型在补选型阶段必问（用户拍板，不给默认替代）。以下给出通用落地点。

### 3.1 app（React Native / Flutter / uni-app）

| 项 | RN（TS） | Flutter（Dart） | uni-app（Vue） |
|----|---------|----------------|---------------|
| 工程 | `@react-native-community/cli` init | `flutter create` | `vue create -p dcloudio/uni-preset-vue` |
| 页面路由 | React Navigation（stack/tab） | Navigator 2.0 / go_router | pages.json |
| 样式 | StyleSheet + 主题 token | ThemeData / TextStyle | uni.scss + rpx |
| 请求 | fetch 封装（FTDD 选 axios 时经统一契约层接入） | http/dio | uni.request |
| 测试 | Jest + RTL | flutter_test | @dcloudio/uni-automator |

- **还原基线跨端一致**：布局/间距/配色/字号按「设计稿刻度」换算（RN 用 dp、Flutter 用逻辑像素、uni-app 用 rpx），与原型对不上的间距一律修实现而非降标准；
- 组件抽离铁律不变：模块私有组件进 `features/<模块>/components/`（或 RN 的按模块 components 目录），跨模块进 `src/components/`（RN/Flutter 同理落到全局组件目录）。

### 3.2 小程序（微信原生 / Taro / uni-app）

| 项 | 微信原生 | Taro（React） | uni-app（Vue） |
|----|---------|--------------|---------------|
| 工程 | 微信开发者工具创建 | `taro init` | uni-app 模板 |
| 页面 | `app.json` pages 注册 | 约定 pages 目录 + config | pages.json |
| 样式 | wxss + rpx | scss + rpx | uni.scss |
| 请求 | `wx.request` → 封装统一契约 | Taro.request | uni.request |
| 组件 | Component/自定义组件 | 与 React 组件一致 | Vue 组件 |

- **设计稿换算**：小程序 rpx 以 750 设计稿为准——原型上的 `px` 值按「设计稿宽度 / 750」换算 rpx；组件抽离铁律与 hooks（逻辑层）同样适用；
- 若 FTDD 未覆盖小程序而本次要开发小程序 → 按 SKILL §六阻塞，提示先补方案。

---

## 四、还原要点（跨端通用）

1. **token 先行**：从原型抽取色板/间距/字号/圆角 → `styles/variables.{scss|less}`（扩展名随 FTDD 选型，CSS 变量），全站引用 token，不写死；
2. **布局基线**：区块顺序、栅格、对齐方式以原型 HTML 结构为准，实现时逐区块核对；
3. **三态齐全**：加载/空/错误三个状态按原型或 PRD 兜底方案实现，禁止只做成功态；
4. **交互细节**：hover/点击/禁用/表单校验反馈与原型交互标注一致；
5. **静态资源**：图片/图标从原型提取（同名/同尺寸），路径登记进产物 README。

---

## 五、工程规范（企业级档）

| 项 | 落地 |
|----|------|
| 代码规范 | ESLint + Prettier（React hooks 规则开启） |
| 提交粒度 | **每完成一个功能点即 commit**，一次提交一件事，便于回滚（SKILL §三 步骤 7） |
| 提交信息 | Conventional Commits：`feat(users): 用户列表页面与分页`、`fix(orders): 空态渲染异常`、`refactor(orders): 状态标签抽为模块组件`、`test(users): 用户列表 hooks 用例`、`chore: 初始化工程骨架`；仓库有约定则从仓库 |
| 提交门禁 | **eslint + stylelint + commitlint 三道全绿才提交**（详见下文 §六）；提交前 diff 自检：无 `console.log`、无临时文件、无密钥 |
| 推送策略 | **不擅自 push**，是否推送远程由用户决定 |
| 类型检查 | `tsc --noEmit` 纳入构建/CI |
| 环境变量 | Vite `import.meta.env`：`.env.development` / `.env.production` |
| 浏览器兼容 | 按 FTDD 决定（Vite 默认 / plugin-legacy） |

---

## 六、提交门禁配置（eslint + stylelint + commitlint）

> 每次提交必须过三道门禁；**报错就修，禁止 `--no-verify` 绕过**。仓库已有配置则直接复用，不重复造轮子。

### 6.1 依赖

```bash
pnpm add -D eslint @eslint/js typescript-eslint eslint-plugin-react-hooks eslint-plugin-react-refresh \
            stylelint stylelint-config-standard-scss stylelint-config-recommended-react \
            @commitlint/cli @commitlint/config-conventional husky lint-staged
```

### 6.2 配置要点

| 工具 | 作用 | 关键规则 |
|------|------|---------|
| **eslint** | JS/TS/React 代码规范 | 开启 `react-hooks` 规则（依赖数组写全）、禁 `any` 相关规则（配合 TS）、禁未使用变量 |
| **stylelint** | 样式规范（`.css/.scss`） | `stylelint-config-standard-scss`；禁止写死色值可用自定义规则约束（色值统一走 token 为约定，靠评审/还原核对兜底） |
| **commitlint** | 提交信息规范 | `@commitlint/config-conventional`：`feat/fix/refactor/test/chore/docs/style/perf` |

```js
// commitlint.config.js
export default { extends: ['@commitlint/config-conventional'] };
```

```json
// package.json（片段）
{
  "scripts": {
    "lint:es": "eslint .",
    "lint:style": "stylelint \"**/*.{css,scss}\"",
    "lint": "pnpm lint:es && pnpm lint:style",
    "prepare": "husky"
  },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix"],
    "*.{css,scss}": ["stylelint --fix"],
    "*.{json,md}": ["prettier --write"]
  }
}
```

```bash
# .husky/pre-commit —— 代码/样式门禁（lint-staged 只跑暂存文件）
pnpm lint-staged

# .husky/commit-msg —— 提交信息门禁
pnpm commitlint --edit "$1"
```

### 6.3 提交流程（每个功能点）

```bash
# 1) 只暂存本次功能点涉及的文件（monorepo 下不卷入其它包）
git add <本次改动文件>

# 2) 门禁（Husky 自动跑；未装 hook 时手动跑一遍）
pnpm lint:es && pnpm lint:style

# 3) 提交（commit-msg hook 校验信息格式）
git commit -m "feat(orders): 订单列表页面与分页"
```

- 门禁失败 → **修到通过**；确需豁免（如第三方代码）必须向用户说明并登记，**不静默 `--no-verify`**；
- 提交后确认：`git status` 干净、`git log --oneline` 信息可读、本次改动未包含无关文件。

---

## 七、monorepo 工程落地（前后端同仓库）

> 前后端共用一个 git 仓库时的落地方式。**仓库既有约定优先**；前端子包位置、共享类型包名、根配置能否改动——不确定就问用户（SKILL §八）。

### 7.1 目录结构

```
<repo>/
├── pnpm-workspace.yaml        # workspace 声明（根级，与后端共享）
├── package.json               # 根：公共 devDependencies + lint/构建脚本
├── turbo.json                 # 可选：任务编排
├── eslint.config.js           # 根级 ESLint（前端可继承 + 覆盖）
├── .stylelintrc.json          # 根级 Stylelint
├── commitlint.config.js       # 根级 commitlint（前后端共用）
├── tsconfig.base.json         # 根级 TS 基础配置
├── apps/
│   ├── web/                   # 前端包（本 Skill 产出，名字以仓库约定为准）
│   │   ├── package.json       # name: "@repo/web"
│   │   ├── vite.config.ts
│   │   ├── vitest.config.ts
│   │   └── src/             # 结构见 assets/project-structure-template.md
│   └── server/                # 后端包（Backend-Dev 产出，前端不改）
└── packages/
    └── shared-types/          # 共享类型包（前后端共用，单一来源）
        ├── package.json       # name: "@repo/shared-types"，main/types 指向 src/index.ts
        └── src/
            ├── index.ts
            ├── order.ts       # 接口请求/响应、枚举、DTO
            └── common.ts      # PageResult / PageParams 等通用结构
```

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

### 7.2 共享类型（前端只引用，不重定义）

```ts
// packages/shared-types/src/order.ts —— 与后端 TDD 接口定义一致
export interface Order {
  id: string;
  status: 'pending' | 'paid' | 'cancelled';
  amount: number;
  createdAt: string;
}
export interface PageResult<T> { list: T[]; total: number; }
export interface PageParams { page: number; pageSize: number; }
```

```ts
// apps/web/src/api/order.ts —— 引用共享类型
import type { Order, PageParams, PageResult } from '@repo/shared-types';

export const orderApi = {
  getOrderList: (params: PageParams) =>
    request<PageResult<Order>>(`/api/orders?${new URLSearchParams(...)}`),
};
```

```json
// apps/web/package.json（片段）
{
  "name": "@repo/web",
  "dependencies": { "@repo/shared-types": "workspace:*" }
}
```

- 前端私有类型（组件 props、UI 状态、表单模型）留在 `apps/web/src/types/`，不进共享包；
- 共享类型需变更 → **停下问用户**（影响后端），确认后前后端同步改（SKILL §五）。

### 7.3 配置与脚本

- `tsconfig.json` 继承根 `tsconfig.base.json`，用 `paths` 映射 `@repo/shared-types`；
- ESLint / Stylelint / commitlint **继承根配置**，前端特有规则只在 `apps/web` 内做最小覆盖；
- 脚本统一从根走：`pnpm --filter @repo/web dev` / `pnpm --filter @repo/web test`；
- **根配置、后端包、其它包 = 改动前必问用户**。
