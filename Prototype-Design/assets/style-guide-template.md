# 样式规范（Style Guide）— {{需求名称}}

> 用途：**设计任何页面前**，把锁定的风格方案展开成一套完整的样式规范（Design Tokens + 组件规范），作为所有页面的唯一视觉底座。生成 HTML 时把本规范落成 CSS 变量 token，全站严格套用，不得另起炉灶。
>
> 本模板由「高级 UI/UX 专家」角色产出，与「步骤 2 端类型」「步骤 3 锁定风格」严格一致。

---

## 0. 设计原则（一句话到三条）

| 原则 | 说明 |
|------|------|
| {{原则 1，如「少即是多，克制留白」}} | {{一句话解释如何落地}} |
| {{原则 2，如「信息密度真实」}} | {{...}} |

---

## 1. 色彩系统（Color）

### 1.1 基础色

| Token | 色值 | 用途 |
|-------|------|------|
| `--color-primary` | `{{#hex}}` | 主色（品牌色、主按钮、选中态） |
| `--color-primary-hover` | `{{#hex}}` | 主色悬停 |
| `--color-primary-active` | `{{#hex}}` | 主色按下 |
| `--color-primary-subtle` | `{{#hex}}` | 主色浅底（选中背景 / 标签底） |
| `--color-accent` | `{{#hex}}` | 点缀色（强调、高亮） |
| `--color-bg` | `{{#hex}}` | 页面背景 |
| `--color-surface` | `{{#hex}}` | 卡片 / 面板 |
| `--color-text` | `{{#hex}}` | 正文 |
| `--color-text-secondary` | `{{#hex}}` | 辅助文字 |
| `--color-text-tertiary` | `{{#hex}}` | 弱提示 / 占位 |
| `--color-border` | `{{#hex}}` | 描边 / 分割线 |

### 1.2 语义色

| Token | 色值 | 用途 |
|-------|------|------|
| `--color-success` | `{{#hex}}` | 成功 / 已完成 |
| `--color-warning` | `{{#hex}}` | 警告 / 待处理 |
| `--color-danger` | `{{#hex}}` | 危险 / 错误 |
| `--color-info` | `{{#hex}}` | 信息提示 |

> 每类色可再给出「浅底 + 深字」一对，用于状态标签（如 `--color-success-subtle` 底 + `--color-success` 字）。

---

## 2. 字体排版（Typography）

| Token | 字号 / 字重 / 行高 | 用途 |
|-------|-------------------|------|
| `--font-h1` | `{{28px / 700 / 1.3}}` | 页面大标题 |
| `--font-h2` | `{{20px / 600 / 1.4}}` | 区块标题 |
| `--font-h3` | `{{16px / 600 / 1.4}}` | 卡片 / 列表项标题 |
| `--font-body` | `{{14px / 400 / 1.6}}` | 正文 |
| `--font-caption` | `{{12px / 400 / 1.5}}` | 辅助 / 说明 |
| `--font-number` | `{{如 18px / 600}}` | 数据 / 金额强调 |

- **字体族**：`{{如 -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif}}`（系统字体栈，避免引入第三方字体导致离线不可用）；
- **层级铁律**：标题 / 正文 / 辅助三级字号与字重必须分层，禁止单一字号字重。

---

## 3. 间距系统（Spacing，4px 网格）

| Token | 值 | 用途 |
|-------|-----|------|
| `--space-1` | `4px` | 图标与文字间、紧凑间距 |
| `--space-2` | `8px` | 元素内边距 |
| `--space-3` | `12px` | 列表项内距 |
| `--space-4` | `16px` | 卡片内边距 / 常规 gap |
| `--space-5` | `24px` | 区块间距 |
| `--space-6` | `32px` | 页面分区间距 |
| `--space-8` | `48px` | 大区块 / 页头间距 |

> 移动端触控目标建议最小 `44px`，Web 端常规 `32~40px`（与端类型一致）。

---

## 4. 圆角（Radius）

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-sm` | `{{4px}}` | 小标签 / 输入框 |
| `--radius-md` | `{{8px}}` | 按钮 / 卡片 |
| `--radius-lg` | `{{12px}}` | 弹层 / 大卡片 |
| `--radius-full` | `999px` | 胶囊标签 / 头像 |

---

## 5. 阴影与描边（Elevation & Border）

| Token | 值 | 用途 |
|-------|-----|------|
| `--shadow-sm` | `{{0 1px 2px rgba(0,0,0,.06)}}` | 卡片默认 |
| `--shadow-md` | `{{0 2px 8px rgba(0,0,0,.08)}}` | 悬浮 / 下拉 |
| `--shadow-lg` | `{{0 8px 24px rgba(0,0,0,.12)}}` | 弹层 / 模态 |
| `--border` | `1px solid {{--color-border}}` | 常规描边 |

> 阴影克制，避免过重（反 AI 味铁律）。

---

## 6. 基础组件规范（Component Spec）

> 每个组件给出「尺寸 + 配色 + 状态（默认 / hover / 禁用）+ 关键细节」，生成页面时严格按此实现。

### 6.1 按钮（Button）

| 状态 | 规格 |
|------|------|
| 主按钮 | 高 `{{40px}}`、圆角 `--radius-md`、底色 `--color-primary`、文字白、内距 `{{8px 16px}}` |
| 次按钮 | 描边 `--border`、透明底、文字 `--color-text` |
| 悬停 | 主按钮 `--color-primary-hover`、次按钮浅灰底 |
| 禁用 | `opacity: .5` 或灰底灰字 |

### 6.2 输入框（Input）

| 状态 | 规格 |
|------|------|
| 默认 | 高 `{{40px}}`、描边 `--color-border`、圆角 `--radius-sm` |
| 聚焦 | 描边 `--color-primary` + 外圈浅色光晕 |
| 错误 | 描边 `--color-danger` + 下方错误提示文案 |

### 6.3 卡片（Card）

| 项 | 规格 |
|----|------|
| 内距 | `--space-4` |
| 圆角 | `--radius-md` |
| 阴影 | `--shadow-sm` |
| 背景 | `--color-surface` |

### 6.4 状态标签（Badge）

| 类型 | 配色 |
|------|------|
| 成功 | `--color-success-subtle` 底 + `--color-success` 字 |
| 警告 | `--color-warning-subtle` 底 + `--color-warning` 字 |
| 危险 | `--color-danger-subtle` 底 + `--color-danger` 字 |

### 6.5 导航（Navigation）

| 端 | 规格 |
|----|------|
| Web | {{侧边栏宽度 / 顶部导航高度，选中态高亮方式}} |
| 移动 | {{底部 Tab 高度、图标+文字结构、选中态}} |

### 6.6 图标（Icon）

- 统一用内联 SVG，线性风格、`1.5px` 描边、尺寸 `{{16px / 20px / 24px}}`；
- 禁用 emoji 当图标。

---

## 7. CSS 变量 Token 汇总（生成 HTML 时直接落成 `:root`）

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
  --color-success: {{#hex}};
  --color-warning: {{#hex}};
  --color-danger: {{#hex}};
  --color-info: {{#hex}};
  /* 字体 */
  --font-h1: {{28px}};
  --font-h2: {{20px}};
  --font-h3: {{16px}};
  --font-body: {{14px}};
  --font-caption: {{12px}};
  /* 间距 */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-8: 48px;
  /* 圆角 / 阴影 */
  --radius-sm: {{4px}};
  --radius-md: {{8px}};
  --radius-lg: {{12px}};
  --radius-full: 999px;
  --shadow-sm: {{0 1px 2px rgba(0,0,0,.06)}};
  --shadow-md: {{0 2px 8px rgba(0,0,0,.08)}};
  --shadow-lg: {{0 8px 24px rgba(0,0,0,.12)}};
}
```

---

> **沉淀完成标志**：用户确认本规范后，才进入「推导核心页面集 + 生成 HTML」阶段；所有页面的配色 / 字号 / 间距 / 圆角 / 阴影 / 组件一律取自本规范，不一致即返工。
