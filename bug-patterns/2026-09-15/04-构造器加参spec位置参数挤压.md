# 构造器加参 × spec 位置参数构造 → 参数错位假失败

> 归属：`bug-patterns/` 错误模式池 ｜ 日期：2026-09-15 ｜ 来源：会话记录挖掘（quiz.service.spec 9 用例假失败：producer 落到 agentGate 槽位、submit 从未被调用）
> 依据：learning-assistant V2 `modules/learn/quiz.service.spec.ts` 参数挤压实录
> 原则：存「一类会再犯的错误」+ 防复发规则。

## 基本信息

| 字段 | 值 |
|---|---|
| 根因类型 | 契约不一致（构造签名变更未同步调用点） |
| 受益 skill | Backend-Dev |
| 等级 | P1（假失败误导排查方向——症状看起来像业务坏了） |
| 建议落点层级 | 错误表加行 |
| 状态 | 已提炼（落点见文末） |

## 现象（同类 bug 长什么样）

- 给 service 构造器中间插入新依赖后，某批测试突然批量失败，症状是「某个依赖的方法从未被调用」或「调到了错误对象上」；
- spec 里 `new XxxService(a, b, c)` 全用位置参数 + `as never`，编译器因 `as never` 吞掉类型不匹配而照常编译——错位静默发生。

## 根因（证据链摘要）

当构造签名在中间插参而测试用位置参数 + `as never` 构造时，后续实参整体左移一格落到错误依赖槽位；`as never` 让 TS 放弃检查，运行时表现为「错误对象上方法不存在 → 被上层 catch 吞成业务错误」。

## 防复发规则（核心，给目标 skill 的可执行规则）

- [ ] 构造器增删参数后，grep 全部 `new Xxx(` 调用点（含 spec）逐一核对参数位置，不依赖编译器（`as never` 会掩盖）
- [ ] spec 构造尽量用测试容器（Test.createTestingModule）或具名对象+对象参数，减少长位置参数链
- [ ] 批量假失败（一个 spec 内多个用例同时坏、症状相同）先查依赖槽位错位，再查业务逻辑

## 提炼回填（Skill-Optimizer 模式③ 填）

| 字段 | 值 |
|---|---|
| 提炼落点 | `DEV/Backend-Dev/SKILL.md` 常见错误对照表新增行（加参 grep 调用点 / 假失败先查错位） |
| 决策记录 | `DEV/Backend-Dev/CONTEXT.md` D-09 |
| 忽略理由 | — |
