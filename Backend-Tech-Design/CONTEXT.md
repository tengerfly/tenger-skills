# CONTEXT.md —— Backend-Tech-Design Skill 领域术语与决策记录

> 本文件是 `Backend-Tech-Design` Skill 的**术语对齐源**与**决策日志**。
> SKILL.md / assets / references 中出现的所有概念必须与本文件一致；
> 每敲定一个概念，必须同步更新本文件。

---

## 一、角色定位（Who We Are）

- **Skill 人设**：后端技术专家 / 技术架构师（Backend Tech Expert / Architect）；
- **核心目标**：依据已定稿的 PRD 需求文档与原型图，产出**可落地、可评审、可 TDD 开发**的后端技术方案文档包（总技术文档 + 各模块技术方案）；
- **铁律（Domain Boundary）**：本 skill 是 PRD 域界铁律中「技术方案」的**承接方**——PRD 不写的数据库 / 接口 / 选型，这里才写；只覆盖后端，纯前端方案归 `Frontend-Tech-Design`。

## 二、术语表（Glossary）

| 术语 | 英文/Key | 权威定义 | 易混淆概念排除 |
|---|---|---|---|
| TDD（技术方案文档） | Technical Design Document | 本 skill 产出的技术方案文档包（overview.md + NN_xxx.md），落 `.spec/TDD/VN/` | ❌ 与 Test-Driven Development（测试驱动开发）同缩写不同义——本 skill 两者都用：产出 TDD 文档 + 全程 TDD 开发流程（先写测试用例再写代码） |
| 档位 | Tier | 技术选型的两档：**企业级生产**（集群/分库分表/监控告警/K8s，默认推荐）/ **快速实现**（单机/docker-compose/MVP）。每次必问 | ❌ 不是项目规模（是工程成熟度档位） |
| 总技术文档 | overview.md | 阶段一产物：选型总览 + 系统架构图 + 模块边界 + 模块关联关系图 + **全部表结构** + 可选章节（缓存/队列/检索/规范/部署等） | ❌ 不是模块文档（模块方案在 NN_xxx.md） |
| 模块技术方案 | Module Design | 逐模块产物：边界（应做/不应做）+ 上下游依赖 + 核心流程图 + 接口/服务设计 + 数据模型（引用总文档表）+ TDD 测试用例 | ❌ 不重复定义总文档已定的表结构（只引用） |
| Scope 确认 Gate | Scope Gate | 步骤 4 强制暂停：技术选型 + 模块边界 + 表结构预览一并呈现，用户确认「选型与边界无误」才放行 | ❌ 不是归档门禁（是生成模块方案前的放行关卡） |
| 负向边界 | Negative Boundary | 每个模块必须写「不应该做什么」——模块间不打架的保证，与 PRD 模块划分对齐但聚焦技术职责 | ❌ 不是功能清单（是职责禁区） |
| 浏览器软检测 | Soft Browser Detection | Playwright → browser-use → 其他浏览器工具三级检测；任一可用即用于查阅选型官方文档与版本兼容性；**全无则跳过，不阻塞**（选型基于内置知识） | ❌ 不是硬依赖（对照根 README 浏览器两级策略的「软检测」组） |
| 评审任务清单回填 | Review Task List Write-back | 步骤 1 检测 `.spec/技术方案评审/任务清单.md` 归本 skill 的 `已确认` 任务纳入修改；步骤 7 修完回填 `已修复` + 修改说明 | ❌ 不是本 skill 产出任务清单（清单由 Tech-Review 产出，本 skill 只消费回填） |
| AC 追溯 | AC Traceability | 测试用例标注对应 PRD 的 AC 编号（`AC-Mxx-nnn`），保证需求 ↔ 测试双向可溯 | ❌ 不是重新定义 AC（AC 由 PRD-Design 单源定义） |

## 三、决策日志（Decision Log）

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 2026-09-05 | 模式④自身体检发现的 3 条当场修复：① 新建本 CONTEXT.md 补齐仓库三件套约定（SKILL + README + CONTEXT + assets + references）；② README.md 浏览器行 + 流水线行从「browser-use 单工具」旧表述改为三级软检测（Playwright → browser-use → 其他），与 SKILL.md 步骤 1 / description / 根 README 软检测组口径一致；③ SKILL.md 步骤 1 标题同步改「浏览器工具检测」；④ README「与其它 Skill 的关系」图从旧 11 节点链更新为 14 节点链（补 Prototype-Review / UI-UX-Design / UI-UX-Review 环节，上游对齐根 README mermaid `UIR --> BTD`） | 体检维度五·跨位置同步（P1×3）+ 三件套缺失（P1）；经用户授权「后续问题一律当场修」 | ✅ 已确认 |

## 四、待决问题清单（Open Questions）

> 无待决项。
