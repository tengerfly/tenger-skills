# 前端测试用例规范

> 用途：指导测试用例编写。先写测试用例，后写实现。测试栈随框架联动：React→Vitest+RTL / Vue→Vitest+Vue Test Utils / RN→Jest+RNTL / Flutter→flutter_test（下文以 React 示例表述，各框架等价映射）。

---

## 一、总则

- **测试框架**：Vitest + 框架配套组件测试库（React→RTL / Vue→VTU / RN→RNTL）+ `@testing-library/jest-dom`；
- **先写测试用例，后写实现方案**——测试用例是开发 TDD 先写测试的直接输入源；
- 测试对象三类：**页面 / 组件 / hooks**（hooks 用 `renderHook` 单独测）；
- 测试用例承接 PRD 的 AC 编号（`AC-Mxx-nnn`），覆盖五类：**渲染 / 交互 / 数据流 / 边界 / 异常**。

---

## 二、测试环境配置

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
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
    },
  },
});
```

```ts
// src/Test/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

---

## 三、组件测试

### 3.1 渲染测试（正向）

```tsx
// src/features/users/components/UserTable.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { UserTable } from './UserTable';

const users = [
  { id: '1', name: '张三', email: 'zhangsan@x.com', role: 'admin' as const },
  { id: '2', name: '李四', email: 'lisi@x.com', role: 'member' as const },
];

describe('UserTable', () => {
  // 承接 AC-M01-001
  it('正常渲染用户列表', () => {
    render(<UserTable users={users} />);
    expect(screen.getByText('张三')).toBeInTheDocument();
    expect(screen.getByText('李四')).toBeInTheDocument();
  });

  // 承接 AC-M01-005
  it('空列表显示空态', () => {
    render(<UserTable users={[]} />);
    expect(screen.getByText('暂无数据')).toBeInTheDocument();
  });
});
```

### 3.2 交互测试

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

describe('UserTable 交互', () => {
  // 承接 AC-M01-002
  it('点击删除按钮触发回调', async () => {
    const onDelete = vi.fn();
    render(<UserTable users={users} onDelete={onDelete} />);
    await userEvent.click(screen.getByRole('button', { name: '删除' }));
    expect(onDelete).toHaveBeenCalledWith(users[0]);
  });
});
```

---

## 四、hooks 测试（renderHook）

```tsx
// src/features/users/hooks/useUserList.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { userApi } from '@/api/user';
import { useUserList } from './useUserList';

vi.mock('@/api/user', () => ({
  userApi: {
    getUserList: vi.fn(),
  },
}));

describe('useUserList', () => {
  // 承接 AC-M01-003
  it('获取成功后写入列表', async () => {
    const mockList = { list: [{ id: '1', name: '张三' }], total: 1 };
    vi.mocked(userApi.getUserList).mockResolvedValue(mockList as never);

    const { result } = renderHook(() => useUserList());
    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.list).toEqual(mockList.list);
    expect(result.current.total).toBe(1);
    expect(result.current.error).toBeNull();
  });

  // 承接 AC-M01-004
  it('接口失败置 error', async () => {
    vi.mocked(userApi.getUserList).mockRejectedValue(new Error('网络异常'));

    const { result } = renderHook(() => useUserList());
    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.error).not.toBeNull();
    expect(result.current.list).toEqual([]);
  });
});
```

---

## 五、五类覆盖要求

| 类型 | 含义 | 示例 |
|------|------|------|
| 渲染 | 组件/hook 正常渲染与输出 | 列表渲染、空态、loading 态 |
| 交互 | 用户操作触发预期行为 | 点击、输入、提交 |
| 数据流 | 数据获取/状态流转正确 | hook 拉取成功写入 state |
| 边界 | 临界值/特殊输入 | 空数据、超长文本、分页边界 |
| 异常 | 失败分支正确反馈 | 接口失败、超时、无权限 |

---

## 六、覆盖矩阵模板

| 用例编号 | 对应 AC | 类型 | 测试对象 | 场景 |
|---------|---------|------|---------|------|
| TC-M{{M}}-001 | AC-M{{M}}-001 | 渲染 | {{组件}} | {{正常渲染}} |
| TC-M{{M}}-002 | AC-M{{M}}-002 | 交互 | {{组件}} | {{用户操作}} |
| TC-M{{M}}-003 | AC-M{{M}}-003 | 数据流 | {{hook}} | {{数据获取成功}} |
| TC-M{{M}}-004 | AC-M{{M}}-004 | 异常 | {{hook}} | {{接口失败}} |
| TC-M{{M}}-005 | AC-M{{M}}-005 | 边界 | {{组件}} | {{空态/极值}} |

---

## 七、测试自检清单

- [ ] 测试框架 Vitest + RTL，环境 jsdom？
- [ ] 先写测试用例，后写实现方案？
- [ ] 组件渲染/交互、hooks 数据流均有覆盖？
- [ ] 五类覆盖（渲染/交互/数据流/边界/异常）齐全？
- [ ] 每个用例标注对应 PRD 的 AC 编号？
- [ ] mock 隔离（api mock、外部依赖 mock），测试可独立运行？
