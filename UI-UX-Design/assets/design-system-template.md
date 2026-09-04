# 设计规范（Design System）— {{产品名称}}

> 用途：UI-UX-Design 步骤 5 产出物。**任何页面生成之前**必须沉淀并经用户确认，落盘 `.superdesign/design-system.md`（CLI 硬性路径）。
> 强制消费：所有生成调用必带 `--context-file` 指向本文件 + 保真约束语（只允许本规范内定义的视觉值）。
> 组件规范对齐 `references/open-source-design-systems.md` 所选开源体系基线，不自造无依据的值。

---

## 0. 设计原则（1-3 条）

| 原则 | 说明 |
|---|---|
| {{如「少即是多，克制留白」}} | {{一句话落地方式}} |

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
- 层级铁律：三级分层，禁止单一字号字重。

---

## 3. 间距系统（4px 网格）

| Token | 值 | 用途 |
|---|---|---|
| `--space-1` ~ `--space-8` | `4/8/12/16/24/32/48px` | 元素内距 / 列表项 / 卡片 / 区块 / 大分区 |

> 触控目标：移动端最小 44px，Web 常规 32~40px。

---

## 4. 圆角与阴影（Radius & Elevation）

| Token | 值 | 用途 |
|---|---|---|
| `--radius-sm/md/lg/full` | `{{4/8/12px / 999px}}` | 输入框 / 卡片按钮 / 弹层 / 胶囊 |
| `--shadow-sm/md/lg` | `{{…}}` | 卡片 / 悬浮下拉 / 弹层模态（克制，防 AI 味） |
| `--border` | `1px solid --color-border` | 常规描边 |

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

---

## 6. 动效原则（Motion）

| 项 | 值 |
|---|---|
| 时长 | 短 `{{150ms}}` / 中 `{{200ms}}` / 长 `{{300ms}}` |
| 缓动 | `{{ease-out 为主}}` |
| 原则 | 只动「进出场 / 反馈」，不做装饰性动画 |

---

## 7. CSS 变量 Token 汇总（生成 HTML 直接落 `:root`）

```css
:root {
  /* 色彩 */
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
  --color-success: {{#hex}}; --color-warning: {{#hex}};
  --color-danger: {{#hex}};  --color-info: {{#hex}};
  /* 字体 */
  --font-h1: {{28px}}; --font-h2: {{20px}}; --font-h3: {{16px}};
  --font-body: {{14px}}; --font-caption: {{12px}}; --font-number: {{…}};
  /* 间距 */
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-5: 24px; --space-6: 32px; --space-8: 48px;
  /* 圆角 / 阴影 */
  --radius-sm: {{4px}}; --radius-md: {{8px}}; --radius-lg: {{12px}}; --radius-full: 999px;
  --shadow-sm: {{…}}; --shadow-md: {{…}}; --shadow-lg: {{…}};
}
```

---

> **放行标志**：用户明确确认本规范 → 落 `.superdesign/design-system.md` → 步骤 7 生成；所有页面视觉值只取自本文件，出现规范外值即返工。
