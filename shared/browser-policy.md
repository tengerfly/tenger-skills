# 浏览器工具两级策略（公共约定）

> 权威源：仓库根 README.md「浏览器工具策略」。各 skill 正文只声明自身级别与动作，检测顺序、两级行为、报错文案以本文件为准，不再各自重复定义。

## 一、检测顺序

`Playwright → browser-use → 其他（如 agent-browser）`。列举不穷举：凡当前环境可用的、能驱动真实浏览器打开页面/交互/截图的工具均算。

## 二、两级行为

| 级别 | 行为 |
|---|---|
| 硬依赖 | 开工前必检；任一可用即开工（记作走查/校验工具）；全部不可用 → 报错并要求安装后重跑，不产出任何交付物 |
| 软检测 | 有则用（执行对应辅助步骤，如选型版本核验），无则跳过该步骤，不阻塞主流程 |

## 三、级别清单

- **硬依赖**：Prototype-Review / UI-UX-Review / Fidelity-Review / Frontend-Tech-Design / Frontend-Dev / Testing
- **软检测**：Tech-Review / Backend-Tech-Design
- **不涉及**：其余 skill 不做检测（仅截图增强的如 UI-UX-Design：浏览器不可用时以替代手段核验，并在产物注明）

## 四、硬依赖报错文案模板

```
【环境错误】未检测到任何可用浏览器工具（检测顺序：Playwright → browser-use → 其他）。
请安装任一浏览器工具后重跑；安装前本 skill 不产出任何交付物。
```

> 注：midscenejs 仅为 Testing 样式视觉断言的可选增强（需装依赖 + 模型配置），不属于检测链；不可用时降级并在 Scope Gate 说明。
