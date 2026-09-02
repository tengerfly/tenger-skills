# 页面还原度校验指南（高保真验收）

> 用途：在编码完成后，核对「实现页」与「高保真原型」的还原度，输出可验收结论。
> 还原度是 Frontend-Dev 的第一原则之一——**还原基线不符 = 未完成**，必须返工到符合才交付。

---

## 一、还原基线的定义

步骤 4 已产出「页面 × 还原基线」清单。每一页的还原基线含：

| 维度 | 说明 | 不符示例 |
|------|------|---------|
| 结构 | 区块顺序、层级、导航是否与原型一致 | 漏区块 / 顺序颠倒 / 多出原型没有的模块 |
| 布局 | 对齐、栅格、间距、宽高比例 | 卡片间距、表格列宽明显走样 |
| 配色 | 色值与 token 一致 | 主按钮颜色、背景色与原位不同 |
| 字号/字重 | 字号字重与原型一致 | 标题/正文层级模糊 |
| 圆角/阴影 | 与原型一致 | 卡片圆角、弹层阴影不同 |
| 图标/图片 | 同一套资源、同尺寸 | 用错图标 / 占位图替代 |
| 文案 | 与原型文案一致 | 按钮文字、空态文案改动 |
| 三态 | 加载/空/错误态齐全且符合 PRD | 只做了成功态 |
| 交互细节 | hover/点击/禁用/表单反馈符合原型与 PRD | 点击无反馈、按钮无禁用态 |

> 还原基线在 Scope Gate 时已呈现给用户确认。若原型无三态设计，按 PRD 兜底方案或组件库标准态实现并在基线中注明。

---

## 二、校验工具与降级策略

```
Playwright 可用 ──► 自动截图比对（首选，推荐）
browser-use 可用 ──► 替代截图工具（Playwright 不可用时）
两者都不可用 ──► 跳过自动截图，静态对照（读原型 HTML 结构/样式值逐一核对）
                + 向用户明示：【提示】未检测到 Playwright 与 browser-use，已跳过自动截图还原校验，改用静态对照。
```

> 编码主流程不依赖浏览器工具；还原校验只是验收手段，工具不可用不阻塞开发，但**结论要如实记录**（自动比对 or 静态对照）。

---

## 三、Playwright 截图比对流程（首选）

### 3.1 准备

```bash
# 项目内安装（未安装时）
pnpm add -D playwright
pnpm exec playwright install chromium
```

### 3.2 写比对脚本（临时脚本，校验后清理或归档进产物 README）

```ts
// scripts/fidelity-check.ts
import { chromium } from 'playwright';
import { readFileSync } from 'node:fs';

const PROTOTYPE_URL = 'file:///abs/path/to/prototype/index.html'; // 原型 HTML
const DEV_URL = 'http://localhost:5173/orders';                    // 实现页

const cases = [
  { name: 'orders-list', prototype: `${PROTOTYPE_URL}`, impl: `${DEV_URL}` },
  // ... 页面 × 原型映射（来自还原基线清单）
];

async function shot(url: string, path: string) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(300);
  await page.screenshot({ path, fullPage: true });
  await browser.close();
}

for (const c of cases) {
  await shot(c.prototype, `shots/${c.name}.prototype.png`);
  await shot(c.impl, `shots/${c.name}.impl.png`);
}
```

### 3.3 比对与记录

- 两张截图并排目视比对（或在脚本内用像素相似度粗筛）；
- 逐项对照还原基线维度，输出结论表：

```
页面：订单列表（orders-list）
结构    ✅ 一致
布局    ✅ 间距/对齐一致
配色    ✅ 色值引用 token，与原型一致
字号    ✅ 一致
三态    ⚠️ 错误态使用组件库标准文案（原型无设计，已在基线注明）
交互    ✅ hover/点击有反馈
结论：还原达标（1 项基线内差异）
```

- **差异两分**：
  - **可接受**：响应式断点行为、字体回退、动效实现方式、组件库标准交互细节（还原基线已注明）；
  - **必须修正**：区块缺失、间距/配色/字号偏差、三态缺失、交互无反馈——进入返工清单，修完复验。

### 3.4 小程序/移动端

- app/小程序端无法直接开浏览器页面时：用「设计稿刻度换算核对」替代截图（RN dp / Flutter 逻辑像素 / 小程序 rpx 按 750 换算），并核对各端真机/工具截图（若有）；
- 有 browser-use 时可用其对小程序开发者工具或预览截图辅助核对。

---

## 四、静态对照（无浏览器工具时兜底）

1. 打开原型 HTML 文件，读取目标区块的 class/结构/内联样式；
2. 打开实现页组件代码与对应 `.module.scss`；
3. 逐项核对：结构层级（DOM 树相似）、布局方式（flex/grid 与原型视觉一致）、间距值（换算后相等）、色值（原型色 → variables token 值一致）、字号字重、文案；
4. 交互与三态按 PRD + 代码审查确认；
5. 输出与 3.3 相同的结论表，并注明「静态对照」方式。

---

## 五、常见还原度问题

| 问题 | 纠正 |
|------|------|
| 色值自由发挥 / 写死 | 全部引用 variables token，值从原型提取 |
| 间距用「大约」「差不多」 | 与原型像素级核对（含换算），偏差即修 |
| 只做成功态 | 补全加载/空/错误三态 |
| 用组件库默认布局顶替原型布局 | 布局基线必须匹配原型，不是「组件库长这样就行」 |
| 图标/图片用错 | 从原型提取同一套资源 |
| 文案改写 | 与原型文案一致（除非 PRD 有修正并登记） |
| 截图工具不可用却不告知 | 如实记录校验方式；自动比对与静态对照结论分开标注 |

---

## 六、验收自检清单

- [ ] 每页逐项对照还原基线维度（结构/布局/配色/字号/圆角阴影/图标/文案/三态/交互）？
- [ ] 自动截图比对（Playwright/browser-use）或已注明静态对照原因？
- [ ] 必须修正差异已返工并复验？
- [ ] 差异记录（可接受项）已登记，交付 README 可查？
