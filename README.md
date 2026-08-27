# tenger-skills

个人 Skills 仓库，用于编写和维护自己的 Claude Skills。

## 简介

本仓库用于沉淀可复用的「技能（Skill）」。每个 Skill 是一份结构化的指导文档，帮助 Claude 在特定场景下采用经过验证的方法与流程完成任务。

### 规划中的 Skill

| Skill | 目录 | 说明 | 状态 |
|-------|------|------|------|
| 竞品分析 | [competitive-analysis](./competitive-analysis) | 竞品调研、对比与分析 | 🚧 规划中 |
| 产品需求文档（PRD） | [prd-writing](./prd-writing) | PRD 编写 | 🚧 规划中 |

## 目录结构

```
tenger-skills/
├── README.md                  # 仓库说明（本文件）
├── competitive-analysis/      # 竞品分析 Skill
│   └── README.md              # 该 Skill 的结构大纲
└── prd-writing/               # 产品需求文档（PRD）Skill
    └── README.md              # 该 Skill 的结构大纲
```

## 什么是 Skill

Skill 是一个以 `SKILL.md` 为核心、可附带资源文件的目录。每个 Skill 通过 `description`（触发条件）被 Claude 自动识别，在匹配的场景下加载并遵循其中的方法。

一个标准的 Skill 目录结构如下：

```
skill-name/
├── SKILL.md        # 主文件（必需）：YAML 元数据 + 正文指令
├── references/     # 参考文档（按需加载）
├── assets/         # 输出模板 / 资源
└── scripts/        # 可执行脚本（可选）
```

> 各 Skill 的完整模块大纲见其目录下的 `README.md`。

## 开发流程

1. 在每个 Skill 目录的 `README.md` 中先列好结构大纲（当前阶段）
2. 逐步填充 `SKILL.md` 正文与资源文件
3. 用测试场景验证 Skill 能否正确触发与执行
4. 迭代优化直至满意

## 参考

- [Anthropic Skills 规范](https://agentskills.io/specification)
