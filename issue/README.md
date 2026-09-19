# issue/ —— 问题池（唯一事实源）

Skill-Optimizer 的核心数据：各 skill 运行中暴露的问题与优化点，长期积累。

## 结构

`issue/<skill名称>/<日期目录>/<问题文件>`

- 每个 skill 一个文件夹（以 skill 目录名命名，如 `PRD-Design/`）
- 每天一个子文件夹（`YYYY-MM-DD`）
- 每个问题一个文件（`<序号>-<简短标题>.md`），模板见 `Skill-Optimizer/assets/issue-template.md`

```
issue/
├── Skill-Optimizer/
│   └── 2026-09-04/
│       └── 01-xxx.md
└── Prototype-Design/
    └── 2026-09-04/
        ├── 01-xxx.md
        └── 02-xxx.md
```

## 写入方

- **各 skill 埋点**（主通道）：执行收尾自查上报，规则见 `Skill-Optimizer/references/instrumentation-guide.md`
- **Skill-Optimizer 兜底 / 挖掘**：用户喊「记个问题 / 复盘」、或从 `chats/` 挖掘确认后落盘
- **Skill-Optimizer 体检**：模式④ 体检发现、经用户裁决「记 issue」的问题（来源填「体检」）

## 问题字段与状态机

- 字段：等级 `P0/P1/P2` + 标签（10 个预定义枚举）+ 优化状态
- 状态机：`待处理 → 处理中 → 已沉淀 / 已忽略`；「已沉淀」必填沉淀目标 + 沉淀位置

## 问题数据流总览（2026-09-19 收敛约定）

原始问题**入口唯一**，反哺**出口分工**——同一问题只进一个入口、反哺只写一个出口，禁止跨池重复记同一件事：

| 层 | 入口（原始问题只进这里） | 出口（综合分析后按类型反哺） |
|---|---|---|
| skill 层 | **本池 `issue/`**（skill 运行问题唯一 intake） | ① 流程缺陷 → 改对应 SKILL.md 主流程 REQUIRED 位 / 错误表；② 评审检出力 → 该评审 skill `references/known-issue-patterns.md`；③ 类别级代码错误 → `bug-patterns/`；④ 用户偏好信号 → `evolution/` |
| 项目层 | `<项目>/.spec/问题日志.md`（一行索引台账）+ 各评审任务清单（详情单一事实源不变） | 跨项目综合分析后：skill 层出口同上；组件资产缺陷 → skills-knowledge `asset-library/anti-patterns/` 或 `cases/failure/` |
| 原材料 | `chats/`（待挖掘聊天记录） | 挖掘确认后落 `issue/` |

- **定期综合分析**输入 = 本池 + 各项目 `.spec/问题日志.md` + `evolution/信号/`；输出 = 上表出口的反哺改动（对 Skill-Optimizer 说「综合分析问题日志」触发）。
- 项目问题日志格式模板：`shared/templates/problem-log-template.md`。
