# 前端分层架构与模块化规范

> 用途：前端代码「怎么分层、怎么组织、组件放哪」的权威规范。模块化防重的第一落地手段是清晰的分层 + 组件抽离铁律。
> 本规范是权威；`assets/` 模板是本规范的骨架，二者冲突时以本规范为准。目录结构以 FTDD overview §6 为唯一来源，本规范给出的是组织原则。

---

## 一、前端分层（依赖单向向下）

```
┌────────────────────────────────────────────────────────────┐
│  页面容器（src/pages/xxx.tsx）                               │
│  职责：页面级编排——组合业务组件 + 组合 hooks + 传数据 + 路由出口 │
│  禁止：写复杂业务逻辑、直接调 api、直接操作 store              │
├────────────────────────────────────────────────────────────┤
│  组件层（基础组件 / 业务组件）                                │
│  职责：渲染 + 交互；业务组件在 features/<模块>/components/     │
│       或 src/components/（见 §三 组件抽离铁律）               │
│  禁止：直接调 api、持有全局状态写逻辑                         │
├────────────────────────────────────────────────────────────┤
│  hooks 逻辑层（src/hooks/ + features/<模块>/hooks/）         │
│  职责：数据获取/表单/权限/主题等可复用逻辑，返回三态            │
│  禁止：操作 DOM、直接渲染 UI                                │
├────────────────────────────────────────────────────────────┤
│  api 请求层（src/api/）                                      │
│  职责：fetch 封装 + 按业务域拆分，与后端接口一一对应            │
│  禁止：写业务逻辑、处理 UI 状态                              │
└────────────────────────────────────────────────────────────┘
```

### 1.1 各层职责边界

| 层 | 做什么 | 不做什么 | 判错口诀 |
|----|--------|---------|---------|
| 页面容器 | 组合组件/hooks、传 props、编排布局 | 业务判断、数据抓取、直接调 api | 页面里出现 `userApi.` 或大段 if 业务 = 越界 |
| 业务组件 | 渲染数据 + 交互回调（props 驱动） | 直接 import api、手写 loading/error | 组件里出现 `fetch`/`userApi` = 越界 |
| hooks | 封装逻辑：请求、表单、权限、主题 | 渲染 JSX、操作 DOM | hook 返回 JSX = 越界 |
| api | fetch 请求、参数拼装、返回类型化数据 | 业务规则、UI 状态 | api 文件里出现组件逻辑 = 越界 |

### 1.2 依赖方向

- 上层可依赖下层，**下层绝不可依赖上层**；同层之间基础组件可被业务组件依赖，反向禁止；
- 业务组件跨模块复用 → 提升到 `src/components/`（共享层），两个模块共同依赖共享层，**禁止 A 模块组件被 B 模块直接 import**；
- hooks 与 api 同理：跨模块复用的 hooks 提升到 `src/hooks/`，跨模块复用的 api 本就按域放 `src/api/`。

---

## 二、模块化组织（按业务域分包）

### 2.1 目录组织原则

```
src/
├── api/                    # fetch 封装（request.ts）+ 按业务域拆分 <模块>.ts
├── components/             # 基础组件 + 跨模块业务组件（全局共享层）
├── hooks/                  # 通用 hooks（useFetch/useDebounce/useAuth…）
├── pages/                  # 页面容器（对应路由，页面 = 路由）
├── styles/                 # variables/mixins/global/theme（设计 token 先落地）
├── features/               # 业务模块（与 FTDD 模块清单一一对应）
│   └── users/              # 模块 users
│       ├── components/     # 模块私有业务组件（模块内复用）
│       ├── hooks/          # 模块私有 hooks（useUserList…）
│       └── index.ts        # 模块入口（按需导出）
├── router/                 # 路由配置 + 守卫 + 懒加载
├── store/                  # 全局状态（按 FTDD）
├── locales/                # i18n 语言包（按需）
├── utils/                  # 纯工具函数
├── types/                  # 前端私有全局类型（组件 props/UI 状态/表单模型）
└── Test/                   # 测试 setup（vitest.setup.ts 等）
```

> monorepo（前后端同仓库）下：接口请求参数/响应/枚举/DTO/分页结构等**前后端共用类型**放共享包（如 `packages/shared-types`），前端 `import type { Order, PageResult } from '@repo/shared-types'` **只引用不重定义**；前端私有类型才放 `src/types/`（详见 SKILL §五）。

> 具体目录树以 FTDD overview §6 为准；features 下模块命名与 FTDD 模块文件名 `NN_xxx` 语义对应（如 `01_用户模块` → `features/users`）。

### 2.2 模块内聚与模块解耦

- **模块内部高内聚**：一个业务域的页面、组件、hooks、api 按域各归其位，禁止散落全局；
- **跨模块只走共享层**：模块 A 想用模块 B 的能力 → 若组件，提升到 `src/components/`；若逻辑，提升到 `src/hooks/`；若数据，走 api/store——**禁止 A 直接 import B 的私有目录**；
- **重复即抽离**：任何 UI 片段/逻辑出现第二次复用前，先抽离再写第二处（见 §三），不允许两份实现。

---

## 三、组件抽离铁律（复用防重核心）

> 组件归属判定 = **复用次数 × 复用范围**，编码当下实时判定。

| # | 条件 | 归属目录 | 依据 |
|---|------|---------|------|
| 1 | 同一模块内被 **≥2 处**复用的 UI/结构 | `src/features/<模块>/components/` | 模块私有业务组件 |
| 2 | **两个不同模块**共用同一组件 | `src/components/` | 跨模块共享层 |
| 3 | 无业务语义、跨工程可复用 | 组件库（选用时）或 `src/components/` | 基础组件 |

### 3.1 判定流程（编码当下执行）

```
要写第 N 处 UI 结构
        │
        ▼
本模块内是否已存在相同结构？
  否 ──► 首次出现：就地写；同时判断「该结构是否可能被其它模块复用？」
                │ 预计会跨模块（如通用用户选择器）
                ▼ 直接放到 src/components/（一次到位）
  是 ──► 第 2 次出现（≥2 次复用）
                │
                ├─ 仅本模块用 ──► 抽成 features/<模块>/components/<X>.tsx
                │
                └─ 已在 ≥2 个模块出现 ──► 提升 src/components/<X>.tsx（删除模块私有副本，更新全部引用）
```

### 3.2 抽离落地规范

- **先抽离后复用**：写第 2 处引用点之前，先把组件抽好，禁止「复制一份、以后再说」；
- **props 契约清晰**：抽离组件用 TypeScript interface 定义 props（必填/可选明确），禁止 `any`；受控优先（`value + onChange`）；
- **归属变更同步**：模块私有 → 全局时，`git mv` 移动文件、更新所有 import、删除旧文件，禁止新旧并存；
- **命名语义化**：`<模块语义><形态>`，如 `UserTable` / `SearchBar` / `OrderStatusTag`；文件同名 PascalCase（`.tsx`）；
- **超过一次跨模块复用的判定要过 Scope 检查**：模块收尾时全量扫描 `components/`，确认没有「应提升未提升」「重复实现」残留。

### 3.3 抽离判断示例

```tsx
// 场景：订单模块内，列表页 + 详情页两处都要展示「订单状态标签」
// 判定：同一模块内 ≥2 处复用 → 抽成模块私有组件
// src/features/orders/components/OrderStatusTag.tsx
import styles from './OrderStatusTag.module.scss';

interface OrderStatusTagProps {
  status: OrderStatus; // 'pending' | 'paid' | 'cancelled'
}

const textMap: Record<OrderStatus, string> = {
  pending: '待支付',
  paid: '已支付',
  cancelled: '已取消',
};

export function OrderStatusTag({ status }: OrderStatusTagProps) {
  return <span className={styles['status-tag']}>{textMap[status]}</span>;
}
```

```tsx
// 场景：用户模块 + 订单模块都用到「用户下拉选择器」
// 判定：跨模块（≥2 模块）共用 → 提升全局
// src/components/UserSelect.tsx（不在任何模块私有目录）
export function UserSelect({ value, onChange }: UserSelectProps) {
  // 通过 useUserOptions hook 取数（通用数据源经 hooks 层）
}
```

---

## 四、hooks 优先与数据流

- **逻辑一律抽成自定义 hooks**，组件只渲染与绑定（表单/请求/权限/主题都不进组件体）；
- **数据获取 hook 三态统一**：返回 `{ data/list, loading, error, refetch }`，组件据此渲染加载/成功/失败三态；
- 数据获取用 `useFetch` 或 TanStack Query（按 FTDD 选型），避免每个 hook 手写重复的 loading/error；
- hooks 目录：通用放 `src/hooks/`，模块私有放 `features/<模块>/hooks/`；命名一律 `use` 前缀；
- **副作用可清理**：`useEffect` 返回清理函数（防内存泄漏）；请求竞态用 AbortController 取消（见 tech-stack-guide §fetch）。

```tsx
// src/features/orders/hooks/useOrderList.ts —— 模块私有 hooks 范式
import { useCallback, useState } from 'react';
import { orderApi, type Order, type OrderListParams } from '@/api/order';

export function useOrderList(initialPageSize = 10) {
  const [list, setList] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchList = useCallback(async (params: Partial<OrderListParams> = {}) => {
    setLoading(true);
    setError(null);
    try {
      const res = await orderApi.getOrderList({ page: 1, pageSize: initialPageSize, ...params });
      setList(res.list);
      setTotal(res.total);
    } catch (e) {
      setError(e as Error);
    } finally {
      setLoading(false);
    }
  }, [initialPageSize]);

  return { list, total, loading, error, fetchList };
}
```

### 数据流总原则（与 FTDD module 一致）

```
页面容器 ──组合──► hooks（useOrderList）──调用──► api（orderApi）──► 后端 TDD 接口
    │                        │
    └──props 下发──► 业务组件（纯渲染 + 回调上抛）
```

---

## 五、状态管理落地

| 状态类型 | 归属 | 落地 |
|---------|------|------|
| 页面/局部状态（筛选/分页/表单值） | 局部 | hooks 内 useState/useReducer |
| 服务端数据（列表/详情/缓存） | 服务端 | TanStack Query / useFetch（按 FTDD） |
| 跨模块共享态（登录态/主题/权限） | 全局 | store（Zustand / Redux Toolkit，按 FTDD） |

- 能局部就不全局：只有跨模块共享的状态才进 store；
- store 中的异步动作也应经 hooks/api 层，组件不直接 dispatch 复杂流程。

---

## 六、架构自检清单

- [ ] 目录与 FTDD overview §6 一致，features 模块与 FTDD 模块清单对应？
- [ ] 分层清晰：页面容器无业务逻辑、组件不直接调 api、hooks 不渲染 JSX？
- [ ] 依赖单向向下，无跨层、无反向依赖？
- [ ] 模块私有组件在 `features/<模块>/components/`，跨模块组件已提升到 `src/components/`？
- [ ] 模块内 ≥2 次复用已抽离？无复制粘贴残留、无「新旧两份并存」？
- [ ] 跨模块引用未直接 import 其它模块私有目录？
- [ ] 逻辑全部 hooks 化，数据获取返回三态？
- [ ] 状态管理按局部/服务端/全局划分，未过度全局化？
