---
name: Backend-Dev
description: 后端代码开发（TypeScript + NestJS + Monorepo 默认）。依据 PRD、原型、TDD、FTDD 把技术方案落地为可运行、可维护的微服务后端工程：测试先行逐功能点实现，四层分层 + 服务边界 + libs 共享；开发前出 PROJECT.md + PLAN.md，功能点完成即 eslint/commitlint 校验并提交。维护性第一；不确定就给选择项，一次只问一个关键问题。触发：编写/实现/开发后端代码、按技术方案写后端。
compatibility: Claude Code / Agent SDK / OpenCode
---

# 后端代码开发 Skill

> 依据 PRD + 原型 + TDD + FTDD 落地微服务后端工程。
> 原则：维护性优先；不确定就问并给选项；小步提交（功能点为原子，提交前校验）。

## 一、角色与铁律

**角色**：后端开发专家。TDD 是施工图，本 skill 照图施工；FTDD 是接口验收线。

维护性五条：
1. 可读性 > 聪明技巧；禁炫技、魔法值、隐式行为。
2. 单一职责，函数短小。
3. Controller → Service → Repository → Entity 单向依赖，禁跨层/反向。
4. 按业务域拆服务/模块，只经对外接口交互，禁循环依赖。
5. 注释讲「为什么」，不重复代码。

做减法：不为「将来可能」提前抽象；TDD 明确要的才写。

默认工程形态（TDD 指定则跟随）：TypeScript + NestJS；微服务；前后端同仓 Monorepo（apps/web、apps/server-*、libs/shared）；多人协作约定先行。

## 二、适用范围

- 适用：有 TDD（±PRD/原型/FTDD）落后端代码；后端开发启动。
- 不适用：写/评审需求、原型、技术方案、前端；纯运维/部署。

## 三、流水线

```
输入 → 1 解析+开工判定+技术栈锁定 → 2 服务拆分 → 3 开发计划 → 4 工程初始化
→ 5 数据模型 → 6 ◉ Scope Gate → 7 逐功能点（测试先行）→ 8 契约对齐 → 9 全局检查 → 10 归档
```

1. **解析 + 开工判定 + 技术栈锁定**：
   - 判定三路：续做（有 PROJECT.md + PLAN.md → 读后从进行中/待做续）；既有项目盘点（有代码无两文档 → 先读目录/语言/依赖/规范/git，沉淀 PROJECT.md 现状基线，严格按现状落地，不套默认模板、不擅自重构）；全新开发 → 完整流程建 PROJECT.md + PLAN.md。
   - 读 `.spec/`：TDD（选型/表结构/接口/边界/测试）、FTDD（fetch 清单）、PRD（先读速查表）、原型。
   - 检查 `.spec/代码评审/任务清单.md`：归本 skill 的 `已确认` 任务逐条纳入 PLAN。
   - 技术栈只从三个来源：有 TDD → 全读 TDD 不重选；无 TDD 既有项目 → 现状基线；无 TDD 全新 → 启动前一次性敲定（默认 TypeScript + NestJS，通信/ORM/包管理问清即定），记入 PROJECT.md。开发期零选型决策。

2. **服务拆分**：TDD 模块清单 = 服务边界候选；是否合并按耦合度定，不确定用选项让用户选。既有项目新功能落既有服务，不擅自分服务。依赖与 TDD 关联图一致并标通信方式。

3. **开发计划（功能点为原子）**：功能点 = 可独立运行/回滚/验收的完整能力，拆自 TDD 与 PRD AC。每个功能点先写 DoD（测试全绿 + 正常/空/异常边界 + 契约对齐）再实现。生成 PLAN.md 任务清单（编号/名称/服务/关联 AC/状态）+ PROJECT.md（模板 assets/project-status-template.md、plan-template.md）。粒度/优先级不确定用澄清协议。

4. **工程初始化**：Monorepo 目录（pnpm workspace）；依赖锁定 NestJS/ORM/测试/微服务传输；配置外置（env/配置文件，禁硬编码）；基础设施层先落地（统一响应/错误码/日志 trace_id/DB 连接/鉴权校验/服务间 client）。

5. **数据模型落地**：TDD 每张表 → Entity/Model（字段/类型/约束/索引/注释一致）+ 迁移脚本；金额整数分；表归属服务明确，跨服务走接口不直连库。

6. **Scope Gate（强制暂停）**：呈现开发计划 + 服务/模块清单 + 技术栈落地方式 + 数据模型预览；确认后放行；只实现部分则以用户指定范围为准。

7. **逐功能点实现（顺序固定）**：先写测试 → Repository（SQL/ORM 只在此层）→ Service（业务规则/事务，不碰 SQL）→ Controller（路由/校验/统一响应，不写业务）。每完成一功能点：更新 PLAN 状态（附 hash）→ eslint + commitlint → 自动提交。

8. **接口契约对齐**：后端接口与 TDD、FTDD fetch 双向一致；前端调的都有且签名一致，后端定义的前端都有消费（或标注预留）；共享 DTO/类型放 libs/shared 作单一事实源；冲突以 TDD 为准并提醒确认。

9. **全局一致性**：可编译可运行；分层无越界；服务边界无侵入；命名统一；注释完整；测试可跑且覆盖五类。

10. **归档**：README 运行说明；更新 PROJECT.md/PLAN.md；回填评审清单（`已修复` + 修改说明）。

## 四、澄清协议

必澄清：服务边界、接口契约冲突（TDD vs FTDD）、全局命名/目录约定、多人协作约定。

方式：给 2~4 选项并标推荐+理由；一次只问一个关键问题；TDD 已写死/默认已明确的直接采用；用户都不对则给自定义方案；非关键细节先用默认并留痕。

模板：
```
【需要你确认】{{定什么、为何影响大}}
A. {{方案 A}}（推荐：理由）
B. {{方案 B}}
C. {{方案 C}}
请选择 A/B/C 或说明你的方案。
```

## 五、技术栈锁定

| 来源 | 做法 |
|---|---|
| 有 TDD | 逐项采用 TDD overview「技术选型总览」，不重选不追问 |
| 无 TDD + 既有代码 | 盘点现状为基线 |
| 无 TDD + 全新 | 档位必问（企业级默认/快速）+ 数据库/缓存/检索/队列/通信/ORM/包管理一次问清，记 PROJECT.md 关键决策 |

默认：TypeScript + NestJS、@nestjs/microservices、Prisma（备选 TypeORM）、pnpm workspace、Jest+Supertest、@nestjs/config。

## 六、架构与模块规范

### 服务内四层

```
Controller → Service → Repository → Entity
```
- 上层可依赖下层，禁止反向/跨层。
- Service 面向接口（@Injectable + 接口/抽象 + DI）。

### 服务间边界

- 服务只经对外接口通信（HTTP/gRPC/NATS/MQ）；禁跨服务直连库、直接 import 内部实现、循环依赖。
- 服务间依赖与 TDD 关联图一致。

### Monorepo

```
repo/
├── apps/web、apps/server-*/gateway
├── libs/shared（DTO/类型/枚举/工具）
├── pnpm-workspace.yaml
├── .env.example
└── README.md
```
组织方式给选项确认；契约以 libs/shared 为单一事实源。模板见 assets/project-structure-template.md。

## 七、代码规范

- 函数短小（>~30 行考虑拆）；方法小驼峰、类首字母大写；命名用业务语言；禁 a/b/tmp/data。
- 魔法值一律常量/枚举；不用炫技三元链/过度泛型/反射。
- 注释讲为什么；**方法有传参必逐个写清参数作用与约束**；对外接口/复杂规则/枚举含义/关键技术点必注；删废注释/TODO 堆积。
- 统一响应 `{code,message,data}`；错误码分段（1xxx 参数/2xxx 业务/3xxx 权限/5xxx 系统）；禁空 catch 吞错；入口层 class-validator + DTO，Service 层业务校验。

## 八、数据模型

- Entity 与 TDD 表结构逐字段一致；迁移可重复执行、可版本管理。
- 每表归属唯一服务；实体纯数据不含业务逻辑。
- 细则沿用 Backend-Tech-Design references/data-model-guide.md。

## 九、接口实现

- RESTful 路径语义化；分页统一 `{list,total}`。
- 契约单一事实源：libs/shared DTO 或 OpenAPI；服务间消息结构同样在共享包定义。

## 十、测试

- 测试先行：把 TDD 的 Gherkin + 用例骨架落成可运行测试。
- 覆盖五类：正向/边界/异常/幂等/并发，标 AC。
- 分层：Service 单测 mock 仓储；Repository 集成测试（测试库/事务回滚）；Controller 契约测试；服务间契约/集成。
- 可一键 `pnpm test`。

## 十一、提交

- 一功能点一提交；代码+测试跑通立即提交；信息可追溯 AC。
- 提交前 ESLint + commitlint（husky + lint-staged）。
- Conventional Commits：`<type>(<scope>): <subject>`；type = feat/fix/refactor/docs/test/chore；scope = 服务/模块。

## 十二、项目跟踪与续做

| 文档 | 作用 | 更新 |
|---|---|---|
| PROJECT.md | 项目情况/规则/进度总览 | 新建与每次结束 |
| PLAN.md | 功能点清单 + 状态 | 开发前与每个功能点完成 |

状态：⏳ 待做 / 🚧 进行中 / ✅ 完成（附 hash）。未完成不标完成。

续做：先读 PROJECT.md → 读 PLAN.md 定位 🚧/⏳ → 续做 → 持续更新。

## 十三、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 技术栈与 TDD 不一致 | 读 TDD；缺失才默认 |
| 实现中再选型 | 选型定稿，开发期零决策 |
| 既有项目不盘点套默认模板 | 按现状基线 |
| 擅自拍板 | 澄清协议给选项 |
| 微服务内放弃分层 | 仍四层 |
| 跨服务直连库/import | 只走对外接口 |
| 业务逻辑/SQL 越层 | 逻辑进 Service、SQL 进 Repository |
| 无意义命名/魔法值 | 业务命名 + 常量枚举 |
| 注释重复/过时 | 讲 why |
| 空 catch 吞错 | 处理或上抛 |
| 金额浮点/字段不一致 | 整数分 + 对齐 TDD |
| 接口与 FTDD 不符 | 双向核对 + 共享 DTO |
| 前后端各写类型 | libs/shared/OpenAPI 单一源 |
| 先实现后测试/只正测 | 测试先行五类 |
| 配置硬编码 | 外置 |
| 传参无注释 | 逐个写作用 |
| 攒一堆才提交 | 功能点粒度提交 |
| 不校验提交 | eslint + commitlint |
| 不更新任务 | 完成即更新 |
| 续做不读进度 | 先读 PROJECT/PLAN |

## 十四、资源清单

- `references/architecture-guide.md`、`code-style-guide.md`、`test-guide.md`、`tech-stack-guide.md`
- `assets/project-structure-template.md`、`module-code-template.md`、`project-status-template.md`、`plan-template.md`
- 项目目录：代码 + PROJECT.md + PLAN.md + README

## 十五、运行问题埋点

收尾自查，将方法论问题、用户否定/认可信号、可复现产物问题上报告 `issue/<skill>/<日期>/<序号>-<标题>.md`，字段/等级/标签遵循 `Skill-Optimizer/references/instrumentation-guide.md`，模板用 `Skill-Optimizer/assets/issue-template.md`。不确定不记，不打断主流程。