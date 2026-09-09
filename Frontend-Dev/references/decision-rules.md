# 编码层组件与规范决策规则（Frontend-Dev Decision Rules）

> 用途：写前端代码时的「组件怎么拆、状态怎么放、样式怎么写、数据表单怎么组织」硬规则库。与 `Frontend-Tech-Design/decision-rules.md` 分工：那份管「方案层怎么定架构」，本份管「编码层怎么守规范」。
> 本 Skill 八条铁律（可读性/单一职责/单向依赖/模块内聚/注释/即问/共享类型/提交校验）+ 还原度优先，优先级最高；本文件补充「组件模式/状态/样式/数据/测试/规范」的量化硬规则。

---

## 一、组件模式决策

| 场景 | 规则 |
|---|---|
| 相关组件共享隐式状态 | 复合组件（Context 共享），如 `Tabs.List / Tabs.Tab` |
| 表单输入 | 受控（显式 state）；一次性简单输入用非受控 + ref |
| 数据逻辑 vs 渲染 | 容器-展示分离：Container 管数据/逻辑，Presentational 纯渲染 |
| 组件内取数 | 逻辑外提 hook；组件内直接 fetch 仅限最小一次性场景 |
| 组件过肥 | ⛔ 反上帝组件：>200 行 / >3 个 useEffect / 多模态堆一文件 → 沿页面接缝拆 |

## 二、状态管理代码

- 状态越局部越好：先组件内 useState/ref，需要才提升。
- 服务端状态（API 缓存）进 TanStack Query/SWR，**不进全局 store 重复缓存**。
- 全局可变状态才用 Zustand/Pinia/RTK；小项目第一天别上 Redux。
- 派生状态用 computed/selector，不存计算结果；乐观更新。

## 三、样式规则

- 设计令牌：颜色/间距/字号用 CSS 变量统一，禁写死色值（铁律）。
- Tailwind 卫生：className >5–8 组就抽组件；用 `cn()` 合并条件类，禁内联复杂条件。
- 禁 `!important`（特殊需注释）；优先 transform/opacity 做动画避免重排。

## 四、数据与表单

- ⛔ 禁止裸 fetch/axios 散落组件：统一收敛到 `src/api/`（request.ts 封装 + 按业务域 `<模块>.ts`），配 TanStack Query queryKey/queryFn。
- 显式处理 loading / error / empty 三态。
- 校验用 zod/yup/valibot，schema 就近放 `*.schema.ts`，组件内不内联长校验。

## 五、测试

- 金字塔：单元（函数/hook）→ 集成（多组件）→ E2E（关键链路）。
- 用 Testing Library「像用户一样测试」，不测实现细节。
- 覆盖率：单测行覆盖 ≥80%；CI 跑 lint 失败阻断合并。

## 六、工程化规范

- TypeScript `strict:true`，禁 `any`、禁 `@ts-ignore`；外部数据用 zod 守卫运行时输入。
- 复杂度：单函数 ≤80 行、圈复杂度 ≤10、嵌套 ≤4 层；提前返回减少嵌套。
- 工具链三件套必配：ESLint + Prettier + Stylelint；Git Hooks（husky+lint-staged）强制；CI 跑 lint。
- 安全：外部输入必校验（白名单）、转义防 XSS、禁 eval/innerHTML、敏感数据禁前端明文存储。
