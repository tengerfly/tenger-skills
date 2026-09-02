# 前端代码编写规范

> 用途：前端代码「怎么写才简洁、可读、可维护」的权威规范。所有示例默认 React + TypeScript + SCSS Modules。
> 本规范是权威；与 FTDD/其它 references 冲突时，以「还原度高 + 可读性优先」原则取舍。

---

## 一、简洁性

### 1.1 组件短小、职责单一

- 一个组件只做一件事；超过 ~80 行或职责混杂即拆；
- 页面容器只做「编排」：组合业务组件 + hooks + 传数据；一屏逻辑复杂时按区块拆子组件；
- 禁止在 JSX 里塞长函数体、长条件链——抽成函数/hook/子组件。

```tsx
// ❌ 页面容器里堆逻辑
function OrderPage() {
  const [list, setList] = useState<Order[]>([]);
  // ...15 行过滤/排序逻辑 + 长 JSX...
}

// ✅ 逻辑下沉 hook，页面只编排
function OrderPage() {
  const { list, total, loading, error, fetchList } = useOrderList();
  return <OrderListView list={list} loading={loading} error={error} onRetry={() => fetchList()} />;
}
```

### 1.2 少写「聪明」代码

- 能用清晰 if/else 就不要炫技三元链、重度 `reduce`、多层解构魔术；
- 禁止魔法值：状态/枚举/文案常量提取，禁止裸 `0/1/'pending'` 散落；
- 文案不硬编码散落：企业级档走 i18n（locales），demo 档至少集中到一个 `constants`（按 FTDD）。

```tsx
// ❌ 魔法值 + 冗余解构
const s = order.status === 0 ? '待支付' : order.status === 1 ? '已支付' : '已取消';

// ✅ 常量映射
const STATUS_TEXT: Record<OrderStatus, string> = {
  pending: '待支付', paid: '已支付', cancelled: '已取消',
};
const s = STATUS_TEXT[order.status];
```

---

## 二、命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| 组件文件/组件名 | **PascalCase，首字符必须大写** | `UserTable.tsx` / `<UserTable>` |
| 方法名/函数名/变量 | **camelCase 小驼峰**，首字符小写 | `getUserList` / `fetchUserList` / `orderList` |
| hooks | `use` 前缀 + 小驼峰 | `useUserList` / `useOrderForm` |
| api 方法 | `getXxx / createXxx / updateXxx / deleteXxx`（小驼峰） | `userApi.getUserList` |
| CSS 类名（class） | **kebab-case，用 `-` 连接** | `.status-tag` / `.user-table` |
| props 回调 | `on` 前缀 + 小驼峰 | `onDelete` / `onRowClick` |
| 布尔 props | `is / has / can` 前缀 | `isLoading` / `hasError` |
| 状态/常量 | 语义化常量，禁止裸值 | `OrderStatus` / `STATUS_TEXT` |

- **三条硬性格式约定**（全项目统一，禁止混用）：
  1. **组件名首字符必须大写**（PascalCase）——React 据此区分「组件」与「原生标签」；小写开头的组件会被当成 HTML 标签渲染，属错误写法；
  2. **CSS class 用 `-` 连接**（kebab-case）——`.user-table`、`.status-tag`，不用下划线、不用驼峰；
  3. **方法/函数名小驼峰**（camelCase）——`getUserList`、`handleDelete`，首字符小写。
- 见名知意：禁止 `a/b/tmp/data/d1` 这类无意义命名；变量名用业务语言（`orders` 而非 `items`）。

---

## 三、TypeScript 类型（严格模式）

- props/state/接口返回全量类型；**禁 `any`、禁 `@ts-ignore`**；
- props 用 interface 声明，必填/可选明确，回调签名完整：

```tsx
interface UserTableProps {
  users: User[];
  loading?: boolean;
  onDelete?: (id: string) => void;      // 可选回调，调用处判空
  onRowClick?: (user: User) => void;
}

export function UserTable({ users, loading = false, onDelete, onRowClick }: UserTableProps) {
  // ...
}
```

- 后端返回结构类型化：api 返回类型与 TDD 接口字段一致（`Order` / `OrderListResult`）；
- `import type` 用于纯类型导入（`verbatimModuleSyntax` 下必需）。

---

## 四、注释规范

- **讲「为什么」**：注释解释设计意图、业务规则、边界/异常原因、取舍（含「为何不还原原型某细节」）；不重复代码已表达内容（`// 遍历 list` 这类废注释删除）；
- **简单易懂**（硬性要求）：
  - 用**简练中文一句话**讲清意图，让不熟悉这段代码的人一眼看懂；
  - **一条注释尽量一行**；复杂规则最多 3 行，拆成多条短注释而不是一大段；
  - 不堆术语、不写长篇大论、不贴大段实现说明（实现细节看代码本身）；
  - 用「因为……所以……」的因果句式写 why，最易读：`// 因为后端按创建时间倒序返回，前端不再二次排序`。
- **必写注释的位置**：
  - api 方法：一行说明「对应后端接口 + 用途」（`// 获取订单列表 —— GET /api/orders`）；
  - hooks：说明返回三态与关键行为；
  - 复杂业务规则 / 非显而易见逻辑：why；
  - 关键技术点（竞态取消 / 缓存失效 / 权限）：说明方案与依据；
  - 状态/枚举：注释每个值的业务含义；
  - 与原型/方案不一致处：说明原因（便于还原核对时追溯）。
- **传参必注（硬性要求）**：**方法/函数/hooks/组件只要有参数，就必须写明每个参数的作用**——用 JSDoc `@param` 逐条说明「是什么、取值含义、边界/默认值」；返回非显而易见时用 `@returns`；组件 props 在 interface 字段上逐条注释：
  ```tsx
  /**
   * 查询订单列表（对应后端 GET /api/orders）
   * @param params 查询参数
   * @param params.page 页码，从 1 开始
   * @param params.pageSize 每页条数，默认 10，最大 100
   * @param signal 取消信号，组件卸载或重复请求时用于中断上一个请求
   * @returns 分页结果：list 为当前页数据，total 为符合条件的总数
   */
  function getOrderList(params: PageParams, signal?: AbortSignal): Promise<PageResult<Order>>;

  interface UserTableProps {
    users: User[];                      // 当前页用户数据；为空时组件内部渲染空态
    loading?: boolean;                  // 加载中：true 显示骨架屏，默认 false
    onDelete?: (id: string) => void;    // 点击删除回调，参数为被删用户 id；未传则隐藏删除按钮
  }
  ```
- **禁止**：废注释、过时注释、TODO 堆积不清理、注释掉的死代码；**有参数却不写参数说明**。

```tsx
// ❌ 冗长、复述代码、堆术语
/**
 * 该方法用于在用户点击取消按钮之后，通过调用后端提供的取消订单 RESTful 接口，
 * 以 POST 的方式提交一个包含订单标识符的请求体，从而实现对指定订单状态的变更操作……（后续 20 行）
 */

// ❌ 复述代码的废注释
const list = orders.filter(o => o.status === 'paid'); // 过滤出已支付的订单

// ✅ 一句话讲 why，简单易懂
// 只统计已支付订单：待支付不计入本页金额合计（业务口径来自 PRD AC-M02-003）
const paidOrders = orders.filter(o => o.status === 'paid');

// ✅ 一行说明依据
// 后端已按创建时间倒序返回，前端不再二次排序，避免打乱分页
const rows = res.list;
```

---

## 五、React 写法约定

- **hooks 规则**：只在顶层调用 hooks；`useEffect`/`useCallback`/`useMemo` 依赖数组写全，开启 `react-hooks/exhaustive-deps`；
- **副作用可清理**：`useEffect` 返回清理函数；请求竞态用 AbortController（见 tech-stack-guide §fetch）；
- **受控优先**：表单/交互组件 `value + onChange` 受控；复杂表单用 `useForm`（react-hook-form 或自研，按 FTDD）；
- **列表 key**：用稳定唯一 id，禁止数组下标；
- **禁止直接修改 state / props**；衍生值用 `useMemo`，避免每帧重算；
- **懒加载**：路由页面 `React.lazy` + `Suspense`（企业级档）。

```tsx
// src/features/orders/hooks/useCancelOrder.ts —— 竞态取消范式
export function useCancelOrder(orderId: string) {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const cancel = useCallback(async () => {
    const controller = new AbortController();
    setSubmitting(true);
    setError(null);
    try {
      await orderApi.cancelOrder(orderId, controller.signal);
      // 成功后由上层刷新列表
    } catch (e) {
      setError(e as Error);
    } finally {
      setSubmitting(false);
    }
    return controller;
  }, [orderId]);

  return { submitting, error, cancel };
}
```

---

## 六、样式写法约定（SCSS Modules）

- 组件样式用 CSS Modules（`X.module.scss`），**类名 kebab-case（用 `-` 连接）**：
  - `<div className={styles['user-table']}>` + `import styles from './X.module.scss';`
  - 类名带 `-` 时，通过中括号访问：`styles['user-table']`（不可 `styles.userTable` 混用）；
- **颜色/间距/字号一律引用 `variables.scss` 的 CSS 变量**，禁止写死色值（还原度高 + 主题可切换的前提）：

```scss
// ❌ 类名不用驼峰、不写死色值
.userTable { color: #4f6ef2; padding: 16px; }

// ✅ 类名 kebab-case + 引用变量
.user-table { color: var(--color-primary); padding: var(--spacing-md); }
```

- 布局优先用 flex/grid，避免负 margin / 绝对定位硬凑；响应式用 `mixins.scss` 断点 mixin；
- 还原度：间距/字号与原型不一致 = 未还原——按 fidelity-guide 逐项核对。

---

## 七、错误处理与边界

- **错误不吞**：请求错误统一 `ApiError` 承载，UI 按 code 分类提示（HTTP/超时/网络）；渲染异常由 `ErrorBoundary` 兜底；
- **三态渲染**：每个数据区具备 加载中（骨架屏/占位）/ 失败（错误提示 + 重试）/ 空数据（空态文案）三态，禁止只写成功态；
- 401 统一跳登录；按钮级权限用 `usePermission` 控制显隐（企业级档）；
- 防抖/节流：搜索/输入用 `useDebounce`，提交防重复用 `submitting` 状态。

---

## 八、自检清单

- [ ] 组件短小单一，页面容器只编排？
- [ ] 逻辑 hooks 化，hooks 无渲染？
- [ ] 命名语义化且格式统一：组件名首字符大写（PascalCase）、class 用 `-` 连接（kebab-case）、方法/函数小驼峰（camelCase）、hooks `use` 前缀、api `getXxx`？
- [ ] TS 严格：props 全类型、无 any、无 @ts-ignore？
- [ ] 无魔法值、无散落硬编码文案（按 FTDD 走 i18n 或集中常量）？
- [ ] 注释**简单易懂**：一句话讲 why、一行写完（复杂规则 ≤3 行），无长篇大论、无术语堆砌、无废注释、无死代码？
- [ ] **传参必注**：方法/函数/hooks/组件每个参数都写了 `@param` 说明作用？
- [ ] 与原型/方案不一致处已注释原因？
- [ ] 不确定之处已向用户确认（未自己发挥）？
- [ ] hooks 依赖数组写全、副作用可清理、竞态已取消？
- [ ] 样式引用 token、CSS Modules 隔离、无写死色值？
- [ ] 三态齐全、错误不吞、ErrorBoundary 兜底？
