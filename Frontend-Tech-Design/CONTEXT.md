# CONTEXT.md —— Frontend-Tech-Design Skill 领域术语与决策记录

> 本文件是 `Frontend-Tech-Design` Skill 的**术语对齐源**与**决策日志**。
> SKILL.md / assets / references 中出现的所有概念必须与本文件一致；
> 每敲定一个概念，必须同步更新本文件。

---

## 一、角色定位（Who We Are）

- **Skill 人设**：前端技术专家 / 前端架构师（Frontend Tech Expert / Architect）；
- **核心目标**：依据已定稿的 PRD 需求文档、低保真原型与后端技术文档（TDD），产出**可落地、可评审、可 TDD 开发**的前端技术方案文档包（总技术文档 + 各模块技术方案）；
- **铁律（Domain Boundary）**：本 skill 是 PRD 与后端 TDD 的**前端承接方**——PRD 不写的页面/组件/hooks/路由/状态/请求封装/样式架构，这里才写；只覆盖前端，后端方案归 `Backend-Tech-Design`。

## 二、术语表（Glossary）

| 术语 | 英文/Key | 权威定义 | 易混淆概念排除 |
|---|---|---|---|
| FTDD | Frontend Technical Design Document | 本 skill 产出的前端技术方案文档包（overview.md + NN_xxx.md），落 `.spec/FTDD/VN/` | ❌ 与 Test-Driven Development 同缩写不同义——本 skill 产出 FTDD 文档 + 全程 TDD 开发流程 |
| 固定技术栈 | Fixed Stack | 不询问直接采用：pnpm + Vite + TypeScript + React 18+（hooks 为主）+ 原生 fetch + Sass/SCSS + Vitest/RTL | ❌ 不是可选项（固定）；用户可选项只有：档位/组件库/暗黑/国际化/兼容性/状态管理/路由 |
| 档位 | Tier | 两档：企业级生产 / demo，每次必问（默认企业级） | ❌ 与 Backend-Tech-Design 的「快速实现」措辞不同（前端叫 demo），语义同级 |
| 内容维度 | Content Dimensions | 总文档 10 方面 + 模块文档 9 方面的固定骨架；逐模块套用同一套维度模板缺一不可 | ❌ 不是章节自由发挥（模板先定维度再填内容） |
| 低保真原型 | Low-Fidelity Prototype | Prototype-Design 产出的可点击 HTML 原型（+ 布局清单），是页面清单与组件拆分的直接输入，页面组件必须与原型一一对应 | ❌ 不是高保真设计稿（那是 UI-UX-Design 的产物，可选输入） |
| 接口契约单源 | API Contract Single Source | 后端 TDD 的接口清单是前端 fetch 封装与接口对接的**唯一依据**，前端不得自造接口 | ❌ 不是前端自定义接口（防前后端契约漂移） |
| 浏览器硬检测 | Hard Browser Detection | Playwright → browser-use → 其他三级检测；任一可用即用于核验组件库/框架官方文档与版本兼容性；**全无则报错提醒安装，不跳过** | ❌ 不是软检测（对照根 README 浏览器两级策略的「硬依赖」组） |
| hooks 数据流 | Hooks Data Flow | 模块技术方案的核心维度：自定义 hooks 承载业务逻辑，组件只做渲染，数据流向 hooks → 组件单向 | ❌ 不是 class 组件时代的数据流（固定 hooks 为主） |

## 三、决策日志（Decision Log）

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 2026-09-05 | 模式④自身体检发现的 4 条当场修复：① 新建本 CONTEXT.md 补齐仓库三件套约定；② SKILL.md description + 正文 + README 共 3 处「高保真原型图」→「低保真原型（Prototype-Design 产出）」，对齐仓库术语体系（Prototype-Design 为低保真）；③ README「与其它 Skill 的关系」图从旧 11 节点链更新为 14 节点链（补 Prototype-Review / UI-UX-Design / UI-UX-Review 环节） | 体检维度一·术语一致（P0）+ 维度五·跨位置同步（P1×2）+ 三件套缺失（P1）；经用户授权「后续问题一律当场修」 | ✅ 已确认 |
| D-02 | 2026-09-05 | 心法优化（注入心法2 + 心法3）：① 心法2「做减法」——新增 §5.7 做减法铁律（demo 档不引入 i18n/主题/复杂状态/权限路由；不为「将来可能复用」提前抽组件/hooks——等复用真出现 ≥2 处再抽；每项选型给「为什么现在就需要」）；② 心法3「讨论先行」——步骤 4 Scope Gate 补「主动邀请抬杠」；③ README 目录结构补 CONTEXT.md 行 | 用户要求按《Vibe Coding 高效能秘籍》心法全面优化 skill；Frontend-Tech-Design 属「规划类 + 开发方案类」注入心法2（做减法）+ 心法3（讨论先行），其档位机制/必问选型/Scope Gate/TDD 已内建 | ✅ 已确认 |

## 四、待决问题清单（Open Questions）

> 无待决项。
