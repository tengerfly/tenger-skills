# 框架具体写法（Framework Patterns）

> 用途：按框架落地时的写法参考。非 React 框架施工请先读 `framework-equivalence-guide.md` 等价映射。

---

## 一、React

- 状态/副作用用 hooks；跨切面用 Context；代码分割 Suspense + lazy；RSC 减少客户端包体；Error Boundaries 兜底。

## 二、Vue 3

- Composition API + SFC（`<script setup>`）；defineProps/defineEmits 类型化；ref/computed/watch；provide/inject 共享；复杂持久化用 Pinia。

## 三、Next.js

- App Router 默认 Server Component；`"use client"` 只在确需客户端时加；交互按钮拆独立 client 组件，页面保持 Server Component。

## 四、Angular

- Standalone（弃 NgModules）；Signals 响应式；`inject()` DI；OnPush 优化变更检测。

## 五、Svelte 5

- Runes（`$state/$derived/$effect`）；SvelteKit 文件路由 + server functions。

> 出处：lobehub frontend-development、qumge frontend-architecture、skills.cat frontend-development。
