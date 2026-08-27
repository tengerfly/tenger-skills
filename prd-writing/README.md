# 产品需求文档（PRD）编写 Skill

> 状态：🚧 规划中 —— 本文件为结构大纲，具体实现待后续逐步完成。

## 一、Skill 简介

指导如何编写清晰、完整、可执行的产品需求文档（PRD），包括功能规格、用户故事、验收标准等。

## 二、标准目录结构（待搭建）

```
prd-writing/
├── SKILL.md                  # 主文件（必需）：元数据 + 核心指令
├── references/               # 参考文档（按需加载）
│   ├── prd-structure.md      # PRD 结构规范
│   └── user-story-guide.md   # 用户故事 / 验收标准写法
├── assets/                   # 输出模板
│   └── prd-template.md       # PRD 模板
└── scripts/                  # 可执行脚本（可选）
```

## 三、标准 Skill 应具备的模块（大纲）

### 1. SKILL.md 前置元数据（YAML Frontmatter）

| 字段 | 是否必需 | 说明 |
|------|---------|------|
| `name` | 必需 | 技能标识，仅字母 / 数字 / 连字符，如 `prd-writing` |
| `description` | 必需 | 触发条件，描述「何时使用」 |
| `compatibility` | 可选 | 所需工具 / 依赖 |

### 2. SKILL.md 正文模块

| 模块 | 作用 | 本 Skill 示例 |
|------|------|--------------|
| 概述 Overview | 核心原则 1–2 句 | 一份好 PRD 的标准 |
| 何时使用 When to Use | 触发条件 + 何时不用 | 编写 / 评审 PRD |
| 核心方法 Core Pattern | 关键写作流程 | 背景 → 目标 → 需求 → 验收 |
| 快速参考 Quick Reference | 速查表 | 常见章节清单 |
| 实现步骤 Implementation | 具体流程 | 逐步执行 |
| 常见错误 Common Mistakes | 易错点 + 修正 | 需求含糊、验收不可测 |

### 3. 资源目录模块

- **references/**：重型参考文档（PRD 结构规范、用户故事指南）
- **assets/**：输出模板（PRD 模板）
- **scripts/**：可执行脚本（可选）

## 四、实现计划（待补充）

> 大纲确认后，逐模块填充内容，并用测试场景验证触发与执行效果。
