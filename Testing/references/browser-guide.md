# 浏览器工具选择与集成（Browser Guide）

> 权威细则：功能遍历、样式断言、接口监听三条线各用哪个浏览器工具，如何检测与组合。

---

## 一、工具分工总览

| 测试线 | 首选工具 | 备选 | 兜底 |
|---|---|---|---|
| 功能遍历（全状态 + 全点击） | **Playwright** | browser-use | —（全无 → 开工预检已报错等安装） |
| 接口性能监听（慢接口） | **Playwright**（`response.timing()`） | `performance.getEntriesByType` | — |
| 样式视觉断言 + 截图 | **midscenejs**（`aiAssert`） | Playwright `toHaveScreenshot` | browser-use 截图人工比对 |

> 三者不是互斥替代，而是**按测试线组合**：功能 + 性能用 Playwright（或 browser-use），样式用 midscenejs。

## 二、检测顺序（执行时按此探测）

```
[检测 1] Playwright 是否可用？
  ├─ 是 → 功能遍历 + 接口监听用 Playwright
  └─ 否 → [检测 2] browser-use 是否可用？
            ├─ 是 → 功能遍历用 browser-use
            └─ 否 → [检测 3] 其他浏览器工具是否可用？（如 agent-browser，列举不穷举）
                      ├─ 是 → 用该工具做功能遍历
                      └─ 否 → 【环境错误】硬性预检失败：报错提醒用户安装，停止工作不测试

[检测 3] midscenejs 是否可用（依赖 + 模型 API Key）？
  ├─ 是 → 样式断言用 midscenejs
  └─ 否 → 降级 Playwright 截图 / browser-use 截图人工比对（向用户说明）
```

## 三、Playwright（首选）

- **优势**：可编程、`page.on('response')` 拿接口耗时、`page.screenshot()` 截图、`toHaveScreenshot` 像素比对；
- **集成**：可直接用 midscenejs 的 Playwright fixture（`@midscene/web/playwright`）在同一个 Playwright 测试里既做功能又做视觉断言；
- **适用**：全状态遍历、全点击遍历、接口耗时监听、截图。

## 四、browser-use（Playwright 不可用时）

- **定位**：用户环境中可用的浏览器工具，替代 Playwright 做功能遍历与截图；
- **局限**：通常没有 `response.timing()` 这类底层网络计时，慢接口监听需改用 `performance.getEntriesByType('resource')`（页面内注入 JS 获取）；
- **适用**：打开页面、点击遍历、截图存证。

## 五、midscenejs（样式/视觉专用）

- **定位**：AI 视觉断言，纯截图驱动、无需选择器，最适合「对照设计稿走查样式」；
- **集成**：`@midscene/web/playwright` fixture，或独立 YAML 脚本（`midscene ./xx.yaml`）；
- **前提**：装依赖 + 配置模型环境变量（`MIDSCENE_MODEL_*`），见 `style-test-guide.md` §二；
- **适用**：`aiAssert`/`aiQuery`/`aiBoolean` 视觉断言、三态验证、`recordToReport` 截图。

## 六、组合示例（推荐方案）

```
功能 + 性能：Playwright（page.on('response') 抓慢接口 + 点击遍历 + 状态遍历）
样式断言：   midscenejs Playwright fixture（aiAssert 对照设计稿 + recordToReport 截图）
```

- 用一个 Playwright 测试工程 + midscenejs fixture，即可同时覆盖三条线，报告统一；
- 若 Playwright 不可用：功能/截图用 browser-use，接口耗时用页面内 `performance` API，样式人工比对。

## 七、工具缺失的处理（硬门禁 + 可选增强降级）

- **任何浏览器工具都不存在（Playwright / browser-use / agent-browser 等全无）= 硬门禁失败**：开工预检（SKILL 步骤 2）直接报错提醒安装，停止工作不测试——不降级、不跳过、不产出测试计划；
- **运行期可选增强缺失**（如 midscenejs 无依赖 / 无模型 Key）→ 降级并告知：必须在测试计划与问题文档中明示降级方案与原因，禁止「声称已自动测试」而实际未做。示例：

```
【提示】未配置 midscenejs 模型，样式测试降级为 Playwright/browser-use 截图 + 人工比对；
       慢接口监听改用页面 performance API 采集（browser-use 无 response.timing 时）。
```

## 八、悬浮层 hover 可达性验证（一类问题：dropdown / tooltip / popover）

> 类别：CSS `:hover`/`group-hover` 类浮层在**真实指针轨迹**下的暴露问题——hover 断点导致移向浮层即隐藏、tooltip 方向越界被容器/相邻元素遮挡、层级（z-index）不足被盖、点击穿透。典型症状来自学径项目：头像下拉菜单与头像间 8px 空隙使菜单中途消失（无法点到设置）；图谱右上 icon 的 tooltip 上浮越过内容区顶被裁剪。**只用合成 hover 事件（JS dispatch）无法触发 `:hover`**，必须用浏览器工具的真实 hover（如 agent-browser `hover <sel/@ref>`、Playwright `page.hover`）。

- [ ] **浮层打开**：hover 触发器（按钮/头像/icon）→ 浮层出现（用 `snapshot` 或截图验证文本可见）；
- [ ] **hover 通路连续（桥接区）**：从触发器移向浮层内目标元素（可 hover 浮层内 ref/selector）→ 浮层**不得中途隐藏**；若浮层定位在触发器下方带空隙（`mt`/gap），hover 轨迹会离开触发器与浮层 → 判定「hover 断点」，正确实现用 `top-full + padding-top` 透明桥接或浮层紧贴；
- [ ] **浮层内元素可点**：hover 到浮层内按钮/链接后执行 `click`，确认未因隐藏/pointer-events 失败；浮层目标离屏/越界会点不到；
- [ ] **tooltip 方向与裁剪**：确认 tooltip 弹出方向不越过会被 `overflow:hidden`/sticky 兄弟（顶栏 z 层）裁剪或遮挡的边界；对疑似越界浮层做**顶部/底部边缘截图**目检；
- [ ] **层级**：浮层 z-index 高于可能覆盖它的 sticky 顶栏与同级卡片；多个相邻浮层互不遮挡关键触发点；
- [ ] **浮层内入口闭环**：下拉/菜单里的一切入口项（如头像菜单「设置」）点击后必须到达其目标载体（弹框/页面/动作），不得是无动作按钮；入口指向外链/云端预览稿时，测试沙箱若无法跟随外域跳转，改做静态 DOM 断言（href 目标存在且指向正确稿）+ 标注「真实浏览器跳转待实现环境复验」；

> 工具备注：agent-browser 的 `hover` 是真实指针移动；对无文本/无 id 的 icon 触发器，先给它补描述性 `id`（利于 snapshot/selector 定位，也利于还原评审与自动化复用）。
> 案例：`.spec/设计评审/沉淀_评审盲区复盘_导航换行与大屏铺开.md`（学径）；通用教训已沉淀于 UI-UX-Review `rendered-quality-checklist.md`。
