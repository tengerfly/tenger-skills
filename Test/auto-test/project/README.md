# Auto-Test 项目资料（project/）

> 定位：`Test/auto-test` Skill 背后的**产品项目研究资料**（企业级 AI 自动化测试平台 Auto-Test，v0.1，待评审）。只作项目研究与历史参考，**不参与测试执行**。
> 来源：2026-09-18 的独立仓库 `D:\project\agent-project\auto-test`（原独立 git 仓库，远端 https://github.com/tengerfly/auto-test ）；2026-10-18 迁入本目录，同日删除 `docs/auto-test-legacy/` 归档。
> 背景：用户 2026-10-18 反馈「auto-test 被改成 auto-test-legacy」不可接受——旧项目资料应作为 auto-test 体系的一部分直接可用，不再以 legacy 名义埋在 `docs/` 下。

## 一、内容清单与迁移对照

| 当前位置 | 内容 | 归档时原路径 |
|---|---|---|
| [项目计划-企业级AI自动化测试.md](项目计划-企业级AI自动化测试.md) | Auto-Test 平台 v0.1 项目计划：定位、市场判断、四个产品决策、架构、里程碑（M0-M4）、风险；文头状态=待评审 | `docs/auto-test-legacy/项目计划-企业级AI自动化测试.md`（文件名不变） |
| [竞品分析报告.md](竞品分析报告.md) | 2026-09-18 AI 自动化测试竞品分析（11 模块：市场 / 竞品 / 功能矩阵 / 痛点 / 商业模式 / 技术可行性） | `docs/auto-test-legacy/.spec/AI自动化测试竞品分析/AI自动化测试竞品分析报告.md` |
| [竞品分析-验收结果详细说明.md](竞品分析-验收结果详细说明.md) | 上述竞品分析的 Pass Gate 验收结论（TC-CA-20260918-01） | `docs/auto-test-legacy/.spec/AI自动化测试竞品分析/验收结果详细说明.md` |
| [旧项目问题日志.md](旧项目问题日志.md) | 旧独立项目的评审 / 测试 / Bug-Fix 问题台账索引（当前为空台账） | `docs/auto-test-legacy/.spec/问题日志.md` |

迁移只做三件事：保留原文；把正文指向旧 `.spec/` 的路径改成同目录可达写法；文件名按上表统一。其余内容未改写。

## 二、与可执行能力的关系

- **执行入口是 [`../SKILL.md`](../SKILL.md)**：测试编排、分层门禁、产物规范以 SKILL.md 及其 references / assets 为准；本目录不承载任何执行步骤、门禁或产物格式。两者冲突时以 SKILL.md 和仓库根 `../../shared/` 契约为准。
- **旧 skill 骨架已被取代并删除**：原独立仓库的 `skills/auto-test/`（SKILL.md + references + assets，version 0.1.0）已被本仓 `Test/auto-test/` 取代（后者含 Fidelity-Review 内嵌、shared 契约对齐、运行问题埋点）；归档时保留的旧骨架副本已随 `docs/auto-test-legacy/` 一起删除，需要追溯时查 git 提交 `b0b78b6`（提交时路径 `docs/auto-test-legacy/skills/auto-test/`）。
- **不改变 Skill 的注册与分发语义**：`governance/skill-registry.yaml` 只登记 `auto-test` → `Test/auto-test`（status=active、contractLevel=legacy-wrapper）；本目录只是该 Skill 目录内的资料子目录，不新增 Skill 条目、不改注册表与契约级别，随 Skill 目录一并分发，也不被契约校验当作 SKILL.md 正文。

## 三、引用与时效口径

- 正文里的 `.spec/...` 是**旧独立项目**当时的目录口径；本仓内指代对应资料时已改为同目录 `./...` 链接（如 `./竞品分析报告.md`），其余历史表述原样保留。
- 本目录是 2026-09-18 的研究快照：Star 数、市场数据、竞品活跃状态与定价均已过时，引用前先核当前事实；任何结论不得反过来覆盖 SKILL.md 的执行规则。
