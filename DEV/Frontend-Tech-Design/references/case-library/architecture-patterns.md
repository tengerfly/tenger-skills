# 前端架构范式（Architecture Patterns）

> 用途：架构风格选型时的决策参考。选型表见 `decision-rules.md` §一。

---

## 一、Feature-Sliced Design（FSD，企业级首选）

- **分层**：app（入口）→ pages（页面）→ widgets（区块）→ features（业务功能）→ entities（业务实体）→ shared（通用）。
- **核心**：单向依赖，上层可用下层，反向禁止。
- **适用**：中大型、多团队、需明确边界。

## 二、Feature / Domain 组织

- `features/<模块>/` 下聚合 components + hooks + api，按业务能力切。
- **适用**：中大型单团队，比 FSD 轻。

## 三、Atomic Design

- 原子（按钮/输入）→ 分子（组合）→ 有机体（区块）→ 模板 → 页面。
- **适用**：共享 UI 组件库；业务逻辑另用 Feature 组织（「共享 UI 用 Atomic，业务用 Feature」）。

## 四、Clean Architecture（前端版）

- 依赖倒置：domain（实体/用例）← application ← interfaces ← infrastructure。
- **适用**：领域逻辑重、要隔离框架依赖。

## 五、Micro-Frontends

- Module Federation / qiankun / single-spa；独立部署、独立技术栈。
- **决策点**：通信（事件/URL/共享 Store）、隔离（Proxy 沙箱/CSS Modules）、共享依赖。
- ⛔ 无独立部署诉求不上（做减法）。

## 六、Next.js App Router

- 默认 Server Component；`"use client"` 只在确需客户端时加；Server Actions 做表单提交。

> 出处：feature-sliced.documentation、github.com/vercel/microfrontends、linkedin React Architecture Types。
