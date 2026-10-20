---
name: ui-ux-review
description: "UI/UX 设计稿评审。依据 PRD、布局清单、design-system 对设计稿做四维独立复审：载体与结构零改动（防漏+防加戏）、文案与字段一致、视觉规范一致（token 出处）、视觉呈现与可交付质量（真实渲染 + 结构级可点击性）。UI-UX-Design 内部门禁的第三方独立兜底：只审不改，输出四份维度报告 + 汇总 + 单一事实源任务清单至 `.spec/设计评审/`。浏览器工具硬依赖：任一可用即渲染截图存证，全无则报错停用。防死循环：判据 + P0/P1 冻结 + 复核只验本轮 + 轮次上限 3（超限后 P0 残留 BLOCKED；P1 残留只能经授权 CONDITIONAL，不得 PASS。触发：评审/走查设计稿、视觉稿核验、对齐 PRD/布局清单、查视觉规范执行。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: "UI-UX-Review"
  compatibility: "Claude Code / Agent SDK / OpenCode"
---


# UI-UX-Review —— UI/UX 设计稿评审

> IRON LAW：**只审不改**——禁改设计稿 HTML、design-system、PRD、布局清单；唯一产物是 `.spec/设计评审/` 下文件。
> 定位：对 UI-UX-Design 产出的设计稿做**独立第三方复审**，兜底其内部门禁自查盲区。只查问题、找成因、给方向。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

**闭环回流（L2）**：P0/P1 条目要标「已沉淀」前，必须先回流 1 条评测用例，并在该用例声明里用 `issueRef` 指回本条问题（值＝本条问题的仓库相对路径，形如 issue/<skill>/<日期>/<NN>-<标题>.md）；没有这条用例就按「未验证」处理，优化状态停在待处理/处理中，不得写「已沉淀」。
判据与字段口径的单一来源是仓库根 `governance/eval-spec.yaml`（`caseTiers.L2` + `issueRef` 节），机械核对由 `scripts/eval/relay.py` 执行；本节只承接义务，不复述其条文（仓库级工具：宿主副本若不含 `governance/` 与 `scripts/`，改人工核对并在报告注明降级）。

## 评审上下文隔离（执行必需）

> 口径：仓库根 `../../shared/review-context-isolation.md`。评审判断只发生在隔离上下文；参与过设计稿产出、修订、自检或评审调度的上下文只能编排，不得自审。

**评审单元 = 四维**：载体与结构零改动 / 文案与字段一致性 / 视觉规范一致性 / 视觉呈现与可交付质量。每维派 1 个独立 fresh 评审子代理（互不可见），汇总由独立汇总子代理完成（只读四份维度报告 + `assets/summary-template.md`）。

**三种形态，职责不得混用**：

| 形态 | 谁执行 | 只做什么 | 不做什么 |
|---|---|---|---|
| A 编排形态 | 产出上下文 / Workflow | 输入解析、上游闸门核对、映射基准、建评审包、派发、收产物核验、按规则落 Gate | 不做任何维度判断 |
| B 维度评审形态 | 隔离子代理（每维 1 个） | 只跑本维度清单，出本维度报告 | 不读其他维度报告、不读内部门禁自检结论、不参考生成过程 |
| C 汇总形态 | 隔离子代理（独立汇总者） | 只读四份维度报告 + 模板，出汇总报告 / 任务清单 / Gate 建议 | 不自行复查维度、不引入新问题 |

- **评审包**：按 `../../shared/templates/review-package.md` 落 `.spec/设计评审/评审包-REV-<YYYYMMDD>-<NN>.md`，只含被审对象精确版本 + 判据集 + 清单/模板 + 边界（维度 / 轮次）+ F1 已确认项 + 输出契约 + 隔离声明；**禁止**放入产出过程、草稿、自检结论、未确认猜测或「已知问题」引导。
- **可选**：先派 1 个取证子代理统一产出截图 / 跨页宽度实测表 / 可见层内部语扫描（机械取证），再派四维评审子代理消费其产物；不强制。
- **无隔离能力**：写评审包 + `dispatch-prompt.md` 交新会话执行，主会话停住不自行评审；仍无隔离执行能力 ⇒ `BLOCKED`（owner / requiredInput=隔离执行能力 / clearCondition）。**不得在同一上下文四维混做，也不得在同一子代理里换「评审者角色」冒充隔离。**

## B 稿复核口径（A 不变）

当归档 README 的「稿源」标记为 AI 自写（B）时，先读 `ui-ux-design/references/self-write-review-gate.md` 与本次需求上下文。以已确认业务/结构/Token 和真实渲染判质量，不套用 A 的云端导入格式、相对链接禁令、em-dash 零容忍或不适用的风格偏好。B 的局部修改只查变更与必要关联回归；新多页稿仍覆盖本次全部交付页。新方向的审美选择不能改写业务需求。

本 Skill 的只审不改、真实浏览器硬依赖、独立复核和正式 Gate 规则不变；无浏览器不能给待验收 B 草稿补发视觉通过。A 稿继续原规则。消费需求按 `../../shared/requirements-context.md` 固定版本、索引定位后读相关原文。

## 一、定位与铁律

**四个评审维度**：

1. **载体与结构零改动**：对照布局清单，独立页面、弹框、抽屉、区块、元素、跳转逐项一致（防漏）；无出处的区块 / 按钮 / 提示 / 装饰一律不得出现（防加戏）。结构不对 = 视觉阶段越权改布局，打回。
2. **文案与字段一致性**：对照 PRD / 布局清单逐字比对标题、CTA、列名、标签、提示语；不得自行添加多余文案。
3. **视觉规范一致性**：对照 `.spec/设计稿/design-system.md`（**归档副本即交付基准**；`.superdesign/design-system.md` 为 CLI 工作源，仅需追溯原文时对照）——所有视觉值（色值 / 字号 / 字重 / 间距 / 圆角 / 阴影 / 组件 / 图标）必须有 token 出处，无规范外值；反 AI 味 12 条目检（清单见 `references/visual-spec-consistency-checklist.md`）。
4. **视觉呈现与可交付质量**：真实渲染设计稿 HTML——规范是否落地、逐入口做**结构级可点击性**验证（真实 `<a href>` 或等价触发；像按钮却点不动 = 缺陷）、控制台报错 / 死链 / 遮挡 / 资源加载失败、关键缺陷截图。
   - 边界：不验真实业务逻辑 / 数据 / 弹框开合逻辑；可点击性只到「入口存在且可点、href 去向与站点地图一致」。

**铁律**：

1. **只审不改**：唯一产物为 `.spec/设计评审/` 下文件。
2. **成因必写**：每条结合对照源与 HTML 剖析（漏读区块、token 被绕过、直编改坏 href、弹框只做静态视觉）；无法推导标「成因未明」，禁臆造。
3. **方向明确**：设计稿问题 → `UI-UX-Design`；布局清单与 PRD 冲突 / 漏载体 → `Prototype-Design`；PRD 自相矛盾 → `PRD-Design`；口径不一 → `双方协同`。
4. **浏览器工具硬前置**：任一可用即渲染截图 + 点击验证；**全无 → 先按 `../../shared/browser-policy.md` §五 获取，仍全无 → 报错停止，不产出评审文档**（策略见该文件 §一/§二）。
5. **单一事实源**：全量问题去重后只收口 `任务清单.md`，初始全部 `待确认`。
6. **第三方独立兜底**：不采信 UI-UX-Design 门禁的「✅ 已通过」；只认对照源 + 真实渲染独立复核。

**适用范围**：适用已归档的设计稿复审；不适用评审 PRD / 原型 / 技术方案，也不改设计稿。

## 二、输入与前置

| 项 | 说明 | 缺失处理 |
|---|---|---|
| PRD（有速查表先建索引） | 需求基准 | ⛔ 停下提示 |
| 布局清单（载体级） + **低保真原型 HTML（区块级）** | **结构基准**：布局清单定载体、原型定区块实物（结构真相源见 `../../shared/baseline-terms.md`） | ⛔ 停下提示 |
| `.spec/设计稿/design-system.md`（**归档副本即交付基准**） | 视觉规范基准（`.superdesign/design-system.md` 为 CLI 工作源，仅追溯时对照） | ⛔ 停下提示 |
| 设计稿工程（HTML + README） | 被审对象 | ⛔ 停下提示 |
| **上游闸门有效性**（`manifest.yaml` 中 PRD / 原型 / design-system 各条的 `status`、`version`、`gate`、`allowDownstream`） | 输入必须是**现行批准版本**，不只是文件存在（`../../shared/gate-policy.md` §6） | 任一 `SUPERSEDED` / 非 `PASS` / `false` → ⛔ 停下，本周期不得出放行 Gate |
| **上游内容指纹**（同条 `contentDigest`；跑 `python scripts/validate_core.py gate --project-root <项目>` 即机械复算；仓库级校验器，宿主副本无 `scripts/` 时改人工复核并注明） | 字段全绿只证明**批准过**，不证明**正文还是那份**。批准后被盗改的基线，字段层永远看不出来（`gate-policy.md` §6 第 6 条） | 任一 `contentDigest`/`subjectDigests` mismatch → 所依据的基线已不存在：本轮结论对漂移输入**判失效**并重跑；重签摘要须有覆盖该次改动的批准记录 |
| 浏览器工具（**硬依赖**） | 渲染截图 + 点击验证 | 全无 → 报错停止 |

**输出**（`.spec/设计评审/`）：四份维度报告、`设计稿评审汇总报告.md`、`任务清单.md`（`待确认` → `已确认` → `已修复`/`已忽略`）、`screenshots/`（硬性）、**`跨页宽度实测表`**（多页交付硬性，逐页含导航外壳 / 页内标题栏 / 主内容列三组值 + 宽屏两档，随第四维报告落盘；无此表则 §七 各条只能标「未验证」）、**`可见层内部语扫描表`**（多页交付硬性，默认渲染态命中清单 + 计数 + 走查开关核验，随第四维报告落盘；无此表则 §八 只能标「未验证」）、**`上游闸门核对表` + `时序核查`**（硬性，随汇总报告落盘；无此表则 Gate 只能记 `BLOCKED`（缺上游闸门核对证据），不得 `PASS`）、**`评审包-REV-<YYYYMMDD>-<NN>.md` + `dispatch-prompt.md`**（硬性，派发隔离评审子代理前落盘）、**`§0.5 评审上下文隔离记录`**（硬性，随汇总报告与各维度报告落盘；缺记录或 `producedByContextInvolved` 非 false ⇒ Gate 只能记 `BLOCKED`（缺评审隔离证据））。

## 三、主流程（9 步 · 步骤 0 = 隔离派发）

0. **〔REQUIRED · 隔离派发〕**：先判定角色——本上下文参与过设计稿产出、修订、自检或评审调度 ⇒ 只做编排，不做维度判断。按 `../../shared/templates/review-package.md` 落评审包 + `dispatch-prompt.md`，派发四维各 1 个 fresh 评审子代理（互不可见）+ 1 个独立汇总子代理；无子代理能力 ⇒ 写包交新会话、主会话停住；仍无 ⇒ `BLOCKED`（缺隔离执行能力）。派发后把子代理 id 回填评审包「评审者」与各报告 §0.5。
1. **〔编排者〕资产解析、上游闸门核对与浏览器预检**（编排者 / 汇总者可做，不含维度判断）：读取上表输入，缺失即停。**〔REQUIRED · 开工前闸门核对〕**逐条读 `.spec/manifest.yaml` 中本评审的上游 artifact（PRD / 原型 / design-system）的 `status`、`version`、`gate`、`allowDownstream`、`blockedBy`：任一为 `SUPERSEDED`、`gate` 非 `PASS`、或 `allowDownstream: false` ⇒ 本周期 Gate **只能记 `BLOCKED`**（命名缺失输入 + owner + 清除条件）、`allowDownstream: false`、写 `blockedBy`；**「判据全闭」单独作为事实记录，不作为放行结论**，限定条件只能落字段、不得写进注释或正文（下游只读 `gate`/`allowDownstream`，读不到注释；口径 `../../shared/gate-policy.md` §6）。此步在开工前完成，避免在作废基线上跑完一轮才发现不能放行。再按铁律 4 预检并记录工具。
2. **〔编排者〕建立映射基准**（编排者 / 汇总者可做，不含维度判断）：提取 PRD 页面 / 文案 / 跳转、布局清单载体划分、design-system token 速查；产出矩阵 `PRD 功能点 / 布局载体 ↔ 设计稿页面（draftId 版本）`。
3. **〔维度评审子代理 · 本维度取证〕渲染走查 + 静态源码审查**：静态服务渲染逐页截图（异常处截入 `screenshots/`）；逐入口点击验证；静态读 HTML 结构 / `<a>` / CSS token / 脚本作证据。**〔REQUIRED · 多页交付〕跨页宽度实测**：真实浏览器逐页量（**全局导航外壳 x·width——跨页必须全等** / 页内标题栏内容行内缘 / 主内容列 x·width·中心 / 1440 与 1920 两档主列宽）并横向比对，按 `references/rendered-quality-checklist.md` §七 出「跨页宽度实测表」；**量测前先按 §5.11 分角色**（承载跨页入口的顶栏/侧栏＝导航外壳，走跨页恒定判据；仅含本页 h1/页头＝页内标题栏，走与内容列对齐判据）——**拿"顶栏跟内容列对齐"去判导航缩宽，会把缺陷判成正确**。**〔REQUIRED〕界面可见层内部语扫描**：默认渲染态（未开走查模式）下按 §八 扫原型说明层（编号牌 / `【设计假设】` / `台账 §x` / `AC-Mxx` / 元信息徽标 / 演示切换条 / 清单对照块）的计算样式，输出命中清单 + 计数，并实测走查开关能否恢复可见。没有这两张表，§七/§八 各条一律标「未验证」，不得计入已查。两条通道独立完成、最后合并互证；**不参考生成过程，不轻信内部门禁**。
4. **〔维度评审子代理 · 本维度检查〕四维对照评审**（每个子代理只跑本维度清单，不读其他维度报告与内部门禁自检结论）：按本维度对应清单（`layout-freeze` / `copywriting-consistency` / `visual-spec-consistency` / `rendered-quality` 四份清单各归其维）逐条过筛（每份含**查漏 + 查多**）；**量测型检项（`rendered-quality-checklist.md` §七 跨页不变量、§八 可见层内部语扫描）必须拿步骤 3 的实测表作证据，缺证据只能标「未验证」，不得判「已查」**；另对照 `references/known-issue-patterns.md`（评审方案例库）过一遍，命中即入相应维度清单。
5. **〔维度评审子代理 · 出报告〕四份维度报告**：四维子代理各按 `assets/dimension-review-template.md` 落盘本维度报告（元数据须填评审上下文与评审包摘要）。
6. **〔汇总子代理〕汇总 + 出 Gate**：只读四份维度报告，按 `assets/summary-template.md` 合并去重、归纳跨页面共性问题（如整批 token 偏差）、统计 P0/P1/P2。**汇总报告必含「上游闸门核对」表**（上游 artifact id｜当时版本｜mtime｜`gate`｜`allowDownstream`｜`contentDigest` 复算结果｜结论）**与「时序核查」节**（基线作废时刻 vs 被审产物 mtime）——缺此表本周期 Gate 只能记 `BLOCKED`（缺上游闸门核对证据），不得记 `PASS`。收口语固定：基线有效时写「本周期判据全闭（轮次 n/3），放行 <Gate>」；基线已作废或上游关闸时写「本周期判据全闭（轮次 n/3）；放行状态 `BLOCKED`，缺 <上游批准 + 增量>」，**不得留下裸 `PASS` 字样供下游截读**。**〔REQUIRED · 隔离证据收口〕** 汇总报告或任一维度报告缺 §0.5 隔离记录、`reviewerRef`/`packageDigest` 为空、或 `producedByContextInvolved` 非 false ⇒ 本周期 Gate 只能记 `BLOCKED`（缺评审隔离证据），不得 `PASS`/`CONDITIONAL`。
7. **〔编排者收账〕任务清单 + 归档**（不做评审判断）：按 `assets/issue-list-template.md` 生成任务清单——每条自足可读（出处 + 现象 + 成因 + 方向）、附修复判据、状态 `待确认`、标注修改方；P0 阻断且须用户确认；P1/P2 由执行方按 `../../shared/ruling-policy.md` 裁决（修 → `已确认`；延/弃 → `已忽略` + 理由 + 回退方式，记 `.spec/rulings.md`），**不逐条等用户**，用户可事后否决；复核只验本轮清单，不无限新增。**证据回勾自检（出报告前必做，防规则空转）**：把本轮引用的清单条目**逐条回勾**有无对应证据产物（截图 / 实测值 / 命令输出 / 实测表）；无证据的条目一律标「未验证」并计入交付边界，**不得计入「已查」**（案例库模式 5）。**问题日志**：归档同时在项目 `.spec/问题日志.md` 台账追加一行索引（日期｜来源｜问题产物｜轮次｜状态｜反哺出口；格式见 skill 源仓库 `../../shared/templates/problem-log-template.md`）。
8. **〔编排者收账〕双向沉淀判定**（不做评审判断）：放行后按 `../../shared/anti-deadloop.md` §4 双向沉淀执行——**A 防复发**：设计稿问题改 `UI-UX-Design`、布局 / 载体问题改 `Prototype-Design`、PRD 口径问题改 `PRD-Design`（记其 CONTEXT D-xx）；**B 检出力**：本 skill `references/known-issue-patterns.md` 按模板加一条（含「检出方法」）。改不了的落 `../../issue/<目标 skill>/<日期>/`（来源=评审闭环，写明双向落点）。判定结果记入汇总报告「沉淀判定」节。

> 门禁闭环、防评审死循环三招（判据 + P0/P1 冻结 + 复核只验本轮）+ 轮次上限 3：满 3 轮未收敛 ⇒ 残留 P0 记 `BLOCKED`；残留 P1 不得 `PASS`，仅可完整授权 `CONDITIONAL`；不自动第 4 轮（口径 `../../shared/anti-deadloop.md` §3 与 `../../shared/gate-policy.md` §3/§4）。

## 四、评审规范

**4.1 严重度分级（只标注，不设门禁）**——P0/P1/P2 定义与处理口径见 `../../shared/gate-policy.md` §1，下表为本域典型示例：

| 级别 | 定义 | 处理 | 典型 |
|---|---|---|---|
| P0 | 结构错位、主流程入口不可点、视觉严重偏离规范、核心文案大面积冲突 | 阻断；修复并通过复核 | 布局规定的弹框无入口；跳转全死链；整页配色另起炉灶 |
| P1 | 局部结构偏差、文案逐字不符、规范局部未执行、单入口死元素、控制台报错 | 必须进任务清单，原则上全修 | 文案不同字；少一张统计卡；按钮无 href |
| P2 | 非关键润色、次要视觉建议、边缘渲染瑕疵 | 记录，执行方裁决（默认延后，附理由与回退） | 留白可斟酌；提示可精炼 |

**4.2 与内部门禁的关系**：本 skill 是 UI-UX-Design 内部门禁的**第三方兜底**——不采信其自查结论，独立复核；发现的问题照常入清单，按铁律 3 归指派修改方。

## 五、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 评审时改设计稿 / 对照源 | 只记问题，给方向（铁律 1） |
| 采信内部门禁「已通过」 | 独立复核（铁律 6） |
| 问题无成因 / 无方向 | 按铁律 2、3 补齐 |
| 只查漏、不查加戏 | 四维清单每份都查漏 + 查多 |
| 只渲染截图、不读源码 | 双通道互证（步骤 3） |
| 清单有条目却没跑量测就判通过（规则空转） | 量测型检项必须带实测表/证据，否则标「未验证」（步骤 3 REQUIRED + 步骤 7 证据回勾） |
| 浏览器不可用仍开工 | 报错停止 |
| 把业务逻辑 / 数据当设计问题 | 本 skill 只到结构级可点击性 |
| 任务清单分散 | 单一事实源（铁律 5） |
| 四份报告维度混写 | 一维一份，汇总再合并 |
| 产出/自检上下文直接做四维评审（同上下文自审） | 评审判断只在隔离上下文：四维各派 1 个 fresh 评审子代理 + 独立汇总子代理；只给评审包；无隔离能力写包交新会话，仍无 ⇒ `BLOCKED`（见「评审上下文隔离」节） |
| 判据全闭就出 `PASS`（没读上游闸门） | 步骤 1 REQUIRED 先核上游 `status`/`version`/`gate`/`allowDownstream`；基线 `SUPERSEDED`／上游关闸 → 本周期只能 `BLOCKED`（步骤 6 收口语固定） |
| 用注释或正文写「本 `PASS` 仅对旧基线成立」 | 限定只能落 `gate`/`allowDownstream`/`blockedBy` **字段**——下游读字段，读不到注释（`../../shared/gate-policy.md` §6） |
| 闭环后不沉淀 | 步骤 8 双向沉淀判定，P0 必沉 |

## 六、资源清单

- `references/layout-freeze-checklist.md` / `copywriting-consistency-checklist.md` / `visual-spec-consistency-checklist.md` / `rendered-quality-checklist.md`：四维清单
- `references/browser-inspection-guide.md`：浏览器渲染走查与点击验证细则（步骤 3/4 用）
- `references/known-issue-patterns.md`：评审方案例库（闭环沉淀的已知问题模式 + 检出方法）
- `../../shared/review-context-isolation.md`、`../../shared/templates/review-package.md`：评审上下文隔离契约与评审包模板（隔离派发 / 汇总用）
- `assets/dimension-review-template.md` / `summary-template.md` / `issue-list-template.md`
- `../../shared/anti-deadloop.md`、`../../shared/browser-policy.md`、`../../shared/baseline-terms.md`（仓库根）：公共约定
- `.spec/设计评审/`：归档目录（含 `screenshots/`）

## 七、运行问题埋点

收尾按 `../../shared/instrumentation-guide.md` 自查上报 `../../issue/UI-UX-Review/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../shared/templates/issue-template.md`；含 Superdesign / UI-UX-Design 侧）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `UI-UX-Review` while exposing it through the v2 Skill contract.

## Trigger

Run when the user explicitly requests this capability or when `WorkFlow/` routes a compatible stage to this wrapper.

## Inputs

- the user's request and confirmed scope;
- current project artifacts, evidence, decisions, and `.spec/workflow.yaml`;
- the retained legacy body, references, assets, and scripts in this directory.

## Preconditions

- read `../../shared/skill-contract.md`, `../../shared/gate-policy.md`, and `../../shared/anti-deadloop.md`;
- read `.spec/manifest.yaml` and `.spec/workflow.yaml` when a project is available;
- verify scope, authorization, repository boundaries, and required upstream artifacts;
- confirm review-context isolation: the producing/reviewing context dispatches fresh isolated reviewers with a review package; if isolation is unavailable ⇒ new session or `BLOCKED` (see `../../shared/review-context-isolation.md`);
- do not overwrite unrelated or uncommitted files.

## Responsibilities

- execute the retained domain capability within its stated scope;
- translate legacy outputs into the current artifact, evidence, decision, and Gate vocabulary;
- record execution, traceability, residual issues, and the next action;
- route work outside this wrapper to the responsible domain Skill.

## Non-goals

- do not silently change product decisions, scope, or acceptance criteria;
- do not invent missing facts, evidence, approvals, or test results;
- do not use legacy Gate values or legacy state files as current truth;
- do not delete retained compatibility material.

## Procedure

1. Read the request, current state, manifest, and upstream handoff.
2. Load only the retained legacy resources needed for this execution.
3. Execute the domain action and keep assumptions separate from evidence.
4. Validate the output against its repair or acceptance criteria.
5. Register artifacts, evidence, decisions, and open items.
6. Write the execution record and `.spec/workflow.yaml`.
7. Emit exactly one Gate and one explicit next action.

## Outputs

- the domain artifact, report, code change, test evidence, or routed task defined by the retained capability;
- `artifactRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, `gate`, and `nextAction`;
- the review package (`.spec/设计评审/评审包-REV-<YYYYMMDD>-<NN>.md`) and `dispatch-prompt.md`, plus each report's §0.5 isolation record (`isolationMode`, `reviewerRef`, `packageDigest`, `parentExecution`, `producedByContextInvolved: false`, `verifiedArtifacts`);
- a failure route when the wrapper cannot complete safely.

## Evidence

Use direct source files, command output, test results, screenshots, dated external sources, or explicit user decisions. Label conclusions as `FACT`, `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, `RECOMMENDATION`, `DECISION`, or `OPEN`. A recommendation is not approval. Review isolation evidence (review-package digest, reviewer reference, reviewer-produced reports/screenshots/measurement tables) must be verified by the orchestrator; a reviewer's self-report is not evidence.

## Gate

Use only `PASS`, `CONDITIONAL`, or `BLOCKED`. `PASS` requires complete inputs and artifacts with no unresolved P0/P1. Residual P0 is always `BLOCKED`. Residual P1 is never `PASS` and may be `CONDITIONAL` only with `exceptionId`, `risk`, `owner`, `dueAt`, `remediation`, `allowDownstream`, and `approvalRef`. Three review rounds are the maximum; never force-pass or start an automatic fourth round.

## Failure Route

If evidence, authorization, scope, or an upstream Gate is missing, set `BLOCKED`, name the missing item and owner, and route to the responsible upstream Skill. If the issue is outside this wrapper's boundary, stop and route it rather than improvising.

## Downstream Contract

Downstream Skills may consume only manifest entries whose status and Gate allow downstream use. They must read `sourceRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, and `nextAction`; they must not infer approval from chat context or file existence.

## State Changes

Record the old state, new state, actor, timestamp, reason, evidence references, Gate, and next action in `.spec/workflow.yaml`. The exact state names come from `governance/state-registry.yaml` in the source repository; an installed copy without that repository must use the state names already present in the project `.spec/workflow.yaml` and must not invent new states.
