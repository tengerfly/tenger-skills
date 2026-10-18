# Frontend-Dev —— 前端代码开发 Skill

> 状态：✅ 定稿
> 定位：依据 PRD + 原型 + 设计稿 + TDD + FTDD，把技术方案落地为可运行、高还原、模块化前端工程。原则：还原度优先 · 模块化防重 · 测试先行 · 不确定即问 · 功能点即提交。

## 一、核心

| 项 | 内容 |
|---|---|
| 输入 | `.spec/FTDD/VN/`（施工图）+ PRD/原型/设计稿/TDD + 用户给定目录与 git |
| 目标端 | web / app / 小程序（步骤 1 判定） |
| 还原基准 | **结构 = 低保真原型；视觉 = 设计稿**（有则以 `.spec/设计稿/` + `design-system.md` 为唯一视觉应然，须 token 对账；无设计稿才回退原型并明示降级） |
| 架构 | 页面容器 → 组件 → hooks → api，单向依赖 |
| 组件归属 | 模块内 ≥2 次 → features/<模块>/components/；跨模块 → src/components/ |
| 业务组件资产 | S1/S2 组件决策链检索外部 AI 知识库复用（经仓库根 skill-knowledge 引用层）；S10 交付沉淀判定（四件套入外部库，先查重防冗余，项目特有不沉） |
| 测试 | 先行，TC-Mxx ↔ AC-Mxx，渲染/交互/数据流/边界/异常 |
| 共享类型 | monorepo 下单一来源，前端只 import 不重定义 |
| 浏览器 | 硬预检，全无报错停 |
| 提交 | 一功能点一 commit；eslint + stylelint + commitlint；不擅自 push |
| 续做 | 先读 PROJECT.md 恢复进度与规则 |

## 二、流程

```
解析（读文档/判端/确认目录+git/浏览器预检）→ 技术栈锁定（读 FTDD；缺失补选型；端不符阻塞）
→ 工程初始化 → 还原基线+token → ◉ Scope Gate → 功能点计划（todo + PROJECT.md）
→ 逐功能点测试先行实现（组件抽离在编码当下判定）+ 提交 → 契约对齐 → 全局一致性 → 交付
```

## 三、目录

```
../frontend-dev/
├── SKILL.md
├── README.md
├── CONTEXT.md
├── references/   # architecture / code-style / test / tech-stack / fidelity / ui-states / motion / web-interface-quality / framework-equivalence / decision-rules / case-library
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

Frontend-Tech-Design（施工图）、Backend-Tech-Design（接口契约源）、prototype-design 与 ui-ux-design（还原基准）、Backend-Dev（同域另一端）。
下游：Code-Review（评审回退修改方，承接 `.spec/代码评审/任务清单.md`）、auto-test（验收；L2 内嵌 Fidelity-Review）。