# UI-UX-Design —— UI/UX 设计稿生成 Skill（Superdesign 底座）

把「PRD + 布局清单 + 低保真原型」变成布局零改动、去 AI 味、风格统一的设计稿 HTML。

- 角色：设计总监 + Superdesign 编排器；视觉稿生成本体由 Superdesign CLI 执行。
- 上游：Prototype-Design 的布局清单（载体级）+ 低保真原型 HTML（区块结构实物）。
- 流程：环境检测 Gate → 输入校验 + 任务清单 → 风格情报 → 风格决策 Gate → 设计规范 Gate → 逐页生成 → 质量门禁 → 归档 `.spec/设计稿/`。

## 目录

| 文件 | 说明 |
|---|---|
| SKILL.md | 9 步 3 Gate / 分工 / 迭代路由 / 成本红线 / 去 AI 味 12 条 |
| CONTEXT.md | 术语 + D-01~D-18 |
| assets/ | layout-inventory-contract / design-task-list / style-proposal / design-system / archive-readme |
| references/ | superdesign-sop / design-review-gate / open-source-design-systems / style-case-library / case-library/（总索引 + design-systems/layouts/components/interactions/flows/a11y）/ patterns/ |

## 硬依赖

```bash
npm install -g @superdesign/cli@latest
superdesign login
```

CLI 已装 + 账号已授权 + SOP 可读，缺一阻塞。

## 关键约定

- 布局零改动：只改好不好看，结构问题回 Prototype-Design。
- 规范先行：design-system.md 未确认，不生成。
- 额度即预算：变体/花钱动作由用户裁决；确定性修正走直编。
- 双目录：`.superdesign/` 工作目录；`.spec/设计稿/` 交付目录。