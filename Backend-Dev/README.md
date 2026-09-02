# Backend-Dev —— 后端代码开发 Skill

> **状态**：✅ 定稿
> **定位**：后端开发专家，依据 PRD + 原型图 + 后端 TDD + 前端 FTDD，把技术方案落地为可运行、可维护的**微服务后端代码工程**（NestJS 优先 + Monorepo + 断点续做）。

## 一、这是什么

一个由 **后端开发专家 / 资深后端工程师** 人设驱动的 Skill：把已定稿的**后端技术方案（TDD）**，翻译成**可直接编译运行、长期可维护**的后端代码工程（微服务 + 分层 + 测试 + 运行说明）。

> 定位说明：`Backend-Tech-Design` 只写「方案」（选型 / 表结构 / 接口 / 模块边界 / 测试用例），本 Skill 只写「代码」——方案是施工图，代码是照图施工。
> **第一原则：维护性优先**（简洁易懂、模块化分明、注释简洁清晰）。
> **第二原则：不确定就问，给选择项**（遇到影响后续大量代码走向的不确定点，停下来让用户确定）。
> **第三原则：小步提交**（每完成一个功能点自动提交一次，提交前 eslint + commitlint 校验，便于精准回滚）。

## 二、核心设计

| 项 | 决定 |
|----|------|
| 名称 | `Backend-Dev` |
| 人设 | 后端开发专家 / 资深后端工程师 |
| 输入 | 优先读项目 `.spec/` 已有 PRD（PRD-Design）+ 原型（Prototype-Design）+ 后端 TDD（Backend-Tech-Design，核心）+ 前端 FTDD（Frontend-Tech-Design，契约），缺失回退用户指定 |
| 架构 | **微服务**：服务内四层分层（Controller → Service → Repository → Entity），服务间只走对外接口 |
| 后端主栈 | **TypeScript + NestJS 优先**；TDD 明确指定其它语言（Go/Java/Python）时才跟随 |
| 仓库形态 | **前后端同仓库 Monorepo**：`apps/web` + `apps/server-*` + `libs/shared`，pnpm workspace |
| 协作形态 | **多人协作（multi）**：服务边界清晰、约定先行、契约单一事实源 |
| 第一原则 | **维护性优先**：代码简洁易懂、模块化分明、注释简洁清晰 |
| 第二原则 | **不确定就问，给选择项**：能给出选择项的必须给，一次只问一个关键问题 |
| 测试 | 测试先行，承接 TDD 测试用例（正向/边界/异常/幂等/并发五类），Jest 优先 |
| 提交 | 每完成一个功能点自动 git commit（便于回滚），提交前 eslint + commitlint 校验（Conventional Commits） |
| 计划与进度 | 开发前列开发计划（功能点为原子）→ 生成任务清单 → 完成一个更新一个；维护 PROJECT.md（基本情况+规则+进度）+ PLAN.md（任务状态），支持断点续做 |
| 注释 | 讲「为什么」；方法有传参必须逐个写明每个参数的作用与约束 |
| 产出 | 可运行后端微服务代码工程（Monorepo + 服务 + 迁移 + 测试 + README） |
| 浏览器 | browser-use 可用则查框架官方文档/版本，不可用则跳过（不阻塞编码） |

## 三、流水线全景

```
续做检测(读PROJECT.md/PLAN.md) ──► 输入解析(读PRD+原型+TDD+FTDD / 技术栈锁定·默认NestJS微服务)
        ──► 服务拆分确认(选择项让用户定) ──► 开发计划(功能点为原子·生成任务清单·写PROJECT/PLAN)
        ──► 工程初始化(Monorepo+依赖+基础设施层) ──► 数据模型落地(表→Entity+迁移)
        ──► Scope Gate ──► 逐功能点实现(测试先行·四层·完成一个更新一个任务·每功能点提交)
        ──► 接口契约对齐(TDD+FTDD双向核对) ──► 全局一致性检查 ──► 归档+更新进度（项目目录）
```

> 全程贯穿「澄清协议」：遇到不确定的选型/边界/契约/命名，停下来给选择项让用户定，不擅自拍板。

## 四、目录结构

```
Backend-Dev/
├── SKILL.md                        # 主指令：双原则 + 流水线 + 澄清协议 + 技术栈锁定 + 微服务/分层/代码/接口/测试规范
├── README.md                       # 本文档
├── references/                     # 深度指南（按需加载）
│   ├── architecture-guide.md       # 微服务架构与模块化规范（服务内四层/服务间边界/Monorepo/数据模型）
│   ├── code-style-guide.md         # 代码编写规范（简洁性/命名/注释/错误处理/统一响应，多语言示例）
│   ├── test-guide.md               # 测试实现规范（测试先行/五类覆盖/分层测试策略，NestJS 示例）
│   └── tech-stack-guide.md         # NestJS 微服务工程落地骨架（Monorepo 目录+依赖+分层示例+其它语言备选）
├── assets/                         # 输出模板
│   ├── project-structure-template.md # Monorepo 工程目录结构模板（前后端同仓库+微服务）
│   ├── module-code-template.md     # 服务/模块代码骨架模板（测试先行+四层+注释+接口契约，NestJS 示例）
│   ├── project-status-template.md  # 项目说明文档（PROJECT.md）模板（基本情况+规则+进度）
│   └── plan-template.md            # 开发计划/任务（PLAN.md）模板（功能点清单+状态跟踪）
└── <项目目录>/                      # 产出：可运行后端微服务代码工程（代码 + PROJECT.md + PLAN.md + README）
```

## 五、快速上手

1. 触发方式：说「帮我写后端代码」「实现后端」「根据技术方案开发」，并给出后端 TDD（+ 前端 FTDD）；
2. Skill 先检测是否续做（读 PROJECT.md / PLAN.md），再锁定技术栈（TDD 缺失/未明确则默认 NestJS 微服务，关键选型用选择项确认）；
3. 列开发计划（功能点为原子）→ 生成任务清单，写 PROJECT.md + PLAN.md；
4. 确认服务拆分与技术栈落地方式后，搭 Monorepo 骨架 + 基础设施层 + 数据模型层；
5. 逐功能点「测试先行」实现（先写测试 → Repository → Service → Controller），每完成一个功能点更新 PLAN.md 任务状态 + 跑 eslint/commitlint 校验 + 自动提交；
6. 对齐前后端接口契约，做全局一致性检查（可编译 / 分层清晰 / 注释完整 / 测试可跑 / 服务边界无侵入）；
7. 归档到**项目目录**，更新 PROJECT.md 进度，附 README 运行说明。

## 六、与其它 Skill 的关系

```
PRD-Design（写需求）──► Prototype-Design（出原型）──► Backend-Tech-Design（写后端技术方案）
        │                       │                            │
        │                       └────────► Frontend-Tech-Design（写前端技术方案）◄──┘
        │                                                       │
        └───────────────────────────────────────────────────────┤
                                                                ▼
                                              Backend-Dev（写后端代码，本 Skill）
```

- `Backend-Tech-Design` 产出后端技术方案（选型/表结构/接口/模块边界/测试用例），是 `Backend-Dev` 的**施工图**，模块边界 = 微服务拆分候选；
- `Frontend-Tech-Design` 产出前端技术方案（fetch 接口对接），是 `Backend-Dev` 的**接口契约验收线**；
- `Backend-Dev` 是技术方案域界铁律中「后端怎么实现」的承接方——方案不写代码，这里才写。


