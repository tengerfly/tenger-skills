# Frontend-Dev —— 前端代码开发 Skill

> 状态：✅ 定稿
> 定位：依据 PRD + 原型 + TDD + FTDD，把技术方案落地为可运行、高还原、模块化前端工程。原则：还原度优先 · 模块化防重 · 测试先行 · 不确定即问 · 功能点即提交。

## 一、核心

| 项 | 内容 |
|---|---|
| 输入 | `.spec/FTDD/`（施工图）+ PRD/原型/TDD + 用户给定目录与 git |
| 目标端 | web / app / 小程序（步骤 1 判定） |
| 还原基准 | 结构 = 低保真原型；视觉 = 设计稿（有则以 `.spec/设计稿/` 为准） |
| 架构 | 页面容器 → 组件 → hooks → api，单向依赖 |
| 组件归属 | 模块内 ≥2 次 → features/<模块>/components/；跨模块 → src/components/ |
| 测试 | 先行，TC-Mxx ↔ AC-Mxx，渲染/交互/数据流/边界/异常 |
| 共享类型 | monorepo 下单一来源，前端只 import 不重定义 |
| 浏览器 | 硬预检，全无报错停 |
| 提交 | 一功能点一 commit；eslint + stylelint + commitlint；不擅自 push |
| 续做 | 先读 PROJECT.md 恢复进度与规则 |

## 二、流程

```
解析（读文档/判端/确认目录+git/浏览器预检）→ 技术栈锁定（读 FTDD；缺失补选型；端不符阻塞）
→ 工程初始化 → 还原基线+token → ◉ Scope Gate → 功能点计划（todo + PROJECT.md）
→ 逐功能点测试先行实现 + 提交 → 组件抽离检查 → 契约对齐 → 全局一致性 → 交付
```

## 三、目录

```
Frontend-Dev/
├── SKILL.md
├── README.md
├── CONTEXT.md
├── references/   # architecture / code-style / test / tech-stack / fidelity / ui-states / framework-equivalence / decision-rules / case-library
├── assets/       # project-structure / module-code / project-status 模板
```

代码产出于用户给定目录，不在本目录内。

## 四、快速上手

1. 给出 FTDD（±PRD/原型/TDD）+ 目标目录与 git 地址。
2. 判端、锁技术栈、搭骨架、列功能点计划。
3. Scope 确认后逐页面测试先行实现；不确定即问。
4. 完成功能点即更新任务并校验提交。
5. 契约对齐 + 全局一致性 + 还原截图核对后交付。

## 五、上下游

Frontend-Tech-Design（施工图）、Backend-Tech-Design（接口契约源）、Prototype-Design/UI-UX-Design（还原基准）、Backend-Dev（同域另一端）。