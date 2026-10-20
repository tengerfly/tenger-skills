# 设计规范（Design System）— {{产品名称}}

> 用途：UI-UX-Design 步骤 5 产出物。**任何页面生成之前**必须沉淀并经用户确认，落盘 `.superdesign/design-system.md`（〔A〕CLI 硬性路径）或 `.spec/设计稿/design-system.md`（〔B〕自写路径）。
> 强制消费：〔A〕所有生成调用必带 `--context-file` 指向本文件 + 保真约束语（只允许本规范内定义的视觉值）；〔B〕每页成稿的 token 唯一来源同为本文件。
> 组件规范对齐 `../references/open-source-design-systems.md` 所选开源体系基线，不自造无依据的值。

---

## 0. 设计原则（1-3 条）

| 原则 | 说明 |
|---|---|
| {{如「少即是多，克制留白」}} | {{一句话落地方式}} |

---

## 0.5 机器可读 Token 头（对齐 DESIGN.md 开放格式 · 2026-09-20 增）

> 对齐 [google-labs-code/design.md](https://github.com/google-labs-code/design.md) 开放格式：落盘时在本节填 YAML 块（与 §7 逐值一致，不得多值少值），使本文件可被生态工具与下游 agent 直读。 prose 描述感觉，token 是规范值——冲突时以 token 为准。

```yaml
design_tokens:
  name: {{产品名称}}
  colors:
    primary: {{#hex}}        # 对应 --color-primary
    bg: {{#hex}}             # 对应 --color-bg
    surface: {{#hex}}        # 对应 --color-surface
    text: {{#hex}}           # 对应 --color-text
    border: {{#hex}}         # 对应 --color-border
    success: {{#hex}}
    warning: {{#hex}}
    danger: {{#hex}}
    info: {{#hex}}
  typography:
    h1: { font-family: {{字体栈}}, font-size: {{28px}}, font-weight: {{700}}, line-height: {{1.3}} }
    h2: { font-family: {{…}}, font-size: {{20px}}, font-weight: {{600}}, line-height: {{1.4}} }
    body: { font-family: {{…}}, font-size: {{14px}}, font-weight: {{400}}, line-height: {{1.6}} }
    caption: { font-family: {{…}}, font-size: {{12px}}, font-weight: {{400}}, line-height: {{1.5}} }
  spacing: { base: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px, "2xl": 48px }
  rounded: { sm: {{4px}}, md: {{8px}}, lg: {{12px}}, full: 999px }
```

> 本节是 §7 的**镜像视图**（面向机器），§7 是**落码视图**（面向 `:root` 对账）——两处值必须同步维护，门禁 §二同时抽查。

---

## 1. 色彩系统（Color）

### 1.1 基础色

| Token | 色值 | 用途 |
|---|---|---|
| `--color-primary` | `{{#hex}}` | 主色（品牌色、主按钮、选中态） |
| `--color-primary-hover` / `-active` / `-subtle` | `{{…}}` | 悬停 / 按下 / 浅底 |
| `--color-accent` | `{{#hex}}` | 点缀强调 |
| `--color-bg` / `--color-surface` | `{{…}}` | 页面背景 / 卡片面板 |
| `--color-text` / `-secondary` / `-tertiary` | `{{…}}` | 正文 / 辅助 / 弱提示 |
| `--color-border` | `{{#hex}}` | 描边 / 分割线 |

### 1.2 语义色（含浅底对，供状态标签用）

| Token | 色值（浅底对） | 用途 |
|---|---|---|
| `--color-success(-subtle)` | `{{…}}` | 成功 / 已完成 |
| `--color-warning(-subtle)` | `{{…}}` | 警告 / 待处理 |
| `--color-danger(-subtle)` | `{{…}}` | 危险 / 错误 |
| `--color-info(-subtle)` | `{{…}}` | 信息提示 |

---

## 2. 字体排版（Typography）

| Token | 字号/字重/行高 | 用途 |
|---|---|---|
| `--font-h1` | `{{28px / 700 / 1.3}}` | 页面大标题 |
| `--font-h2` | `{{20px / 600 / 1.4}}` | 区块标题 |
| `--font-h3` | `{{16px / 600 / 1.4}}` | 卡片 / 列表项标题 |
| `--font-body` | `{{14px / 400 / 1.6}}` | 正文 |
| `--font-caption` | `{{12px / 400 / 1.5}}` | 辅助说明 |
| `--font-number` | `{{…}}` | 数据 / 金额强调 |

- 字体族：`{{系统字体栈}}`（离线可用，禁止引入需联网的第三方字体）；
- 层级铁律：三级分层，禁止单一字号字重；标题与正文字号拉开阶梯式比例（如 24→18→14→12px），字重分级（标题 600~700 / 正文 400），全部文字同一字号字重 = 视觉层级崩坏。

---

## 3. 间距系统（4px 网格）

| Token | 值 | 用途 |
|---|---|---|
| `--space-1` ~ `--space-8` | `4/8/12/16/24/32/40/48px` | 元素内距 / 列表项 / 卡片 / 区块 / 大分区 |

> 触控目标：移动端最小 44px，Web 常规 32~40px。

---

## 4. 圆角与阴影（Radius & Elevation）

| Token | 值 | 用途 |
|---|---|---|
| `--radius-sm` / `-md` / `-lg` / `-full` | `4 / 8 / 12px / 999px` | 输入框 / 卡片按钮 / 弹层 / 胶囊 |
| `--shadow-sm` / `-md` / `-lg` | `{{…}}` | 卡片 / 悬浮下拉 / 弹层模态（克制，防 AI 味） |

> 常规描边不单设变量，直接用 `1px solid var(--color-border)`（§1.1 的 `--color-border` 即描边色）。

---

## 5. 组件规范（Component Spec）

> 每组件给出「尺寸 + 配色 + 状态（默认/hover/active/disabled）+ 关键细节」。生成页面严格照此实现。

### 5.1 按钮（Button）

| 状态 | 规格 |
|---|---|
| 主按钮 | 高 `{{40px}}`、圆角 `--radius-md`、底 `--color-primary`、白字、内距 `{{8px 16px}}` |
| 次按钮 / 文字按钮 / 危险按钮 | `{{…}}` |
| hover / disabled | `{{…}}` |

### 5.2 输入框（Input）与表单（Form）

| 项 | 规格 |
|---|---|
| 输入框 | 高 `{{40px}}`、默认/聚焦/错误三态 `{{…}}` |
| 选择器 / 日期 / 开关 | `{{…}}` |
| 表单布局 | 标签位置（`{{顶部/左侧}}`）、标签宽、必填标记、错误文案位置 |

### 5.3 表格（Table）——数据密集页核心

| 项 | 规格 |
|---|---|
| 行高 / 行密度 | `{{48px，适中密度}}` |
| 表头 | 字重 `{{600}}`、底色 `{{--color-bg}}`、高 `{{44px}}` |
| 行交互 | hover 底色 `{{…}}`；行点击与行内按钮的区分方式 |
| 状态标签列 | 语义色浅底对（§1.2） |
| 分页 | 位置（`{{右下}}`）、每页条数、页码样式 |
| 空态 / 加载态 | `{{空态插画或占位文案、骨架屏或 spinner}}` |

### 5.4 列表（List）

| 项 | 规格 |
|---|---|
| 行结构 | 左（头像/图标 `{{…px}}`）+ 中（标题 + 描述）+ 右（操作/时间/状态） |
| 行间距 / 分隔 | `{{…}}` |
| 悬停 / 选中态 | `{{…}}` |

### 5.5 卡片（Card）与统计卡（Stat Card）

| 项 | 规格 |
|---|---|
| 卡片 | 内距 `--space-4`、圆角 `--radius-md`、阴影 `--shadow-sm`、底 `--color-surface` |
| 统计卡 | 数值字号（`--font-number`）、标签、趋势标记（涨跌色） |

### 5.6 弹框（Modal）与抽屉（Drawer）

| 项 | 弹框 | 抽屉 |
|---|---|---|
| 宽度 | `{{如 480/640/800px 三档}}` | `{{如 480px}}`，贴 `{{右}}` 侧 |
| 遮罩 | `{{rgba(0,0,0,.45)}}` | 同左 |
| 结构 | 标题 + 关闭钮 / 内容区 / 底部操作栏（按钮顺序 `{{主右次左}}`） | 同左 |
| 进出场 | `{{淡入 + 上移 8px，200ms}}` | `{{右侧滑入，240ms}}` |

### 5.7 导航（Navigation）

| 端 | 规格 |
|---|---|
| Web | `{{侧边栏宽 220px 折叠 64px / 顶部导航高 56px；选中态：浅底 + 主色字 + 左侧指示条}}` |
| 移动 | `{{底部 Tab 高 56px、图标+文字、选中态}}` |
| 面包屑 / 页头 | `{{…}}` |

### 5.8 状态标签（Badge）与 Tab

| 项 | 规格 |
|---|---|
| Badge | 语义色浅底对、圆角 `--radius-full`、内距 `{{2px 8px}}`、字号 `--font-caption` |
| Tab | 下划线式 / 胶囊式 `{{…}}`、选中态、徽标 |

### 5.9 图标（Icon）

- 统一线性风格、`1.5px` 描边、尺寸 `{{16/20/24px}}`，来源 `{{iconify 图标集名}}`；
- 禁用 emoji 当图标。

### 5.10 界面状态设计规范（UI States）

> 页面绝不只有「正常显示（Success）」一种状态。凡布局清单/原型中出现下列状态的页面，设计稿必须给出对应状态稿；各状态视觉呈现遵循本表，保证全站一致。1–8 为通用必备状态，9–10 仅涉 AI 生成/对话功能时适用。

| # | 状态 | 触发场景 | 设计稿呈现要求 |
|---|---|---|---|
| 1 | Skeleton 骨架屏 | 页面首次加载 | 与最终页面结构一致的灰色占位块（标题条/文本行/卡片轮廓），不用转圈 spinner 整页代替，减少视觉抖动 |
| 2 | Loading 加载中 | 局部提交 / 刷新 | 按钮 Spin + 禁用样式（暗示防重复提交） |
| 3 | Success 成功 | 数据正常返回 | 正常稿；空数据与长文本截断（Ellipsis）样式一并定义 |
| 4 | Empty 空态 | 查询结果为 0 | 引导插画 + 一句现状说明 +「新建条目」CTA，禁止整页留白 |
| 5 | Error 业务错误 | 500/502 服务端异常 | 友好 Toast 或错误 Banner +「重新加载」/「联系管理员」出口 |
| 6 | Disabled 禁用 | 缺少操作前置条件 | 变灰 + `cursor: not-allowed` + Tooltip 说明缺少什么条件 |
| 7 | Permission Denied | 403 无权限 | 无权限专属插画 + 申请权限引导入口 |
| 8 | Network Error | 断网 / 网络超时 | 顶部全局 Offline 提示条（断网常驻、恢复连接自动消失） |
| 9 | Streaming 流式打字 | AI 文本生成中（SSE） | 打字机逐字输出 + 光标闪烁（Blinking Cursor）；仅 AI 对话/生成类页面适用 |
| 10 | Partial Data 增量数据 | AI 结构化输出生成中 | 已到字段先渲染、缺失字段占位（渐进呈现）；仅 AI 结构化输出场景适用 |

> 组件级状态（按钮 hover/active/disabled 等）按 §5 各组件规范执行，与本节页面级状态互为补充。

---

### 5.11 页面宽度分层（Page Width Tiers）

**〔先分角色，再定档位——两角色不可套同一口径〕**

| 角色 | 判据 | 宽度口径 |
|---|---|---|
| **全局导航外壳** | 承载跨页一级入口的顶栏 / 侧栏（本产品无侧栏时＝顶栏） | **跨页恒定**：同容器宽、同左缘、同内距，**不随内容档位缩放**；限宽页不得把导航外壳一起居中缩窄 |
| **页内标题栏** | 只含本页 h1／页头操作，不承载跨页导航 | 与该页**内容主列**同宽对齐（报纸式上下对齐） |

> 辨析来源：travel-agent 2026-10-11 走查纠正的是「页内标题栏用全局宽容器、与内容列不对齐」；knowledge-bases 2026-10-12 走查纠正的是反向错误——「全局导航外壳随内容档位被 `max-width` 一起缩窄居中，跨页跳变」。两条都成立，因为角色不同。**混用会让一条规则把另一条的 bug 判成正确**（本项目 §5.11 旧版即因此把 `.app--reading` 落在页框上）。

| 档位 | 内容主列 | 全局导航外壳 | 适用页面 |
|---|---|---|---|
| 限宽居中页 | `width:100%; max-width:Npx; margin-inline:auto` + 大屏断点放大 | 恒定满宽（跨页同一档） | 内容阅读/表单/后台列表 |
| 全宽铺满页 | 铺满视口 | 恒定满宽（与限宽页同一档） | 数据大屏/仪表盘 |

- 页面归属清单、内容列宽、导航外壳宽在生成前与用户确认后填入本节（核对见 design-review-gate §五.B）；
- **限宽只能落在内容主列容器上**：`max-width` 加在承载导航外壳的页框／根容器＝P1 缺陷（导航跟着缩）；
- 限宽值是「当前屏基准」非死值：大屏断点放大（如 ≥1536 → N2），禁单一 `max-w` 死锁、禁不同页写法不一致；
- 限宽页内容主列禁止内部二次窄列；
- **跨页不变量实测**：全部页面的导航外壳左缘／宽度在 1440 与 1920 两档下必须逐一相等，无测量值只能标「未验证」。

## 6. 动效原则（Motion）

> 判据见 `../references/motion-design-guide.md`（决策四问 / 强度档 / 曲线与时长 token）；本节定档，§7 落 token。

| 项 | 值 |
|---|---|
| 强度档 | `{{静态 / 克制流动 / 编排}}`（随风格决策定，缺省克制流动） |
| 时长 | 反馈 `{{120ms}}` / 小浮层 `{{160ms}}` / 下拉 `{{200ms}}` / 弹层抽屉 `{{240ms}}`（常规 UI <300ms；弹层 / 抽屉类按档放宽至 ≤500ms） |
| 缓动 | 进入 `--ease-out` / 移动 `--ease-in-out` / 抽屉 `--ease-drawer`（自定义曲线，禁 ease-in） |
| 原则 | 只动「进出场 / 反馈」；无目的不动、高频（键盘触发）不动、可打断 |

---

## 7. CSS 变量 Token 汇总（生成 HTML 直接落 `:root`）

> **一条一行**（便于下游机械对账：本表条数 = 下游 `styles/variables` 应落条数）；本表与 §1~§4、§6 声明必须一致，不得缺项。

```css
:root {
  /* 色彩 · 基础（§1.1） */
  --color-primary: {{#hex}};
  --color-primary-hover: {{#hex}};
  --color-primary-active: {{#hex}};
  --color-primary-subtle: {{#hex}};
  --color-accent: {{#hex}};
  --color-bg: {{#hex}};
  --color-surface: {{#hex}};
  --color-text: {{#hex}};
  --color-text-secondary: {{#hex}};
  --color-text-tertiary: {{#hex}};
  --color-border: {{#hex}};
  /* 色彩 · 语义（§1.2，各含浅底对 -subtle） */
  --color-success: {{#hex}};
  --color-success-subtle: {{#hex}};
  --color-warning: {{#hex}};
  --color-warning-subtle: {{#hex}};
  --color-danger: {{#hex}};
  --color-danger-subtle: {{#hex}};
  --color-info: {{#hex}};
  --color-info-subtle: {{#hex}};
  /* 字体（§2） */
  --font-h1: {{28px}};
  --font-h2: {{20px}};
  --font-h3: {{16px}};
  --font-body: {{14px}};
  --font-caption: {{12px}};
  --font-number: {{…}};
  /* 间距（§3，4px 网格，连续无跳号） */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 40px;
  --space-8: 48px;
  /* 圆角 / 阴影（§4） */
  --radius-sm: {{4px}};
  --radius-md: {{8px}};
  --radius-lg: {{12px}};
  --radius-full: 999px;
  --shadow-sm: {{…}};
  --shadow-md: {{…}};
  --shadow-lg: {{…}};
  /* 动效曲线（§6，自定义曲线，禁 ease-in） */
  --ease-out: {{cubic-bezier(0.23, 1, 0.32, 1)}};
  --ease-in-out: {{cubic-bezier(0.77, 0, 0.175, 1)}};
  --ease-drawer: {{cubic-bezier(0.32, 0.72, 0, 1)}};
}
```

---

> **放行标志**：用户明确确认本规范 → 落 `.superdesign/design-system.md` → 步骤 7 生成；所有页面视觉值只取自本文件，出现规范外值即返工。
