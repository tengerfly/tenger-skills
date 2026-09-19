---
name: UI-UX-Design
description: UI/UX 设计稿生成（双路径：Superdesign 云端 / AI 自写）。依据 PRD + Prototype-Design 的布局清单与低保真原型，先推荐三套差异化风格方案，沉淀并确认设计规范后，逐页生成布局零改动、反 AI 味、风格统一的设计稿 HTML，过质量门禁后归档 `.spec/设计稿/`。开工先探测 Superdesign 额度：有额度走云端出稿（A 路径），无额度转 AI 自写（B 路径，references/self-write-sop.md），不阻塞。额度即预算，花钱动作先问。触发：生成设计稿/UI 设计/视觉稿/把原型变成设计稿。
compatibility: Claude Code / Agent SDK / OpenCode
---

# UI/UX 设计稿生成 Skill（双路径：Superdesign 云端 / AI 自写）

> IRON LAW：**布局零改动 + 规范先行 + 第一版不算数**——布局清单与低保真原型是结构真相源；设计规范未确认前禁止任何生成调用；任何路径生成的第一版都是草稿，必须过自检环 + pre-flight 才算数。
> 本 skill 是设计总监 + 编排器：管标准、决策、门禁、归档。生成本体双路径：**A = Superdesign CLI 云端出稿**（`references/superdesign-sop.md`）；**B = 会话模型 AI 自写**（`references/self-write-sop.md`，无额度时的默认）。

## 一、定位与铁律

**三条铁律**：

1. **布局零改动**：载体、区块、元素、跳转逐项与布局清单 + 低保真原型一致；只改好不好看，**不碰有什么 / 在哪 / 怎么跳**。布局有问题 → 停下回 Prototype-Design。
2. **规范先行**：任何生成前设计规范必须已确认；每次生成必带规范 + 保真约束语。`design-system.md` 是下游 FTDD 与 Frontend-Dev 的视觉规范依据，随 `.spec/设计稿/` 交付。
3. **额度即预算**：变体数量、生成轮次、花钱动作**永远先问用户**；额度不足不是阻塞理由——转 B 路径（AI 自写）继续。

**适用范围**：适用「PRD + 布局清单 + 低保真原型齐备，生成设计稿 / UI / 视觉稿」；不适用画原型（Prototype-Design）、写 / 评审需求（PRD-Design / PRD-Review）、评审原型（Prototype-Review）、实现前端（Frontend-Dev）、海报 / Logo / 营销素材。

## 二、输入与前置

| 项 | 说明 | 缺失处理 |
|---|---|---|
| **环境（A 路径三件套）** | CLI 已装（`superdesign --version`）、账号已授权（`auth status`）、SOP 可读（`references/superdesign-sop.md`）。**B 路径仅需浏览器工具**（自检环截图） | A 三件套或额度任一不过 → **转 B 路径**（路由见步骤 1），不阻塞；B 无浏览器 → 降级源码机械检查 + 用户确认，README 注明 |
| 布局清单（载体级：宿主 / 入口 / 出口齐全、PRD 页面防丢弃） | 结构契约 | ⛔ 缺一阻塞；字段缺失就地问，**不得脑补** |
| 低保真原型 HTML（+ `原型/README.md` 佐证端类型/跳转） | 区块结构实物 | ⛔ 缺一阻塞 |
| PRD（有速查表先建索引） | 文案来源（按锚点取，**一字不差**） | 缺则按布局清单推进并标注 |
| `.spec/设计评审/任务清单.md` | `已确认` 且修改方为本 skill 的任务逐条纳入 | 无则跳过 |
| 浏览器工具（〔A〕仅截图增强；〔B〕自检环关键，见上） | 截图存 `screenshots/` | 不可用则降级并在归档 README 注明（策略见 `shared/browser-policy.md`） |

**双输入校验**按 `assets/layout-inventory-contract.md` 执行。

**目录分工**：〔A〕`.superdesign/` = 工作目录（design-system + 基线复刻 + `resume.json`），**不是交付物**；〔B〕无工作目录，design-system 直接落交付目录。`.spec/设计稿/` = 评审与 PIPELINE 唯一认的交付物（〔B〕下同时是唯一事实源，无云端副本）。

## 三、主流程（9 步 · 4 Gate）

```
输入 → ◉1 环境检测与路径路由 → 2 输入解析 → 3 风格情报 → ◉4 风格决策 → ◉5 设计规范
→ 〔A〕6 项目创建 + 7 逐页生成（云端） / 〔B〕7 自写生成环 → ◉8 质量门禁 → 9 落盘归档
```

**1. ◉ 环境检测与路径路由 Gate**：先验 A 路径三件套 + **额度探测**（轻量命令实测或用户告知；报无额度 / 失效即视为不过）。全过 → **A 路径**（Superdesign 云端）；任一不过 → 一句话告知用户后转 **B 路径**（AI 自写，按 `references/self-write-sop.md`），**不阻塞**。路径一经确定全程不混用（不 A 出首稿又 B 延展）。

**2. 输入解析**：纳入评审任务清单；执行双输入校验；**逐页读原型 HTML，按视觉顺序提取区块行（区块 / 组件 / 内容 / 交互）——只翻译不改动**；展开设计任务清单（`assets/design-task-list-template.md`）。

**3. 风格情报**：〔A〕Superdesign 灵感库（`search-prompts` → `get-prompts --full`，先索引后取全文）；〔B〕外部风格源（awesome-design-md 品牌集合 / `npx extract-design-system` / browser 实抓，见 self-write-sop §八）；共同：**案例库体系**按序检索（总索引 `references/case-library/00-README.md`）：`patterns/index.md` 高频模式 → `case-library/flows.md` 用户流与状态表达 → `layouts.md` / `components.md` / `interactions.md` → `case-library/design-systems.md` + `open-source-design-systems.md` 体系基线 → `style-case-library.md` 自有深案例与踩坑。外部资源取用前**验证可达与许可**；命中资源须**实抓提取**（`web_fetch` / `extract-website`，1~3 个/场景；失败标注跳过禁编造）；**参考 ≠ 照抄**，提取值仍须过步骤 5 用户确认；案例库更新由用户手动发起。

**4. ◉ 风格决策 Gate**：**先出一行「设计读」**（读作：〈产品类型〉给〈受众〉，走〈气质〉语言；受众与气质取自 PRD，见 `assets/style-proposal-template.md` §〇）——读错则三套方案全废，用户可先纠偏；再出三套**真实差异化**方案（配色 / 排版 / 密度 / 交互气质含动效强度档，禁止只换主色；〔B〕每套绑定一个锚点 token 包 + 失格条件，见 self-write-sop §十），默认文字 + 色板小样，按 `assets/style-proposal-template.md` 出；**出稿对比花额度须用户同意**（该通道在步骤 6 基线复刻出稿后执行，属本 Gate 的补充确认，完成后回填该模板 §六/§七）。参考站用 `extract-website --url --design-md` 提取 DNA，用户三选一（完全采用 / 借鉴融合 / 更新现有），**禁静默混搭**。

**5. ◉ 设计规范 Gate**：选定风格按 `assets/design-system-template.md` 展开（原则 / 色彩 / 字体 / 间距 4px / 圆角阴影 / 组件规范 / 界面状态 / 页面宽度分层 / 动效——按 `references/motion-design-guide.md` 定强度档与曲线 / 时长 token / CSS token），对齐开源基线；布局清单 / 原型中出现空、错、加载、禁用等状态的页面，状态稿按模板 §5.10 一并纳入；用户确认后落盘：〔A〕`.superdesign/design-system.md`（副本进 `.spec/设计稿/`）；〔B〕直接落 `.spec/设计稿/design-system.md`。模板带 DESIGN.md 开放格式 YAML token 头（`assets/design-system-template.md` §0.5）。**规范未确认禁任何生成调用**；生成必带保真约束语（只使用 design-system 定义的字体 / 颜色 / 间距 / 组件，不得引入规范外视觉）。

**6. 项目创建（仅 A）**：新项目先做基线复刻（灰调 HTML、结构 100% 正确），`create-project --template <复刻> --device <端> --no-open` 取 projectId；续跑先查 `.superdesign/resume.json`，缺失用 `fetch-design-nodes` 找回，**禁止重复建项目**；品牌资产先 `upload-asset --purpose brand` 再以 reference-id 传。

**7. 逐页生成**：〔A〕首张主流程页 `create-design-draft`（只接受一个 `-p`）+ `--context-file .superdesign/design-system.md`；出画布 URL 给用户确认后再 `execute-flow-pages` 批量延展（1–10 页/次，JSON 先过目）；变体一律 `iterate --mode branch`（数量用户定，默认 2）；用户原话传 `--user-request`。〔B〕**自写生成环**（self-write-sop §一/§六）：每页走「设计计划 → 唯一性自查 → 成稿 → 渲染截图 → 有界自检（1 全量 + 1 确认封顶）→ pre-flight」；首张主流程页先出、用户确认视觉方向后再延展其余页；变体 = 同布局并行写 2 版不同锚点方向。

**8. ◉ 质量门禁（全绿才放行）**：按 `references/design-review-gate.md` 六查——① 布局零改动（多删改返工）② 规范一致性（规范外视觉值返工）③ 反 AI 味 12 条（§4.3 + 扩充机械项）④ 文案保真（与 PRD / 布局清单逐字一致、无杜撰）⑤ 布局基线与全站组件不变量 ⑥ 稿源同步核验（〔A〕云端稿 import 回传核验；〔B〕本地渲染核验）。

**9. 落盘归档**：〔A〕`get-design --draft-id --output .spec/设计稿/<页面>.html`；〔B〕本地文件即交付物（核对路径与命名，无导出步骤）。按 `assets/archive-readme-template.md` 写 README（页面 / 〔A〕projectId + draftId 或〔B〕稿源=AI 自写 + git 版本 / 规范出处 / 端类型 / **§7 token 条数对账基线**）；回填评审任务清单（`已确认` → `已修复` + 修改说明）；**回填后须触发 `UI-UX-Review` 复核，不得自判通过**（闭环与上限规则见 `shared/anti-deadloop.md` §一/§二）；埋点收尾。

> **下游交接口径**：`design-system.md` §7「CSS 变量 Token 汇总」是下游 Frontend-Tech-Design（§8.6 登记条数）与 Frontend-Dev（`styles/variables` 逐条对账）的**视觉唯一来源**；低保真原型不承载视觉基准（见 `shared/baseline-terms.md`）。

## 四、关键规范

**4.1 生成与迭代路由**：

| 意图 | 路由 | 命令 |
|---|---|---|
| 看不同方向 / 出选项 | branch | `iterate-design-draft --draft-id <id> -p "<方向1>" -p "<方向2>" --mode branch --context-file .superdesign/design-system.md` |
| 选定方向上改（需设计判断） | replace | 同上 `--mode replace` |
| 确定性修正（文案 / 链接 / 精确间距 / 已上传图） | **直编（免额度）** | `get-design` → 本地改 → `import-design-draft --into <draftId> --html-file <file> --generated-by <模型>` |
| 回旧版 | revert（免额度） | `revert-design-draft --draft-id <id> --to-version <n>` |

- 用户选定 branch 结果后设为当前，后续走 replace / 直编，不再开新 branch；意图歧义先问清。
- **〔B〕自写路由**：看不同方向 = 同布局并行写 2 版（不同锚点包，self-write-sop §十）；选定方向上改 = 该页 replace 式重写（受有界验证约束）；确定性修正 = 本地直改（pre-flight 抽查）；回旧版 = git 或 `<页面>.v<n>.html` 副本。
- **400 过载**：把超大上下文按 ~900 行裁到实际渲染段后**重试同一调用**；绝不瘦成最小上下文重试（模型会凭规范发明假页）。
- 同一页超 3 轮不收敛 → **停下对齐**，不烧额度。

**4.2 直编契约与闭环**（〔A〕用于 import 回传；〔B〕该契约即生成契约，且闭环简化——本地 `.spec/设计稿/` 即唯一事实源，无云端回传步骤）：

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
| 穿衣静态化：把原型可跳转/可展开结构降级为纯样式 hover（死按钮、无锚点行） | 交互结构随布局零改动一并冻结：原型中真实 <a>/按钮在设计稿用 <a href="#锚点"> 或等价触发保留 |
| Tailwind 默认尺度直用（rounded-sm/shadow-md/0.5 步长间距/中间字重），未映射设计 token | 生成提示词与自检都按 token 对照表逐值映射；门禁 ② 用「规范外值全文扫描」兜底 |
| 风格提案的动效档带入已收敛的归档规范（提案最低限编排 ≠ 规范无编排） | 步骤 5 规范落定后，生成约束语只引规范 §动效，不再引提案 |
| 〔B〕第一版直接当定稿交付 | Iron Law：成稿必过渲染截图自检 + pre-flight（self-write-sop §一/§七） |
| 〔B〕无截图自查，或打磨超「1 全量 + 1 确认」上限 | 有界验证封顶；浏览器不可用 → 源码机械检查 + 用户确认并在 README 注明 |
| 〔B〕凭记忆编风格不查情报源 | 先查 case-library + 外部风格源；0 结果显式标 fallback，禁编造 |
| 〔B〕em-dash / 装饰 eyebrow / div 假截图 / 同页同意图多 CTA 标签 | 机械检查零容忍（design-review-gate §三扩充项） |

## 六、资源清单

- `references/superdesign-sop.md`（A 路径）、`self-write-sop.md`（B 路径）、`design-review-gate.md`、`motion-design-guide.md`（动效设计决策；步骤 5/8 用）、`open-source-design-systems.md`、`style-case-library.md`、`case-library/`（00-README 总索引 + design-systems / layouts / components / interactions / flows / a11y-checklist）、`patterns/index.md`
- `assets/layout-inventory-contract.md`、`design-task-list-template.md`、`style-proposal-template.md`、`design-system-template.md`、`archive-readme-template.md`
- `shared/anti-deadloop.md`、`shared/baseline-terms.md`、`shared/receiving-review.md`（仓库根）：公共约定（含接收评审纪律）
- `.spec/设计稿/` 交付目录；`.superdesign/` 工作目录

## 七、运行问题埋点

收尾按 `Skill-Optimizer/references/instrumentation-guide.md` 自查上报 `issue/UI-UX-Design/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `Skill-Optimizer/assets/issue-template.md`；含生成本体侧：A=Superdesign 云端额度/命令行为，B=自写质量与自检环）。不确定不记，不打断主流程。
