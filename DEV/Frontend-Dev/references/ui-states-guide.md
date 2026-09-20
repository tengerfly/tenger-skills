# 10 大 UI 状态实现指南（UI States）

> 用途：前端开发按本指南实现页面状态。状态总逻辑架构**框架无关**（适用 React / Vue / 小程序），实现写法注记框架差异。
> 上游：FTDD 模块文档 §9「异常与边界」已逐页声明适用状态——本指南是它的实现细化。
> 视觉：有设计稿时状态呈现以 `.spec/设计稿/` 状态稿为准（design-system §5.10）；无设计稿按组件库标准态并在还原基线中注明。

---

## 一、为什么需要状态设计

页面绝不只有「正常显示（Success）」一种状态。缺乏状态设计的代码在网络波动、权限缺失、AI 生成中断时用户体验极度糟糕。状态覆盖与功能正确性同级：**FTDD 声明的适用状态缺失 = 功能点未完成**。

---

## 二、10 大 UI 状态实现对照表

| # | 状态 | 触发场景 | 实现要点 | 反模式 |
|---|---|---|---|---|
| 1 | Skeleton 骨架屏 | 页面首次加载 | 显示与最终页面结构一致的灰色占位块，减少视觉抖动（React：`loading && <Skeleton />`；Vue：`v-if` 同理） | 整页转圈 spinner；占位结构与真实页面不一致 |
| 2 | Loading 加载中 | 局部提交 / 刷新 | 提交按钮 Spin + `disabled` 防重复提交；由 hooks 返回的 `loading` 驱动 | 按钮点击后仍可点，产生重复数据 |
| 3 | Success 成功渲染 | 数据正常返回 | 渲染真实内容；空数组转 Empty 态；长文本 Ellipsis 截断 | 成功态里塞一切；长文本撑爆容器 |
| 4 | Empty 空态 | 查询结果为 0 | 引导插画 + 现状说明 + CTA（如「新建条目」）；空态表达全站唯一 | 整页空白；同站多种空态样式 |
| 5 | Error 业务错误 | 500/502 服务端异常 | 友好 Toast / 错误 Banner +「重新加载」（触发 `refetch`）；给出口不给堆栈 | 白屏；只 console.error 无 UI 反馈 |
| 6 | Disabled 禁用 | 缺少操作前置条件 | 条件不满足 → disabled + `cursor: not-allowed` + Tooltip 说明缺什么（React：`disabled={!valid}`；Vue：`:disabled`） | 可点但点了报错；禁用不给原因 |
| 7 | Permission Denied | 403 无权限 | 路由守卫拦截 + 无权限页（插画 + 申请权限引导）；按钮级 `usePermission` / `v-if` 控制显隐 | 403 当 500 报错；隐藏入口不留提示 |
| 8 | Network Error | 断网 / 网络超时 | 顶部全局 Offline Banner（断网常驻、恢复自动消失）；失败自动重试或给重试入口；超时 AbortController | 断网页面假死无提示；各组件各自弹错 |
| 9 | Streaming 流式打字 | AI 文本生成中（SSE） | 流式读取（EventSource / fetch stream）增量渲染；打字机效果 + 光标闪烁；滚动自动吸底（用户上翻暂停）；封装为 hooks（React）/ 组合式函数（Vue） | 等完整响应一次渲染；输出时滚动条乱跳 |
| 10 | Partial Data 增量数据 | AI 结构化输出（JSON）生成中 | 宽松/渐进 JSON 解析：已到字段先渲染、缺失字段占位；流完整后再整体校验 | 未完整就 `JSON.parse` 抛错整页崩 |

> 1–8 为通用必备状态；9–10 仅涉 AI 生成/对话功能时适用。

---

## 三、落地方式

1. **状态来源**：容器/页面侧 hooks（React）或组合式函数（Vue）产出统一状态 `{data, loading, error, refetch}`；展示组件只按 props 渲染对应状态分支，不自取数据（容器/展示法则见 FTDD `references/component-design-guide.md` §1.1；部署环境两 skill 平级：`../Frontend-Tech-Design/references/`）。
2. **基线先行**：开发计划阶段把 FTDD §9 适用状态逐页列入还原基线与功能点 DoD；每功能点提交前适用状态齐全。
3. **测试**：每个适用状态至少一条用例（编号沿用 TC ↔ AC）；流式/增量用 mock SSE / 分片数据驱动。
4. **全局一致性**：同类状态全站同一组件/样式（空态组件、错误 Banner、Offline 条全局单例），禁止各页面各写一套。

---

## 四、自查清单

- [ ] FTDD §9 声明的适用状态逐态已实现？
- [ ] 首次加载走 Skeleton 而非整页 spinner？
- [ ] 提交按钮 loading 期间 disabled 防重复？
- [ ] 空态有插画 + CTA，全站唯一表达？
- [ ] 错误有重试出口；禁用有 Tooltip 原因？
- [ ] 断网有全局 Offline Banner 且恢复自动重试？
- [ ] （涉 AI）流式打字光标闪烁 + 吸底；增量 JSON 渐进解析不崩？
