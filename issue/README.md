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
└── PRD-Design/
    └── 2026-09-05/
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
