# Backend-Tech-Design —— 后端技术方案文档编写 Skill

> 状态：✅ 定稿
> 定位：依据 PRD 与原型图，产出可落地、可评审、可 TDD 开发的后端技术方案包。TDD = Technical Design Document，也是 Test-Driven Development 的输入源。

## 一、边界与输入

- 上游：`.spec/PRD/`（PRD-Design）+ 原型（Prototype-Design）+ 设计稿（可选，UI-UX-Design）；缺失回退用户指定。
- 域界：PRD 不写的数据库/接口/选型，这里写；前端方案归 Frontend-Tech-Design。
- 档位：每次必问，默认企业级生产；每个决策点过收敛证明（失败/涨 10 倍/漏项 + 用户认可）才定稿。
- 语言：按需求推荐（高并发→Go、企业级→Java、AI→Python）。
- 浏览器：软检测（Playwright → browser-use → 其他），全无跳过不阻塞。

## 二、核心流程

```
解析 PRD+原型 → **非功能需求澄清**（规模/延迟/一致性/合规/可用性，设计输入先于选型）→ 选型澄清（逐点拷问后一次定全）→ 总技术文档 → ◉ Scope Gate
→ 逐模块方案（流程图 + TDD 用例）→ 全局一致性 → 归档 .spec/TDD/VN/
```

开发期零选型决策：语言/服务拆分/通信/ORM/包管理/DB/缓存/队列/测试/部署全部在方案期敲定，Backend-Dev 照图施工。

## 三、产出

- `overview.md`：选型总览 + 架构图 + 模块边界 + 关联图 + 全部表结构 + 可选章节。
- `NN_xxx.md`：模块边界 + 依赖 + 流程图 + 接口/服务设计 + 数据模型（引用总文档）+ 实现细节与决策 + TDD 测试用例。
- 落盘 `.spec/TDD/VN/`。

## 四、目录

```
../backend-tech-design/
├── SKILL.md
├── README.md
├── CONTEXT.md                 # 术语 + 决策日志
├── references/                # tdd-structure / tech-stack / decision-rules / module-design / data-model / socratic-grilling / case-library/
├── assets/                    # overview-template / module-template
└── .spec/TDD/VN/              # 产出
```

## 五、快速上手

1. 用户给出 PRD（±原型/设计稿）说「写后端技术方案 / 写 TDD / 做技术设计」。
2. 问档位（默认企业级）→ 按需求推荐语言与组件；每点追问失败/涨 10 倍/漏项与边界，收敛后才算定稿。
3. 确认选型与模块边界 → 生成总技术文档。
4. 逐模块生成方案（含流程图、TDD 用例）。
5. 全局一致性通过后归档 `.spec/TDD/VN/`。

## 六、上下游

PRD-Design → Prototype-Design → （评审/设计稿链路）→ Backend-Tech-Design → Backend-Dev。

- PRD/原型是需求与结构输入；方案是 PRD 域界的后端技术承接方。
- Tech-Review 的评审任务由本 skill 消费并回填。