# 第 2 章：JSX 与 ReactElement —— 标签变成对象

## 本章在全局的位置

上一章看到管线入口是 `root.render(<App />)`。本章放大这个 `<App />`：它不是 HTML，本章讲清它被编译成什么、出厂时长什么样、为什么它只是张"描述单据"。

## 前置知识

### 转译器（Babel / SWC）
浏览器不认识 JSX。构建时转译器把 `<div className="a">hi</div>` 机械地改写成普通函数调用 `jsx("div", {className: "a", children: "hi"})`。所以 JSX 的全部语义 = 这个函数的语义，本章读的就是它。

## 核心问题

一行 JSX 是怎么变成一个 JS 对象的？这个对象里有什么、没什么？

## 主线流程图

```mermaid
flowchart LR
    A["你写的 JSX"] -->|"转译器改写"| B["jsx(type, config) 调用"]
    B --> C["jsxProd: 剥 key + 组装 props"]
    C --> D["ReactElement 出厂<br/>$$typeof/type/key/ref/props"]
    D -->|"只是描述单据<br/>没有任何实例"| E["交给协调器<br/>下一章: 变成 Fiber"]
```

## 关键点讲解

### 编译产物：jsx 与 jsxs 两个入口

📍 `packages/react/src/jsx/ReactJSX.js:28`

转译器只会生成 `jsx`、`jsxs`、`jsxDEV` 三种调用，从 `ReactJSX.js` 导出。`jsxs`（s = static）用于"children 是写死的数组"的场景，让运行时跳过一些检查；`jsxDEV` 是开发版，额外带校验和调试信息。生产环境跑的是 `jsxProd`。

### jsxProd 装配：剥 key，能复用就不拷贝

📍 `packages/react/src/jsx/ReactJSXElement.js:291-347`

`jsxProd(type, config, maybeKey)` 做两件事。第一，把 `key` 从 props 里抽出来单独存（key 是给协调器的指令，不是给组件的属性，所以不能留在 props 里——第 6 章 diff 会用它）。第二，组装 props：如果 config 里没有 key，**直接把 config 对象本身当 props 用**，一次都不拷贝。

为什么不担心外部修改？源码注释（`ReactJSXElement.js:323-333`）说得很直白：jsx 是编译器目标，编译器保证每次传的都是新造的对象；`createElement` 才需要拷贝，因为它可能被手写调用、传入旧对象。顺带一提，源码特意用 for-in 复制而不是 `delete` 删 key——因为 `delete` 会让 V8 把对象降级成慢速的字典模式。

### Element 出厂结构：五个字段的纯对象

📍 `packages/react/src/jsx/ReactJSXElement.js:170-237`

```js
element = {
  $$typeof: REACT_ELEMENT_TYPE,
  type,      // 'div' 或函数组件
  key,
  ref,
  props,     // 所有属性 + children
};
```

生产环境的 ReactElement 就这五个字段，一个普通 JS 对象。它是**不可变的描述单据**：开发版会 `Object.freeze`（`ReactJSXElement.js:276-279`），你也改不了。children 就藏在 `props.children` 里——`<a><b/></a>` 不过是 `{type:'a', props:{children:{type:'b'}}}` 的嵌套。

注意里面没有的东西：没有 DOM 节点、没有组件实例、没有状态。Element 只是"我要一个 div，class 是 a，里面放 hi"这句话的对象化。什么时候兑现，是后面章节的事。

### $$typeof：对象身份证，兼防注入

📍 `packages/shared/ReactSymbols.js:16`

```js
export const REACT_ELEMENT_TYPE: symbol = Symbol.for(
  'react.transitional.element',
);
```

`Symbol.for(key)` 取"全局符号注册表"里以 key 注册的 Symbol——同一个 key 在页面任何角落取到的是同一个值，跨模块、跨多份 React 拷贝都认得（这也是为什么用 `Symbol.for` 而不是裸 `Symbol()`：裸的每次都是新值，别人认不出）。搜索关键词：MDN Symbol.for。

它同时是一道安全墙：如果服务端把用户提交的 JSON 直接渲染进页面，攻击者构造的普通对象没有这个 Symbol 身份证，React 拒绝把它当组件树渲染，堵住"JSON 注入任意组件"的洞。本版本的符号值已从老的 `react.element` 换成 `react.transitional.element`——新旧版本混用时两边对象互不认账，这就是 React 19 系版本一致性检查存在的原因之一。

### ref 已经变成普通 prop

📍 `packages/react/src/jsx/ReactJSXElement.js:175-179`

新版本里 `ref` 不再从顶层参数读，而是 `props.ref` 就是事实源；`element.ref` 只留一个访问时打印弃用告警的 getter。这是给 React Compiler 和未来版本铺路：ref 统一进 props 之后，编译器处理它和处理其他 prop 就没有区别了。

### createElement：手写版的保守装配

📍 `packages/react/src/jsx/ReactJSXElement.js:610`

`createElement(type, config, children)` 和 jsx 干的是同一件事，但处处保守：不能假设 config 是新对象所以要拷贝、要从 config 里剥 key/ref、children 从第三个参数起全部拼进 `props.children`。jsx 之所以敢做"直接复用 config"的优化，正因为它是编译器专属通道。日常手写工具函数建议用 createElement 语义（或干脆复用现成 Element），别假装自己是编译器。

### Element ≠ 实例：为什么要两个东西

把 Element 直接当节点用不行吗？不行：Element 是值，可以随便存、随便传、渲染十次；而"节点"（有状态、有 DOM、有生命周期）是可变实体，一份就是一份。React 把**不可变的描述**（Element）和**可变的实体**（下一章的 Fiber）拆开，diff 比较的正是两张单据——单据相同，实体就可以原封不动复用。这是整个渲染模型的分界线。

## 收束

一行 JSX 经过转译器变成 `jsx()` 调用，出厂一个 `{$$typeof, type, key, ref, props}` 的不可变描述对象。但描述对象自己不会动，把单据变成有状态的运行时实体，靠的是下一章的主角——Fiber。
