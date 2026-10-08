# features/ 复杂功能域目录

一个业务域一个子目录，只放「跨页面复用或体量过大不宜内联进页面」的逻辑与组件，页面保持薄：

```
features/<domain>/
  hooks/useXxx.ts        # 状态逻辑 hook（如 SSE 对话流：增量聚合 + AbortController 可中断）
  components/XxxModal.tsx # 该域的弹框/抽屉/复杂组件
```

约定：

- hook 命名 `useXxx`，入参为普通参数，返回「状态 + 操作函数」；内部可调用 `src/api/` 的请求函数（含 `streamRequest`）。
- feature 组件可依赖本域 api 模块，但不得反向 import `pages/`。
- 简单页面不建 feature，数据与交互直接写在 `pages/XxxPage.tsx` 里，避免过度拆层。
- 页面级测试放在页面同目录（`XxxPage.test.tsx`），复杂 hook 可在 feature 目录内配 `useXxx.test.ts`。
