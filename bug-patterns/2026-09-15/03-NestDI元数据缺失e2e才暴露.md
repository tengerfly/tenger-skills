# Nest DI 元数据缺失——tsc 全绿但运行时容器解析失败

> 归属：`bug-patterns/` 错误模式池 ｜ 日期：2026-09-15 ｜ 来源：会话记录挖掘（rollout 签名：Nest can't resolve dependencies×41）
> 依据：learning-assistant V2 `agent/` 层（ExternalToolBridge / tools / AgentRuntime / SearchKnowledgeTool）健康检查 e2e 才暴露
> 原则：存「一类会再犯的错误」+ 防复发规则。

## 基本信息

| 字段 | 值 |
|---|---|
| 根因类型 | 契约不一致（编译期契约 ≠ 运行时 DI 契约） |
| 受益 skill | Backend-Dev |
| 等级 | P0（全 AppModule 启动失败；tsc/test 单测全绿不可发现） |
| 建议落点层级 | 错误表加行 + Gate 预检项（全模块启动冒烟纳入回归） |
| 状态 | 已提炼（落点见文末） |

## 现象（同类 bug 长什么样）

- `Nest can't resolve dependencies of the XxxProvider (?, Object). Please make sure that the argument Object at index [0] is available in the ...Module context.`；
- 触发形态三连：①构造参数类型写 `Pick<Repository<T>, 'find'>` 等投影类型，不加 `@Inject(getRepositoryToken(...))`；②构造参数是**接口**（如 `AgentLlmPort`）；③参数类用 `import type { DataSource }` 导入——`emitDecoratorMetadata` 对以上三类产出 `Object`/`Function` 元数据；
- 单测（手工 new / stub 注入）全绿，tsc 零错误，唯一暴露口 = TestingModule 启动全 AppModule 的 e2e。

## 根因（证据链摘要）

当 provider 构造参数的类型信息不能被 `emitDecoratorMetadata` 反射为可解析的 DI token（投影类型/接口/type-only 导入）时，Nest 运行时拿到 `Object` 元数据而容器中无对应 provider → 启动期解析失败；类型检查与单测都不覆盖这条运行时契约。

## 防复发规则（核心，给目标 skill 的可执行规则）

- [ ] provider 构造参数凡非「类类型」一律显式 `@Inject(token)`（getRepositoryToken / Symbol token / 字符串 token）
- [ ] 需要 DI 的类**禁用 `import type`** 导入其构造参数类型（type-only 导入会被抹掉元数据）
- [ ] 新增 provider 后核对所在 Module 的 `TypeOrmModule.forFeature([...])` 是否含全部被 `@Inject(getRepositoryToken(...))` 引用的实体
- [ ] 回归门禁必须含一条「全 AppModule 启动冒烟」（e2e health 级），不允许只有手工 new 的单测

## 提炼回填（Skill-Optimizer 模式③ 填）

| 字段 | 值 |
|---|---|
| 提炼落点 | `Backend-Dev/SKILL.md` 常见错误对照表新增行（显式 @Inject / 禁 type-only 导入 DI 参数 / 启动冒烟门禁） |
| 决策记录 | `Backend-Dev/CONTEXT.md` D-09 |
| 忽略理由 | — |
