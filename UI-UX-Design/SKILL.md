---
name: UI-UX-Design
description: UI/UX 设计稿生成（Superdesign 底座）。依据 PRD + Prototype-Design 的布局清单与低保真原型，先推荐三套差异化风格方案，沉淀并确认设计规范（.superdesign/design-system.md）后，逐页生成布局零改动、去 AI 味、风格统一的设计稿 HTML，过质量门禁后归档 `.spec/设计稿/`。额度即预算，花钱动作先问。触发：生成设计稿/UI 设计/视觉稿/把原型变成设计稿。
compatibility: Claude Code / Agent SDK / OpenCode
---

# UI/UX 设计稿生成 Skill（Superdesign 底座）

> 把「PRD + 布局清单 + 低保真原型」变成布局零改动、去 AI 味、风格统一的设计稿。本 skill 是设计总监 + 编排器：管标准、决策、门禁、归档；不手写设计稿 HTML。

## 一、原则

1. **布局零改动**：布局清单 + 低保真原型 = 结构真相源。载体、区块、元素、跳转逐项一致；只改好不好看，不碰有什么/在哪/怎么跳。布局有问题 → 停下回 Prototype-Design。
2. **规范先行**：任何生成前设计规范必须已确认；每次生成必带规范 + 保真约束语。design-system.md 是下游前端技术方案（FTDD）与前端开发（Frontend-Dev）的视觉规范依据，随 `.spec/设计稿/` 交付。
3. **额度即预算**：变体数量、生成轮次、花钱动作永远先问用户。

## 二、适用范围

- 适用：PRD + 布局清单 + 低保真原型齐备，生成设计稿/UI/视觉稿。
- 不适用：画原型（Prototype-Design）、写/评审需求（PRD-Design/Review）、评审原型（Prototype-Review）、实现前端（Frontend-Dev）、海报/Logo/营销素材。

## 三、流水线（9 步 · 3 Gate）

```
输入 → ◉1 环境检测 → 2 输入解析 → 3 风格情报 → ◉4 风格决策 → ◉5 设计规范
→ 6 项目创建 → 7 逐页生成 → ◉8 质量门禁 → 9 落盘归档
```

1. **环境检测 Gate（硬依赖）**：CLI 已装（`superdesign --version`，否则 `npm i -g @superdesign/cli@latest`）、账号已授权（`auth status`，否则 `superdesign login`）、SOP 可读（references/superdesign-sop.md 存在）。任一不过 → 给安装指引并阻塞；环境问题不耗额度。
2. **输入解析**：
   - 检查 `.spec/设计评审/任务清单.md`：`已确认` 且修改方为 UI-UX-Design 的任务逐条纳入。
   - 双输入校验（`assets/layout-inventory-contract.md`）：布局清单（载体级：宿主/入口/出口齐全、PRD 页面防丢弃）+ 低保真原型 HTML；缺一阻塞，字段缺失就地问，不得脑补。
   - 逐页读原型 HTML，按视觉顺序提取区块行（区块/组件/内容/交互）——只翻译不改动。
   - 展开设计任务清单（`assets/design-task-list-template.md`）。PRD 文案按速查表锚点取，一字不差。
3. **风格情报**：Superdesign 灵感库（search-prompts → get-prompts --full，先索引后取全文）；开源规范库（Ant/Aroo/shadcn/Material token，更新由用户手动发起）；真实案例库（同类产品风格基线 + 踩坑清单）。
4. **风格决策 Gate**：三套真实差异化方案（配色/排版/密度/交互气质，禁止只换主色），默认文字 + 色板小样；出稿对比花额度须用户同意。参考站用 `extract-website --url --design-md` 提取 DNA，用户三选一（完全采用/借鉴融合/更新现有），禁静默混搭。
5. **设计规范 Gate**：选定风格按 `assets/design-system-template.md` 展开（原则/色彩/字体/间距 4px/圆角阴影/组件规范/界面状态/动效/CSS token），对齐开源基线；布局清单/原型中出现空、错、加载、禁用等状态的页面，状态稿按模板 §5.10 界面状态规范一并纳入；用户确认后落 `.superdesign/design-system.md`，副本进 `.spec/设计稿/`。规范未确认禁任何生成调用。生成必带保真约束语（只使用 design-system 定义的字体/颜色/间距/组件，不得引入规范外视觉）。
6. **项目创建**：新项目先做基线复刻（灰调 HTML、结构 100% 正确），`create-project --template <复刻> --device <端> --no-open` 取 projectId；续跑先查 `.superdesign/resume.json`，缺失用 fetch-design-nodes 找回，禁止重复建项目；品牌资产先 `upload-asset --purpose brand` 再以 reference-id 传。
7. **逐页生成**：首张主流程页 `create-design-draft`（只接受一个 -p）+ `--context-file .superdesign/design-system.md`；出画布 URL 给用户确认后再 `execute-flow-pages` 批量延展（1–10 页/次，JSON 先过目）；变体一律 `iterate --mode branch`（数量用户定，默认 2）；用户原话传 `--user-request`。
8. **质量门禁（全绿才放行）**：按 `references/design-review-gate.md` 四查——布局零改动（多删改返工）、规范一致性（规范外视觉值返工）、反 AI 味 12 条、文案保真（与 PRD/布局清单逐字一致、无杜撰）。
9. **落盘归档**：`get-design --draft-id --output .spec/设计稿/<页面>.html`；按 `assets/archive-readme-template.md` 写 README（页面/projectId/draftId/规范出处/端类型）；回填评审清单；埋点收尾。

## 四、生成与迭代路由

| 意图 | 路由 | 命令 |
|---|---|---|
| 看不同方向/出选项 | branch | `iterate-design-draft --draft-id <id> -p "<方向1>" -p "<方向2>" --mode branch --context-file .superdesign/design-system.md` |
| 选定方向上改（需设计判断） | replace | 同上 `--mode replace` |
| 确定性修正（文案/链接/精确间距/已上传图） | 直编（免额度） | `get-design` → 本地改 → `import-design-draft --into <draftId> --html-file <file> --generated-by <模型>` |
| 回旧版 | revert（免额度） | `revert-design-draft --draft-id <id> --to-version <n>` |

- 用户选定 branch 结果后设为当前，后续走 replace/直编，不再开新 branch；意图歧义先问清。
- 400 过载：把超大上下文按 ~900 行裁到实际渲染段后重试同一调用；绝不瘦成最小上下文重试。
- 同一页超 3 轮不收敛 → 停下对齐，不烧额度。

### 直编契约

完整 HTML 文档（DOCTYPE→/html）；Tailwind 类样式；图标用 `<iconify-icon>` 自带 CDN script；body 无 class、布局在一个根 div；每个 `<a>` 有唯一描述性 id 且不嵌套；链接用完整 https 或 `#hash`，禁相对路径。违规被拒或 warnings[] 必须处理。

### 直编闭环

本地改完 → 本地渲染请用户确认 → **同一轮内 `import-design-draft` 回传云端** → `get-design` 核 version 递增并同步 README。云端（宿主入口指向的 draft URL）是评审单一事实源；只改本地 = 用户看到旧稿，「待回传」不跨会话。

## 五、命令速查

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

- 命令契约以 `--help` 实测为准；`create-design-draft` 多 -p 被静默丢弃；`--context-file` 支持 `path:start:end`；`extract-website` 60–120s。

## 六、去 AI 味铁律（12 条）

1. 禁 emoji 当图标；
2. 禁紫蓝渐变默认背景；
3. 禁装饰性渐变光斑/blob；
4. 禁 hero+三卡片+CTA 模板结构（布局照清单）；
5. 禁重阴影/过度玻璃拟态；
6. 内容密度真实，不空旷留白；
7. 配色从产品定位推导，不默认 AI 蓝；
8. 字体层级分明（标题/正文/辅助）；
9–11. 无出处按钮/提示文案/区块一律不得出现；
12. 简洁克制，少即是多。

## 七、交付结构

```
.spec/设计稿/
├── README.md（页面清单 + projectId/draftId + 规范出处 + 端类型）
├── design-system.md（副本；源在 .superdesign/）
├── <页面>.html
├── screenshots/（Playwright 可用时）
└── ...
```

`.superdesign/`（design-system + 基线复刻 + resume.json）是工作目录不是交付物；`.spec/设计稿/` 是评审与 PIPELINE 只认的交付物。

## 八、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 跳过环境检测 | 步骤 1 三件套 |
| 无原型直接跑 | 双输入缺一阻塞 |
| 结构缺失脑补 | 就地问用户 |
| 提取区块时增删 | 只翻译不改动 |
| 顺手改布局 | 回 Prototype-Design |
| 无规范就生成 | 步骤 5 Gate |
| 生成不带规范/约束语 | 必带 |
| create 传多个 -p | 只一个；变体用 branch |
| 擅自加变体/轮次 | 额度先问 |
| 400 瘦上下文重试 | 裁实际渲染段重试 |
| 小修花额度重生成 | 走直编 |
| branch 未选就 replace | 先让用户选 |
| 方案只换主色 | 真实差异 |
| 出现无出处按钮/区块 | 零加戏 + 布局冻结 |
| 视觉值出规范 | 门禁返工 |
| 重复建项目 | resume.json/fetch 找回 |
| import 用相对路径 | 只 https/data:，先 upload-asset |
| 只改本地宣布完成 | 同一轮回传云端并核 version + 宿主链 + README |

## 九、资源清单

- `references/superdesign-sop.md`、`design-review-gate.md`、`open-source-design-systems.md`、`style-case-library.md`
- `assets/layout-inventory-contract.md`、`design-task-list-template.md`、`style-proposal-template.md`、`design-system-template.md`、`archive-readme-template.md`
- `.spec/设计稿/` 交付目录；`.superdesign/` 工作目录

## 十、运行问题埋点

收尾自查，将方法论问题、用户否定/认可信号、可复现产物问题（含 Superdesign 底座侧）上报 `issue/UI-UX-Design/<日期>/<序号>-<标题>.md`，字段/等级/标签遵循 `Skill-Optimizer/references/instrumentation-guide.md`，模板用 `Skill-Optimizer/assets/issue-template.md`。不确定不记，不打断主流程。