> LEGACY COMPATIBILITY NOTICE: This file preserves historical material. The active Skill, Gate, state, artifact, and evidence rules are defined by `shared/skill-contract.md`, `shared/gate-policy.md`, `shared/anti-deadloop.md`, `shared/artifact-contract.md`, `governance/`, and `.spec/workflow.yaml`. 现行流程与边界见 [SKILL.md](SKILL.md)；旧流程全文见 references/legacy-skill.md。

# PRD-Design —— 工业级 PRD 生成 Skill（历史名称；canonical id：`prd-design`）

> 状态：✅ 定稿
> 术语与决策基准：[CONTEXT.md](CONTEXT.md)（术语表 + D-01~D-34）

## 一、定位与第一原则

Staff 级产品经理人设，把想法变成边界清晰、模块合理、流程闭环、验收可测的 PRD 交付包。

第一原则：先把需求考虑清楚、写清楚；度量、灰度、技术实现都是需求清楚之后的事。

## 二、核心特性

1. 两段式流水线：总览期收敛 7 点 → 总览两图 → 流程与范围 Gate；模块期澄清② → 模块图逐模块确认 → 字段方案 → 成文。全程询问 → 图确认 → 编写。
2. 域界铁律：禁数据库字段类型、API、控件、选型；负面清单见 tech-feasibility-guide。
3. 强制 Mermaid：总纲关联图 + 双向核对表，逐边闭环。
4. Gherkin 单源验收：每模块唯一权威章节 `AC-Mxx-nnn`，即 TDD 输入源。
5. 双 Gate + 回炉：范围 Gate / 终审 Gate + 模块内联自检 + 全局 Pass Gate。
6. 页面归并下沉：PRD 只在 §3.1 写功能区块，载体划分归 Prototype-Design。
7. PRD 速查表：全链路 L0 入口，六大索引 + 锚点，同版本归档。
8. 苏格拉底拷问门槛：grill-me 式决策树逐轮单步提问；边界与流程节点逐项拷问，未过「收敛证明」不落笔。

## 三、流程

```
想法 → 澄清①(7点·逐点拷问) → 泳道图+关联图 → overview → ◉ 范围 Gate
→ 逐模块（澄清②·逐节点拷问→模块图确认→字段方案→九章成文+自检）→ 全局 Pass Gate → ◉ 终审 → 归档
```

## 四、目录

```
prd-design/
├── SKILL.md
├── README.md
├── CONTEXT.md
├── references/   # prd-structure / mermaid-patterns / gherkin-guide / tech-feasibility-guide / socratic-grilling / case-library
├── assets/       # overview / module / quickref / eval 模板
└── .spec/PRD/VN/ # overview + 速查表 + NN_xxx + 验收结果详细说明
```

## 五、快速上手

1. 提出想法或说「写 PRD / 升级到 V2」。
2. 每次一个带推荐答案的问题，做选择题即可；回答后会被追问反方、边界与流程节点，直到该点收敛。
3. 拍板点：7 点收敛 → 图与范围 → 每模块字段方案 → 终审。
4. 模块 §9 验收标准可直接交给开发做 TDD。
