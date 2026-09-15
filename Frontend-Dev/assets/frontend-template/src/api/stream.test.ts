import { describe, expect, it, vi } from 'vitest';
import { streamRequest } from './stream';

/** 用 SSE 帧文本构造流式 Response（一次性下发） */
function sseResponse(frames: string[], status = 200) {
  const text = `${frames.join('\n')}\n`;
  const body = new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(text));
      controller.close();
    },
  });
  return new Response(body, { status });
}

describe('streamRequest（SSE 流式封装）', () => {
  it('逐帧回调 token，[DONE] 正常结束', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(sseResponse(['data: {"token":"你"}', 'data: {"token":"好"}', 'data: [DONE]'])),
    );
    const tokens: string[] = [];

    await streamRequest('/chat/stream', { body: { q: 1 }, onToken: (token) => tokens.push(token) });

    expect(tokens).toEqual(['你', '好']);
  });

  it('event:error 帧：抛业务错误', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(sseResponse(['event: error', 'data: {"message":"模型故障"}'])));

    await expect(streamRequest('/chat/stream', { onToken: () => undefined })).rejects.toThrow('流式输出失败');
  });

  it('HTTP 非 2xx：抛连接失败', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('err', { status: 502 })));

    await expect(streamRequest('/chat/stream', { onToken: () => undefined })).rejects.toThrow('流式连接失败');
  });
});
