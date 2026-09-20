# 浏览器工具选择与集成

## 一、分工
| 测试线 | 首选 | 备选/兜底 |
|---|---|---|
| 功能遍历 | Playwright | browser-use |
| 接口性能 | Playwright response.timing | performance entries |
| 样式断言 | midscenejs aiAssert | Playwright 截图 / browser-use 人工比对 |

按测试线组合，非互斥。

## 二、检测顺序
Playwright → browser-use → 其他工具（agent-browser 等）；全无 = 硬门禁失败，报错停止。midscenejs 缺失 = 降级并明示。

## 三、工具要点
- Playwright：可编程、监听耗时、截图、像素比对；可接 midscenejs fixture 一条链路跑功能+视觉。
- browser-use：替代功能遍历/截图；无 response.timing 时用页面 performance API。
- midscenejs：纯截图 AI 断言；需依赖 + MIDSCENE_MODEL_* 配置。

## 四、缺失处理
- 任何浏览器工具都不存在 → 报错等安装，不测试、不产计划。
- midscenejs 等可选增强缺失 → 降级并明示（计划/文档记录，禁声称已自动测试）。

## 五、悬浮层 hover 可达性
- 浮层出现后，指针从触发器连续移向浮层目标，不得中途隐藏；有间隙即 hover 断点，用 top-full+padding-top 桥接或紧贴。
- 浮层内元素可点；弹出方向不越过 overflow/sticky 边界；z 高于同级。
- 下拉/菜单入口必须到达目标载体；无法跳外域时做 DOM href 断言并标注待真实验证。
- icon 触发器补描述性 id 便于 hover/snapshot/自动化。
- 用真实 hover（Playwright page.hover/agent-browser hover），合成 hover 不触发 :hover。