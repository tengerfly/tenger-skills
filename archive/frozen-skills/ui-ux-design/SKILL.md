---
name: ui-ux-design
description: "UI/UX 设计稿生成（双路径：Superdesign 云端 / AI 自写）。A 路径沿用 PRD/原型、三套风格方案、云端生成和原门禁；B 路径按新设计/延展/局部修改裁剪，复用已确认规范，生成并验证本地 HTML。用户指定自写时直接走 B；否则探测 Superdesign，有额度走 A，不可用转 B。额度即预算，花钱动作先问。触发：生成设计稿/UI 设计/视觉稿/把原型变成设计稿。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: "UI-UX-Design"
  compatibility: "Claude Code / Agent SDK / OpenCode"
---


# UI/UX 设计稿生成 Skill（双路径：Superdesign 云端 / AI 自写）

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

**闭环回流（L2）**：P0/P1 条目要标「已沉淀」前，必须先回流 1 条评测用例，并在该用例声明里用 `issueRef` 指回本条问题（值＝本条问题的仓库相对路径，形如 issue/<skill>/<日期>/<NN>-<标题>.md）；没有这条用例就按「未验证」处理，优化状态停在待处理/处理中，不得写「已沉淀」。
判据与字段口径的单一来源是仓库根 `governance/eval-spec.yaml`（`caseTiers.L2` + `issueRef` 节），机械核对由 `scripts/eval/relay.py` 执行；本节只承接义务，不复述其条文（仓库级工具：宿主副本若不含 `governance/` 与 `scripts/`，改人工核对并在报告注明降级）。

## 入口分流（先执行，避免混用规则）

- 用户明确指定 AI 自写 → 直接读取 `references/self-write-sop.md`，不探测或调用 Superdesign。
- 未指定时仍按下方步骤 1 探测 A 的环境/额度；满足则沿用原 A 流程，任一不满足则进入 B SOP。不在同一任务中混合云端和本地稿源。
- **B 路径转入后在其 SOP 内完成输入、规范、生成、检查和归档，不继续执行下方 A 的步骤 2–9、A 专属铁律、直编契约、审美禁令或模板门禁（铁律 4 的 ①②③ 文案分类与结构冻结义务在 B SOP 中重述并适用）。** B 的前置与优先级见 SOP，检查只用 `references/self-write-review-gate.md`。
- 以下保留 A 主流程与兼容说明，A 的额度/确认/导入/回传/评审不变。B 不因任务轻量降低安全、业务保真或证据诚实，也不以此改变 A 的行为。

> 〔A 路径专属 Iron Law〕**布局零改动 + 规范先行 + 第一版不算数**——布局清单与低保真原型是结构真相源；设计规范未确认前禁止任何生成调用；A 路径生成的第一版都是草稿，必须过自检环 + pre-flight 才算数。
> 本 skill 是设计总监 + 编排器：管标准、决策、门禁、归档。生成本体双路径：**A = Superdesign CLI 云端出稿**（`references/superdesign-sop.md`）；**B = 会话模型 AI 自写**（`references/self-write-sop.md`，无额度时的默认）。

## 一、定位与铁律

**四条通用铁律**（路径专属 Iron Law 另见 §三 步骤 1 与 B SOP）：

1. **布局零改动**：载体、区块、元素、跳转逐项与布局清单 + 低保真原型一致；只改好不好看，**不碰有什么 / 在哪 / 怎么跳**。布局有问题 → 停下回 Prototype-Design。
2. **规范先行**：任何生成前设计规范必须已确认；每次生成必带规范 + 保真约束语。`design-system.md` 是下游 FTDD 与 Frontend-Dev 的视觉规范依据，随 `.spec/设计稿/` 交付。
3. **额度即预算**：变体数量、生成轮次、花钱动作**永远先问用户**；额度不足不是阻塞理由——转 B 路径（AI 自写）继续。
4. **设计稿不是原型换皮**：原型是「快速表达需求」的沟通装置，设计稿是「按 UI 角度把产品做出来」的交付物。铁律 1 冻结的是**结构**（有什么 / 在哪 / 怎么跳），**不冻结呈现判断**——文案措辞、信息层级、视觉权重、注记去留都必须由 UI 重新判断。**以「与原型文案/结构逐字一致」当验收判据＝违反本条**（该判据会把 UI 判断判成「漂移缺陷」，等于取消设计）。

   **原型文字分三类，只有第 ① 类逐字保真**：

   | 类 | 判据 | 处理 |
   |---|---|---|
   | ① 已批准产品文案 | PRD／布局清单逐字规定的界面文字（按钮标签、状态名、提示语、错误文案） | **一字不差**（门禁 ④ 逐字对账） |
   | ② 原型说明层 | 原型为「把意思表达出来」写的解释性文字：`【设计假设】`、`PRD 未写`、`台账 §x`、`§6.4 检查点`、`AC-Mxx`、`U-xxx` 编号牌、`（示意／走查占位）`、`默认首屏` 这类元信息徽标、演示切换条、清单对照块 | **不得出现在界面可见层**；改挂到默认关闭的走查模式（见下） |
   | ③ 原型占位口语 | 结构对但口吻是写给评审者看的（"此处留占位 —，不自造标题"） | 按产品文案规范**重写成人话**，不原样搬运 |

   **② 类的可追溯性不许丢**：注记层用 `body` 级开关承载（默认 `display:none`，走查模式打开后恢复可见），既保 UI-UX-Review／Fidelity-Review 的「清单行 ↔ 界面元素」映射证据，又不污染产品视图。**禁止直接删除**（删了就断追溯）。

**适用范围**：适用「PRD + 布局清单 + 低保真原型齐备，生成设计稿 / UI / 视觉稿」；不适用画原型（Prototype-Design）、写 / 评审需求（PRD-Design / PRD-Review）、评审原型（Prototype-Review）、实现前端（Frontend-Dev）、海报 / Logo / 营销素材。

## 二、输入与前置

| 项 | 说明 | 缺失处理 |
|---|---|---|
| **环境（A 路径三件套）** | CLI 已装（`superdesign --version`）、账号已授权（`auth status`）、SOP 可读（`references/superdesign-sop.md`）。**B 路径仅需浏览器工具**（自检环截图） | A 三件套或额度任一不过 → **转 B 路径**（路由见步骤 1），不阻塞；B 无浏览器 → 降级源码机械检查 + 用户确认，README 注明 |
| 布局清单（载体级：宿主 / 入口 / 出口齐全、PRD 页面防丢弃） | 结构契约 | ⛔ 缺一阻塞；字段缺失就地问，**不得脑补** |
| 低保真原型 HTML（+ `原型/README.md` 佐证端类型/跳转） | 区块结构实物 | ⛔ 缺一阻塞 |
| PRD（有速查表先建索引） | 文案来源（按锚点取，**一字不差**） | 缺则按布局清单推进并标注 |
| `.spec/设计评审/任务清单.md` | `已确认` 且修改方为本 skill 的任务逐条纳入 | 无则跳过 |
| 浏览器工具（〔A〕仅截图增强；〔B〕自检环关键，见上） | 截图存 `screenshots/` | 不可用则降级并在归档 README 注明（策略见 `../../shared/browser-policy.md`） |

**双输入校验**按 `assets/layout-inventory-contract.md` 执行。

**目录分工**：〔A〕`.superdesign/` = 工作目录（design-system + 基线复刻 + `resume.json`），**不是交付物**；〔B〕无工作目录，design-system 直接落交付目录。`.spec/设计稿/` = 评审与 PIPELINE 唯一认的交付物（〔B〕下同时是唯一事实源，无云端副本）。

## 三、主流程（9 步 · 4 Gate）

```
输入 → ◉1 环境检测与路径路由 → 2 输入解析 → 3 风格情报 → ◉4 风格决策 → ◉5 设计规范
→ 〔A〕6 项目创建 + 7 逐页生成（云端） → ◉8 质量门禁 → 9 落盘归档
〔B〕步骤 1 分流后 → 独立 self-write-sop（不接 A 步骤 2–9）
```

**1. ◉ 环境检测与路径路由 Gate**：先验 A 路径三件套 + **额度探测**（轻量命令实测或用户告知；报无额度 / 失效即视为不过）。全过 → **A 路径**（Superdesign 云端）；任一不过 → 一句话告知用户后转 **B 路径**（AI 自写，按 `references/self-write-sop.md`），**不阻塞**。路径一经确定全程不混用（不 A 出首稿又 B 延展）。

**2. 输入解析**：纳入评审任务清单；执行双输入校验；**逐页读原型 HTML，按视觉顺序提取区块行（区块 / 组件 / 内容 / 交互）——结构只翻译不改动**；**逐行按铁律 4 的 ①②③ 给原型文字分类**（① 逐字保真 / ② 移出可见层 / ③ 重写），分类结果随设计任务清单一并登记，未登记的行默认按 ① 处理并标 `OPEN`；展开设计任务清单（`assets/design-task-list-template.md`）。

**3. 风格情报**：〔A〕Superdesign 灵感库（`search-prompts` → `get-prompts --full`，先索引后取全文）；〔B〕参考资源按独立 SOP 按需加载；〔A〕**案例库体系**按序检索（总索引 `references/case-library/00-README.md`）：`patterns/index.md` 高频模式 → `case-library/flows.md` 用户流与状态表达 → `layouts.md` / `components.md` / `interactions.md` → `case-library/design-systems.md` + `open-source-design-systems.md` 体系基线 → `style-case-library.md` 自有深案例与踩坑。外部资源取用前**验证可达与许可**；命中资源须**实抓提取**（`web_fetch` / `extract-website`，1~3 个/场景；失败标注跳过禁编造）；**参考 ≠ 照抄**，提取值仍须过步骤 5 用户确认；案例库更新由用户手动发起。

**4. ◉ 风格决策 Gate**：**先出一行「设计读」**（读作：〈产品类型〉给〈受众〉，走〈气质〉语言；受众与气质取自 PRD，见 `assets/style-proposal-template.md` §〇）——读错则三套方案全废，用户可先纠偏；再出三套**真实差异化**方案（配色 / 排版 / 密度 / 交互气质含动效强度档，禁止只换主色；〔B〕不执行本步骤，是否探索风格由独立 SOP 判断），默认文字 + 色板小样，按 `assets/style-proposal-template.md` 出；**出稿对比花额度须用户同意**（该通道在步骤 6 基线复刻出稿后执行，属本 Gate 的补充确认，完成后回填该模板 §六/§七）。参考站用 `extract-website --url --design-md` 提取 DNA，用户三选一（完全采用 / 借鉴融合 / 更新现有），**禁静默混搭**。

**5. ◉ 设计规范 Gate**：选定风格按 `assets/design-system-template.md` 展开（原则 / 色彩 / 字体 / 间距 4px / 圆角阴影 / 组件规范 / 界面状态 / 页面宽度分层 / 动效——按 `references/motion-design-guide.md` 定强度档与曲线 / 时长 token / CSS token），对齐开源基线；布局清单 / 原型中出现空、错、加载、禁用等状态的页面，状态稿按模板 §5.10 一并纳入；用户确认后落盘：〔A〕`.superdesign/design-system.md`（副本进 `.spec/设计稿/`）；〔B〕直接落 `.spec/设计稿/design-system.md`。模板带 DESIGN.md 开放格式 YAML token 头（`assets/design-system-template.md` §0.5）。**规范未确认禁任何生成调用**；生成必带保真约束语（只使用 design-system 定义的字体 / 颜色 / 间距 / 组件，不得引入规范外视觉）。

**6. 项目创建（仅 A）**：新项目先做基线复刻（灰调 HTML、结构 100% 正确），`create-project --template <复刻> --device <端> --no-open` 取 projectId；续跑先查 `.superdesign/resume.json`，缺失用 `fetch-design-nodes` 找回，**禁止重复建项目**；品牌资产先 `upload-asset --purpose brand` 再以 reference-id 传。

**7. 逐页生成**：〔A〕首张主流程页 `create-design-draft`（只接受一个 `-p`）+ `--context-file .superdesign/design-system.md`；出画布 URL 给用户确认后再 `execute-flow-pages` 批量延展（1–10 页/次，JSON 先过目）；变体一律 `iterate --mode branch`（数量用户定，默认 2）；用户原话传 `--user-request`。〔B〕已转入独立 SOP，不执行本步骤；按任务类型生成/局改，经检查通过的首版可以交付。

**8. ◉ 质量门禁（A 路径，全绿才放行）**：按 `references/design-review-gate.md` 六查——① 布局零改动（多删改返工）② 规范一致性（规范外视觉值返工）③ 反 AI 味 12 条（§4.3 + 扩充机械项）④ 文案保真（① 类与 PRD / 布局清单逐字一致、无杜撰；**② 类原型说明层在可见层命中数必须为 0，③ 类须有重写记录**——见铁律 4）⑤ 布局基线与全站组件不变量（**含跨页导航外壳宽度实测三值一致**，见 `assets/design-system-template.md` §5.11 角色分流）⑥ 稿源同步核验（〔A〕云端稿 import 回传核验；〔B〕本地渲染核验）。**〔边界〕本门禁是产出方自查，不是独立评审**：第三方独立复核由 `UI-UX-Review` 按 `../../shared/review-context-isolation.md` 在隔离上下文（隔离评审子代理）执行；产出上下文不得自审、不得自判通过。

**9. 落盘归档（A 路径；B 按独立 SOP §七）**：〔A〕`get-design --draft-id --output .spec/设计稿/<页面>.html`；〔B〕本地文件即交付物（核对路径与命名，无导出步骤）。按 `assets/archive-readme-template.md` 写 README（页面 / 〔A〕projectId + draftId 或〔B〕稿源=AI 自写 + git 版本 / 规范出处 / 端类型 / **§7 token 条数对账基线** / **上游基线指纹**）；**〔REQUIRED · 上游基线指纹〕**README 必须登记本批所依据的上游 artifact：`artifactId` + `version` + 该文件 mtime，并按 `../../shared/artifact-contract.md` §2 写入其 `sourceRefs`——只写「PRD v0.2 APPROVED」这类无 id、无 mtime 的松散说法不算登记。上游被覆盖式修订或转 `SUPERSEDED` 时，本批即基准失效，须重判而非沿用（口径 `../../shared/gate-policy.md` §6）；返工交付同理声明**返工当时**的上游版本与 mtime。**〔REQUIRED · 回填边界〕**回填评审任务清单**只允许动状态列与修复说明并标回填方**（`已确认` → `已修复` + 修改说明）；**Gate 结论、放行状态、轮次判定属评审方单一事实源，编写方一律不得自写**；**回填后须触发 `UI-UX-Review` 复核，不得自判通过**（闭环与上限规则见 `../../shared/anti-deadloop.md` §2/§3）；埋点收尾。

> **下游交接口径**：`design-system.md` §7「CSS 变量 Token 汇总」是下游 Frontend-Tech-Design（§8.6 登记条数）与 Frontend-Dev（`styles/variables` 逐条对账）的**视觉唯一来源**；低保真原型不承载视觉基准（见 `../../shared/baseline-terms.md`）。

## 四、关键规范

**4.1 生成与迭代路由**：

| 意图 | 路由 | 命令 |
|---|---|---|
| 看不同方向 / 出选项 | branch | `iterate-design-draft --draft-id <id> -p "<方向1>" -p "<方向2>" --mode branch --context-file .superdesign/design-system.md` |
| 选定方向上改（需设计判断） | replace | 同上 `--mode replace` |
| 确定性修正（文案 / 链接 / 精确间距 / 已上传图） | **直编（免额度）** | `get-design` → 本地改 → `import-design-draft --into <draftId> --html-file <file> --generated-by <模型>` |
| 回旧版 | revert（免额度） | `revert-design-draft --draft-id <id> --to-version <n>` |

- 用户选定 branch 结果后设为当前，后续走 replace / 直编，不再开新 branch；意图歧义先问清。
- **〔B〕自写路由**：仅按 `references/self-write-sop.md`，不继承此表的整页 replace、固定变体数量或云端导入限制。
- **400 过载**：把超大上下文按 ~900 行裁到实际渲染段后**重试同一调用**；绝不瘦成最小上下文重试（模型会凭规范发明假页）。
- 同一页超 3 轮不收敛 → **停下对齐**，不烧额度。

**4.2 直编契约与闭环**（〔A〕用于 import 回传；〔B〕不适用此契约，使用独立 SOP 的本地生成契约）：

- **契约**：完整 HTML 文档（`DOCTYPE` → `/html`）；Tailwind 类样式；图标用 `<iconify-icon>` 自带 CDN script；`body` 无 class、布局在一个根 div；每个 `<a>` 有唯一描述性 id 且不嵌套；链接用完整 `https` 或 `#hash`，**禁相对路径**。违规被拒或 `warnings[]` 必须处理。
- **闭环**：本地改完 → 本地渲染请用户确认 → **同一轮内 `import-design-draft` 回传云端** → `get-design` 核 version 递增并同步 README。**云端（宿主入口指向的 draft URL）是评审单一事实源**；只改本地 = 用户看到旧稿，「待回传」不跨会话。

**4.3 反 AI 味（12 条 + 官方聚类参照）**：

> **官方聚类参照（Anthropic frontend-design）**：以下五组特征**成组出现**时是 AI 生成的最强破绽——① 暖奶油底（≈`#F4F1EA`）+ 高对比衬线标题 + 赤陶点缀（≈`#D97757`，容易被读成「破绽色」）；② 近黑底 + 单一高饱和酸绿 / 朱红点缀；③ 大报式版式（发丝细线、零圆角、密集分栏）；④ SaaS 卡片套件（内容切成完全相同的圆角卡片、统一 blur 阴影、渐变洗色）；⑤ 模板化五金件（每个标题上方全大写 eyebrow、中点连接元信息「A · B · C」、`WORD — fragment` 标签、带色调近黑、等宽字体做小号数据标签、链接后追加 `→`）。
> **判据**：这些特征对某些 brief 是**合法选择**，但它们是**默认值而非选择**，且**无论主题都会出现**。**brief 已明确视觉方向的地方严格照做（brief 原话优先）；brief 留白的地方，不要把自由度花在这些默认值上。**
> **三处最常见的排版破绽**：只在标题里强调某一个词（斜体 / 加粗 / 换色）、用全大写做标签、在内容上方加多余的 eyebrow。
> **两条自我约束**：① **大胆只花在一个地方**——让一个元素成为记忆点，其余保持安静，砍掉不服务 brief 的装饰；② **动效克制**——一个编排好的瞬间胜过每个 section 都 fade-and-slide-up + 每张卡都加 hover。
> **自查法**：把方案代入一个相似的 prompt 走一遍；若会落到同一处 = 通用默认，改掉并说明改了什么、为什么。
> **AI Slop Test（放行自问）**：把稿子给人看并说「这是 AI 做的」，他会立刻相信吗？会 → 落入了机器默认审美，回到「大胆只花在一个地方」重审。

1. 禁 emoji 当图标；
2. 禁紫蓝渐变默认背景；
3. 禁装饰性渐变光斑 / blob；
4. 禁 hero + 三卡片 + CTA 模板结构（布局照清单）；
5. 禁重阴影 / 过度玻璃拟态；
6. 内容密度真实，不空旷留白；
7. 配色从产品定位推导，不默认 AI 蓝；
8. 字体层级分明（标题 / 正文 / 辅助）；
9–11. 无出处的按钮 / 提示文案 / 区块一律不得出现；
12. 简洁克制，少即是多。

**4.4 命令速查（〔A〕路径；〔B〕无 CLI，按 `references/self-write-sop.md` 执行）**：

```bash
superdesign --version / auth status
superdesign search-prompts --tags "style" --query "<关键词>"
superdesign get-prompts --slugs "<slug>" --full
superdesign extract-website --url "<站点>" --design-md
superdesign create-project --title "<项目>" --template <复刻.html> --device desktop --no-open
superdesign create-design-draft --project-id <id> --title "<页面>" -p "<提示词>" --context-file .superdesign/design-system.md
superdesign iterate-design-draft --draft-id <id> -p "<方向>" --mode branch|replace --context-file ...
superdesign execute-flow-pages --draft-id <id> --pages '[{"title":"...","prompt":"..."}]' --context-file ...
superdesign get-design --draft-id <id> --output <路径>.html
superdesign revert-design-draft --draft-id <id> --to-version <n>
superdesign upload-asset <file> --project-id <id> --purpose brand|content|reference
```

命令契约以 `--help` 实测为准；`create-design-draft` 多 `-p` 被静默丢弃；`--context-file` 支持 `path:start:end`；`extract-website` 60–120s。

**4.5 交付结构**：

```
.spec/设计稿/
├── README.md（页面清单 + projectId/draftId + 规范出处 + 端类型）
├── design-system.md（副本；源在 .superdesign/）
├── <页面>.html
├── screenshots/（Playwright 可用时）
└── ...
```

## 五、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 跳过环境检测 | 步骤 1 三件套 |
| 无原型直接跑 | 双输入缺一阻塞 |
| 结构缺失脑补 | 就地问用户 |
| 提取区块时增删 | 只翻译不改动 |
| 顺手改布局 | 回 Prototype-Design |
| 无规范就生成 | 步骤 5 Gate |
| 生成不带规范 / 约束语 | 必带 |
| create 传多个 `-p` | 只一个；变体用 branch |
| 擅自加变体 / 轮次 | 额度先问 |
| 400 瘦上下文重试 | 裁实际渲染段重试 |
| 小修花额度重生成 | 走直编 |
| branch 未选就 replace | 先让用户选 |
| 方案只换主色 | 真实差异 |
| 出现无出处按钮 / 区块 | 零加戏 + 布局零改动 |
| 视觉值出规范 | 门禁返工 |
| 设计读未写 / 与受众错位 | 步骤 4 先出设计读，用户纠偏后再出方案 |
| 动效无目的 / 强度档与规范不一致 | 按 motion-design-guide 决策四问；门禁 §二 动效合规 |
| 重复建项目 | `resume.json` / fetch 找回 |
| import 用相对路径 | 只 `https` / `data:`，先 `upload-asset` |
| 只改本地宣布完成 | 同一轮回传云端并核 version + 宿主链 + README |
| README 只写「PRD v0.2 APPROVED」这类无 id / 无 mtime 的说法 | 步骤 9 REQUIRED 登记**上游基线指纹**（`artifactId` + `version` + mtime）并写 `sourceRefs`；上游转 `SUPERSEDED` 即基准失效、须重判 |
| 修复方在评审任务清单里自写「第二轮 Gate：PASS」 | 回填**只动状态列 + 修复说明并标回填方**；Gate / 放行 / 轮次判定属评审方单一事实源，编写方不得自写（步骤 9 REQUIRED） |
| 穿衣静态化：把原型可跳转/可展开结构降级为纯样式 hover（死按钮、无锚点行） | 交互结构随布局零改动一并冻结：原型中真实 <a>/按钮在设计稿用 <a href="#锚点"> 或等价触发保留 |
| Tailwind 默认尺度直用（rounded-sm/shadow-md/0.5 步长间距/中间字重），未映射设计 token | 生成提示词与自检都按 token 对照表逐值映射；门禁 ② 用「规范外值全文扫描」兜底 |
| 风格提案的动效档带入已收敛的归档规范（提案最低限编排 ≠ 规范无编排） | 步骤 5 规范落定后，生成约束语只引规范 §动效，不再引提案 |
| 〔B〕第一版直接当定稿交付 | 〔B〕Iron Law：成稿必过渲染截图自检 + pre-flight（self-write-sop §一/§七） |
| 〔B〕无截图自查，或打磨超「1 全量 + 1 确认」上限 | 有界验证封顶；浏览器不可用 → 源码机械检查 + 用户确认并在 README 注明 |
| 〔B〕凭记忆编风格不查情报源 | 先查 case-library + 外部风格源；0 结果显式标 fallback，禁编造 |
| 〔B〕em-dash / 装饰 eyebrow / div 假截图 / 同页同意图多 CTA 标签 | 机械检查零容忍（design-review-gate §三扩充项） |
| **页内标题栏**（不承载跨页导航的 h1／页头）与内容主列宽度不一致（P1）：窄内容列页（如 860px 对话流）标题栏仍用全局宽容器，上下不对齐 | design-system §5.11 逐页登记**页内标题栏**宽=该页内容主列宽（报纸式上下对齐）；生成提示词显式写「标题栏内层容器宽 NNNpx 与内容主列同宽」；门禁 §五.B 核对。**限定：本条不适用于承载跨页入口的全局导航外壳**（来源：travel-agent 设计稿 2026-10-11 用户走查） |
| **全局导航外壳随内容档位缩窄**（P1）：把 `max-width` 加在承载顶栏／侧栏的页框或根容器上，限宽页的整条一级导航被一起居中缩窄，跨页左缘跳变（首页满宽 → 检索页缩到 860 居中） | 档位 `max-width` **只落内容主列容器**；导航外壳跨页恒定同宽同左缘；门禁 ⑤ 跑跨页导航外壳三值（1280/1440/1920）实测，任一不等即返工（来源：knowledge-bases 设计稿 2026-10-12 用户走查） |
| 原型换皮：以「与原型结构/文案逐字一致」为生成契约与验收 FACT，UI 判断被判成漂移缺陷 | 铁律 4：结构冻结、呈现判断不冻结；逐字对账只针对 ① 类已批准产品文案；构建脚本的 verify 判据须按 ①②③ 分类豁免 ②③ |
| 原型说明层泄漏到界面（P1）：`U-xxx` 编号牌、`【设计假设】`、`台账 §x`、`AC-Mxx`、`PRD 未写`、`（示意／走查占位）`、`默认首屏` 元信息徽标、演示切换条、清单对照块在产品稿页面上可见 | 铁律 4 ② 类：注记层改挂 `body` 级走查开关（默认 `display:none`，可打开恢复可见），**不删**；门禁 ④ 对可见层做内部语扫描，命中数必须为 0（来源：knowledge-bases 设计稿 2026-10-12，实测 253 个编号牌 + 201 处注记 + 9 处导航元徽标） |
| 照抄原型口语当界面文案（P2）：结构对但文字是写给评审者看的说明句 | 铁律 4 ③ 类：按产品文案规范重写成人话，重写记录登记进设计任务清单 |
| 全站公共区块逐页手写导致结构漂移（P0，用户多次纠正）：顶栏等跨页公共组件每页各写各的（选中态/身份区/头像/链接数不一致），同一组件出现多种形态 | design-system 组件规范定义**唯一 DOM 模板 + 逐页参数表**（顶栏参数=容器宽/选中项/身份态），批量生成提示词写明「全站共用同一顶栏组件仅参数变化」；门禁新增机械检查：抽取各页公共区块标记做**逐字一致性比对**（除参数外不得有任何差异）；批量出稿后必跑（来源：travel-agent 设计稿 2026-10-11 用户走查，判「严重问题」） |

## 六、资源清单

- `references/superdesign-sop.md`（A 路径）、`self-write-sop.md`（B 路径）、`design-review-gate.md`、`motion-design-guide.md`（动效设计决策；步骤 5/8 用）、`open-source-design-systems.md`、`style-case-library.md`、`case-library/`（00-README 总索引 + design-systems / layouts / components / interactions / flows / a11y-checklist）、`patterns/index.md`
- `assets/layout-inventory-contract.md`、`design-task-list-template.md`、`style-proposal-template.md`、`design-system-template.md`、`archive-readme-template.md`
- `../../shared/anti-deadloop.md`、`../../shared/baseline-terms.md`、`../../shared/receiving-review.md`（仓库根）：公共约定（含接收评审纪律）
- `.spec/设计稿/` 交付目录；`.superdesign/` 工作目录

## 七、运行问题埋点

收尾按 `../../shared/instrumentation-guide.md` 自查上报 `../../issue/UI-UX-Design/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `../../shared/templates/issue-template.md`；含生成本体侧：A=Superdesign 云端额度/命令行为，B=自写质量与自检环）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

B 先按共享执行强度分流：轻量独立结果使用任务摘要，下方正式状态/manifest/Gate 写入只用于 B 的标准/完整交接；A 沿用原完整兼容流程不变。

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `UI-UX-Design` while exposing it through the v2 Skill contract.

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
- a failure route when the wrapper cannot complete safely.

## Evidence

Use direct source files, command output, test results, screenshots, dated external sources, or explicit user decisions. Label conclusions as `FACT`, `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, `RECOMMENDATION`, `DECISION`, or `OPEN`. A recommendation is not approval.

## Gate

Use only `PASS`, `CONDITIONAL`, or `BLOCKED`. `PASS` requires complete inputs and artifacts with no unresolved P0/P1. Residual P0 is always `BLOCKED`. Residual P1 is never `PASS` and may be `CONDITIONAL` only with `exceptionId`, `risk`, `owner`, `dueAt`, `remediation`, `allowDownstream`, and `approvalRef`. Three review rounds are the maximum; never force-pass or start an automatic fourth round.

## Failure Route

If evidence, authorization, scope, or an upstream Gate is missing, set `BLOCKED`, name the missing item and owner, and route to the responsible upstream Skill. If the issue is outside this wrapper's boundary, stop and route it rather than improvising.

## Downstream Contract

Downstream Skills may consume only manifest entries whose status and Gate allow downstream use. They must read `sourceRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, and `nextAction`; they must not infer approval from chat context or file existence.

## State Changes

Record the old state, new state, actor, timestamp, reason, evidence references, Gate, and next action in `.spec/workflow.yaml`. The exact state names come from `governance/state-registry.yaml` in the source repository; an installed copy without that repository must use the state names already present in the project `.spec/workflow.yaml` and must not invent new states.
