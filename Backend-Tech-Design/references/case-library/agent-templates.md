# Agent 项目模板（Agent Templates）

> 用途：Node.js 技术栈写 LLM / Agent 后端时的起点模板与关键决策参考。套用前仍须走 S3 选型收敛证明——模板解决「怎么接」，非功能（鉴权 / 限流 / 持久化 / 可观测）仍按本 skill 各章节补全（见 §一.7 必补清单）。

---

## 一、NestJS + Vercel AI SDK（vercel/ai 官方 examples/nest）

### 1. 场景

Node/TS 团队用 NestJS 做 AI 应用后端：聊天对话、流式生成、Agent 工具调用；前端（含 AI SDK 的 useChat）消费 UIMessage 流（SSE）。

### 2. 技术挑战

| 挑战 | 说明 |
|---|---|
| LLM 响应慢 | 首字延迟秒级、整段生成可到分钟级，必须 SSE 流式输出，不能等完整 JSON |
| 框架对接 | AI SDK 对 Next.js 等 Web 框架是一等公民；NestJS 需手动把流管道接到 Express response |
| 流中夹带结构化数据 | 除文本外常要推进度 / 工具调用状态 / 引用来源（custom data parts） |
| 错误泄漏 | provider 报错细节（模型名、内部信息）不能透传客户端，默认要 mask |

### 3. 选型决策

| 决策点 | 选择 | 理由 | 备注 |
|---|---|---|---|
| LLM 接入层 | Vercel AI SDK（`ai` + `@ai-sdk/openai`） | 统一 provider 接口，换模型 = 换一行 provider 包；流式 / 工具调用抽象好 | 多 provider 场景价值最大；备选：各厂商官方 SDK（接口不统一） |
| 流式对接 | `@Res()` 注入 Express 原生 response + `pipeUIMessageStreamToResponse` | 直写响应流，绕开 Nest 拦截器与 JSON 序列化 | Nest 原生 `@Sse`（Observable）不适配 UIMessage 协议的帧格式与首包语义 |
| 自定义数据流 | `createUIMessageStream` + `writer.write` / `writer.merge` | 一条 SSE 流里混排自定义 data part 与 LLM 文本 | 前端 useChat 按 `data-*` 类型分派 |
| 错误处理 | 流级 `onError` 回调，默认 mask | 防内部信息泄漏；确需暴露时在回调显式返回 | 安全默认值，别图省事放开 |

### 4. 目录结构（模板本体，最小 3 文件）

```
examples/nest/
├── src/
│   ├── main.ts            # bootstrap：dotenv/config + NestFactory.create + listen(8080)
│   ├── app.module.ts      # 空 module，后续按域挂 controller/provider
│   └── app.controller.ts  # AI 端点（核心参考，见下）
├── nest-cli.json / tsconfig.json
└── package.json           # NestJS + ai + @ai-sdk/openai + jest/ts-jest/supertest
```

### 5. 关键代码（精简摘录）

最简流式端点：

```ts
@Post('/')
async root(@Res() res: Response) {
  const result = streamText({
    model: openai('gpt-4o'),        // 换 provider = 换这一行（如 anthropic(...)）
    prompt: 'Invent a new holiday and describe its traditions.',
  });
  pipeUIMessageStreamToResponse({
    response: res,
    stream: toUIMessageStream({ stream: result.stream }),
  });
}
```

自定义 data parts + 错误 mask（Agent 项目常用形态）：

```ts
@Post('/stream-data')
async streamData(@Res() response: Response) {
  const stream = createUIMessageStream({
    execute: ({ writer }) => {
      writer.write({ type: 'start' });                       // sendStart:false 时手动发首包
      writer.write({ type: 'data-custom', data: { ... } });  // 自定义结构化数据（进度/引用等）
      const result = streamText({ model: openai('gpt-4o'), prompt: '...' });
      writer.merge(toUIMessageStream({
        stream: result.stream,
        sendStart: false,
        onError: error => '生成失败，请稍后重试',              // 默认 mask，防泄漏
      }));
    },
  });
  pipeUIMessageStreamToResponse({ stream, response });
}
```

依赖要点（模板内 `workspace:*` 需替换为实际安装版本）：

- 运行时：`ai` + `@ai-sdk/openai`（AI SDK v5，UIMessage 协议）、`@nestjs/{common,core,platform-express}`、`reflect-metadata`、`rxjs`
- 测试：自带 `jest` + `ts-jest` + `supertest`（`*.spec.ts` 约定，可直接对接本 skill 的 TDD 用例形态）

### 6. 反模式

- 把 LLM 错误原文透传客户端——泄漏 provider 与内部实现信息，保持默认 mask。
- 对 `@Res()` 直写的流再过拦截器 / 序列化管道——会破坏 SSE 帧（`@Res()` 模式下拦截器失效是特性不是坑；Guard 在进 handler 前执行，鉴权仍可用）。
- 端点里硬编码模型名 / provider——收进 ConfigService 统一配置，便于换模型与多模型路由。
- 为「接 LLM」引入 socket.io / WebSocket——单向生成流 SSE 已够；只在双向交互（语音、协作编辑）时上 WebSocket。

### 7. 套用模板必补清单（模板未含，按本 skill 规范补全）

| 项 | 落在哪 |
|---|---|
| provider / 模型 / 密钥配置进 ConfigService，禁硬编码 | overview 选型总览 |
| 会话与消息持久化（UIMessage 存表） | 总文档表结构（data-model-guide） |
| Agent 工具注册与执行边界（白名单 / 超时 / 结果大小上限） | 模块方案 + 弹性与容错章节 |
| 限流 / 超时 / abortSignal 透传（客户端断连即停生成） | `reliability-patterns.md` |
| 可观测：token 用量、首字时间（TTFT）、总延迟埋点 | overview 监控章节 |
| 网关 SSE 透传（Nginx `proxy_buffering off` 等） | 部署章节 |

### 8. 出处

- 模板：https://github.com/vercel/ai/tree/main/examples/nest （vercel/ai 官方示例）
- AI SDK 文档：https://ai-sdk.dev
