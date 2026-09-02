# 组件与 hooks 设计规范

> 用途：指导组件分层、拆分原则与 hooks 优先的模块化开发。

---

## 一、组件分层

| 分层 | 定义 | 目录 | 示例 |
|------|------|------|------|
| 基础组件 | 无业务语义、跨项目复用 | `src/components/` | Button / Modal / Table / Form |
| 业务组件 | 有业务语义、模块内复用 | `src/features/<模块>/components/` | UserCard / OrderList |
| 页面容器 | 页面级编排组件 | `src/pages/` | `pages/users/index.tsx` |

**分层铁律**：
- 页面容器只做「编排」：组合业务组件 + 调用 hooks + 传数据，不写复杂业务逻辑；
- 业务组件可复用基础组件，禁止反向依赖（基础组件不得 import 业务组件）；
- 跨模块复用的业务组件提升到 `src/components/`（全局），仅单模块用的留在 `features/<模块>/components/`。

---

## 二、组件拆分原则

1. **单一职责**：一个组件只做一件事，职责混杂即拆；
2. **可复用优先**：出现两次以上的 UI 片段抽成组件；
3. **props 契约清晰**：用 TypeScript interface 约束 props，必填/可选明确，禁止 `any`；
4. **受控优先**：表单/交互类组件优先受控模式（value + onChange）；
5. **无副作用渲染**：渲染纯函数化，副作用放 hooks（useEffect）或事件处理器。

**props 契约示例**：
```tsx
interface UserTableProps {
  users: User[];
  loading?: boolean;
  onRowClick?: (user: User) => void;
  onDelete?: (id: string) => Promise<void>;
}
```

---

## 三、hooks 优先（模块化开发核心）

> 逻辑一律抽成自定义 hooks，组件只负责渲染与绑定。

### 3.1 hooks 分层

| 类型 | 目录 | 示例 |
|------|------|------|
| 通用 hooks | `src/hooks/` | `useFetch` / `useDebounce` / `useLocalStorage` |
| 模块私有 hooks | `src/features/<模块>/hooks/` | `useUserList` / `useOrderForm` |

### 3.2 hooks 命名与职责

| 领域 | hook | 职责 |
|------|------|------|
| 数据获取 | `useFetch` / `useQuery` | 请求 + loading/error/data 状态管理 |
| 表单 | `useForm` | 表单值、校验、提交状态 |
| 权限 | `useAuth` / `usePermission` | 登录态、按钮/路由级权限 |
| 主题 | `useTheme` | 暗黑模式/主题切换 + 持久化 |
| 通用 | `useDebounce` / `useLocalStorage` | 通用工具逻辑 |

### 3.3 hooks 设计要点

- **单一数据流**：hook 返回 `{ data, loading, error, refetch }` 统一形态，组件据此渲染三态（加载/成功/失败）；
- **可复用可测试**：hooks 独立于组件，用 `renderHook` 单独测试；
- **副作用可清理**：`useEffect` 返回清理函数，防内存泄漏；
- **依赖明确**：`useEffect`/`useCallback`/`useMemo` 依赖数组写全。

### 3.4 数据获取 hook 示例

```tsx
// src/hooks/useFetch.ts
import { useCallback, useEffect, useState } from 'react';

interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useFetch<T>(fetcher: () => Promise<T>, deps: unknown[] = []): FetchState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const run = useCallback(() => {
    setLoading(true);
    setError(null);
    fetcher()
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    run();
  }, [run]);

  return { data, loading, error, refetch: run };
}
```

---

## 四、模块化目录结构约定

```
src/
├── api/                    # fetch 请求封装（request.ts + 按域拆分）
├── components/             # 基础组件 + 跨模块业务组件
├── hooks/                  # 通用 hooks
├── pages/                  # 页面容器（对应路由）
├── styles/                 # 全局样式（variables/mixins/global/theme）
├── features/               # 业务模块（模块化开发）
│   └── users/
│       ├── components/     # 模块私有业务组件
│       ├── hooks/          # 模块私有 hooks
│       └── index.tsx       # 模块入口
├── router/                 # 路由配置
├── store/                  # 全局状态（Zustand/Redux）
├── locales/                # 国际化语言包（可选）
├── utils/                  # 工具函数
└── types/                  # 全局类型定义
```

---

## 五、组件方案自检清单

- [ ] 组件分层清晰（基础/业务/页面容器）？
- [ ] 每个组件单一职责、props 用 TS 约束？
- [ ] 业务逻辑下沉 hooks，组件只渲染？
- [ ] 数据获取统一走 `useFetch`/`useQuery`，三态齐全？
- [ ] 无副作用渲染，副作用在 hooks/事件处理器？
- [ ] 目录按模块化组织，跨模块复用组件已提升？
