# 前端方案决策规则与量化阈值（FTDD Decision Rules）

> 用途：写前端技术方案时的「架构怎么选、状态怎么定、性能怎么扛」决策库。与 `../Frontend-Dev/decision-rules.md` 分工：本份管「方案层怎么定架构」，那份管「编码层怎么守规范」。
> 写法范式（借鉴 peterhdd engineering-frontend-developer）：`When + 场景 → 动作 + 量化阈值 + 理由`。本 Skill 铁律（端形态+框架每次必问、收敛证明）优先级最高。

---

## 一、架构范式选型（按规模）

| 规模 | 架构 | 说明 |
|---|---|---|
| <10 人小项目 | Flat / 简单 Monorepo | 够用即可 |
| 中大型、多业务域 | Feature/Domain 组织（feature/ 聚合 components+hooks+api） | 按业务能力组织 |
| 企业级、多团队 | Feature-Sliced Design（FSD）+ Monorepo（Nx/Turborepo） | app/pages/widgets/features/entities/shared 单向依赖 |
| 超大规模、独立部署 | Micro-Frontends（Module Federation/qiankun/single-spa） | 独立部署 |

## 二、微前端决策（仅超大规模才引入）

- **通信**：优先浏览器事件 / URL / 共享 Store（Redux Toolkit/Zustand），避免微应用间直接 API 调用（退化成分布式单体）。
- **隔离**：JS 用 Proxy 沙箱、CSS 用 Shadow DOM / CSS Modules。
- **性能**：按需加载 + 预加载 + 共享依赖（包体可降 30%–60%）。
- ⛔ 做减法：无独立部署/多团队诉求不上微前端。

## 三、状态管理选型

| 场景 | 方案 |
|---|---|
| UI 局部状态 | useState / ref |
| 跨组件协调 | 状态提升 |
| 全局子树（主题/语言/鉴权） | Context / provide-inject |
| 服务端数据缓存 | TanStack Query / SWR（**不进全局 store 重复缓存**） |
| 全局可变状态 | Zustand / Pinia / RTK（小项目第一天别上 Redux） |
| 表单状态 | react-hook-form（复杂）/ useState（简单） |

- 派生状态用 computed/selector，不存计算结果；乐观更新提升响应感。

## 四、性能硬规则 + 量化阈值

| 指标 | 阈值 | 动作 |
|---|---|---|
| 初始 JS bundle | < 200KB gzipped | 超则 React.lazy/dynamic import 路由级分割 |
| LCP | > 2.5s（Lighthouse CI） | 视为阻断 bug，定位瓶颈 |
| CLS | > 0.1 | 图片/视频加尺寸、预留空间 |
| CI 覆盖率 | ≥80% | 每个组件 ≥1 渲染 + 1 交互测试 |
| 组件行数 | >300 行 | 拆分 |
| 动效 | 只用 transform/opacity | 避免触发布局重排 |

- 性能六板斧：渲染策略（SSR/RSC/流式）→ 代码分割 → 资源优化（WebP/AVIF/srcset/CDN）→ 缓存（SW/hash）→ 异步（Worker）→ 监控闭环（Lighthouse/Sentry）。

## 五、构建工具选型

- Vite：新项目默认；Webpack：老项目/Webpack-only 插件；Turbopack：Next 14+；esbuild：库打包/脚本。
- Monorepo：<5 packages 用 workspaces；5–20 Turborepo；>20 Nx。

## 六、渲染策略决策

| 场景 | 策略 |
|---|---|
| 内容变化 <1 次/小时（营销/文档） | SSG |
| 个性化/SEO 关键动态页 | SSR |
| 认证后的内部工具 | CSR |
| 多数静态、定期更新 | ISR |
| RSC | 默认 Server Component，需 useState/useEffect/onClick/浏览器 API 才 `"use client"` |

## 七、安全

- 令牌：Access Token 存内存，Refresh Token 存 HttpOnly Cookie，静默刷新 + 自动登出。
- 防 XSS：CSP 头、转义用户内容、避免 dangerouslySetInnerHTML。
- 防 CSRF：SameSite Cookie + 双重提交令牌。
- 第三方脚本加 SRI 校验。
