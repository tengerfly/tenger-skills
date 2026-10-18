---
name: backend-dev
description: "后端代码开发（TypeScript + NestJS + Monorepo 默认）。依据 PRD、原型、TDD、FTDD 把技术方案落地为可运行、可维护的微服务后端工程：测试先行逐功能点实现，四层分层 + 服务边界 + libs 共享；开发前出 PROJECT.md + PLAN.md，功能点完成即 eslint/commitlint 校验并提交；业务能力模块先检索外部 AI 知识库复用（经仓库根 skill-knowledge 引用层，防冗余沉淀）。维护性第一；不确定就给选择项，一次只问一个关键问题。触发：编写/实现/开发后端代码、按技术方案写后端。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: "Backend-Dev"
  compatibility: "Claude Code / Agent SDK / OpenCode"
---

# 后端代码开发 Skill

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## 先判任务强度

先按 `../../shared/execution-profiles.md` 选择强度，按 `../../shared/requirements-context.md` 读取本次需求原文与依赖。低风险独立任务直接走“确认验收点 → 相关代码/接口盘点 → 局部实现 → 针对性验证 → 结果”；缺少完整 TDD/FTDD、PROJECT/PLAN 不单独阻塞，可用同一任务摘要中的局部计划替代。复用现有栈与组件，不强制新模板、外部资产沉淀、完整 Scope Gate 或自动提交；关键业务/接口未知仍须澄清，风险变化则升级。

下文完整开发步骤与产物要求用于标准/完整；轻量仍保留适用的业务约束、范围、实现质量与测试要求，不宣称正式 Gate 通过。无浏览器可交付待视觉验证代码，但不能声称视觉/交互验收通过。


> IRON LAW：**开发期零选型决策**——技术栈只从 TDD / 现状基线 / 开工前一次性敲定三个来源来，中途不重选。
> 依据 PRD + 原型 + TDD + FTDD 落地后端工程。原则：维护性优先；不确定就问并给选项；小步提交。

## 一、定位与铁律

**角色**：后端开发专家。**TDD 是施工图**，本 skill 照图施工；**FTDD 是接口验收线**。

**铁律**：

1. 分层单向：Controller → Service → Repository → Entity；禁跨层、禁反向，**SQL 只出现在 Repository**。
2. 服务只经对外接口通信：禁跨服务直连库、禁 import 对方内部实现、禁循环依赖。
3. **测试先行**：先写测试再写实现，覆盖五类（正向 / 边界 / 异常 / 幂等 / 并发）。
4. 技术栈只从三个来源（TDD → 现状基线 → 开工前一次敲定），开发期不重选。
5. 契约单一事实源：共享 DTO / 类型放 `libs/shared`，前后端各写一份即违规。
6. 一功能点一提交；提交前 eslint + commitlint 必过。
7. **未验证不得声明完成**（证据先于声明，见仓库根 `../../shared/evidence-before-claims.md`）。
8. 只写本 skill 该写的——不代写需求 / 原型 / 技术方案 / 前端。

**维护性五条**（贯穿全程）：可读性 > 聪明技巧（禁炫技、魔法值、隐式行为）；单一职责、函数短小；分层单向依赖；按业务域拆模块、只经接口交互；注释讲「为什么」不重复代码。

**做减法**：不为「将来可能」提前抽象；TDD 明确要的才写。

**适用范围**：适用「有 TDD（±PRD/原型/FTDD）落后端代码」；不适用写评审需求、原型、技术方案、前端、纯运维部署。

**默认工程形态**（TDD 指定则跟随）：TypeScript + NestJS；微服务；前后端同仓 Monorepo（`apps/web`、`apps/server-*`、`libs/shared`）；多人协作约定先行。

## 二、输入与前置

| 输入 | 作用 | 缺失处理 |
|---|---|---|
| `.spec/TDD/VN/` | **施工图**：选型 / 表结构 / 接口 / 边界 / 测试 | ⛔ 阻塞（无 TDD 走「现状基线」或「开工前一次敲定」两路） |
| `.spec/PRD/VN/`（先读 `PRD速查表.md`）、`.spec/原型/`、`.spec/FTDD/VN/` | 需求与接口验收线（fetch 清单） | 缺则按已有文档推进并标注 |
| `.spec/代码评审/任务清单.md` | 归本 skill 的 `已确认` 任务逐条纳入 PLAN | 无则跳过 |
| `PROJECT.md` + `PLAN.md`（项目目录） | 续做定位（⏳ 待做 / 🚧 进行中 / ✅ 完成） | 无则新建；有代码无则先盘点现状基线 |
| **接收评审纪律** | 清单条目先对照代码核实再改，不清楚先澄清（部分理解 = 错误实施），禁表演性认同；「按规范完整实现」类建议先查真实使用（YAGNI） | 见仓库根 `../../shared/receiving-review.md` |

## 三、主流程（10 步）

> 每步做完再进下一步；◉ = 强制暂停等用户确认。

**S1 开工判定与解析**：
- **三路判定**：续做（有 PROJECT.md + PLAN.md → 读后从进行中/待做续）；既有项目盘点（有代码无两文档 → 按仓库根 `../../shared/dev-common.md` §一沉淀「项目现状基线」，严格按现状落地，不套默认模板）；全新开发 → 完整流程建两文档。
- **仓库前置（REQUIRED）**：确认项目有 git 仓库；无则在允许修改范围内 `git init` + 提交基线（不 push、不改远端），否则铁律 6「一功能点一提交」、回滚基线与评审按提交定位都无法执行——无 git 不是跳过提交纪律的理由。
- **契约开工清单（REQUIRED，标准/完整）**：开工前按本次模块一次性列全「所需错误码 / 枚举值 / 共享字段 / 跨模块接口」，报授权方批量补齐；实现期不硬编码新错误码，也不每个模块各停一次等裁决（knowledge-bases 第 41 轮实测：缺 SET_NAME_CONFLICT/SET_NOT_FOUND/EvalSetOrigin 造成多次 round-trip）。
- **续做输入瘦身（REQUIRED）**：续做/多模块并行时，只读「本次要改模块」的 TDD 分篇 §4~§6 + 契约分册相关节 + 该模块现有代码与测试；跨模块依赖按 S2 关联图定点读，不按目录顺序通读全部 TDD/PRD/FTDD。判据：读入量以「能开工当前功能点」为限；读完一个模块的施工图就落一个模块，不为「先看全貌」把六七个模块的文档串行读完再动手（knowledge-bases 第 41 轮实测：全量通读使首个模块落地延迟 15+ 分钟，而分模块推进的参考实现同时间已交付 2 个模块）。
- 读 `.spec/`：TDD（选型/表结构/接口/边界/测试）、FTDD（fetch 清单）、PRD（先读速查表）、原型；检查评审任务清单并纳入 PLAN。
- **技术栈锁定**：有 TDD → 逐项采用 TDD「技术选型总览」，不重选不追问；无 TDD + 既有代码 → 盘点现状为基线；无 TDD + 全新 → 开工前一次敲定（默认 TypeScript + NestJS / `@nestjs/microservices` / Prisma（备选 TypeORM）/ pnpm workspace / Jest+Supertest / `@nestjs/config`），记入 PROJECT.md 关键决策。
- **组件决策链（调度 AI 知识库，涉业务能力模块/新组件/基建/通用能力 REQUIRED；命中即复用或适配复用，禁重复手写同类业务模块）**：① 盘点本仓已有基建（AGENTS.md / 依赖清单，已有必须用）→ ② 检索外部 AI 知识库 `$env:SKILLS_KNOWLEDGE_ROOT/asset-library/`（blueprints 判型收敛 → capabilities → patterns/composites → adapters；使用入口与同步协议见仓库根 `../../skill-knowledge/README.md`；**未配置 `$env:SKILLS_KNOWLEDGE_ROOT` 时按 `../../skill-knowledge/README.md` 的降级规则跳过检索并登记，不伪造命中**）→ ③ **命中 → 锁版本（pattern@x + adapter@x）直接复用并记录 selected / rejected / unresolved；命中但不完全适用 → 兼容性适配优先**（扩参数 / 加 adapter / 版本演进既有资产），**禁新建并列冗余组件（硬性条件）**；确实无法适配 → 记 asset-gap 说明与既有资产的差异、经用户确认才新建，或采用其他方案留在项目内不进库；未命中 → 走封装七步法（`asset-library/shared/component-authoring.md`，造前写 asset-gap；新组件七步全走，小改动轻量通道①+⑥）→ ④ 交付时做沉淀判断（四出口：Case / Candidate / 更新既有 / 反模式；**沉淀前必查重**，见 S10），并回写 asset-usage（实际使用版本，偏差记 deviation）与 evidence（命令/结果/局限，无证据视为未完成）。五门禁（检索/选择/实现/验证/沉淀）由 Workflow 据 `pipeline-state.yaml` 拦截。全程受目标项目 AGENTS.md 映射表 + lint/CI 机器兜底约束。
- **批判性审视**：对 TDD 或计划本身有疑虑先向用户提出，不闷头执行。

**S2 服务拆分**：TDD 模块清单 = 服务边界候选；是否合并按耦合度定，不确定用选项让用户选。既有项目新功能落既有服务，不擅自分服务。依赖与 TDD 关联图一致并标通信方式。

**S3 开发计划（功能点为原子）**：功能点 = 可独立运行 / 回滚 / 验收的完整能力，拆自 TDD 与 PRD AC。每个功能点先写 DoD（测试全绿 + 正常/空/异常边界 + 契约对齐）再实现。生成 `PLAN.md` 任务清单（编号 / 名称 / 服务 / 关联 AC / 状态）+ `PROJECT.md`（模板 `assets/project-status-template.md`、`plan-template.md`）。
- **粒度判据**：功能点 = **自带测试周期、值得一个新鲜评审者单独把关**的最小单元；配置 / 脚手架 / 文档折进需要它们的那个功能点；只在「评审者可能接受 A 却打回 B」处切分。
- **计划必含**：每功能点写清 `Files`（新建/修改的**精确路径**）+ `Interfaces`（消费谁、产出谁的**精确签名**：函数名 / 参数 / 返回类型）。
- **禁占位符**：不得出现 TBD / TODO /「稍后实现」/「加适当错误处理」/「同功能点 N」。
- **计划自审三查**：① 需求覆盖——每条 AC 能指到具体功能点；② 占位符扫描——按上条清零；③ **命名与类型一致性**——同一函数/字段在各处叫法与签名一致（A 处 `clearLayers()`、B 处 `clearFullLayers()` = 隐藏 bug）。

**S4 工程初始化**：Monorepo 目录（pnpm workspace）；依赖锁定 NestJS / ORM / 测试 / 微服务传输；配置外置（env / 配置文件，禁硬编码）；基础设施层先落地（统一响应 / 错误码 / 日志 trace_id / DB 连接 / 鉴权校验 / 服务间 client）。结构见 §4.1。

**S5 数据模型落地**：TDD 每张表 → Entity / Model（字段 / 类型 / 约束 / 索引 / 注释一致）+ 迁移脚本；金额整数分；表归属服务明确，跨服务走接口不直连库。细则见 §4.3。

**S6 ◉ Scope Gate（强制暂停）**：呈现开发计划 + 服务/模块清单 + 技术栈落地方式 + 数据模型预览；确认后放行；只实现部分则以用户指定范围为准。

**S7 逐功能点实现（顺序固定）**：先写测试 → Repository（SQL / ORM 只在此层）→ Service（业务规则 / 事务，不碰 SQL）→ Controller（路由 / 校验 / 统一响应，不写业务）。每完成一功能点：更新 PLAN 状态（附 hash）→ eslint + commitlint → 自动提交。

**S8 接口契约对齐**：后端接口与 TDD、FTDD fetch 双向一致；前端调的都有且签名一致，后端定义的前端都有消费（或标注预留）；共享 DTO / 类型放 `libs/shared` 作单一事实源；冲突以 TDD 为准并提醒确认。

**S9 全局一致性 + 生产就绪**：一致性（可编译可运行、分层无越界、服务边界无侵入、命名统一、注释完整、测试可跑且覆盖五类、覆盖率企业级 ≥80%）；生产就绪按 **§4.9 清单**逐项打勾，缺项不算完成；性能按 **§4.9** 口径核对。

**S10 归档 + 回填**：README 运行说明；**业务组件沉淀判定（⚠️ REQUIRED）**：本项目开发的业务能力模块——项目内真实使用且跨项目有复用潜力（可剥离项目特有依赖参数化）→ 按「职责边界 / 窄接口 / 最小示例 / 自测证据」四件套沉淀到外部 AI 知识库 `$env:SKILLS_KNOWLEDGE_ROOT/`（asset-library 沉淀闭环：evidence 回写 → 四出口判断，规格见其使用手册）；**沉淀前必查重（硬性条件）**：库内已有近似组件 → 一律走「更新既有 / 兼容适配」出口，禁新建并列冗余组件；确需新建须记 asset-gap 差异说明并经用户确认；判定结果留痕 PROJECT.md；强绑定本项目领域模型 / 数据结构的项目特有组件**不沉**（防为沉而沉）；更新 PROJECT.md / PLAN.md；回填评审任务清单（`已修复` + 修改说明）。回填后须触发 `Code-Review` 复核，不得自判通过（闭环与上限规则见仓库根 `../../shared/anti-deadloop.md` §一/§二）。

## 四、关键规范

> 正文只留判据；细则按需加载对应 references。

**4.1 架构与分层**：
- **服务内四层**（单向）：`Controller → Service → Repository → Entity`；上层可依赖下层，禁反向 / 跨层；Service 面向接口（`@Injectable` + 接口/抽象 + DI）。
- **服务间边界**：只经对外接口通信（HTTP / gRPC / NATS / MQ）；禁跨服务直连库、禁 import 内部实现、禁循环依赖；依赖关系与 TDD 关联图一致。
- **Monorepo 结构**：`repo/` 下 `apps/web`、`apps/server-*/gateway`、`libs/shared`（DTO/类型/枚举/工具）、`pnpm-workspace.yaml`、`.env.example`、`README.md`；组织方式给选项确认；契约以 `libs/shared` 为单一事实源。模板见 `assets/project-structure-template.md`。

**4.2 代码规范**：函数短小（>~30 行考虑拆）；方法小驼峰、类首字母大写；命名用业务语言，禁 `a`/`b`/`tmp`/`data`；魔法值一律常量或枚举；不用炫技三元链 / 过度泛型 / 反射；注释讲 why，**方法有传参必逐个写清参数作用与约束**，对外接口 / 复杂规则 / 枚举含义必注，删废注释与 TODO 堆积；统一响应 `{code,message,data}`，错误码分段（1xxx 参数 / 2xxx 业务 / 3xxx 权限 / 5xxx 系统），禁空 catch 吞错，入口层 class-validator + DTO、Service 层业务校验。

**4.3 数据模型**：Entity 与 TDD 表结构逐字段一致；迁移可重复执行、可版本管理；每表归属唯一服务；实体纯数据不含业务逻辑。细则沿用 `../backend-tech-design/references/data-model-guide.md`。

**4.4 接口实现**：RESTful 路径语义化；分页统一 `{list,total}`（大表 / 深翻页用游标分页，见 `decision-rules.md` §三；游标场景 total 为近似值或省略并注明）；契约单一事实源 = `libs/shared` DTO 或 OpenAPI；服务间消息结构同样在共享包定义。

**4.5 测试**：测试先行（把 TDD 的 Gherkin + 用例骨架落成可运行测试）；覆盖五类并标 AC；分层——Service 单测 mock 仓储、Repository 集成测试（测试库 / 事务回滚）、Controller 契约测试、服务间契约 / 集成；可一键 `pnpm test`。

**4.6 提交**：一功能点一提交，代码 + 测试跑通立即提交，信息可追溯 AC；提交前 ESLint + commitlint（husky + lint-staged）；Conventional Commits `type(scope): subject`，type = feat/fix/refactor/docs/test/chore，scope = 服务 / 模块。

**4.7 项目跟踪与续做**：

| 文档 | 作用 | 更新时机 |
|---|---|---|
| `PROJECT.md` | 项目情况 / 规则 / 进度总览 | 新建时与每次结束 |
| `PLAN.md` | 功能点清单 + 状态 | 开发前与每个功能点完成 |

状态：⏳ 待做 / 🚧 进行中 / ✅ 完成（附 hash）——**未完成不标完成**。续做：先读 PROJECT.md → 读 PLAN.md 定位 🚧/⏳ → 续做 → 持续更新。

**4.8 澄清协议**：必澄清——服务边界、接口契约冲突（TDD vs FTDD）、全局命名 / 目录约定、多人协作约定。提问方式与统一模板见仓库根 `../../shared/dev-common.md` §二（给 2~4 选项 + 推荐 + 理由、一次只问一个关键问题、可批量列编号清单逐条确认、结论留痕）；TDD 已写死或默认已明确的直接采用，非关键细节先用默认并留痕。

**4.9 生产就绪与性能**：
- **生产就绪清单**（逐项打勾，缺项不算完成）：接口文档完整（OpenAPI / 等价形式）· 数据库迁移已验证可重复执行 · 容器镜像可构建 · 配置全部外置 · 健康检查端点 · 指标端点 · 结构化日志含关联 ID · 敏感操作审计日志 · 限流配置 · 优雅停机 · 启动时环境校验 · Runbook（启动 / 回滚 / 常见故障处置）。
- **性能**：关键接口有 p95 目标且与方案对得上；重任务异步化；热点查询有索引与缓存策略；外部调用有超时 / 重试 / 限流。

## 五、常见错误对照表

> 公共错误行（现状基线 / 零选型 / 拍板 / 传参注释 / 提交粒度 / 门禁 / 进度更新）见仓库根 `../../shared/dev-common.md` §三；下表为本 skill 后端领域行。

| 错误 | 纠正 |
|---|---|
| 技术栈与 TDD 不一致 | 读 TDD；缺失才默认 |
| 微服务内放弃分层 | 仍四层（§4.1） |
| 跨服务直连库 / import | 只走对外接口 |
| 业务逻辑 / SQL 越层 | 逻辑进 Service、SQL 进 Repository |
| 无意义命名 / 魔法值 | 业务命名 + 常量枚举 |
| 注释重复 / 过时 | 讲 why |
| 空 catch 吞错 | 处理或上抛 |
| 金额浮点 / 字段不一致 | 整数分 + 对齐 TDD |
| 接口与 FTDD 不符 | 双向核对 + 共享 DTO |
| 前后端各写类型 | `libs/shared` / OpenAPI 单一源 |
| 先实现后测试 / 只正测 | 测试先行五类 |
| 配置硬编码 | 外置 |
| 计划含占位符 | 按 S3「禁占位符」清零 |
| 没跑就报「完成」 | 铁律 7，出本次证据 |
| 灰度/迁移改造只给 handler 注桩、不补行为断言 | 注入 stub 只是接线不是测试；对照 TDD §9 覆盖矩阵逐 TC 编号 grep spec 断言，缺一即欠账（AgentV2 评审 CR-01 教训）
| 改业务提示词不同步 mock seed matcher | 提示词常量改动后，把全部 registerStream/script/registerJson 的 matcher 拿到新提示词实文里 grep 验证命中（CR-02 教训：讲解链路 mock 必失败）|
| 脚本批量改码遇混合换行（CRLF/LF）锚点错位 | 逐文件探测换行类型；多处插入原串定位倒序应用；优先 Edit 工具改单文件，脚本批改即改即编译（../../bug-patterns/2026-09-15/01） |
| heredoc / re.sub 转义吞噬生成坏源码 | 反斜杠字面量用 chr(92) 拼接；re.sub 替换串含反斜杠改用 lambda；生成后立即编译（../../bug-patterns/2026-09-15/02） |
| run_code/模板字符串二次转义把 `\b` 写成控制字符 | 生成源码后立即扫控制字符 + 编译；正则优先 `new RegExp`/`includes`（../../shared/dev-common.md §四） |
| PowerShell 文本管线改 UTF-8 源码致中文损坏 | 源码编辑只用 read/edit/write；禁 `Get-Content -Raw \| Set-Content` 改源码（../../shared/dev-common.md §四） |
| SSE/流式端点被全局响应拦截器包成 JSON 信封 | 新增 SSE/流式出口先查全局 interceptor：按 `Accept: text/event-stream` 或路径放行原样输出；e2e 必须断言事件名与 data 不是信封（knowledge-bases M04 实测：不豁免则 event 名丢失） |
| Nest provider 构造参数用投影类型/接口/type-only 导入 → 运行时 DI 解析失败（tsc 全绿） | 非类类型参数显式 @Inject(token)；DI 参数禁 import type；forFeature 实体清单与 token 对应；回归必含全 AppModule 启动冒烟（../../bug-patterns/2026-09-15/03） |
| 构造器加参后 spec 位置参数错位（as never 掩盖）→ 批量假失败 | grep 全部 new 调用点逐一补参；批量同症状假失败先查槽位错位；提交前 eslint --fix + commitlint 预检（../../bug-patterns/2026-09-15/04、05） |
| 同类业务能力模块不检索直接重写 | S1 组件决策链先查外部 AI 知识库，命中复用 |
| 库内已有近似组件仍新建并列组件 | 兼容性适配优先 / 走「更新既有」出口；新建须 asset-gap 差异说明 + 用户确认（硬性条件，S1/S10） |
| 可复用业务组件交付即丢不沉淀 | S10 沉淀判定（⚠️ REQUIRED）：四件套入外部 AI 知识库，项目特有不沉 |

## 六、资源清单

- `references/architecture-guide.md`、`code-style-guide.md`、`test-guide.md`、`tech-stack-guide.md`、`decision-rules.md`
- `references/case-library/`：语言规范 + API/安全 + 质量工程化 + 同行样本（按需加载）
- `assets/project-structure-template.md`、`module-code-template.md`、`project-status-template.md`、`plan-template.md`
- 仓库根 `../../skill-knowledge/`：**AI 知识库引用层**——外部库 `$env:SKILLS_KNOWLEDGE_ROOT/` 的使用入口 / 映射表 / 防冗余硬规则 / 双仓同步协议（见其 README；S1 检索 / S10 沉淀经此对接）
- `../../shared/dev-common.md`、`../../shared/receiving-review.md`、`../../shared/evidence-before-claims.md`、`../../shared/anti-deadloop.md`（仓库根）：公共约定
- 项目目录：代码 + `PROJECT.md` + `PLAN.md` + `README`

## 七、运行问题埋点

收尾按 `../../shared/instrumentation-guide.md` 自查上报 `../../issue/Backend-Dev/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../shared/templates/issue-template.md`）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

下方正式状态/manifest/Gate 写入步骤适用于标准/完整交接；轻量独立任务按共享执行强度使用同一任务摘要，不执行正式状态写入、不伪造批准。

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `Backend-Dev` while exposing it through the v2 Skill contract.

## Trigger

Run when the user explicitly requests this capability or when `WorkFlow/` routes a compatible stage to this wrapper.

## Inputs

- the user's request and confirmed scope;
- current project artifacts, evidence, decisions, and `.spec/workflow.yaml`;
- the retained legacy body, references, assets, and scripts in this directory.

## Preconditions

- read `../../shared/skill-contract.md`, `../../shared/gate-policy.md`, and `../../shared/anti-deadloop.md`;
- read `.spec/manifest.yaml` and `.spec/workflow.yaml` when a project is available;
- verify scope, authorization, repository boundaries, and required upstream artifacts;
- do not overwrite unrelated or uncommitted files.

## Responsibilities

- execute the retained domain capability within its stated scope;
- translate legacy outputs into the current artifact, evidence, decision, and Gate vocabulary;
- record execution, traceability, residual issues, and the next action;
- route work outside this wrapper to the responsible domain Skill.

## Non-goals

- do not silently change product decisions, scope, or acceptance criteria;
- do not invent missing facts, evidence, approvals, or test results;
- do not use legacy Gate values or legacy state files as current truth;
- do not delete retained compatibility material.

## Procedure

1. Read the request, current state, manifest, and upstream handoff.
2. Load only the retained legacy resources needed for this execution.
3. Execute the domain action and keep assumptions separate from evidence.
4. Validate the output against its repair or acceptance criteria.
5. Register artifacts, evidence, decisions, and open items.
6. Write the execution record and `.spec/workflow.yaml`.
7. Emit exactly one Gate and one explicit next action.

## Outputs

- the domain artifact, report, code change, test evidence, or routed task defined by the retained capability;
- `artifactRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, `gate`, and `nextAction`;
- a failure route when the wrapper cannot complete safely.

## Evidence

Use direct source files, command output, test results, screenshots, dated external sources, or explicit user decisions. Label conclusions as `FACT`, `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, `RECOMMENDATION`, `DECISION`, or `OPEN`. A recommendation is not approval.

## Gate

Use only `PASS`, `CONDITIONAL`, or `BLOCKED`. `PASS` requires complete inputs and artifacts with no unresolved P0/P1. Residual P0 is always `BLOCKED`. Residual P1 is never `PASS` and may be `CONDITIONAL` only with `exceptionId`, `risk`, `owner`, `dueAt`, `remediation`, `allowDownstream`, and `approvalRef`. Three review rounds are the maximum; never force-pass or start an automatic fourth round.

## Failure Route

If evidence, authorization, scope, or an upstream Gate is missing, set `BLOCKED`, name the missing item and owner, and route to the responsible upstream Skill. If the issue is outside this wrapper's boundary, stop and route it rather than improvising.

## Downstream Contract

Downstream Skills may consume only manifest entries whose status and Gate allow downstream use. They must read `sourceRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, and `nextAction`; they must not infer approval from chat context or file existence.

## State Changes

Record the old state, new state, actor, timestamp, reason, evidence references, Gate, and next action in `.spec/workflow.yaml`. The exact state names come from `governance/state-registry.yaml`.
