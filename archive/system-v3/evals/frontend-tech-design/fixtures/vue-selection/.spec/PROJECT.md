# PROJECT.md（前端工程基线）

- 项目：任务看板（内部工具）
- 上游 FTDD 选型（已定稿，施工不得重选）：
  - 端形态：web 端 SPA
  - 技术框架：**Vue 3.5**（Composition API + `<script setup>`）
  - 状态：**Pinia**
  - 路由：**Vue Router 4**
  - 组件库：**Element Plus**
  - 测试：**Vitest + Vue Test Utils**（逻辑层用 composables 单测）
  - 样式：Sass + `<style scoped>`
- 本批次任务：给「任务列表页」写页面组件测试与路由配置。
- 备注：工程内没有 React 依赖，`package.json` 也不打算加。
