# Frontend-Tech-Design —— 前端技术方案文档编写 Skill

> **状态**：✅ 定稿
> **定位**：前端技术专家，依据 PRD + 原型图 + 后端 TDD，产出可落地、可 TDD 开发的前端技术方案文档包。

## 一、这是什么

一个由 **前端技术专家 / 前端架构师** 人设驱动的 Skill：把已定稿的 PRD 需求文档、低保真原型（Prototype-Design 产出）与后端技术文档（TDD），翻译成**技术选型清晰、页面组件划分明确、每个模块可 TDD 开发**的前端技术方案文档包。

> 术语说明：FTDD = **Frontend Technical Design Document（前端技术方案文档）**，是 `PRD-Design`（PRD 只写需求）与 `Backend-Tech-Design`（后端技术方案）的前端承接方；同时全程遵循 **Test-Driven Development（测试驱动开发）**——先写测试用例、再写代码。

## 二、核心设计

| 项 | 决定 |
|----|------|
| 名称 | `Frontend-Tech-Design` |
| 输入 | 优先读项目 `.spec/` 已有 PRD（PRD-Design）+ 原型（Prototype-Design）+ 后端 TDD（Backend-Tech-Design），缺失回退用户指定 |
| 固定技术栈 | pnpm + Vite + TypeScript + React（hooks 为主）+ 原生 fetch + CSS 预编译 + Vitest |
| 档位 | 每次必问：企业级生产 / demo（推荐默认企业级） |
| 组件库 | 每次必问，让用户决定 |
| 主题/国际化 | 每次必问：是否实现暗黑模式、主题切换、国际化 |
| 浏览器兼容性 | 每次必问：不指定则用 Vite 默认 |
| 内容维度 | 总文档 10 方面 + 模块文档 10 方面（先定维度模板，逐模块套用） |
| 产出 | 总技术文档（选型+架构图+页面清单+组件清单+目录结构+模块边界+全局规范）+ 各模块技术方案（组件拆分+hooks+fetch 对接+测试用例） |
| 测试用例 | 组件测试 + hooks 测试（Vitest + React Testing Library，承接 PRD 的 AC） |
| 浏览器工具 | 硬性预检 Playwright → browser-use → 其他（如 agent-browser），任一可用即用；全无则**直接报错提醒安装**（不跳过） |

## 三、流水线全景

```
输入解析(读PRD+原型+后端TDD / 浏览器工具检测·全无报错) ──► 技术选型澄清(档位+组件库+主题+国际化+兼容性必问)
        ──► 总技术文档 ──► Scope Gate ──► 逐模块方案 ──► 全局一致性检查 ──► 归档到 .spec/
```

## 四、目录结构

```
Frontend-Tech-Design/
├── SKILL.md                        # 主指令：内容维度 + 流水线 + 技术选型澄清 + 页面组件/hooks/fetch/CSS/测试规范
├── README.md                       # 本文档
├── CONTEXT.md                      # 术语对齐源 + 决策日志
├── references/                     # 深度指南（按需加载）
│   ├── doc-structure.md            # 技术方案文档结构指南（总文档 10 方面 + 模块文档 10 方面）
│   ├── tech-stack-guide.md         # 前端技术选型指南（档位差异 + 组件库/状态管理/路由/测试对比 + 浏览器兼容性）
│   ├── component-design-guide.md   # 组件与 hooks 设计规范（分层/拆分原则/hooks 优先）
│   ├── fetch-guide.md              # fetch 请求封装规范（完整实例 + 类型 + 业务方法）
│   ├── css-guide.md                # CSS 架构规范（Sass/模块化/全局抽离/主题）
│   ├── module-design-guide.md      # 模块技术方案编写指南（边界/页面组件拆分/数据流/自检清单）
│   └── test-guide.md               # 前端测试用例规范（Vitest + RTL + 覆盖矩阵）
├── assets/                         # 输出模板
│   ├── overview-template.md        # 总技术文档模板（选型+架构图+页面组件清单+目录结构+模块边界+全局规范）
│   └── module-template.md          # 模块技术方案模板（组件拆分+hooks+fetch 对接+测试用例）
└── .spec/FTDD/VN/          # 产出：overview.md + NN_xxx.md
```

## 五、快速上手

1. 触发方式：说「帮我写前端技术方案」「写 FTDD 文档」「做前端架构设计」，并给出 PRD（+原型图 +后端 TDD）；
2. Skill 先问档位（企业级 / demo，默认企业级），再问组件库、暗黑模式/主题、国际化、浏览器兼容性；
3. 确认选型与模块边界后，生成总技术文档（含架构图、页面清单、组件清单、目录结构、fetch/CSS/hooks 全局规范）；
4. 逐模块生成技术方案（含组件拆分、hooks 数据流、fetch 接口对接、测试用例）；
5. 全局一致性检查通过后归档 `.spec/FTDD/VN/`。

## 六、与其它 Skill 的关系

```
PRD-Design（写需求）──► Prototype-Design（出原型）──► Prototype-Review（审原型）
        │                       │                            │
        │                       │                            ▼
        │                       │            UI-UX-Design（出设计稿，⑥ 可选）
        │                       │                            │
        │                       │                            ▼
        │                       │            UI-UX-Review（审设计稿，⑦ 可选跟随）
        │                       │                            │
        ├──► Backend-Tech-Design（写后端技术方案，⑧）◄────────┘
        │                       │
        └── PRD-Review（审需求） └──► Frontend-Tech-Design（写前端技术方案，⑨）
```

- `PRD-Design` 产出 PRD（含 PRD 速查表），是前端方案的需求输入；
- `Prototype-Design` 产出低保真原型 + 布局清单，前端页面清单、组件拆分必须与原型一一对应；
- `Backend-Tech-Design` 产出后端技术方案（含接口清单），前端 fetch 封装与接口对接的唯一依据（TDD → FTDD 硬串行）；
- `Frontend-Tech-Design` 是 PRD 域界铁律中「前端怎么设计与实现」的承接方——PRD 不写控件/选型，这里才写。


