# Frontend-Dev —— 前端代码开发 Skill

> **状态**：✅ 定稿
> **定位**：前端开发专家，依据 PRD + 原型 + 后端 TDD + 前端 FTDD，把技术方案落地为可运行、高还原、模块化的前端代码工程（支持 monorepo 前后端同仓库 + 共享类型）。

## 一、这是什么

一个由 **前端开发专家 / 资深前端工程师** 人设驱动的 Skill：把已定稿的**前端技术方案（FTDD）**，翻译成**还原度高、模块化清晰、可直接运行**的前端代码工程（多端页面 + 组件 + hooks + 测试 + 运行说明）。

> 定位说明：`Frontend-Tech-Design` 只写「方案」（选型 / 页面清单 / 组件清单 / 目录结构 / fetch 对接 / 测试用例），本 Skill 只写「代码」——方案是施工图，代码是照图施工。**第一原则：还原度优先 · 模块化防重 · 测试先行 · 不确定即问 · 功能点即提交。**

## 二、核心设计

| 项 | 决定 |
|----|------|
| 名称 | `Frontend-Dev` |
| 人设 | 前端开发专家 / 资深前端工程师 |
| 输入 | 优先读项目 `.spec/` 已有 PRD（PRD-Design）+ 原型（Prototype-Design）+ 后端 TDD（Backend-Tech-Design）+ 前端 FTDD（Frontend-Tech-Design，核心），缺失回退用户指定 |
| 目标端 | 步骤 1 判定：web / app / 小程序；多端分工程分别产出 |
| 产出位置 | **步骤 1 用户提供**：目标目录 + git 地址；目录名用给定目录名或用户自定义名称（不套用按端命名约定），未提供则必问 |
| monorepo | **前后端同仓库**：按仓库 workspace 约定落位（前端子包）；接口请求/响应/枚举等**共享类型单一来源**（`packages/shared-types`），前端 `import type` 引用不重定义；根配置改动前必问 |
| 技术栈 | 优先从 FTDD 读选型，不重新选型；FTDD 缺失则补选型（档位 + 组件库 + 端选型必问）；覆盖端不符则阻塞 |
| 第一原则 | **还原度优先 · 模块化防重 · 测试先行 · 不确定即问 · 功能点即提交** |
| 架构 | 五层：页面容器 → 业务/基础组件 → hooks → api；依赖单向向下 |
| 模块化 | `features/<模块>/components/`（模块私有）+ `src/components/`（跨模块/基础） |
| 组件抽离铁律 | 模块内 ≥2 次复用 → `features/<模块>/components/`；两个模块共用 → 提升到 `src/components/` |
| 测试 | 测试先行，承接 FTDD 模块测试用例（TC-Mxx ↔ AC-Mxx，渲染/交互/数据流/边界/异常） |
| 还原校验 | Playwright 截图比对 → browser-use → 均不可用则跳过并提示，静态对照兜底 |
| 不确定即问 | 遇到不确定问题不自己发挥，停下来问用户；有选项则给出选项（含推荐项）让用户选（SKILL §八） |
| 开发计划/任务 | 开发前列「功能点」原子开发计划 → 生成开发任务清单（todo 面板 + `PROJECT.md`）；每完成一个功能点更新任务状态 |
| 进度文档 | `PROJECT.md`：基本情况 + 项目规则 + 开发计划与任务清单 + 关键决策 + 还原核对；断点续做先读它恢复进度与规则 |
| 提交策略 | 每完成一个功能点即 `git commit`（一次提交一件事，方便回滚）；**提交过 eslint + stylelint + commitlint，不绕过**；不擅自 push |
| 注释 | 简单易懂：简练中文一句话讲「为什么」，一行写完，复杂规则 ≤3 行；**方法/函数/hooks/组件有传参必写 `@param` 说明作用** |
| 命名规范 | 组件名**首字符大写**（PascalCase）；CSS class 用 `-` 连接（kebab-case）；方法/函数名**小驼峰**（camelCase） |
| 产出 | 可运行前端工程（多端页面 + 组件 + hooks + 测试 + README + PROJECT.md），落在用户指定目录（含 git 仓库） |

## 三、流水线全景

```
输入解析(读PRD+原型+TDD+FTDD+PROJECT.md / 判定端 / 确认产出目录+git / 浏览器工具检测) ──► 技术栈锁定(读FTDD·缺失补选型·不符阻塞)
        ──► 工程初始化(目录+依赖+基础设施+monorepo接入) ──► 原型还原基线+token提取 ──► Scope Gate
        ──► 生成开发计划与任务清单(功能点为原子 → todo + PROJECT.md) ──► 逐页面实现(测试先行·api→hooks→组件→页面容器)
        ──► 组件抽离落地检查 ──► 接口契约对齐(TDD+FTDD双向核对) ──► 全局一致性检查(含还原核对)
        ──► 交付(收口 PROJECT.md + 提交历史 + README)

※ 全程穿插「不确定即问」：遇不确定即停下来问用户并给选项，不自己发挥
※ 每个功能点完成 → 更新任务状态(todo+PROJECT.md) → 自检 → git commit(过 eslint+stylelint+commitlint)
※ 断点续做：先读 PROJECT.md 恢复进度与规则，从「未做/进行中」继续
```

## 四、目录结构

```
Frontend-Dev/
├── SKILL.md                        # 主指令：第一原则 + 流水线 + 端判定 + 产出位置 + monorepo/共享类型 + 组件抽离铁律 + 不确定即问 + 开发计划/任务 + 功能点提交 + 还原校验 + 代码/测试规范
├── README.md                       # 本文档
├── references/                     # 深度指南（按需加载）
│   ├── architecture-guide.md       # 前端分层与模块化规范（分层职责/依赖方向/组件抽离铁律/目录组织/hooks 优先）
│   ├── code-style-guide.md         # 前端代码编写规范（简洁性/命名/TS 类型/注释简单易懂+传参必注/SCSS token，React/TS 示例）
│   ├── test-guide.md               # 测试实现规范（测试先行/承接 FTDD 用例/五类覆盖/Vitest+RTL 配置）
│   ├── tech-stack-guide.md         # 各端工程落地骨架 + §六 提交门禁（eslint/stylelint/commitlint）+ §七 monorepo 落地
│   └── fidelity-guide.md           # 页面还原度校验（Playwright/browser-use/静态对照流程 + 差异分类）
├── assets/                         # 输出模板
│   ├── project-structure-template.md # 工程目录结构模板（对齐 FTDD §6 + 基础设施 + monorepo 落位 + 提交门禁文件 + 运行说明）
│   ├── module-code-template.md     # 页面/模块代码骨架模板（测试先行 + api/hooks/组件/页面容器 + 抽离 + 还原核对 + 更新任务 + 提交）
│   └── project-status-template.md  # PROJECT.md 模板（基本情况 + 项目规则 + 开发计划与任务清单 + 关键决策 + 还原核对）
```

> 产出位置不在此目录内：代码落在**用户在步骤 1 给定的目标目录 + git 地址**（目录名用给定目录名或用户自定义名称）。

## 五、快速上手

1. 触发方式：说「帮我写前端页面」「实现前端」「根据前端技术方案写代码」，并给出前端 FTDD（+ PRD / 原型 / TDD）+ **目标目录与 git 地址**；
2. Skill 先**读 `PROJECT.md`（若有，恢复进度与规则，断点续做）**，确认产出位置（目录 + git 地址，未提供则必问），判定目标端（web / app / 小程序）与仓库形态（单包 / monorepo），FTDD 存在则读选型（缺失才补选型：档位 + 组件库 + 端选型必问，覆盖端不符则阻塞）；
3. 搭工程骨架 + 全局基础设施（request / styles token / router / 通用 hooks / 错误边界 + monorepo 接入 + 提交门禁）+ 原型还原基线；
4. Scope 确认范围后，**列「功能点」原子开发计划 → 生成开发任务清单（todo 面板 + `PROJECT.md`）**；
5. 逐页面「测试先行」实现（先写测试 → api → hooks → 组件 → 页面容器）；**遇到不确定即停下来问用户并给选项**；
6. 每完成一个功能点 → **更新任务状态（todo + PROJECT.md）** → 自检 → `git commit`（过 eslint + stylelint + commitlint，一次提交一件事，不擅自 push）；
7. 执行组件抽离落地检查 + 接口契约对齐 + 全局一致性检查（含还原核对：Playwright / browser-use / 静态对照）；
8. 交付：代码在用户指定目录，收口 `PROJECT.md` + README 运行说明与关键决策记录。

## 六、与其它 Skill 的关系

```
PRD-Design（写需求）──► Prototype-Design（出原型）──► Backend-Tech-Design（写后端技术方案）
        │                       │                            │
        │                       └────────► Frontend-Tech-Design（写前端技术方案）◄──┘
        │                                                       │
        │                                                       ▼
        └───────────────────────────────────────────────────────► Frontend-Dev（写前端代码，本 Skill）
```

- `Frontend-Tech-Design` 产出前端技术方案（选型/页面清单/组件清单/目录结构/fetch 对接/测试用例），是 `Frontend-Dev` 的**施工图**；
- `Backend-Tech-Design` 产出后端接口清单，是 `Frontend-Dev` 的**接口契约源**；
- `Prototype-Design` 产出高保真原型，是 `Frontend-Dev` 的**还原目标**；
- `Backend-Dev` 与 `Frontend-Dev` 是「技术方案域界铁律」两端代码承接方——方案不写代码，这里才写。


