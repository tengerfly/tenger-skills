# 组件模式（Component Patterns）

> 用途：写组件时的模式参考。决策见 `decision-rules.md` §一。

---

## 一、复合组件（Compound Components）

- 用 Context 共享隐式状态：`Tabs.List` / `Tabs.Tab` 写法。
- 范例：`Card.Header` / `Card.Body` 组合。

## 二、受控 vs 非受控

- 表单用受控（显式 state）；一次性简单输入可用非受控 + ref。

## 三、容器-展示分离

- 数据/逻辑在 Container，纯渲染在 Presentational；展示组件只接 props + 回调，不发请求、不绑全局状态库。

## 四、Render Props / HOC

- Render Props：把渲染逻辑作 props 传入（函数子组件）。
- HOC：跨组件复用逻辑的高阶组件；现代更推荐 hooks。

## 五、逻辑外提

- 组件只渲染，取数/状态/转换进 hook/composable。
- 数据获取统一返回 `{data/list, loading, error, refetch}`。

## 六、反模式

- 上帝组件（>200 行 / >3 useEffect）→ 沿接缝拆。
- 组件内直接 fetch → 抽 hook + api service。

> 出处：github.com/vasanthk/react-bits、github.com/krasimir/react-in-patterns、lobehub frontend-development。
