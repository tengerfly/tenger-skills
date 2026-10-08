# 框架等价映射指南（Framework Equivalence）

> 用途：FTDD 选型为非 React 框架（Vue 3 / Taro / uni-app / React Native / Electron / Flutter）时，把本 skill 各 guide 的 React 基线写法映射到所选框架施工。
> ⛔ 铁律：**施工框架必须与 FTDD 选型一致**，禁自主切回 React 基线；本指南未覆盖的框架细节以所选框架官方文档为准（浏览器工具可查）。

---

## 一、核心概念等价映射（总表）

| 通用概念 | React（默认基线） | Vue 3 | Taro（React 语法） | uni-app（Vue3） | React Native | Electron | Flutter（备选） |
|---|---|---|---|---|---|---|---|
| 逻辑层单元 | hooks `useXxx` | 组合式函数 composables | hooks（+ Taro 专用：useRouter 等） | composables | hooks | 同渲染层框架 | Riverpod / Bloc |
| 组件写法 | 函数组件 + JSX | SFC `<template>` + `<script setup>` | 函数组件 + JSX | SFC | 函数组件 + RN 核心组件 | 渲染层同 React/Vue | Widget 树 |
| 路由/导航 | React Router v6 | Vue Router 4 | app.config.ts 声明式 + Taro.navigateTo | pages.json + uni.navigateTo | React Navigation / Expo Router | Web 路由（渲染层） | Navigator / go_router |
| 全局状态 | Zustand / RTK | Pinia | Zustand / RTK | Pinia | Zustand / RTK | 同渲染层 | Riverpod / Bloc |
| 请求 | fetch 封装 | fetch 封装 | Taro.request 封装 | uni.request 封装 | fetch 封装 | 渲染层 fetch / 主进程 net | dio |
| 样式隔离 | CSS Modules（*.module.scss/less） | scoped / CSS Modules | Sass + rpx | scoped + rpx | StyleSheet | 渲染层同 React/Vue | ThemeData 主题 |
| 测试 | Vitest + RTL | Vitest + VTU | Vitest + Taro 测试库 | Vitest | Jest + RNTL | 渲染层同 Web | flutter_test |
| 工程/入口 | main.tsx + Vite | main.ts + Vite | app.ts + app.config.ts | main.js + pages.json | App.tsx（Expo） | main + preload（electron-vite） | main.dart |

---

## 二、施工切换规则（读 React 基线 guide 时的替换规则）

1. **目录结构**：React 基线 `pages/components/hooks` 在 Vue3 对应 `views/components/composables`；Taro/uni-app 用声明式页面配置替代 router 目录；RN/Flutter/Electron 按各自脚手架；
2. **逻辑层**：各 guide 中「hooks」一律读作「逻辑层单元」——Vue3 落地为 composables（`src/composables/`），`{data, loading, error, refetch}` 返回形态保持一致；
3. **测试**：RTL 示例映射为 VTU（`mount` + `wrapper.find`）/ RNTL / flutter_test；用例编号 `TC ↔ AC` 与先测后写规则不变；
4. **样式**：CSS Modules 语境在 Vue 下默认 scoped（或按 FTDD 选 CSS Modules）；token 变量（CSS variables）各框架通用，扩展名/载体按框架；
5. **请求契约**：封装原则（baseURL/超时/取消/ApiError/token 注入）各端等价实现，接口按域拆分、与后端 TDD 一一对应不变；
6. **UI 状态**：10 大 UI 状态（`ui-states-guide.md`）的「React 写法」列按 §一 映射到所选框架，**状态行为要求不减**（缺失 = 功能点未完成的判定同样适用）。

---

## 三、切换自查清单（开工前 + 交付前各过一遍）

- [ ] 施工框架 = FTDD 选型？（不一致 → ⛔ 阻塞对齐，禁自主切换）
- [ ] 逻辑层/路由/状态/请求/测试五项均按 §一 映射到所选框架？
- [ ] UI 组件库与框架配套（来自 FTDD 选型，清单见 FTDD `tech-stack-guide.md` §三）？
- [ ] 10 大 UI 状态已按所选框架落地，行为要求不减？
- [ ] 样式 token 仍走 variables（扩展名/载体按框架）？
- [ ] 框架特有工程约定（声明式路由/原生配置/脚手架）已登记 PROJECT.md？
