# 样式测试指南（Style Test Guide · midscenejs + 视觉验收）

> 权威细则：给 Agent 装眼睛的三层看、midscenejs 自然语言回归断言、axe-core 精确阈值、三态、截图存证、成本控制与降级。
> 来源：Vibe Coding 高效能秘籍 第三章（vc-06「给 Agent 装上眼睛」、vc-07「用自然语言沉淀 UI 回归测试」）。

---

## 一、核心认知：代码闭环罩不住的 UI 视觉层

typecheck 验类型、lint 验风格、单测验逻辑，但「页面长得对不对」只有看到 UI 才能回答。**代码每一行都是「对」的，DOM 结构也「对」，只有真实渲染那一帧是错的**（z-index 遮挡、长文本溢出、暗色对比度塌掉、窄屏错位）。

因此样式测试 = 给 Agent 装上眼睛，让「看」变成可执行的验证环节。核心方法论是**三层「看」的能力**，每解锁一层抓一类新问题。

---

## 二、三层「看」的能力（给 Agent 装眼睛）

| 关卡 | 能力 | 抓哪类问题 | 工具动作 |
|---|---|---|---|
| 第一关 | **睁开眼**（截图视觉验证） | 布局/遮挡/配色/层级（代码 review 十轮看不出） | 截图，模型看像素回答「长得对不对」 |
| 第二关 | **动手**（读页面结构 + 交互） | 逻辑漏洞（空表单能提交等，要填/点/看走完交互链） | `snapshot` 读元素树（DOM/可访问性树）驱动交互，省 token |
| 第三关 | **造条件**（边界状态主动走一遍） | 长文本溢出、暗色对比度、窄屏错位（正常数据不触发） | 塞极端数据、切主题、改视口，再截图 |

**两条路线配合**：
- **截图视觉验证**：模型直接看渲染像素，回答「长得对不对」——布局/遮挡/配色归它；
- **读页面结构**：拿页面可访问性树或 DOM（结构化描述，比截图省 token 得多），回答「有没有、能不能」——按钮在不在、表单能不能填、点了跳哪归它。
- **组合拳**：结构驱动交互（找到输入框→填→点提交），截图做最终视觉验收（截一张确认提示对不对）。

> 典型命令（agent-browser 举例）：`open` → `snapshot -i`（拿元素引用）→ `click` → `get count`（判断「有没有出现某元素」）。纯靠读结构和查状态就能挖出交互逻辑漏洞。

---

## 三、7 类 UI 坑（静态检查全抓不到，靠「看」才抓得到）

> 作为样式测试的走查锚点清单，逐页过一遍：

| 坑 | 现象 | 靠哪种能力 |
|---|---|---|
| 面板遮挡 | 弹出面板被下方卡片盖住（z-index） | 截图视觉验证 |
| 菜单被裁 | 行内操作菜单被容器裁掉（overflow:hidden） | 截图视觉验证 |
| 长文本溢出 | 超长内容把相邻列挤出屏幕 | 造长数据 + 截图 |
| 暗色对比度 | 副标题/次要文字灰到看不清 | 切主题 + 截图（配 axe-core） |
| 校验失效 | 空表单也能提交成功 | 先填表再提交再判断 |
| 提示被遮 | 成功提示被顶栏挡住 | 交互后立即截图 |
| 窄屏错位 | 手机尺寸下按钮被挤出屏幕 | 改视口 + 截图 |

---

## 四、midscenejs 定位与能力（自然语言回归断言）

midscenejs（https://midscenejs.com/zh/）是**视觉驱动的 UI 自动化 Agent**：直接分析截图定位元素与断言，**无需维护 DOM 选择器**。

> **为什么不用传统 e2e 选择器**：① 选择器脆弱——`.filterbar .more-filter-btn` 绑死 DOM/类名，重构就断，断因与「功能坏没坏」无关，用例攒多后维护成本高、最终整套废弃；② `toBeVisible` 验的是 DOM 可见性（有没有尺寸、有没有 display:none），**不管元素是否被别的东西盖住**——遮挡/被裁/对比度/溢出这些视觉问题，传统断言写都写不出来。

核心 API：

| API | 用途 | 示例 |
|---|---|---|
| `aiAssert` | 断言页面是否符合自然语言描述，不符即抛错 | `await aiAssert('"更多筛选"弹出的面板完整可见，没有被下方表格盖住')` |
| `aiTap`/`aiInput` | 用自然语言定位并点击/输入（无选择器） | `await aiTap('右上角的"更多筛选"按钮')` |
| `aiQuery` | 提取结构化数据（如所有可见按钮文案） | `await aiQuery<string[]>('页面上所有按钮文案')` |
| `aiBoolean` | 判断某现象是否成立 | `await aiBoolean('页面是否有元素溢出遮挡')` |
| `aiWaitFor` | 等待某状态出现 | `await aiWaitFor('列表加载完成')` |
| `startObserving` | 连续采样页面帧，事后对「录像」断言 | 见 §五 第三种用例形态 |

---

## 五、四种用例形态（覆盖「页面错 / 要交互 / 瞬时 UI」）

> 写样式用例时先判断属于哪一类，选对应写法。

1. **页面本身就是错的**：一句 `aiAssert` 完事（长文本溢出、暗色对比度、窄屏错位）。窄屏多一步 `setViewportSize` 提前造条件。
   ```ts
   await page.setViewportSize({ width: 390, height: 780 });
   await page.reload();
   await aiAssert('页面顶部能看到完整的"更多筛选"按钮，筛选栏没有任何内容被裁切或伸出右边缘');
   ```
2. **要先交互推进状态**：填表 → 点提交 → 再断言（空表单校验失效类）。
   - **测试信号要选可靠的**：不拿「坏掉的 toast」做判断（toast 本身坏了会误判），改看弹窗状态——「断言弹窗仍打开并给出校验错误，而不是已提交关闭」。
3. **瞬时 UI**（toast 一闪而过）：截图断言对瞬时 UI 天然失效 → 用 `startObserving` 连续采样帧，事后对整段「录像」断言：
   ```ts
   const observer = await agent.startObserving();
   await agent.aiTap('"发送邀请"按钮');
   await page.waitForTimeout(1500); // 等 toast 弹出再停采样，采样窗口盖住 toast 出现时机
   const observation = await observer.stop();
   await observation.aiAssert('提交过程中出现完整可见的成功提示 toast，没有被顶部导航栏挡住');
   ```
   - **踩坑**：`stop()` 不能点完立刻执行（toast 还没弹出录像就停了），中间补等待。
4. **精确数值类**（对比度等）：不用 AI 断言，用 axe-core（见 §六）。

---

## 六、AI 视觉断言的软肋 + axe-core 精确阈值

AI 视觉断言给的是**人类观感级别**判断，能覆盖大部分场景。但有明确数字定义的东西（如 **WCAG 对比度 4.5:1**）会漏判——模型看截图觉得「还能读」就不报红，实际对比度可能只有 2.76:1。

**精确数值交给确定性代码**：`axe-core` 读渲染后每个文字节点的计算样式（前景色/背景色/字号），代入 WCAG 亮度公式算比值，低于阈值报违规（哪个元素、当前比值多少，写得清清楚楚）。

```bash
pnpm add -D @axe-core/playwright
```
```ts
import AxeBuilder from '@axe-core/playwright';
test('暗色模式下文字对比度达标', async ({ page, aiTap }) => {
  await aiTap('顶部的"暗色"切换按钮');   // 操作用 aiTap，不用选择器
  const results = await new AxeBuilder({ page }).withRules(['color-contrast']).analyze();
  expect(results.violations).toEqual([]);
});
```

> **分工原则**：模糊的观感交给模型（aiTap/aiAssert），精确的数值交给代码（axe-core），同一份 spec 各司其职。

---

## 七、成本控制：cache（断言永不缓存）

每一步 `aiTap`/`aiAssert` 都是一次视觉模型调用，用例多了会慢（几十条十几分钟）。

- **cache 机制**：「规划/定位」结果（点哪个按钮、元素在哪）缓存复用，页面没大变不调模型；但**断言永不缓存**——断言是测试的目的本身，缓存断言就等于没测。
- 结果：重复劳动被 Cache 省掉，真正的判断一次都不能少。

---

## 八、环境准备

### 8.1 安装

```bash
pnpm add -D @midscene/web @midscene/cli @playwright/test @axe-core/playwright
npx playwright install chromium
```

### 8.2 模型配置（环境变量，选一个视觉模型）

```bash
# 示例：通义千问 Qwen3-VL（阿里云 DashScope）
export MIDSCENE_MODEL_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export MIDSCENE_MODEL_API_KEY="你的-key"
export MIDSCENE_MODEL_NAME="qwen3-vl-plus"
export MIDSCENE_MODEL_FAMILY="qwen3-vl"
```

> 也支持豆包 SEED、DeepSeek-V4-Flash-Vision、GPT、Gemini、Kimi 等。模型配置详见 midscenejs 官方文档「模型配置」页。

### 8.3 与 Playwright 集成（推荐）

```ts
import { test } from '@midscene/web/playwright';

test('首页空态样式', async ({ page, aiAssert }) => {
  await page.goto('http://localhost:3000');
  await aiAssert('空态插画与文案居中显示，无错位、无溢出、无遮挡');
});
```

---

## 九、样式测试执行流程

> **基准选择（与 Fidelity-Review 内嵌衔接）**：存在 UI 设计稿基准（`.spec/设计稿/` 或用户指定外部稿）时，还原度走查交由 `Fidelity-Review` Testing 场景执行（视觉/交互/超长文案专项，就地收轻量清单）；本指南负责三态 + 基础视觉断言 + 7 类坑走查，视觉基线与设计稿保持一致。无设计稿基准则回退原型基准 + midscenejs 视觉断言。

1. **建视觉基线**：优先从 UI 设计稿（`.spec/设计稿/` HTML/design-system token）提取每页关键视觉项（布局 / 间距 / 配色 / 字号 / 圆角 / 三态）；无设计稿时从原型 HTML 提取，作为断言依据；
2. **逐页断言**：每页写若干条 `aiAssert`，重点核对：
   - 布局：区块位置、对齐方式、栅格；
   - 间距：卡片/行间距、内边距均匀；
   - 配色：主色/语义色与设计稿一致；
   - 字号字重：标题/正文/辅助层级分明；
   - 三态：加载 / 空 / 错误；
3. **7 类坑走查**：按 §三 清单逐页过一遍（面板遮挡/菜单被裁/长文本溢出/暗色对比度/校验失效/提示被遮/窄屏错位），造条件（塞长数据/切主题/改视口）主动暴露；
4. **三态逐页验证**：
   - 加载态：进入页面瞬间截图（骨架屏/进度条是否正确）；
   - 空态：无数据时截图（空态文案/插画是否居中）；
   - 错误态：mock 接口失败时截图（错误提示 + 重试入口是否存在）；
5. **截图存证**：发现样式问题，立即 `recordToReport` 或 `page.screenshot()` 存 `screenshots/<页面>_<问题简述>_<序号>.png`。

---

## 十、样式问题判定标准

| 问题类型 | 判定 | 典型表现 |
|---|---|---|
| 错位 | 布局与设计稿不符 | 元素跑偏、栅格错列 |
| 溢出 | 内容超出容器 | 文字/图片溢出卡片、横向滚动条 |
| 遮挡 | 元素互相遮盖 | 弹窗被盖、按钮被遮 |
| 间距不符 | 间距/内边距与设计稿不一致 | 卡片间距过大过小 |
| 配色不符 | 色值与设计稿 token 不一致 | 主色/语义色用错 |
| 字号不符 | 字号/字重层级错误 | 标题与正文字号混乱 |
| 对比度不足 | 文字与背景对比度低于 WCAG 阈值 | 暗色下灰字几乎看不见（用 axe-core 算） |
| 三态缺失/错乱 | 加载/空/错误态缺失或样式错 | 空态文案溢出、错误态无重试按钮 |

---

## 十一、工具降级方案

| 优先级 | 工具 | 说明 |
|---|---|---|
| 1 | midscenejs | AI 视觉断言 + 自动截图，最优；需模型 API Key |
| 2 | Playwright `toHaveScreenshot` | 像素级截图比对，需基线截图；无 AI 语义判断 |
| 3 | browser-use 截图 + 人工比对 | 截图后人工对照设计稿，最兜底 |

> midscenejs 不可用（无依赖/无 Key）时，降级到 Playwright 或 browser-use 截图，并向用户说明：`【提示】未配置 midscenejs，样式测试已降级为截图人工比对。`（midscenejs 为可选增强；全部浏览器工具均不可用属硬门禁失败，开工预检即报错等安装，不进入降级链。）
