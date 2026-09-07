# Testing —— 项目测试 Skill

> 状态：✅ 定稿
> 定位：高级测试专家，依据 PRD + 设计稿/原型，本地启动真实项目做全流程测试，交付分级、可复现、有证据的问题文档。原则：全状态 · 全点击 · 样式必截图 · 慢接口必列 · 问题必分级。

## 一、测什么

- 功能：每个对象所有状态 + 页面全可点击元素 + 异常分支。
- 样式：midscenejs 视觉断言 + 三态 + 截图；有设计稿时内嵌 Fidelity-Review 做还原检查。
- 接口性能：全接口耗时监听，慢接口逐条列出（默认 >1000/3000/5000ms）。

## 二、流程

```
解析 → 环境准备（浏览器硬预检）→ 测试计划+用例 → ◉ Scope Gate
→ 功能 → 样式 → 性能 → 汇总问题文档 → 归档 .spec/测试/
```

先计划后执行；浏览器工具全无报错停；P0/P1/P2 + 复现 + 证据。

## 三、目录

```
Testing/
├── SKILL.md / README.md / CONTEXT.md
├── references/（test-case / style-test / acceptance-loop / api-perf / browser）
├── assets/（test-process / test-case / bug-report 模板）
└── .spec/测试/
```

## 四、快速上手

1. 给项目代码位置 + 启动命令 + PRD/设计稿（缺则问）。
2. Scope 确认范围/用例/工具/阈值后自动执行。
3. 交付问题文档交 Frontend-Dev / Backend-Dev 返工。