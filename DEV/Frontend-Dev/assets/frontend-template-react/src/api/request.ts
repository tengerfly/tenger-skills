const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const DEFAULT_TIMEOUT = 15000;

/** 供原生 FormData/SSE 直接拼路径使用 */
export const API_BASE_URL = BASE_URL;

/** 统一请求错误（HTTP/超时/网络/后端业务 code） */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly code?: string | number,
    public readonly data?: unknown,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: unknown;
  timeout?: number;
  signal?: AbortSignal;
}

/**
 * 统一 fetch 封装：解包后端统一响应 { code, message, data }，成功 code=0 返回 data。
 * 非 0 业务码 / HTTP 非 2xx / 超时 / 网络异常统一抛 ApiError，页面层只管捕获展示。
 */
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', headers = {}, body, timeout = DEFAULT_TIMEOUT, signal } = options;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  const abort = () => controller.abort();
  signal?.addEventListener('abort', abort);
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: { 'Content-Type': 'application/json', ...headers },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
    const payload = (await res.json().catch(() => null)) as {
      code?: number;
      message?: string;
      data?: T;
    } | null;
    if (!res.ok) {
      throw new ApiError(res.status, payload?.message ?? `请求失败：${res.status}`);
    }
    if (payload && typeof payload.code === 'number' && payload.code !== 0) {
      throw new ApiError(res.status, payload.message ?? '业务处理失败', payload.code);
    }
    return (payload?.data ?? (payload as T)) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError(0, '请求超时或已取消', 'TIMEOUT');
    }
    throw new ApiError(0, '网络异常，请检查网络连接', 'NETWORK_ERROR');
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', abort);
  }
}
