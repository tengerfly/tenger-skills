# Backend-Dev —— 后端代码开发 Skill

> 状态：✅ 定稿
> 定位：后端开发专家，依据 PRD + 原型 + 后端 TDD + 前端 FTDD，把技术方案落地为可运行、可维护的微服务后端代码工程（NestJS 优先 + Monorepo + 断点续做）。

## 一、边界

- `Backend-Tech-Design` 写方案（选型/表结构/接口/模块边界/测试用例）；本 Skill 只写代码——方案是施工图，代码照图施工。
- 原则：维护性优先；不确定就问并给选项；小步提交（功能点一次提交，提交前 eslint + commitlint）。

## 二、核心设计

| 项 | 决定 |
|---|---|
| 人设 | 后端开发专家 / 资深后端工程师 |
| 输入 | `.spec/PRD/`、`.spec/原型/`、`.spec/TDD/VN/`（核心）、`.spec/FTDD/VN/`（契约）；缺失回退用户指定 |
| 架构 | 微服务；服务内四层（Controller → Service → Repository → Entity），服务间只走对外接口 |
| 主栈 | TypeScript + NestJS 优先；TDD 明确其它语言（Go/Java/Python）时跟随 |
| 仓库 | 前后端同仓 Monorepo：apps/web + apps/server-* + libs/shared，pnpm workspace |
| 测试 | 测试先行，承接 TDD 用例（正向/边界/异常/幂等/并发），Jest 优先 |
| 提交 | 一功能点一 commit（Conventional Commits），提交前 eslint + commitlint |
| 跟踪 | PROJECT.md（情况/规则/进度）+ PLAN.md（任务状态），支持断点续做 |
| 产出 | 可运行后端微服务代码工程（代码 + 迁移 + 测试 + README） |

## 三、流水线

```
续做检测+输入解析+技术栈锁定（S1，三路判定）→ 服务拆分确认 → 开发计划（功能点原子）
→ 工程初始化（Monorepo+基础设施） → 数据模型（表→Entity+迁移） → ◉ Scope Gate
→ 逐功能点实现（测试先行·四层·更新任务·提交） → 契约对齐 → 全局一致性 → 归档
```

全程遇到不确定的选型/边界/契约/命名，给选择项让用户定，不擅自拍板。

## 四、目录

```
Backend-Dev/
├── SKILL.md                    # 主指令
├── README.md                   # 本文档
├── CONTEXT.md                  # 术语源 + 决策日志
├── references/                 # 深度指南（按需加载）
│   ├── architecture-guide.md   # 架构与模块化
│   ├── code-style-guide.md     # 代码规范
│   ├── test-guide.md           # 测试规范
│   ├── tech-stack-guide.md     # 工程落地骨架
│   ├── decision-rules.md       # 编码层工程决策规则
│   └── case-library/           # 语言规范/API安全/质量工程化/同行样本
├── assets/                     # 输出模板
│   ├── project-structure-template.md
│   ├── module-code-template.md
│   ├── project-status-template.md
│   └── plan-template.md
└── <项目目录>/                  # 代码产出（代码 + PROJECT.md + PLAN.md + README）
```

## 五、快速上手

1. 用户给出后端 TDD（±前端 FTDD）并说「帮我写后端代码 / 实现后端 / 根据技术方案开发」。
2. 先判续做（读 PROJECT.md / PLAN.md），再锁技术栈（TDD 缺失默认 NestJS 微服务，关键选型用选项确认）。
3. 列开发计划（功能点原子）→ 写 PROJECT.md + PLAN.md。
4. 确认服务拆分与技术栈落地后搭骨架 + 基础设施 + 数据模型。
5. 逐功能点测试先行实现，完成即更新 PLAN 并校验提交。
6. 对齐契约，跑全局一致性，归档项目目录并更新 PROJECT.md。

## 六、上下游关系

```
PRD-Design → Prototype-Design → Backend-Tech-Design ─┐
                                Frontend-Tech-Design ─┴→ Backend-Dev（本 Skill）
```

- `Backend-Tech-Design`：施工图；模块边界 = 微服务拆分候选。
- `Frontend-Tech-Design`：接口契约验收线（fetch 对接）。
- `Backend-Dev` 是技术方案域界中「后端怎么实现」的承接方。
- 下游：Code-Review（评审回退修改方，承接 `.spec/代码评审/任务清单.md`）。