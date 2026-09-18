---
name: Backend-Dev
description: 后端代码开发（TypeScript + NestJS + Monorepo 默认）。依据 PRD、原型、TDD、FTDD 把技术方案落地为可运行、可维护的微服务后端工程：测试先行逐功能点实现，四层分层 + 服务边界 + libs 共享；开发前出 PROJECT.md + PLAN.md，功能点完成即 eslint/commitlint 校验并提交。维护性第一；不确定就给选择项，一次只问一个关键问题。触发：编写/实现/开发后端代码、按技术方案写后端。
compatibility: Claude Code / Agent SDK / OpenCode
---

# 后端代码开发 Skill

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
7. **未验证不得声明完成**（证据先于声明，见仓库根 `shared/evidence-before-claims.md`）。
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
| **接收评审纪律** | 清单条目先对照代码核实再改，不清楚先澄清（部分理解 = 错误实施），禁表演性认同；「按规范完整实现」类建议先查真实使用（YAGNI） | 见仓库根 `shared/receiving-review.md` |

## 三、主流程（10 步）

> 每步做完再进下一步；◉ = 强制暂停等用户确认。

**S1 开工判定与解析**：
- **三路判定**：续做（有 PROJECT.md + PLAN.md → 读后从进行中/待做续）；既有项目盘点（有代码无两文档 → 按仓库根 `shared/dev-common.md` §一沉淀「项目现状基线」，严格按现状落地，不套默认模板）；全新开发 → 完整流程建两文档。
- 读 `.spec/`：TDD（选型/表结构/接口/边界/测试）、FTDD（fetch 清单）、PRD（先读速查表）、原型；检查评审任务清单并纳入 PLAN。
- **技术栈锁定**：有 TDD → 逐项采用 TDD「技术选型总览」，不重选不追问；无 TDD + 既有代码 → 盘点现状为基线；无 TDD + 全新 → 开工前一次敲定（默认 TypeScript + NestJS / `@nestjs/microservices` / Prisma（备选 TypeORM）/ pnpm workspace / Jest+Supertest / `@nestjs/config`），记入 PROJECT.md 关键决策。
- **组件决策链（调度组件库，涉新组件/基建/通用能力 REQUIRED）**：① 盘点本仓已有基建（AGENTS.md / 依赖清单，已有必须用）→ ② 检索 AI 组件库 `D:\project\agent-project\skills-knowledge\asset-library\`（capabilities → patterns/composites → adapters）→ ③ 命中 → 锁版本（pattern@x + adapter@x）并记录 selected / rejected / unresolved；未命中 → 走封装七步法（`asset-library/shared/component-authoring.md`，造前写 asset-gap；新组件七步全走，小改动轻量通道①+⑥）→ ④ 交付时做沉淀判断（四出口：Case / Candidate / 更新既有 / 反模式），并回写 asset-usage（实际使用版本，偏差记 deviation）与 evidence（命令/结果/局限，无证据视为未完成）。五门禁（检索/选择/实现/验证/沉淀）由 Workflow 据 `pipeline-state.yaml` 拦截。全程受目标项目 AGENTS.md 映射表 + lint/CI 机器兜底约束。
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

**S10 归档 + 回填**：README 运行说明；更新 PROJECT.md / PLAN.md；回填评审任务清单（`已修复` + 修改说明）。回填后须触发 `Code-Review` 复核，不得自判通过（闭环与上限规则见仓库根 `shared/anti-deadloop.md` §一/§二）。

## 四、关键规范

> 正文只留判据；细则按需加载对应 references。

**4.1 架构与分层**：
- **服务内四层**（单向）：`Controller → Service → Repository → Entity`；上层可依赖下层，禁反向 / 跨层；Service 面向接口（`@Injectable` + 接口/抽象 + DI）。
- **服务间边界**：只经对外接口通信（HTTP / gRPC / NATS / MQ）；禁跨服务直连库、禁 import 内部实现、禁循环依赖；依赖关系与 TDD 关联图一致。
- **Monorepo 结构**：`repo/` 下 `apps/web`、`apps/server-*/gateway`、`libs/shared`（DTO/类型/枚举/工具）、`pnpm-workspace.yaml`、`.env.example`、`README.md`；组织方式给选项确认；契约以 `libs/shared` 为单一事实源。模板见 `assets/project-structure-template.md`。

**4.2 代码规范**：函数短小（>~30 行考虑拆）；方法小驼峰、类首字母大写；命名用业务语言，禁 `a`/`b`/`tmp`/`data`；魔法值一律常量或枚举；不用炫技三元链 / 过度泛型 / 反射；注释讲 why，**方法有传参必逐个写清参数作用与约束**，对外接口 / 复杂规则 / 枚举含义必注，删废注释与 TODO 堆积；统一响应 `{code,message,data}`，错误码分段（1xxx 参数 / 2xxx 业务 / 3xxx 权限 / 5xxx 系统），禁空 catch 吞错，入口层 class-validator + DTO、Service 层业务校验。

**4.3 数据模型**：Entity 与 TDD 表结构逐字段一致；迁移可重复执行、可版本管理；每表归属唯一服务；实体纯数据不含业务逻辑。细则沿用 `Backend-Tech-Design/references/data-model-guide.md`。

**4.4 接口实现**：RESTful 路径语义化；分页统一 `{list,total}`（大表 / 深翻页用游标分页，见 `decision-rules.md` §三；游标场景 total 为近似值或省略并注明）；契约单一事实源 = `libs/shared` DTO 或 OpenAPI；服务间消息结构同样在共享包定义。

**4.5 测试**：测试先行（把 TDD 的 Gherkin + 用例骨架落成可运行测试）；覆盖五类并标 AC；分层——Service 单测 mock 仓储、Repository 集成测试（测试库 / 事务回滚）、Controller 契约测试、服务间契约 / 集成；可一键 `pnpm test`。

**4.6 提交**：一功能点一提交，代码 + 测试跑通立即提交，信息可追溯 AC；提交前 ESLint + commitlint（husky + lint-staged）；Conventional Commits `type(scope): subject`，type = feat/fix/refactor/docs/test/chore，scope = 服务 / 模块。

**4.7 项目跟踪与续做**：

| 文档 | 作用 | 更新时机 |
|---|---|---|
| `PROJECT.md` | 项目情况 / 规则 / 进度总览 | 新建时与每次结束 |
| `PLAN.md` | 功能点清单 + 状态 | 开发前与每个功能点完成 |

状态：⏳ 待做 / 🚧 进行中 / ✅ 完成（附 hash）——**未完成不标完成**。续做：先读 PROJECT.md → 读 PLAN.md 定位 🚧/⏳ → 续做 → 持续更新。

**4.8 澄清协议**：必澄清——服务边界、接口契约冲突（TDD vs FTDD）、全局命名 / 目录约定、多人协作约定。提问方式与统一模板见仓库根 `shared/dev-common.md` §二（给 2~4 选项 + 推荐 + 理由、一次只问一个关键问题、可批量列编号清单逐条确认、结论留痕）；TDD 已写死或默认已明确的直接采用，非关键细节先用默认并留痕。

**4.9 生产就绪与性能**：
- **生产就绪清单**（逐项打勾，缺项不算完成）：接口文档完整（OpenAPI / 等价形式）· 数据库迁移已验证可重复执行 · 容器镜像可构建 · 配置全部外置 · 健康检查端点 · 指标端点 · 结构化日志含关联 ID · 敏感操作审计日志 · 限流配置 · 优雅停机 · 启动时环境校验 · Runbook（启动 / 回滚 / 常见故障处置）。
- **性能**：关键接口有 p95 目标且与方案对得上；重任务异步化；热点查询有索引与缓存策略；外部调用有超时 / 重试 / 限流。

## 五、常见错误对照表

> 公共错误行（现状基线 / 零选型 / 拍板 / 传参注释 / 提交粒度 / 门禁 / 进度更新）见仓库根 `shared/dev-common.md` §三；下表为本 skill 后端领域行。

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
| 脚本批量改码遇混合换行（CRLF/LF）锚点错位 | 逐文件探测换行类型；多处插入原串定位倒序应用；优先 Edit 工具改单文件，脚本批改即改即编译（bug-patterns/2026-09-15/01） |
| heredoc / re.sub 转义吞噬生成坏源码 | 反斜杠字面量用 chr(92) 拼接；re.sub 替换串含反斜杠改用 lambda；生成后立即编译（bug-patterns/2026-09-15/02） |
| Nest provider 构造参数用投影类型/接口/type-only 导入 → 运行时 DI 解析失败（tsc 全绿） | 非类类型参数显式 @Inject(token)；DI 参数禁 import type；forFeature 实体清单与 token 对应；回归必含全 AppModule 启动冒烟（bug-patterns/2026-09-15/03） |
| 构造器加参后 spec 位置参数错位（as never 掩盖）→ 批量假失败 | grep 全部 new 调用点逐一补参；批量同症状假失败先查槽位错位；提交前 eslint --fix + commitlint 预检（bug-patterns/2026-09-15/04、05） |

## 六、资源清单

- `references/architecture-guide.md`、`code-style-guide.md`、`test-guide.md`、`tech-stack-guide.md`、`decision-rules.md`
- `references/case-library/`：语言规范 + API/安全 + 质量工程化 + 同行样本（按需加载）
- `assets/project-structure-template.md`、`module-code-template.md`、`project-status-template.md`、`plan-template.md`
- `shared/dev-common.md`、`shared/receiving-review.md`、`shared/evidence-before-claims.md`、`shared/anti-deadloop.md`（仓库根）：公共约定
- 项目目录：代码 + `PROJECT.md` + `PLAN.md` + `README`

## 七、运行问题埋点

收尾按 `Skill-Optimizer/references/instrumentation-guide.md` 自查上报 `issue/Backend-Dev/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `Skill-Optimizer/assets/issue-template.md`）。不确定不记，不打断主流程。
