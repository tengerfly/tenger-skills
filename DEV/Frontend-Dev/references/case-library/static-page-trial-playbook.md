# 静态页试做 Playbook（还原度冲刺 + 24 分钟节奏）

> **状态：标准 SOP（2026-09-16 用户定稿）**——由 Frontend-Dev 主流程强制引用：S1 输入瘦身（§1）/ S7 视图模型先行与节奏纪律（§3/§6）/ §4.7 验收脚本化（§5）/ §4.9 口径表（§4）。§4 口径决策模式与 §6 节奏纪律为硬性纪律，非可选参考；单点案例背景见 ../../../../issue/Frontend-Dev/2026-09-16/01~02。
>
> 场景：设计稿已定稿（`.spec/设计稿/`），按 FTDD 模块逐页产出静态页（mock 数据、无真实请求），以高还原度一次过验收。
> 出处：儿童益智动画生成平台 首页/资产库两页试做（2026-09-15/16，均一次过双开截图验收）。
> 适用边界：React/Vite/Less/CSS Modules 工程语境；其他框架按 framework-equivalence-guide 等价映射。**只管流程与判断模式，视觉/文案基准仍以设计稿唯一应然（铁律 1）**。

## 1. 输入瘦身（目标 ≤8 min）

| 读 | 不读 |
|---|---|
| 本页设计稿 html（逐字逐块） | design-system.md（token 已对账进 variables，冲突查口径表） |
| FTDD 本模块 §3~§5（组件拆分/fetch 表/状态） | SKILL 正文与 references（惯例已内化） |
| shared 契约中本页类型段 | 上一页已读过的契约段 |
| 全局组件 props 签名（Button/Modal 等，一眼扫） | 全局组件实现细节 |

## 2. 复用资产清单（零脚手架）

工程配置、token 层（variables/global 的 .page-column）、AppHeader/Button/Modal、mock→api→hook→组件→页面容器分层、测试 setup，全部沿用已验收页的**文件结构与命名**。新页面 = 复制分层骨架换内容，禁止重新设计目录。

## 3. 编码套路（目标 ≤10 min，24 文件内）

1. `features/<模块>/types.ts` 先写视图模型：契约缺口一律 **Ext 后缀视图扩展补位 + ⚠️ 留痕注释**（缺口内容、出处、对接时裁决），禁止静默造字段。
2. 顺序固定：constants → mocks（文案逐字对齐设计稿）→ api（JSDoc 标注真实端点与切换时机）→ hooks（`{data/list, loading, error, refetch}` 四件套）→ components（每组件配 module.less）→ page 容器 → router → test。
3. 占位交互（无后端无法接通的按钮）留一行 why 注释，不做假功能。
4. 测试承接 FTDD TC 编号子集：渲染 1 条 + 每类核心交互 1 条即可（静态试做不做全矩阵）。

## 4. 口径决策模式（遇设计稿冲突不考证，直接套）

- **状态稿稿面尺寸 ≠ 实现尺寸**：抽屉/弹框等覆盖层取 design-system §5.5 档位（抽屉 480px、弹框 480 起），稿内小尺寸视为排版示意，留痕即可。
- **全局组件一致性 > 单页状态稿**：全局 Modal/Button 已定稿的字号样式，不因某页状态稿的特例字号改全局。
- **契约口径 > 不一致的稿面文案**：FTDD TC 明确「精确到版本」类硬口径，统一套公式渲染，留痕差异。
- 以上若为首次出现：落地当页并回写 PROJECT 口径表；再遇到同类：查表直接用。

## 5. 验收脚本化（目标 ≤5 min，替代逐状态手动截图）

`apps/web/tools/verify-page.mjs`（puppeteer-core + 系统 Edge，无浏览器下载）一次跑完：设计稿↔实现页 1366/1920/2560 三档整页双开截图 + 关键交互状态截图（config 声明 clicks/assertText/resetTexts）+ 顶栏列↔内容列逐像素断言（left/width 全等），产物落 `.spec/设计稿/screenshots/verify-<页>/`，断言失败退出码 ≠0。新页面只需在 `verify-pages.config.mjs` 登记一条。人工只看截图拼图做还原度判断。

**无头浏览器操作 React 页的可靠路径**（IAB/CDP 通用坑）：
- 点击：`page.evaluate` 内按文本找元素 `.click()`，不用坐标/CDP 合成点击（不触发 React 合成事件）。
- 受控输入：原型 setter + dispatchEvent **不触发** React onChange；直调 `input[Object.keys(input).find(k => k.startsWith('__reactProps$'))].onChange({ target: { value } })`。
- 截图偶发超时/帧撕裂：先查 DOM 断言再重截，勿信单张异常帧。

## 6. 节奏纪律

- 门禁一次过：lint+test+build 串行一条命令，每页一次功能点提交（还原度修正可追加一提交）。
- 单页基准 ~24-26 min；**批量模式**（一次会话 2-3 页）第 2 页起 ~18-22 min（输入/文档/提交摊薄）。
- PROJECT.md 回填用固定段式（进度行 + 契约缺口 + 口径表追加），记忆收尾一次成段。
