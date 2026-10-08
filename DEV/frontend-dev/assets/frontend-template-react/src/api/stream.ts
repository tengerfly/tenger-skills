import { API_BASE_URL } from './request';

export interface StreamOptions {
  method?: 'POST' | 'GET';
  body?: unknown;
  /** 每收到一帧增量文本回调一次 */
  onToken: (token: string) => void;
  signal?: AbortSignal;
}

/**
 * SSE 流式请求（AI 对话等增量输出场景）。
 * 帧契约与后端统一约定一致：`data:{"token":"..."}` 逐帧增量、`data:[DONE]` 结束、`event:error` 表示失败。
 * 用法见源项目 web/src/features/learn/hooks/useChatStream.ts（增量聚合成一条消息 + AbortController 可中断）。
 */
export async function streamRequest(path: string, options: StreamOptions): Promise<void> {
  const { method = 'POST', body, onToken, signal } = options;
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
    signal,
  });
  if (!res.ok || !res.body) throw new Error('流式连接失败');
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let sawError = false;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';
    for (const line of lines) {
      if (line.startsWith('event:')) {
        sawError = line.includes('error');
        continue;
      }
      const data = line.replace(/^data:\s*/, '').trim();
      if (!data || data === '[DONE]') continue;
      if (sawError) throw new Error('流式输出失败，请重试');
      try {
        const frame = JSON.parse(data) as { token?: string };
        if (typeof frame.token === 'string') onToken(frame.token);
      } catch {
        // 忽略非 JSON 的 SSE 边界行
      }
    }
  }
}
