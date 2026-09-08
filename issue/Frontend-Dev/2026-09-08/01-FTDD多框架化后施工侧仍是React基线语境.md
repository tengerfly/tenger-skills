# FTDD 多框架化后 Frontend-Dev 施工侧仍是 React 基线语境

> 归属 skill：`Frontend-Dev` ｜ 日期：2026-09-08 ｜ 来源：体检

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P1 |
| 标签 | 流程缺陷、接口契约 |
| 优化状态 | 待处理 |

> 等级口径：P0 方法论硬伤/每次必犯/阻塞；P1 明显影响/高频；P2 轻微/建议

## 现象

同日（2026-09-08）FTDD 完成选型机制重构（D-07）：端形态与技术框架每次必问，可选 Vue3 / Taro / uni-app / React Native / Electron（Flutter 备选）。但施工侧 Frontend-Dev 的指南体系仍是 React 基线语境：

- `SKILL.md` §四端差异表「工程：Vite + React SPA」「路由：React Router v6」；§六技术栈锁定组件库推荐 Ant/Arco/Naive（React 系）；
- `references/architecture-guide.md` / `code-style-guide.md` / `test-guide.md` / `tech-stack-guide.md` 全部以 React hooks + Vitest + RTL 表述，无 Vue（Pinia/组合式函数/VTU）、Taro、uni-app、RN、Electron 的施工等价指引。

## 期望 vs 实际

- **期望**：FTDD 选定任意受支持框架后，Frontend-Dev 能按选型获得对应框架的施工指引（逻辑层/组件/路由/状态/请求/测试的框架等价写法），施工不回退到 React 默认。
- **实际**：FTDD 选 Vue3/Taro/uni-app 等 → Frontend-Dev 只有 React 指南，Agent 大概率按 React 语境施工或自行发挥。

## 修复方向

后续专项优化 Frontend-Dev（建议单独会话执行，不宜顺手大改）：

1. SKILL §六技术栈锁定补「框架施工指引路由」：按 FTDD 选型分发到对应施工指南；
2. references 增加框架等价映射（逻辑层 hooks↔组合式函数、测试 RTL↔VTU/RNTL、状态 Zustand↔Pinia、请求 fetch↔Taro.request/uni.request/dio）——可在现有 guide 加「框架等价映射」节而非重写；
3. 铁律/错误对照表补「施工框架与 FTDD 选型不一致 | 阻塞对齐」。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | （待处理） |
| 沉淀位置 | （待处理） |
| 忽略理由 | — |
