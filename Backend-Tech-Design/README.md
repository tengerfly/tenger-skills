# Backend-Tech-Design —— 后端技术方案文档编写 Skill

> **状态**：✅ 定稿
> **定位**：后端技术专家，依据 PRD 与原型图，产出可落地、可 TDD 开发的后端技术方案文档包。

## 一、这是什么

一个由 **后端技术专家 / 技术架构师** 人设驱动的 Skill：把已定稿的 PRD 需求文档与原型图，翻译成**技术选型清晰、模块边界明确、每个模块可 TDD 开发**的后端技术方案文档包。

> 术语说明：TDD = **Technical Design Document（技术方案文档）**，是 `PRD-Design`（PRD 只写需求）的技术承接方；同时全程遵循 **Test-Driven Development（测试驱动开发）**——先写测试用例、再写代码。

## 二、核心设计

| 项 | 决定 |
|----|------|
| 名称 | `Backend-Tech-Design` |
| 输入 | 优先读项目 `.spec/` 已有 PRD（PRD-Design）+ 原型图（Prototype-Design），缺失回退用户指定 |
| 档位 | 每次必问：企业级生产 / 快速实现（推荐默认企业级） |
| 语言 | 无偏好，按需求特征推荐（高并发→Go，企业级→Java，AI→Python） |
| 产出 | 总技术文档（选型+架构图+模块边界+关联+表结构）+ 各模块技术方案（流程图+测试用例） |
| 测试用例 | Gherkin 场景 + 代码级用例骨架（承接 PRD 的 AC） |
| 浏览器 | 软检测：Playwright → browser-use → 其他浏览器工具，任一可用即查官方文档，全无则跳过不阻塞 |

## 三、流水线全景

```
输入解析(读PRD+原型 / 浏览器工具软检测) ──► 技术选型澄清(档位必问) ──► 总技术文档 ──► Scope Gate ──► 逐模块方案 ──► 全局一致性检查 ──► 归档到 .spec/
```

## 四、目录结构

```
Backend-Tech-Design/
├── SKILL.md                        # 主指令：流水线 + 技术选型澄清 + 模块边界 + TDD测试用例规范
├── README.md                       # 本文档
├── references/                     # 深度指南（按需加载）
│   ├── tdd-structure.md            # 技术方案结构范式（必须/可选章节 + 开关规则）
│   ├── tech-stack-guide.md         # 技术选型指南（语言/数据库/缓存/检索/队列/Docker + 档位差异）
│   ├── module-design-guide.md      # 模块技术方案编写指南（边界/流程图/TDD测试用例）
│   └── data-model-guide.md         # 表结构设计规范（字段要素/命名/索引/约束）
├── assets/                         # 输出模板
│   ├── overview-template.md        # 总技术文档模板（选型+架构图+模块边界+关联+表结构）
│   └── module-template.md          # 模块技术方案模板（方案+流程图+测试用例）
└── .spec/TDD/VN/          # 产出：overview.md + NN_xxx.md
```

## 五、快速上手

1. 触发方式：说「帮我写后端技术方案」「写 TDD 文档」「做技术设计」，并给出 PRD（+原型图）；
2. Skill 先问档位（企业级 / 快速，默认企业级），再按需求推荐语言与各组件选型；
3. 确认选型与模块边界后，生成总技术文档（含架构图、全部表结构）；
4. 逐模块生成技术方案（含流程图、TDD 测试用例）；
5. 全局一致性检查通过后归档 `.spec/TDD/VN/`。

## 六、与其它 Skill 的关系

```
PRD-Design（写需求）──► Prototype-Design（出原型）──► Prototype-Review（审原型）
        │                                                            │
        │                                                            ▼
        │                                            UI-UX-Design（出设计稿，⑥ 可选）
        │                                                            │
        │                                                            ▼
        │                                            UI-UX-Review（审设计稿，⑦ 可选跟随）
        │                                                            │
        └──────────── PRD-Review（审需求）            ▼
                                     Backend-Tech-Design（写后端技术方案，⑧）
```

- `PRD-Design` 产出 PRD（含 PRD 速查表），是 `Backend-Tech-Design` 的需求输入；
- `Prototype-Design` 产出低保真原型 + 布局清单；`UI-UX-Design` 产出设计稿（⑥ 可选，跳过时上游为原型评审产物）——帮助理解交互与页面结构；
- `Backend-Tech-Design` 是 PRD 域界铁律中「技术方案文档（TDD）」的承接方——PRD 不写数据库/接口/选型，这里才写。


