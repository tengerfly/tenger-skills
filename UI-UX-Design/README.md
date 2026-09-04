# UI-UX-Design —— UI/UX 设计稿生成 Skill（Superdesign 底座）

把「PRD + 布局清单 + 低保真原型」变成**布局零改动、去 AI 味、风格统一**的设计稿级 HTML。

- **角色**：设计总监 + Superdesign 编排器——管标准、决策、门禁、归档；视觉稿生成本体由 Superdesign 底座执行（CLI 驱动，画布迭代）。
- **上游**：`Prototype-Design`（重构后）产出**双输入**——「布局清单」（载体级：载体划分 + 宿主/入口/出口，不含页内区块级拆解）与「低保真原型 HTML」（页内区块结构实物）；本 skill 定义其输入契约（`assets/layout-inventory-contract.md`），对齐 D-10 双输入契约。
- **核心流程**：环境检测 Gate → 布局清单校验 + 设计任务清单 → 风格情报 → **风格决策 Gate**（三套差异化方案，默认零额度）→ **设计规范 Gate**（生成前沉淀 Design System，用户确认）→ 逐页生成（Superdesign）→ **质量门禁**（布局零改动 / 规范一致性 / 反 AI 味 / 文案保真）→ 归档 `.spec/设计稿/`。

## 目录

| 文件 | 说明 |
|---|---|
| `SKILL.md` | 核心标准：流水线 9 步 3 Gate / 分工模型 / 迭代路由 / 成本红线 / 去 AI 味 12 条 |
| `CONTEXT.md` | 术语表 + 决策日志（D-01~D-09）+ 待决问题 |
| `assets/layout-inventory-contract.md` | 布局清单输入契约（Prototype-Design 对齐此产出） |
| `assets/design-task-list-template.md` | 设计任务清单（逐页 brief）+ 基线复刻规则 |
| `assets/style-proposal-template.md` | 三套风格方案提案（双通道：文字小样 / 出稿对比） |
| `assets/design-system-template.md` | 设计规范模板（Design Tokens + 全组件规范） |
| `assets/archive-readme-template.md` | 归档 README 模板 |
| `references/superdesign-sop.md` | Superdesign SOP 吸收版（场景路由 / 命令陷阱 / 资产路由 / 直编契约 / 续跑） |
| `references/design-review-gate.md` | 质量门禁检查表（四大项全绿放行） |
| `references/open-source-design-systems.md` | 开源设计系统沉淀库（Ant / Arco / shadcn / M3） |
| `references/style-case-library.md` | 真实案例库（生长型） |

## 环境依赖（三件套硬依赖，缺一阻塞）

```bash
npm install -g @superdesign/cli@latest   # CLI
superdesign login                         # 浏览器授权（一次）
superdesign init                          # 官方 skill 文件落位（可选，本 skill 自带 SOP）
```

## 关键约定

- **布局零改动**：视觉阶段只改「好不好看」，不碰结构；结构问题回 Prototype-Design。
- **规范先行**：没有确认过的 design-system.md，就没有任何生成调用。
- **额度即预算**：变体数量、花钱动作永远用户裁决；确定性修正走直编（免额度）。
- **双目录**：`.superdesign/` 是 CLI 工作目录（手段）；`.spec/设计稿/` 是交付物（评审与 Workflow 只认它）。
