# 样式测试指南（Style Test Guide · midscenejs）

> 权威细则：如何用 midscenejs 做 AI 视觉断言、验证三态、截图存证；以及工具降级方案。

---

## 一、midscenejs 定位与能力

midscenejs（https://midscenejs.com/zh/）是**视觉驱动的 UI 自动化 Agent**：直接分析截图定位元素与断言，**无需维护 DOM 选择器**，天然适合「对照设计稿做视觉走查」。

核心 API（本 Skill 主要用到）：

| API | 用途 | 示例 |
|---|---|---|
| `aiAssert` | 断言页面是否符合自然语言描述，不符即抛错 | `await agent.aiAssert('订单列表每行间距均匀，无错位')` |
| `aiQuery` | 提取结构化数据（如所有可见按钮文案） | `await agent.aiQuery<string[]>('页面上所有按钮文案')` |
| `aiBoolean` | 判断某现象是否成立 | `await agent.aiBoolean('页面是否有元素溢出遮挡')` |
| `aiTap`/`aiInput` | 定位并点击/输入 | `await agent.aiTap('右上角的关闭按钮')` |
| `recordToReport` | 把当前截图记入报告 | `await agent.recordToReport('空态截图', { content: '首页空态' })` |
| `aiWaitFor` | 等待某状态出现 | `await agent.aiWaitFor('列表加载完成')` |

> midscenejs 还有 YAML 脚本模式（`web:` + `tasks:` + `aiAssert:`），适合写一次性巡检脚本；JS/TS 模式适合嵌入测试框架做断言。

## 二、环境准备

### 2.1 安装

```bash
pnpm add -D @midscene/web @midscene/playwright tsx   # 或 npm install -D ...
```

### 2.2 模型配置（环境变量，选一个视觉模型）

```bash
# 示例：通义千问 Qwen3-VL（阿里云 DashScope）
export MIDSCENE_MODEL_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export MIDSCENE_MODEL_API_KEY="你的-key"
export MIDSCENE_MODEL_NAME="qwen3.7-plus"
export MIDSCENE_MODEL_FAMILY="qwen3"
```

> 也支持豆包 SEED、DeepSeek-V4-Flash-Vision、GPT、Gemini、Kimi 等。模型配置详见 midscenejs 官方文档「模型配置」页。

### 2.3 与 Playwright 集成（推荐）

```ts
import { test } from '@midscene/web/playwright';

test('首页空态样式', async ({ page, aiAssert }) => {
  await page.goto('http://localhost:3000');
  await aiAssert('空态插画与文案居中显示，无错位、无溢出、无遮挡');
});
```

## 三、样式测试执行流程

1. **建视觉基线**：从原型 HTML 提取每页关键视觉项（布局 / 间距 / 配色 / 字号 / 圆角 / 三态），作为断言依据；
2. **逐页断言**：每页写若干条 `aiAssert`，重点核对：
   - 布局：区块位置、对齐方式、栅格；
   - 间距：卡片/行间距、内边距均匀；
   - 配色：主色/语义色与设计稿一致；
   - 字号字重：标题/正文/辅助层级分明；
   - 三态：加载 / 空 / 错误；
3. **三态逐页验证**：
   - 加载态：进入页面瞬间截图（骨架屏/进度条是否正确）；
   - 空态：无数据时截图（空态文案/插画是否居中）；
   - 错误态：mock 接口失败时截图（错误提示 + 重试入口是否存在）；
4. **截图存证**：发现样式问题，立即 `recordToReport` 或 `page.screenshot()` 存 `screenshots/<页面>_<问题简述>_<序号>.png`。

## 四、样式问题判定标准

| 问题类型 | 判定 | 典型表现 |
|---|---|---|
| 错位 | 布局与设计稿不符 | 元素跑偏、栅格错列 |
| 溢出 | 内容超出容器 | 文字/图片溢出卡片、横向滚动条 |
| 遮挡 | 元素互相遮盖 | 弹窗被盖、按钮被遮 |
| 间距不符 | 间距/内边距与设计稿不一致 | 卡片间距过大过小 |
| 配色不符 | 色值与设计稿 token 不一致 | 主色/语义色用错 |
| 字号不符 | 字号/字重层级错误 | 标题与正文字号混乱 |
| 三态缺失/错乱 | 加载/空/错误态缺失或样式错 | 空态文案溢出、错误态无重试按钮 |

## 五、工具降级方案

| 优先级 | 工具 | 说明 |
|---|---|---|
| 1 | midscenejs | AI 视觉断言 + 自动截图，最优；需模型 API Key |
| 2 | Playwright `toHaveScreenshot` | 像素级截图比对，需基线截图；无 AI 语义判断 |
| 3 | browser-use 截图 + 人工比对 | 截图后人工对照设计稿，最兜底 |

> midscenejs 不可用（无依赖/无 Key）时，降级到 Playwright 或 browser-use 截图，并向用户说明：`【提示】未配置 midscenejs，样式测试已降级为截图人工比对。`（midscenejs 为可选增强；全部浏览器工具均不可用属硬门禁失败，开工预检即报错等安装，不进入降级链。）
