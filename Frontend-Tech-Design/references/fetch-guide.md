# fetch 请求封装规范

> 用途：统一用原生 fetch 封装请求层。技术方案中必须写好该实例，开发据此实现。

---

## 一、总则

- **统一用原生 fetch，不引入 axios**；
- 封装统一入口 `src/api/request.ts`；
- 接口按业务域拆分 `src/api/<模块>.ts`，方法签名与后端 TDD 接口一一对应；
- 必须覆盖：baseURL、超时（AbortController）、统一错误（ApiError）、token 注入、取消支持。

---

## 二、统一封装实例（可直接运行）

```ts
// src/api/request.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';
const DEFAULT_TIMEOUT = 10000;

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: unknown;
  timeout?: number;
  signal?: AbortSignal; // 外部取消信号
}

/** 统一业务错误：status 为 HTTP 状态码，0 表示网络层错误 */
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

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', headers = {}, body, timeout = DEFAULT_TIMEOUT, signal } = options;

  // 内部超时控制器 + 外部取消联动
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  const onExternalAbort = () => controller.abort();
  signal?.addEventListener('abort', onExternalAbort);

  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    signal: controller.signal,
  };

  if (body !== undefined) {
    config.body = JSON.stringify(body);
  }

  // token 注入
  const token = localStorage.getItem('access_token');
  if (token) {
    (config.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const cleanup = () => {
    clearTimeout(timer);
    signal?.removeEventListener('abort', onExternalAbort);
  };

  try {
    const res = await fetch(`${BASE_URL}${path}`, config);
    cleanup();

    if (!res.ok) {
      throw new ApiError(res.status, `请求失败：${res.status}`, 'HTTP_ERROR');
    }
    return (await res.json()) as T;
  } catch (err) {
    cleanup();
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError(0, '请求超时或已取消', 'TIMEOUT');
    }
    throw new ApiError(0, '网络异常，请检查网络连接', 'NETWORK_ERROR');
  }
}
```

---

## 三、业务方法拆分（按域）

```ts
// src/api/user.ts
import { request } from './request';

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'member';
  createdAt: string;
}

export interface UserListResult {
  list: User[];
  total: number;
}

export interface CreateUserPayload {
  name: string;
  email: string;
  role: User['role'];
}

export const userApi = {
  /** 分页查询用户列表 —— 对应后端 TDD：GET /api/users */
  getUserList: (params: { page: number; pageSize: number; keyword?: string }) => {
    const qs = new URLSearchParams({
      page: String(params.page),
      pageSize: String(params.pageSize),
    });
    if (params.keyword) qs.set('keyword', params.keyword);
    return request<UserListResult>(`/api/users?${qs.toString()}`);
  },

  /** 创建用户 —— 对应后端 TDD：POST /api/users */
  createUser: (payload: CreateUserPayload) =>
    request<User>(`/api/users`, { method: 'POST', body: payload }),

  /** 更新用户 —— 对应后端 TDD：PUT /api/users/:id */
  updateUser: (id: string, payload: Partial<CreateUserPayload>) =>
    request<User>(`/api/users/${id}`, { method: 'PUT', body: payload }),

  /** 删除用户 —— 对应后端 TDD：DELETE /api/users/:id */
  deleteUser: (id: string) => request<void>(`/api/users/${id}`, { method: 'DELETE' }),
};
```

---

## 四、使用示例（在 hooks 中调用）

```tsx
// src/features/users/hooks/useUserList.ts
import { useCallback, useState } from 'react';
import { userApi, type User } from '@/api/user';

export function useUserList(initialPageSize = 10) {
  const [list, setList] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchList = useCallback(async (page = 1, keyword?: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await userApi.getUserList({ page, pageSize: initialPageSize, keyword });
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

---

## 五、请求层自检清单

- [ ] 统一入口 `request.ts`，无散落裸 fetch？
- [ ] baseURL 用环境变量，超时用 AbortController？
- [ ] 统一错误类型 `ApiError`，业务可区分 HTTP 错误 / 超时 / 网络异常？
- [ ] token 注入 + 401 统一处理（跳登录）？
- [ ] 业务方法按域拆分，签名与后端 TDD 接口一一对应？
- [ ] 组件通过 hooks 调用请求，不直接 import 业务 api？
