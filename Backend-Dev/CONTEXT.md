# CONTEXT.md —— Backend-Dev Skill 领域术语与决策记录

> Backend-Dev 的术语对齐源与决策日志。SKILL.md / assets / references 的概念必须与此一致；每敲定一个概念须同步更新本文件。

## 一、角色与边界

- 人设：后端开发专家 / 资深后端工程师。
- 目标：依据定稿 TDD，把技术方案落地为可运行、可维护的微服务后端代码工程。
- 三原则：维护性优先；不确定就问、给选择项（一次一问）；小步提交（功能点一次提交 + eslint/commitlint）。
- 域界：「照图施工」——TDD 是施工图，不重新设计、不改需求；前端归 Frontend-Dev。

## 二、术语表

| 术语 | 英文/Key | 定义 | 排除 |
|---|---|---|---|
| 功能点（原子） | Feature Atom | 可独立运行/回滚/验收的完整业务能力；开发计划、提交、任务跟踪的原子粒度 | 不是一行代码，也不是攒一堆才提交 |
| 四层分层 | 4-Layer Architecture | Controller → Service → Repository → Entity，依赖单向向下；SQL 只进 Repository，业务逻辑只进 Service | 微服务不等于放弃分层 |
| 微服务边界 | Service Boundary | TDD 模块清单是服务拆分候选边界；服务间只走对外接口（HTTP/gRPC/NATS/队列），禁跨服务直连库或 import 内部实现 | 不是一模块必一服务（按耦合度拆合，不确定用澄清协议） |
| Monorepo | Monorepo | 前后端同仓：apps/web + apps/server-* + libs/shared，pnpm workspace | 不是单仓单应用 |
| 契约单一事实源 | Contract Single Source | 前后端共用类型/DTO 放 libs/shared（或 OpenAPI 生成），禁各写一份；冲突以 TDD 为准并提醒确认 | 不是前端自定义接口 |
| 澄清协议 | Clarification Protocol | 给 2~4 个选项（推荐+理由）、一次一问；TDD 已写死的不问；非关键细节用默认并留痕 | 不是连环提问 |
| 续做模式 | Resume Mode | 有 PROJECT.md + PLAN.md → 先读恢复上下文，从进行中/待做继续 | 不是重新初始化 |
| 测试先行 | Test-First | 先写测试（承接 TDD 用例）再实现；覆盖正向/边界/异常/幂等/并发，标 AC | 不是后补测试 |
| 断点续做 | Checkpoint Resume | PLAN.md 状态（⏳/🚧/✅+hash）保证进度可查、随时可续 | 不是靠会话记忆 |
| 小步提交 | Small-step Commit | 一功能点一 commit；提交前 eslint + commitlint（Conventional Commits） | 不是每行一提交 |
| 项目现状基线 | Existing-Project Baseline | 既有代码无 PROJECT/PLAN → 先盘点结构/栈/依赖/规范/git 沉淀 PROJECT.md；按现状开发，不套默认模板、不擅自重构 | 现状优先于模板 |
| 开发期零选型决策 | Zero Selection at Dev | 选型只来三个来源：读 TDD / 项目现状 / 无 TDD 全新开发启动前一次问清并记 PROJECT.md；实现期不再补选型 | 不是开发期逐步澄清 |
| 编码层决策规则 | Decision Rules | decision-rules.md：框架选型/分层职责/API/鉴权/数据层/质量六板斧/安全编码的硬规则 | 与 Backend-Tech-Design 决策规则分工：那份管方案层，本份管编码层 |
| 案例库 | Case Library | case-library/：language-patterns + api-security + quality-engineering + 同行样本 | 借鉴不照搬，TDD 选型优先 |

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 2026-09-05 | 新建 CONTEXT.md，补齐仓库三件套（SKILL+README+CONTEXT+assets+references） | 体检发现 CONTEXT 缺失（P1），经授权当场修 | ✅ 已确认 |
| D-02 | 2026-09-05 | 注入心法「做减法」：§1.1 补不提前抽象——TDD 明确要的才写，需求出现再重构 | 按 Vibe Coding 心法全面优化；Backend-Dev 属开发类 | ✅ 已确认 |
| D-03 | 2026-09-05 | 步骤 3 补「验收标准前置（DoD）」：功能点动手前先写完成定义并进 PLAN.md，完成后按同一标准自检 | 学习笔记 3.1：先给任务级验收标准、完成后自检自打回 | ✅ 已确认 |
| D-04 | 2026-09-05 | 开工方式二分改三模式 + 技术栈决策不落开发期：新增既有项目盘点模式；技术栈三来源锁定；澄清场景删技术栈；步骤 2 既有项目不擅自分服务；术语表补两条 | 用户要求技术方案阶段定全确定、已有项目先盘点再按结构开发 | ✅ 已确认 |
| D-05 | 2026-09-08 | 新增 decision-rules（编码层硬规则：框架/分层/API/鉴权/数据层/质量六板斧/安全）+ case-library（语言规范/API安全/质量工程化/同行样本 4 文件） | 用户提供后端开发案例库资源清单，要求系统增强 | ✅ 已确认 |
| D-06 | 09-09 | 体检修复 6 项：统一响应结构 {code,message,data} 对齐（decision-rules）；分页游标/total 口径闭合；tech-stack-guide browser-use 提及补回退；README 上下游补 Code-Review；现状基线/澄清协议/错误表公共行收口 shared/dev-common.md（R7）；data-model-guide 跨 skill 引用补路径分隔符（S2）+埋点统一 | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |

## 四、待决问题

无。