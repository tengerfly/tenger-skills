# CONTEXT.md —— UI-UX-Design 术语与决策记录

> UI-UX-Design 的术语对齐源与决策日志；概念须与 SKILL/assets/references 一致。

## 一、角色与边界

- 人设：资深 UI/UX 设计总监 + Superdesign 编排器。
- 目标：把 PRD + 布局清单 + 低保真原型变成布局零改动、去 AI 味、风格统一的设计稿。
- 边界：管标准/决策/门禁/归档；不手写 HTML、不做布局决策、不写 PRD/评审/前端代码。

## 二、术语表

| 术语 | 定义 | 排除 |
|---|---|---|
| 布局清单 | Prototype-Design 的载体级结构交付物，与低保真原型 HTML 同为结构真相源 | 不是 PRD；不含区块级 |
| 布局零改动 | 载体/区块/元素/跳转与双输入一致；禁增删移区块 | 视觉可变 |
| 设计稿 | Superdesign 生成的 HTML（projectId/draftId 寻址） | 不是原型/前端代码 |
| 设计规范 | 生成前沉淀的 Tokens+组件规范；源 template → `.superdesign/design-system.md` | 不是风格提案 |
| 风格 DNA | 配色/排版/密度/圆角阴影/交互气质，三方案真差异 | 不只换主色 |
| 基线复刻 | 结构正确、灰调无风格 HTML，作 create-project template | 不是复刻现有 UI |
| 设计任务清单 | 逐页 brief：区块→组件映射（只翻译不改动） | 不是布局清单 |
| 三件套硬依赖 | CLI+授权+SOP，缺一阻塞 | 不是软检测 |
| 迭代路由 | branch/replace/直编三分 | 不是一律重生成 |
| 直编 | 导出→本地精确改→import 回传同 draft | 必须回传云端 |
| 保真约束语 | 生成必带：只用 design-system 内视觉值 | 不是可选项 |
| 生成额度 | Superdesign 计次资源，归用户 | 非无限，花钱先问 |
| 归档 | 定稿导出 `.spec/设计稿/` | 不是 `.superdesign/` |

## 三、决策日志

| # | 日期 | 决策 | 理由 | 状态 |
|---|---|---|---|---|
| D-01 | 09-04 | 职责切分：原型层管结构，设计层管视觉 | 用户指定分工 | ✅ |
| D-02 | 09-04 | 布局清单输入契约由消费方（本 skill）定义 | 接口契约消费方定义 | ✅ |
| D-03 | 09-04 | 底座 Superdesign；skill 名不绑工具名 | 用户指定 | ✅ |
| D-04 | 09-04 | `.superdesign/` 工作 + `.spec/设计稿/` 交付双目录 | CLI 硬约定；评审只认 .spec | ✅ |
| D-05 | 09-04 | 命名 UI-UX-Design | 与仓内命名一致 | ✅ |
| D-06 | 09-04 | 环境即刻安装并授权 | 用户选现在安装 | ✅ |
| D-07 | 09-04 | 设计规范单一事实源；生成必带 context + 约束语 | 规范先行；官方 fidelity 规则 | ✅ |
| D-08 | 09-04 | 风格双通道：默认零额度小样；出稿对比须同意 | credits 归用户 | ✅ |
| D-09 | 09-04 | 场景路由 C 案：布局清单为真相源，不做无实然复刻 | 设计阶段无前端代码 | ✅ |
| D-10 | 09-04 | Q1：双输入契约（载体级清单 + 原型承载区块结构） | 不违背最快产出；原型即结构真相 | ✅ |
| D-11 | 09-04 | 开源系统库更新由用户手动发起 | 用户裁决节奏自控 | ✅ |
| D-12 | 09-05 | 两份执行文档补 PRD 速查表入口 | 防跨位置失同步 | ✅ |
| D-13 | 09-05 | README 决策编号同步；心法自评无需额外注入 | UI-UX-Review 承担独立评审 | ✅ |
| D-14 | 09-05 | 风格决策加 register 语境先决（brand vs product） | 防 Slop 关键先决 | ✅ |
| D-15 | 09-08 | 沉淀「界面状态设计规范（10 大 UI States）」入 design-system 模板 §5.10，规范 Gate 与门禁纳入状态稿检查 | 外部方法论 ui-ux-design.md：企业级前端要求状态稳健，不只 Success 态；规范先行链路 | ✅ |
| D-16 | 09-08 | 原则 2 规范先行补下游依据表述：design-system.md 是 FTDD 与 Frontend-Dev 的视觉规范依据，随 .spec/设计稿/ 交付 | 用户裁决：设计稿 skill 必须给出设计规范，后续前端方案依据该规范 | ✅ |
| D-17 | 09-08 | 建案例库体系：references/case-library/（00-README 总索引 + design-systems 含 awesome-design-md 54 站 / layouts / components / interactions 含动效 / flows 含状态表达 / a11y-checklist）+ patterns/index.md 高频模式速查；条目统一字段（场景→问题→解法→可借鉴点→出处→截图→代码→a11y）+ 元数据标签；SKILL 步骤 3 写六库检索顺序 | 用户裁决：案例库分视觉/布局/交互类补全 skill；资源来自用户整理清单（9 大类 40+）+ 外部 awesome-design-md；审核后补状态表达/图形资产维度与统一元数据 | ✅ |
| D-18 | 09-08 | 案例库补实抓纪律：步骤 3 命中资源须 web_fetch/extract-website 实抓提取要点（1~3 个/场景），失败标注跳过禁编造，写死进 SKILL 步骤 3 与 00-README | 用户质询「设计时会不会真去案例网站查」——索引必须配可执行抓取动作才不是死清单 | ✅ |
| D-19 | 09-08 | 体检修复：00-README「四库分工」→「五库分工」（表格实为 5 行）；patterns/index.md 学径出处路径去掉绕行 `../case-library/../` | Skill-Optimizer 模式④体检（六维机械核验） | ✅ |

## 四、待决问题

Q1~Q3 均已解决（见 D-10/D-11/Workflow D-09）。无待决。