# 状态管理选型（State Management）

> 用途：定状态方案的决策参考。选型表见 `decision-rules.md` §三。

---

## 一、状态分类（6 类，决策树起点）

| 类别 | 作用范围 | 工具 |
|---|---|---|
| Local | 单组件 | useState / ref / signal |
| Shared | 组件子树 | Context / provide-inject / props |
| Global | 整个应用 | Zustand / Redux / Pinia / NgRx |
| Server | 远程数据缓存 | TanStack Query / SWR / Apollo |
| URL | 浏览器 URL | React Router / Vue Router 参数 |
| Form | 表单输入 | react-hook-form / Formik / VeeValidate |

## 二、最佳实践

- 状态越局部越好：先组件内，需要才提升。
- 服务端状态进 TanStack Query/SWR，**不进全局 store 重复缓存**。
- 全局可变状态才用 Zustand/Pinia/RTK；小项目第一天别上 Redux。
- 派生状态用 computed/selector，不存计算结果。
- 乐观更新提升响应感。

## 三、2026 趋势

- React Compiler（React 19 稳定）自动 memo，手写 useMemo/useCallback 多为 code smell。
- AI 流式 UI 当「streaming server state」单独建模。

> 出处：lobehub frontend-development、skillmd frontend-coding、vuejs.org 状态管理。
