# CONTEXT.md —— Backend-Dev Skill 领域术语与决策记录

> 本文件是 `Backend-Dev` Skill 的**术语对齐源**与**决策日志**。
> SKILL.md / assets / references 中出现的所有概念必须与本文件一致；
> 每敲定一个概念，必须同步更新本文件。

---

## 一、角色定位（Who We Are）

- **Skill 人设**：后端开发专家 / 资深后端工程师（Backend Developer）；
- **核心目标**：依据已定稿的后端技术方案（TDD），把「技术方案」落地为「可运行、可维护的微服务后端代码工程」；
- **三大原则**：① 维护性优先（可读性 > 炫技）；② 不确定就问、给选择项（一次只问一个关键问题）；③ 小步提交（每功能点一次提交 + eslint/commitlint 校验）；
- **铁律（Domain Boundary）**：「照图施工」——TDD 是施工图，本 skill 不重新设计、不改需求；只覆盖后端，前端实现归 `Frontend-Dev`。

## 二、术语表（Glossary）

| 术语 | 英文/Key | 权威定义 | 易混淆概念排除 |
|---|---|---|---|
| 功能点（原子） | Feature Atom | 一个可独立运行、可独立回滚、可独立验收的完整业务能力（如「用户登录」），是开发计划 / 提交 / 任务跟踪的原子粒度 | ❌ 不是一行代码（也不是攒一堆才提交） |
| 四层分层 | 4-Layer Architecture | 服务内部 Controller → Service → Repository → Entity，依赖单向向下；SQL 只进 Repository、业务逻辑只进 Service | ❌ 微服务不等于放弃分层（服务内部仍保持清洁分层） |
| 微服务边界 | Service Boundary | TDD「模块清单」是服务拆分候选边界；服务间只通过对外接口通信（HTTP/gRPC/NATS/队列），禁止跨服务直连数据库或 import 内部实现 | ❌ 不是一模块必须一服务（按耦合度合并/拆分，不确定用澄清协议） |
| Monorepo | Monorepo | 前后端同仓库：`apps/web` + `apps/server-*` + `libs/shared`，pnpm workspace 统一管理 | ❌ 不是单仓单应用 |
| 契约单一事实源 | Contract Single Source | 前后端共用类型/DTO 放 `libs/shared`（或 OpenAPI 生成），禁止各写一份；冲突时以 TDD 为准并提醒用户确认 | ❌ 不是前端自定义接口（防契约漂移） |
| 澄清协议 | Clarification Protocol | 不确定就问的落地规程：优先给 2~4 个选择项（推荐项+理由）、一次一问、TDD 已写死的不问、非关键细节用默认值并留痕 | ❌ 不是连环轰炸提问 |
| 续做模式 | Resume Mode | 检测到项目已有 `PROJECT.md` + `PLAN.md` → 先读两文档恢复上下文，从「进行中/待做」功能点继续，不重头开始 | ❌ 不是重新初始化工程 |
| 测试先行 | Test-First | 每个功能点先写测试（承接 TDD 测试用例）再写实现；覆盖五类：正向/边界/异常/幂等/并发，标注 AC 编号 | ❌ 不是先实现后补测试 |
| 断点续做 | Checkpoint Resume | 通过 PLAN.md 任务状态（⏳待做/🚧进行中/✅完成+hash）保证进度可查、随时可续 | ❌ 不是靠会话记忆恢复 |
| 小步提交 | Small-step Commit | 每功能点一次 git commit，提交前强制 eslint + commitlint（Conventional Commits），保证仓库随时可运行、可精准回滚 | ❌ 不是每行一提交（也不是攒一堆） |

## 三、决策日志（Decision Log）

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 2026-09-05 | 模式④自身体检发现的 1 条当场修复：新建本 CONTEXT.md 补齐仓库三件套约定（SKILL + README + CONTEXT + assets + references）——Backend-Dev 是最早迭代的 skill 之一，正文结构健康，唯一缺失为 CONTEXT | 体检三件套缺失（P1）；经用户授权「后续问题一律当场修」 | ✅ 已确认 |

## 四、待决问题清单（Open Questions）

> 无待决项。
