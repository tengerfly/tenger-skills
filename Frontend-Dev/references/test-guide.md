# 前端测试实现规范（测试先行）

> 用途：指导把 FTDD 模块文档 §9 的 TDD 测试用例落地成可运行的 Vitest + React Testing Library 测试。
> **测试先行**：每个模块/页面先写测试（标注 TC-Mxx-nnn ↔ AC-Mxx-nnn），再写实现；测试未写、实现不开工。

---

## 一、总则

- **测试框架固定**：Vitest + React Testing Library + `@testing-library/jest-dom`（按 FTDD；其它端按所选框架测试方案）；
- 测试对象三类：**页面容器 / 组件 / hooks**（hooks 用 `renderHook` 单独测）；
- 用例承接 FTDD 覆盖矩阵：渲染 / 交互 / 数据流 / 边界 / 异常；
- 用例编号沿用 FTDD：`TC-M{{模块}}-nnn`，标注对应 PRD `AC-M{{模块}}-nnn`；
- mock 隔离：api 层 mock（`vi.mock('@/api/xxx')`），测试可独立运行，不发真实请求。

---

## 二、环境配置（web 端）

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/Test/setup.ts'],
    globals: true,
    coverage: { provider: 'v8', reporter: ['text', 'html'] },
  },
});
```

```ts
// src/Test/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => cleanup());
```

> 路径别名 `@/` 需在 `vite.config.ts` 与 `vitest.config.ts` 同时配置 `resolve.alias`。

---

## 三、测试组织方式

测试文件与实现**同目录**（`.test.tsx` / `.test.ts`），方便跳转与随模块归档：

```
src/features/orders/
├── components/
│   ├── OrderStatusTag.tsx
│   └── OrderStatusTag.test.tsx
├── hooks/
│   ├── useOrderList.ts
│   └── useOrderList.test.tsx
└── OrderListPage.test.tsx        # 页面容器测试
src/api/order.test.ts             # api 契约测试（可选：mock fetch 校验请求参数）
```

---

## 四、组件测试（渲染 + 交互）

```tsx
// src/features/orders/components/OrderStatusTag.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { OrderStatusTag } from './OrderStatusTag';

describe('OrderStatusTag', () => {
  // 承接 AC-M02-001（渲染）
  it('pending 状态显示「待支付」', () => {
    render(<OrderStatusTag status="pending" />);
    expect(screen.getByText('待支付')).toBeInTheDocument();
  });

  // 承接 AC-M02-003（边界）
  it('未知状态有兜底文案', () => {
    render(<OrderStatusTag status={'unknown' as OrderStatus} />);
    expect(screen.getByText('未知')).toBeInTheDocument();
  });
});
```

```tsx
// 交互：userEvent 模拟点击/输入/提交
import userEvent from '@testing-library/user-event';

describe('SearchBar', () => {
  it('输入关键字后回车触发搜索', async () => {
    const user = userEvent.setup();
    const onSearch = vi.fn();
    render(<SearchBar onSearch={onSearch} />);
    await user.type(screen.getByPlaceholderText('请输入关键字'), 'abc');
    await user.keyboard('{Enter}');
    expect(onSearch).toHaveBeenCalledWith('abc');
  });
});
```

---

## 五、hooks 测试（数据流 + 异常）

```tsx
// src/features/orders/hooks/useOrderList.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { orderApi } from '@/api/order';
import { useOrderList } from './useOrderList';

vi.mock('@/api/order', () => ({
  orderApi: { getOrderList: vi.fn() },
}));

describe('useOrderList', () => {
  // 承接 AC-M02-004（数据流）
  it('获取成功后写入列表与总数', async () => {
    vi.mocked(orderApi.getOrderList).mockResolvedValue({
      list: [{ id: '1', status: 'paid' }],
      total: 1,
    } as never);

    const { result } = renderHook(() => useOrderList());
    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.list).toHaveLength(1);
    expect(result.current.total).toBe(1);
    expect(result.current.error).toBeNull();
  });

  // 承接 AC-M02-005（异常）
  it('接口失败置 error 且 list 为空', async () => {
    vi.mocked(orderApi.getOrderList).mockRejectedValue(new Error('网络异常'));

    const { result } = renderHook(() => useOrderList());
    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.error).not.toBeNull();
    expect(result.current.list).toEqual([]);
  });
});
```

---

## 六、页面容器测试

页面容器测试以「组装正确、三态可见」为主，尽量轻：

```tsx
// src/features/orders/OrderListPage.test.tsx
vi.mock('@/api/order');
vi.mock('@/router', () => ({ useNavigate: () => vi.fn() })); // 按实际依赖 mock

it('加载失败时展示错误态与重试按钮', async () => {
  vi.mocked(orderApi.getOrderList).mockRejectedValueOnce(new Error('boom'));
  render(<OrderListPage />);
  expect(await screen.findByText('加载失败')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: '重试' })).toBeInTheDocument();
});
```

---

## 七、五类覆盖要求（与 FTDD 覆盖矩阵一致）

| 类型 | 含义 | 示例 |
|------|------|------|
| 渲染 | 组件正常渲染与输出 | 状态文案、列表项、空态 |
| 交互 | 用户操作触发预期行为 | 点击删除、输入搜索、提交表单 |
| 数据流 | 数据获取/状态流转正确 | hook 拉取成功写入 state |
| 边界 | 临界值/特殊输入 | 空列表、超长文本、未知枚举 |
| 异常 | 失败分支正确反馈 | 接口失败置 error、重试可用 |

> FTDD 模块文档 §9 已给出骨架与覆盖矩阵；开发时**先落测试文件**（可先红），再写实现至绿。未在 FTDD 列出的新组件，按同类覆盖补齐并登记。

---

## 八、测试自检清单

- [ ] 测试先行：每个组件/hooks/页面有对应测试，编号标注 TC ↔ AC？
- [ ] 覆盖五类：渲染/交互/数据流/边界/异常？
- [ ] api 全部 mock，无真实网络请求？
- [ ] 三态（loading/error/空）有断言？
- [ ] `pnpm test` 全绿、无 flaky（不依赖顺序/定时器抖动）？
- [ ] 覆盖率达标（企业级档：行覆盖 ≥80%，按 FTDD 约定）？
