# 前端开发案例库（Case Library）索引

> 定位：写前端代码时**按需加载**的落地参考。与 Frontend-Tech-Design 的 case-library 分工：那份管「架构/工程化/选型」，本份管「组件模式/框架写法/编码规范」。
> 来源：lobehub frontend-development、qumge frontend-architecture、skillmd frontend-coding、react-bits。已精编浓缩。

## 一、目录

| 文件 | 内容 | 何时读 |
|---|---|---|
| `static-page-trial-playbook.md` | **标准 SOP（SKILL 主流程 S1/S7/§4.7/§4.9 引用）**：输入瘦身/复用清单/编码套路/口径决策模式/验收脚本化/节奏纪律 | 逐页产出静态页时**必按此执行** |
| `component-patterns.md` | 复合/受控/容器展示/Render Props/HOC 模式 | 写组件时 |
| `framework-patterns.md` | React/Vue/Next/Angular/Svelte 框架写法 | 按框架落地时 |
| `quality-conventions.md` | 测试 + 工程化规范（cnblogs 大厂规范） | 搭工程质量时 |
| `agent-skill-samples.md` | 同类前端开发 Skill 结构样本 | 优化本 Skill 结构时 |

## 二、统一案例字段

> 场景 → 技术栈 → 问题 → 解法/关键代码 → 出处 → 适用边界。

## 三、使用原则

1. **规范回溯到 FTDD**：FTDD 选型/UI 规范优先，case-library 只补通用写法。
2. **多框架等价映射**：非 React 框架按 `framework-equivalence-guide.md` 等价映射，案例的 hooks/RTL/CSS Modules 语境读作所选框架等价物。
3. **还原度优先**：案例只借鉴实现模式，不改视觉/文案基准。
