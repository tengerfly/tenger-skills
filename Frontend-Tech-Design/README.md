# Frontend-Tech-Design —— 前端技术方案文档编写 Skill

> 状态：✅ 定稿
> 定位：依据 PRD + 低保真原型 + 后端 TDD，产出可落地、可评审、可 TDD 开发的前端技术方案包。FTDD = Frontend Technical Design Document。

## 一、固定栈与必问项

固定：pnpm + Vite + TypeScript + React hooks + 原生 fetch + Sass/SCSS + Vitest/RTL。

必问：档位（企业级/demo，默认企业级）、组件库、暗黑/主题、i18n、浏览器兼容。推荐默认即定稿；开发期零选型决策。

## 二、产出

- 总文档：选型 + 架构图 + 页面/组件清单 + 目录结构 + 模块边界 + 全局规范（fetch/hooks/CSS）+ 测试策略 + 模块关联图。
- 模块文档：边界 + 依赖 + 页面组件拆分 + hooks 数据流 + fetch 对接 + 状态管理 + 关键点 + 实现细节与决策 + 异常边界 + TDD 用例。
- 落盘 `.spec/FTDD/VN/`。

## 三、流程

```
解析（PRD+原型+TDD，浏览器硬检测）→ 选型澄清（问完即定稿）→ overview → ◉ Scope Gate
→ 逐模块方案 → 全局一致性 → 归档
```

浏览器工具硬前置：全无报错停（选型依赖官方版本信息）。

## 四、目录

```
Frontend-Tech-Design/
├── SKILL.md / README.md / CONTEXT.md
├── references/（doc-structure / tech-stack / component-design / fetch / css / module-design / test）
├── assets/（overview-template / module-template）
└── .spec/FTDD/VN/
```

## 五、快速上手

1. 给 PRD（±原型 + TDD）说「写前端技术方案 / FTDD」。
2. 问档位与必问选型。
3. 确认后生成总文档 → 逐模块方案 → 一致性检查 → 归档。

## 六、上下游

PRD/原型是需求与结构输入；TDD 接口清单是 fetch 唯一依据（硬串行）；Frontend-Dev 照图施工。