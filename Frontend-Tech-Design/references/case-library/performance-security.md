# 性能与安全（Performance & Security）

> 用途：写性能/安全章节的落地参考。量化阈值见 `decision-rules.md` §四。

---

## 一、性能六板斧

1. **渲染策略**：SSR/RSC/流式（Next.js 默认即优化）。
2. **代码分割**：路由级 + 组件级 React.lazy + 预取。
3. **资源优化**：WebP/AVIF、响应式 srcset、CDN、font-display 防 CLS。
4. **缓存**：Service Worker、版本/hash 缓存、Cache First/Network First。
5. **异步**：Web Worker 处理 CPU 密集、requestIdleCallback 分解渲染。
6. **监控闭环**：Lighthouse/WebPageTest 测 → Sentry/RUM 采 → 优化 → 回测。

## 二、量化阈值

| 指标 | 阈值 |
|---|---|
| 初始 bundle | <200KB gzipped |
| LCP | >2.5s 阻断 |
| CLS | >0.1 |
| Lighthouse CI | Performance/A11y/Best Practices ≥90 |
| axe-core | WCAG 2.1 AA 零违规 |

## 三、安全清单

- 令牌：Access Token 存内存（非 localStorage），Refresh Token 存 HttpOnly Cookie。
- 防 XSS：CSP 头、转义、避免 dangerouslySetInnerHTML。
- 防 CSRF：SameSite Cookie + 双重提交令牌。
- 第三方脚本 SRI 校验。
- HTTPS/HSTS。

## 四、无障碍

- 交互组件必加 ARIA + 键盘处理（Enter/Space/Escape）。
- 表单 input 关联 label，错误 aria-describedby。
- 颜色传达含义时加第二指示（图标/文字）。

> 出处：github.com/thedaviddias/Front-End-Checklist、OWASP、nextjs.org 生产清单。
