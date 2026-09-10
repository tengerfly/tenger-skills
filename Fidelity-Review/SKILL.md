---
name: Fidelity-Review
description: 页面还原度评审（视觉 + 交互还原）。依据 UI 设计稿（优先 `.spec/设计稿/`，缺失可用外部设计稿）对前端实现页逐页比对：视觉不一致、交互不对、超长文案健壮性问题。只审不改：截图存证，输出分级问题清单（现象/出处/成因/截图/建议），三模式交付——独立调用落盘 `.spec/页面还原评审/`（报告+任务清单+截图）；被 Testing 调用时就地出轻量清单；被 Code-Review 调用时（⑬-前 并行）问题交 Code-Review 合并进 `.spec/代码评审/任务清单.md`（标来源=Fidelity-Review）。浏览器工具硬性前置，全无则报错停用。防死循环：判据 + P0/P1 冻结 + 复核只验本轮 + 轮次上限 3（超限清 P0 后放行）。触发：页面还原度评审、UI 还原检查、视觉走查、对照设计稿查前端页面。
compatibility: Claude Code / Agent SDK / OpenCode
---

# Fidelity-Review —— 页面还原度评审

> IRON LAW：**截图必证**——一切样式 / 视觉 / 溢出问题必须配浏览器截图，无截图的样式问题不算记录。
> 三模式：独立 / Testing 场景 / 代码评审场景（⑬-前 与 Code-Review 并行）。

## 一、定位与铁律

**角色**：对前端实现页对照 UI 设计稿做逐页还原度评审。**只对还原度负责**——不评业务逻辑、接口契约、代码架构（归 Testing / Code-Review）。

**三个评审面**：

1. **视觉还原**：逐页核对布局、层级、颜色、字号字重、间距、圆角阴影、图标图片、状态（含 10 大 UI 状态）、暗色模式、窄屏视口。设计稿为应然，实现页为实然；对比度等可数值定义项（WCAG ≥ 4.5:1）用 axe-core 判定，不靠观感。
2. **交互还原**：核对可点元素能否点击、反馈是否正确、交互方式与设计稿一致（按钮 / 跳转 / Tab / 弹层 / 表单校验）。边界：只到「是否按设计稿还原、是否可用」。
3. **内容健壮性（超长文案专项）**：真实 / 极端长文案下不得溢出容器、遮挡邻元素、换行错乱、挤压布局、异常截断；设计稿排版正常而实现页崩 = 问题。

**与相邻 skill 的边界**：

| Skill | 关系 |
|---|---|
| `UI-UX-Design` | 通道 A 基准生产方；设计稿缺陷回改 |
| `Frontend-Dev` | 被审对象 + 主要修改方（其 `fidelity-guide` 是开发自查，本 skill 是第三方还原验收） |
| `UI-UX-Review` | 评「设计稿 vs PRD/布局清单」，本 skill 评「实现页 vs 设计稿」，不重叠 |
| `Code-Review` | 评代码层契约 / 架构；⑬-前 与本 skill **并行**审前端，本 skill 只出还原度问题并交其合并 |
| `Testing` | 可调用本 skill 做 UI 还原检查（Testing 场景） |

**铁律**：

1. **只审不改**：禁改实现页代码、设计稿、design-system；唯一产出为报告 / 清单 / 截图（或 Testing 轻量清单）。
2. **截图必证**：命名 `<页面>_<问题>_<序号>.png`；交互问题截图表现不了则附操作步骤。
3. **成因必写**：剖析成因（默认样式未对照稿、色值未走 token、容器未加省略 / min-width、flex 溢出、真实文案更长）；推不出标「成因未明」。
4. **方向明确**：给具体修改建议（改哪个文件 / 哪类样式 / 加什么约束）和修改方——实现问题 → `Frontend-Dev`；设计稿自身缺陷 → `UI-UX-Design`；源于 PRD 口径变化 → 双方协商。
5. **浏览器工具硬前置**：任一可用即截图 + 点击验证；**全无 → 报错停止，产出为空，安装后重跑**（策略见 `shared/browser-policy.md`）。
6. **只对还原度负责**：页面起不来即阻塞。

## 二、输入与前置

**设计稿基准双通道**（双基准术语见仓库根 `shared/baseline-terms.md`）：

| 通道 | 来源 | 说明 |
|---|---|---|
| A（优先） | `.spec/设计稿/` | 设计稿 HTML + `design-system.md`，可直接渲染并机械比对 token |
| B（缺失） | 用户指定外部稿 | Figma 导出 / PNG / README / 静态导出；无 token 只能目测 + 刻度换算 |

通道 B 报告须标注「基准=外部设计稿，按像素目测比对」。存在 A 用 A；A 缺失或用户明确给外部稿用 B 并确认。

**输入**：设计稿基准；前端实现页（本地工程 + 启动命令 + URL，或部署 URL）；可选 PRD / 布局清单辅助判断交互该不该有（读速查表建索引后按锚点回原文）。

**三模式输出**：

- **模式一 · 独立调用** → `.spec/页面还原评审/`：`页面还原度评审报告.md`（视觉 + 交互 + 长文案分组，每条含截图引用与修改建议）、`任务清单.md`、`screenshots/`。
- **模式二 · Testing 场景**：不另建任务清单，按 `assets/mini-issue-template.md` 就地出轻量清单交 Testing 汇总。
- **模式三 · 代码评审场景（⑬-前 与 Code-Review 并行）**：报告落 `.spec/代码评审/前端页面还原度评审.md`，问题交 Code-Review **合并进** `.spec/代码评审/任务清单.md`（每条标「来源=Fidelity-Review」）；**不另建清单**，轮次与放行由 Code-Review 闭环统一管理，回退方 = `Frontend-Dev`。

## 三、主流程（7 步）

1. **输入解析与预检**：读 `.spec/设计稿/` 或向用户要外部稿并记录通道；确认实现页目录 / 启动命令 / 逐页 URL（未提供必问，不猜测）；按铁律 5 预检浏览器工具；**确认运行模式**（独立 / Testing / 代码评审并行）。
2. **页面清单 × 基准对齐**：按 `references/design-source-guide.md` 建逐页映射 `实现页 URL ↔ 设计稿页面`，记录响应式断点；通道 A 摘 token 速查，通道 B 记录目测基准；生成比对范围清单交用户确认后再继续。
3. **双开截图 + 点击验证**：相同视口并排截图；逐元素点击记录有反应 / 无反应 / 反应对不对。**独立走查纪律**：只认渲染产物与基准，不参考实现者说明或自查结论；任务重可开独立会话 / 换模型交叉复查。
4. **视觉 + 交互 + 逐区块断言走查**：视觉按 `references/visual-checklist.md`（含设计稿有而实现没有、实现多出的**双向比对**）；交互按 `references/interaction-checklist.md`（可点性 / 反馈 / 方式一致 / 跳转链路）；逐区块断言见 §4.2；另对照 `references/known-issue-patterns.md`（评审方案例库）过一遍，命中即入问题清单。
5. **超长文案专项**：按 `references/overflow-guide.md`，识别动态文本位，用真实业务文案 + 更极端长文案替换后截图判定；给出 min-width / ellipsis / flex 收缩等修改方向。
6. **分级输出报告**：按 `assets/review-report-template.md` 生成报告；每条含编号 / 页面 / 基准出处 / 现象+截图 / 期望 vs 实际 / 成因 / 严重度 / 建议 / 修改方；分组统计 P0/P1/P2。
7. **三模式收尾**：
   - **独立模式**：按 `assets/issue-list-template.md` 生成任务清单（自足可读 + 修复判据 + 修改方 + P0/P1 阻断 + 逐条确认裁决；要改 → `已确认`，不改 → `已忽略` + 理由；复核只验本轮清单）；放行后按 `shared/anti-deadloop.md` §五 判定（P0 双向必沉）——**A 防复发**：还原类问题改 `Frontend-Dev`、设计稿缺陷改 `UI-UX-Design`（记其 CONTEXT D-xx）；**B 检出力**：本 skill `references/known-issue-patterns.md` 按模板加一条（含「检出方法」）。
   - **Testing 场景**：按 `assets/mini-issue-template.md` 就地出轻量清单，不生成任务清单。
   - **代码评审场景**：报告落 `.spec/代码评审/前端页面还原度评审.md`，问题清单交 Code-Review 合并（标来源）；不单独确认、不单独计轮次；**双向沉淀判定交 Code-Review 统一执行**（含本 skill 的 `known-issue-patterns.md`）。

## 四、评审规范

**4.1 严重度分级（只标注，不设门禁）**——P0/P1/P2 定义与处理口径见 `shared/anti-deadloop.md` §三，下表为本域典型示例：

| 级别 | 定义 | 处理 | 典型 |
|---|---|---|---|
| P0 | 整体结构 / 布局严重不符、主视觉走样、核心入口点不动或跳错、长文案大面积崩坏 | 阻断交付，修复并通过复核 | 列表页实现成卡片流且主按钮消失；整页配色脱离设计稿；按钮点了无反应 |
| P1 | 局部偏差明显、单元素不可点、交互方式不同、状态缺失、长文案破坏局部布局 | 必须进任务清单，原则上全修 | 弹框确认按钮点不动；卡片标题两行排版崩开 |
| P2 | 像素级微差、次要细节、轻微换行可接受 | 记录，由用户裁决 | 间距差 2px；图标色偏一档 |

**4.2 逐区块断言（页面级截图无法暴露的局部偏离必须单列）**：标题字号体系一致；空态唯一且间距正确；弹框 / Tab 方向与设计稿一致；Loading 居中；设计稿状态稿（空 / 错 / 禁用 / 断网等）与实现页逐态一致；错误 / 选择状态在切换时重置；文案逐字取自设计稿；待确认等入口位于设计稿指定的 icon 位。

**4.3 防死循环差异**：三招（修复判据 / 分级冻结 / 轮次上限 3）与任务清单状态机定义见 `shared/anti-deadloop.md`；本 skill 差异 = 独立模式超 3 轮不收敛 → 清 P0 后放行，残留 P1 记遗留并告知用户。

## 五、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 无截图报样式问题 | 铁律 2 必配截图 |
| 把业务逻辑当还原度问题 | 归 Testing |
| 与 UI-UX-Review / Code-Review 边界混跑 | 按 §一 边界；⑬-前 并行但各管各域 |
| ⑬-前 另建任务清单 | 交 Code-Review 合并，标来源 |
| 页面起不来仍评审 | 步骤 1 阻塞并提示 |
| 通道 B 声称 token 一致 | 只能目测，报告标注基准 |
| 长文案崩当不是 bug | P1 必录必给改法 |
| 只报现象无成因 / 改法 | 铁律 3、4 |
| 浏览器不可用仍开工 | 硬性预检报错等安装 |
| 漏查实现页多出的内容 | 双向比对（步骤 4） |
| 闭环后不沉淀 | 独立模式收尾做沉淀判定，P0 必沉 |

## 六、资源清单

- `references/visual-checklist.md`、`interaction-checklist.md`、`overflow-guide.md`、`design-source-guide.md`、`browser-guide.md`、`decision-rules.md`
- `references/known-issue-patterns.md`：评审方案例库（闭环沉淀的已知问题模式 + 检出方法）
- `references/case-library/`：像素方法学 + 同行样本（按需加载）
- `assets/review-report-template.md`、`issue-list-template.md`、`mini-issue-template.md`
- `shared/anti-deadloop.md`、`shared/baseline-terms.md`、`shared/browser-policy.md`（仓库根）：公共约定
- `.spec/页面还原评审/`：独立模式归档目录；`.spec/代码评审/`：并行模式报告落点；`CONTEXT.md`：术语 + 决策日志

## 七、运行问题埋点

收尾按 `Skill-Optimizer/references/instrumentation-guide.md` 自查上报 `issue/Fidelity-Review/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `Skill-Optimizer/assets/issue-template.md`；含协作侧）。不确定不记，不打断主流程。
