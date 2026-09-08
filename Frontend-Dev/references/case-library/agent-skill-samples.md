# 同类前端开发 Skill 结构样本（Agent Skill Samples）

> 用途：优化本 Skill 结构时的借鉴范本（只借鉴组织方式，不搬运内容）。

---

## 一、lobehub frontend-development（设计原则范本）

- 5 设计原则（单一职责/组合优于继承/受控vs非受控/容器展示/复合组件）+ 6 类状态决策树（local/shared/global/server/URL/form）+ 框架范式。
- 借鉴点：状态分类决策树 + 设计原则（已融入 decision-rules.md）。

## 二、qumge frontend-architecture（编码规范范本，最贴近）

- 四层分离（UI/Logic/Data/Type/Validation）+ 文件职责与大小 + Next RSC + Vue composables 精细规则。
- 借鉴点：API 放 service 文件、表单 schema 校验、Tailwind 卫生（className>5-8 抽组件）。

## 三、skillmd frontend-coding（references 组织范本）

- 9 个 references 子文件（component-patterns/react-patterns/vue-patterns/state-management/typescript/performance-testing）。
- 借鉴点：按关注点拆分 references 子文件。

## 四、vasanthk/react-bits + krasimir/react-in-patterns

- React 模式大典，作为 case-library 的模式索引。

> 出处：lobehub.com、qumge.com、skillmd.ai、github.com/vasanthk/react-bits。
