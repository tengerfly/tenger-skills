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
| AI 知识库引用层 | skill-knowledge | 外部 AI 知识库 `$env:SKILLS_KNOWLEDGE_ROOT/`（仓库根 `../../skill-knowledge/` 为调度侧引用层）的调度侧引用：S1 组件决策链检索复用，S10 按四件套（职责边界 / 窄接口 / 最小示例 / 自测证据）沉淀进外部库 | 防冗余硬条件：已有近似组件 → 兼容性适配/更新既有，禁新建并列组件；项目特有组件不沉；不是 `libs/shared`（那共享的是契约类型，不是可复用业务模块） |

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 2026-09-05 | 新建 CONTEXT.md，补齐仓库三件套（SKILL+README+CONTEXT+assets+references） | 体检发现 CONTEXT 缺失（P1），经授权当场修 | ✅ 已确认 |
| D-02 | 2026-09-05 | 注入心法「做减法」：§1.1 补不提前抽象——TDD 明确要的才写，需求出现再重构 | 按 Vibe Coding 心法全面优化；Backend-Dev 属开发类 | ✅ 已确认 |
| D-03 | 2026-09-05 | 步骤 3 补「验收标准前置（DoD）」：功能点动手前先写完成定义并进 PLAN.md，完成后按同一标准自检 | 学习笔记 3.1：先给任务级验收标准、完成后自检自打回 | ✅ 已确认 |
| D-04 | 2026-09-05 | 开工方式二分改三模式 + 技术栈决策不落开发期：新增既有项目盘点模式；技术栈三来源锁定；澄清场景删技术栈；步骤 2 既有项目不擅自分服务；术语表补两条 | 用户要求技术方案阶段定全确定、已有项目先盘点再按结构开发 | ✅ 已确认 |
| D-05 | 2026-09-08 | 新增 decision-rules（编码层硬规则：框架/分层/API/鉴权/数据层/质量六板斧/安全）+ case-library（语言规范/API安全/质量工程化/同行样本 4 文件） | 用户提供后端开发案例库资源清单，要求系统增强 | ✅ 已确认 |
| D-06 | 09-09 | 体检修复 6 项：统一响应结构 {code,message,data} 对齐（decision-rules）；分页游标/total 口径闭合；tech-stack-guide browser-use 提及补回退；README 上下游补 Code-Review；现状基线/澄清协议/错误表公共行收口 ../../shared/dev-common.md（R7）；data-model-guide 跨 skill 引用补路径分隔符（S2）+埋点统一 | 全仓冗余专项体检（用户裁决全量修复 + R9 评审模板参数化） | ✅ |
| D-07 | 09-09 | 终检修复 1 项：归档步骤「回填评审清单」→「回填评审任务清单」 | 全仓终检（冗余专项体检修复后复审，用户裁决全修） | ✅ |
| D-08 | 09-10 | 门禁闭环配套：步骤 10 回填评审任务清单后须重跑 `Code-Review` 复核（不得自判通过）；满 3 轮按仓库根 `../../shared/anti-deadloop.md` §二 处理。配套：⑬-后 门禁放行才是 ⑫ 前端开发的开工前置 | Workflow 门禁闭环改造配套（用户要求写一个审一个） | ✅ |
| D-09 | 09-10 | 吸收外部精华：步骤 9「全局一致性」扩为「**全局一致性 + 生产就绪检查**」——①一致性补测试覆盖率企业级 ≥80%；②**生产就绪清单 12 项逐项打勾**（接口文档/迁移可重复执行/容器镜像/配置外置/健康检查/指标端点/结构化日志含关联 ID/审计日志/限流/优雅停机/启动环境校验/Runbook）；③性能：关键接口 p95 目标对齐、重任务异步化、热点索引与缓存、外部调用超时重试限流。另步骤 3 计划规范 + 步骤 1 接收评审（同日早前） | 来源：`VoltAgent/awesome-claude-code-subagents` 的 `backend-developer`（生产就绪检查 / p95 <100ms / 覆盖率 >80% / 可观测性 / 容器化 / 配置与密钥管理） | ✅ |
| D-10 | 09-10 | **结构重构（统一骨架）**：章节 15 → 7——§一 定位与铁律（Iron Law「开发期零选型决策」+ 铁律瘦身 8 条 + 维护性五条 + 做减法）；§二 输入与前置（表格化，含 TDD 施工图 / 评审清单与接收评审纪律 / PROJECT+PLAN / 技术栈三来源）；§三 主流程 10 步（S1 开工判定与解析合并原「技术栈锁定」；S3 计划规范内联；**S9 的生产就绪 12 项清单下沉 §4.9**，解决「长清单塞流程步骤」）；§四 关键规范 4.1~4.9（归并原 §四~§十二：架构分层/Monorepo/代码规范/数据模型/接口/测试/提交/项目跟踪/澄清协议/生产就绪）；§五 错误表 / §六 资源 / §七 埋点。old-vs-new 审计：原 15 章内容全部有归属，无功能丢失 | 用户要求：整理成顺畅流程（Skill-Optimizer 全量体检） | ✅ |
| D-11 | 09-15 | 常见错误对照表 +4 行（混合换行批量改码 / heredoc·re.sub 转义 / Nest DI 元数据三连 / 构造器加参 spec 错位 + 提交预检），来源=learning-assistant V2 会话挖掘沉淀（../../bug-patterns/2026-09-15/01~05 已提炼） | 会话记录挖掘（Skill-Optimizer 模式②→③） | ✅ |
| D-12 | 09-15 | 全仓一致性纠偏：README 流水线把 S1 三路判定合并为一个方框（原拆成两框致 11 步 ≠ SKILL 10 步） | 四代理并行七维体检 | ✅ |
| D-13 | 2026-09-19 | 业务组件资产化闭环：S1 增业务组件检索（命中复用禁重复手写）；S10 增 REQUIRED 沉淀判定（四件套入仓库根 `../../skill-knowledge/业务组件/backend/`，项目特有不沉、判定留痕 PROJECT.md）；错误表 +2 行；description 补能力；README 核心表 +1 行；新建仓库根 `../../skill-knowledge/`（池 README 定目录与四件套规格，源仓库根集中池不随副本部署） | 用户要求：开发中用到的业务组件抽象封装沉淀 skill-knowledge，作为后续开发的组件资产 | ✅ |

| D-14 | 2026-09-19 | 组件闭环统一外部 AI 知识库：S1「业务组件检索」并入组件决策链（blueprints 判型收敛入口 + 指向仓库根 skill-knowledge 引用层）；增防冗余硬条件（命中但不适用 → 兼容性适配优先，禁新建并列冗余组件；无法适配须 asset-gap 差异说明 + 用户确认，或留项目内不进库）；S10 沉淀落点由本仓 `../../skill-knowledge/业务组件/backend/` 改为外部库 asset-library 沉淀闭环 + 沉淀前必查重；错误表 +1 行；description/资源清单/README 同步；术语表改「AI 知识库引用层」 | 用户拍板：AI 组件统一在外部仓 skills-knowledge 作 AI 知识库，skill 侧只留引用+映射表，两边同步更新映射表；防冗余为硬性条件 | ✅ |
| D-15 | 2026-10-18 | **外部 AI 知识库路径可移植化**：S1 组件决策链、S10 沉淀判定、资源清单、术语表四处的外部库路径由本机绝对路径改为环境变量 `$env:SKILLS_KNOWLEDGE_ROOT/`；S1 补「未配置 `$env:SKILLS_KNOWLEDGE_ROOT` 时按 `../../skill-knowledge/README.md` 的降级规则跳过检索并登记，不伪造命中」；顺带清掉术语表路径中的控制字符 | 用户 2026-10-18 要求可移植 / 换机可用（其他机器 / 宿主 / 项目直接可用） | ✅ 已确认 |
## 四、待决问题

无。
