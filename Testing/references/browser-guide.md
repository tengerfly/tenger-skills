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
