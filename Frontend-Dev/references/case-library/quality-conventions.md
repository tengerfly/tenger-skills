# 测试与工程化规范（Quality & Conventions）

> 用途：搭工程质量时的规范参考。硬规则见 `decision-rules.md` §五/§六。

---

## 一、测试

- 金字塔：单元（函数/hook）→ 集成（多组件）→ E2E（关键链路）。
- 最小测试覆盖：工具→单测、重要 hook→单测、主表单→校验测试、关键流→E2E。
- Testing Library「像用户一样测试」，不测实现细节；覆盖率 ≥80%。
- colocate 或 tests/ 二选一并保持一致。

## 二、工程化规范（cnblogs 大厂规范）

- 命名/格式/注释/日志/TS/复杂度/安全编码/ESLint/Prettier/Stylelint/husky+lint-staged/SonarQube 门禁/覆盖率。
- 目录按功能模块分组（components/hooks/api/types/utils），避免循环依赖，每文件只导出一个主功能。
- TS `strict:true` 禁 any；外部数据 zod 守卫。
- 复杂度：函数 ≤80 行、圈复杂度 ≤10、嵌套 ≤4 层。

## 三、安全编码

- 外部输入必校验（白名单）、转义防 XSS、禁 eval/innerHTML、敏感数据禁前端明文存储。

## 四、状态管理落地

- 服务端状态 TanStack Query/SWR；全局可变 Zustand/Pinia；Pinia + 加密 localStorage 做安全存储（掘金实战）。

> 出处：cnblogs.com/pengjiali/p/19157334、qumge frontend-architecture、juejin.cn Pinia 实战。
