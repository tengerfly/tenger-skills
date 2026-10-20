import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError, request } from './request';

/** 构造统一响应格式的成功 Response */
function okResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

describe('request（统一请求封装）', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it('成功：解包 {code,message,data} 返回 data', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ code: 0, message: 'ok', data: { message: 'pong' } }));
    vi.stubGlobal('fetch', fetchMock);

    const data = await request<{ message: string }>('/demo/ping');

    expect(data).toEqual({ message: 'pong' });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/demo/ping'),
      expect.objectContaining({ method: 'GET' }),
    );
  });

  it('HTTP 非 2xx：抛 ApiError 且带 status', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(okResponse({ code: 500, message: '服务器开小差' }, 500)));

    await expect(request('/boom')).rejects.toMatchObject({
      name: 'ApiError',
      status: 500,
      message: '服务器开小差',
    });
  });

  it('业务码非 0：抛 ApiError 且带后端 code/message', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(okResponse({ code: 4001, message: '参数不合法', data: null })));

    const error = await request('/biz-fail').catch((err: unknown) => err as ApiError);

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ code: 4001, message: '参数不合法' });
  });

  it('网络异常：抛 NETWORK_ERROR', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));

    await expect(request('/net-fail')).rejects.toMatchObject({ code: 'NETWORK_ERROR' });
  });

  it('超时：默认 15s 未响应抛 TIMEOUT', async () => {
    vi.useFakeTimers();
    // mock fetch 须与真 fetch 一致地响应 abort 信号，否则中断无法传导
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((_url: string, init?: RequestInit) =>
        new Promise((_resolve, reject) => {
          init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
        }),
      ),
    );

    const pending = request('/slow');
    const expectation = expect(pending).rejects.toMatchObject({ code: 'TIMEOUT' });
    await vi.advanceTimersByTimeAsync(15_000);
    await expectation;
  });
});
