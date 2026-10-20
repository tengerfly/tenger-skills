# 微交互与动效案例库（Interactions & Motion）

> 定位：案例库·交互类。微交互按「触发方式 × 反馈类型」矩阵组织；动效实现资源单独一节。
> 约束：设计稿动效遵守 design-system §6/§7（强度档 / 时长档 / 曲线 token，判据见本 skill `../motion-design-guide.md`；只动进出场 / 反馈，不做装饰性动画）；复杂动效仅限营销站场景。

---

## 一、微交互矩阵（触发 × 反馈）

| 触发 \ 反馈 | 确认 | 引导 | 奖励 | 状态 |
|---|---|---|---|---|
| hover | {{按钮 hover 位移/底色}} | {{tooltip 浮现}} | — | {{卡片抬升}} |
| click | {{水波纹/按压回弹}} | {{步骤引导高亮}} | {{彩带/气球}} | {{加载态}} |
| scroll | — | {{滚动显现}} | — | {{吸顶/进度}} |
| state | {{成功勾选动画}} | {{空态引导 CTA}} | {{里程碑庆祝}} | {{骨架屏→内容}} |

## 二、微交互案例资源

| 名称 | 链接 | 许可 | 案例库价值 |
|---|---|---|---|
| GitHub Topic: micro-interactions | https://github.com/topics/micro-interactions | — | 微交互仓库聚合，按星标排序找优质实现 |
| react-rewards | https://github.com/thedevelobear/react-rewards | MIT | 「奖励式」微交互（彩带/气球），情绪化反馈范式 |
| react-useanimations | https://github.com/useAnimations/react-useanimations | MIT | Lottie 动画图标集合 |
| v-wave | https://github.com/justintaddei/v-wave | MIT | Vue 的 Material 水波纹指令 |
| micro-interactions-library | https://github.com/silvvrodriguez/micro-interactions-library | — | 原生 JS+CSS 轻量微交互，适合学习与拆解 |
| Hover.css | https://github.com/IanLunn/Hover | MIT | 链接/按钮/图片的 CSS3 hover 动效套件 |
| Ramotion animated-tab-bar | https://github.com/Ramotion/animated-tab-bar | MIT | iOS 标签栏交互动效范式 |

## 三、动效实现资源

| 名称 | 链接 | 许可 | 案例库价值 |
|---|---|---|---|
| Framer Motion | https://www.framer.com/motion/ | MIT | React 动效事实标准 |
| GSAP | https://gsap.com | 免费个人/商业需授权 | 时间轴级复杂动效 |
| Lottie | https://lottiefiles.com | 免费层 | 轻量矢量动画 |
| Motion Primitives | https://motion-primitives.com | MIT | 动效优先的界面原语 |
| Transitions.dev | https://transitions.dev | 免费 | 复制即用的过渡/微交互 CSS 片段 |

**沉淀格式**：每条 1 个 GIF/录屏 + 代码路径 + 「触发方式 / 反馈类型 / 时长缓动 / 无障碍备忘（prefers-reduced-motion）」。
