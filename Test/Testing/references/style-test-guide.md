# 样式测试指南（midscenejs + 视觉验收）

## 一、为什么需要视觉层
代码行和 DOM 都可能对，真实渲染仍会错（遮挡、溢出、暗色对比度、窄屏）。样式测试 = 给 Agent 装眼睛。

## 二、三层能力
| 层 | 能力 | 工具 |
|---|---|---|
| 睁眼看 | 截图视觉验证 | 截图让模型判「长得对不对」 |
| 动手 | 读元素树驱动交互 | snapshot/click，省 token |
| 造条件 | 塞极端数据/切主题/改视口 | 再截图 |

组合：结构驱动交互 + 截图做最终视觉验收。

## 三、7 类坑
面板遮挡、菜单被裁、长文本溢出、暗色对比度、校验失效、提示被遮、窄屏错位——均靠看/交互/造条件暴露。

## 四、midscenejs
视觉驱动，无需 DOM 选择器（选择器脆弱且验不了遮挡/对比度/溢出）。

| API | 用途 |
|---|---|
| aiAssert | 自然语言断言，不符抛错 |
| aiTap/aiInput | 自然语言定位点击/输入 |
| aiQuery/aiBoolean | 提取数据/判断现象 |
| aiWaitFor | 等待状态 |
| startObserving | 连续采样，事后断言瞬时 UI |

## 五、四类用例
1. 页面本身就错：改视口 + 一句 aiAssert。
2. 需交互推进：填→点→断言；信号选可靠（看弹窗状态，不看可能坏掉的 toast）。
3. 瞬时 UI：startObserving 采样 → 动作 → 等窗口盖住出现时机 → stop 后 aiAssert。
4. 精确数值：用 axe-core，不用 AI。

## 六、axe-core
AI 对对比度是观感级会漏判；用 `@axe-core/playwright` 的 `color-contrast` 规则精确算比值。

```bash
pnpm add -D @axe-core/playwright
```
```ts
const results = await new AxeBuilder({ page }).withRules(['color-contrast']).analyze();
expect(results.violations).toEqual([]);
```

## 七、成本控制
aiTap/aiAssert 每次都是视觉模型调用。规划/定位可缓存，**断言永不缓存**。

## 八、环境
```bash
pnpm add -D @midscene/web @midscene/cli @playwright/test @axe-core/playwright
npx playwright install chromium
```
配置 MIDSCENE_MODEL_BASE_URL/API_KEY/NAME/FAMILY（支持 Qwen-VL 等）。集成用 `@midscene/web/playwright` 的 test 注入 page/aiTap/aiAssert。

## 九、执行流程
1. 建视觉基线：有设计稿以 `.spec/设计稿/` 为准；无则原型；还原走查交 Fidelity-Review Testing 场景。
2. 逐页 aiAssert 核对布局/间距/配色/字号层级/三态。
3. 7 类坑逐页造条件走查。
4. 三态逐页验证并截图。
5. 问题立即截图 `screenshots/<页面>_<问题>_<序号>.png`。

## 十、判定
错位/溢出/遮挡/间距/配色/字号/对比度不足/三态缺失错乱，按类型判问题。

## 十一、降级
midscenejs → Playwright toHaveScreenshot → browser-use 截图人工比对；缺失可选增强降级并明示；浏览器全无属硬门禁，开工即停。