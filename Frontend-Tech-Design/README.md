# Frontend-Tech-Design —— 前端技术方案文档编写 Skill

> 状态：✅ 定稿
> 定位：依据 PRD + UI 设计稿（缺省回退低保真原型）+ 后端 TDD，产出可落地、可评审、可 TDD 开发的前端技术方案包。FTDD = Frontend Technical Design Document。

## 一、默认基线与必问项

默认基线：pnpm + Vite + TS + React hooks + 原生 fetch + Sass/Less（按生态选）+ Vitest/RTL。

必问：档位（企业级/demo，默认企业级）、端形态（Web PC/H5/小程序/App/桌面/多端一套）、技术框架（默认 React，可换 Vue3/Taro/uni-app/React Native/Electron，Flutter 备选；**用户确认才定稿**）、组件库（随框架从配套清单联动推荐）、暗黑/主题、i18n、浏览器兼容、**无障碍目标（默认 WCAG 2.1 AA）**、**性能预算（Core Web Vitals + 首屏包体上限）**。推荐默认即定稿（框架/端形态除外）；开发期零选型决策。每个决策点先过拷问收敛证明（失败/涨 10 倍/漏项 + 边界/节点），一两句回答不定稿。

## 二、产出

- 总文档：选型（含关键决策记录）+ 架构图 + 页面/组件清单（标注原型=结构、设计稿=视觉）+ 目录结构 + 模块边界 + 全局规范（fetch/hooks/CSS/**UI 规范=token+界面状态**/**a11y 规范**/**性能预算**）+ 测试策略 + 模块关联图。
- 模块文档：边界 + 依赖 + 页面组件拆分 + hooks 数据流 + fetch 对接 + 状态管理 + 关键点 + 实现细节与决策 + 异常边界 + TDD 用例。
- 落盘 `.spec/FTDD/VN/`。

## 三、流程

```
解析（PRD+设计稿/原型+TDD，浏览器硬检测）→ 选型澄清（逐点拷问→定稿）→ overview → ◉ Scope Gate
→ 逐模块方案 → 全局一致性 → 归档
```

浏览器工具硬前置：全无报错停（选型依赖官方版本信息）。

## 四、目录

```
Frontend-Tech-Design/
├── SKILL.md / README.md / CONTEXT.md
├── references/（doc-structure / tech-stack / component-design / fetch / css / module-design / test / socratic-grilling / decision-rules / case-library）
├── assets/（overview-template / module-template）
└── .spec/FTDD/VN/
```

## 五、快速上手

1. 给 PRD（±设计稿/原型 + TDD）说「写前端技术方案 / FTDD」。
2. 问档位与必问选型；每个点会追问失败/涨 10 倍/漏项与边界，直到收敛证明齐才定稿。
3. 确认后生成总文档 → 逐模块方案 → 一致性检查 → 归档。

## 六、上下游

PRD/设计稿/原型是需求与结构输入；TDD 接口清单是请求层唯一依据（硬串行）；Frontend-Dev 照图施工。