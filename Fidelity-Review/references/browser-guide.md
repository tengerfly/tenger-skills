# 浏览器工具预检与双开截图并排比对法（Browser Guide）

> 用途：确定本次截图/点击工具，执行「实现页 ↔ 设计稿页」的双开截图，为视觉/交互/超长文案走查提供证据。

---

## 一、工具硬性预检（铁律五）

检测顺序与判定（全仓库统一口径）：

```
Playwright 可用 ──► 首选（自动控制、稳定截图、支持点击/输入/监听）
Playwright 异常 ──► browser-use 或其他浏览器工具（如 CodeBuddy 的 agent-browser）替代
全部不可用     ──► 报错停止、不产出任何评审文档：
                    【环境错误】未检测到任何可用的浏览器工具（Playwright / browser-use /
                    agent-browser 等）。页面还原度评审硬性依赖浏览器截图走查与交互验证，
                    请先安装并启用任一浏览器工具，安装完成后重新运行本 skill。
```

> 本 skill 的截图与点击是**硬性产出**（铁律二/五），无浏览器工具 → 不降级为纯静态源码核对（静态核对无法验证真实渲染的溢出/层级/交互反馈）。

---

## 二、Playwright 双开截图流程（首选）

### 2.1 安装（未安装时，在实现页工程内）

```bash
pnpm add -D playwright
pnpm exec playwright install chromium
```

### 2.2 写双开截图脚本（临时脚本，评审后清理或归档进产物）

```ts
// shots/fidelity-shots.ts
import { chromium } from 'playwright';

const DESIGN = 'http://localhost:8088/orders.html'; // 设计稿页（通道 A 本地静态服务 / file://）
const IMPL   = 'http://localhost:5173/orders';       // 实现页
const OUT    = 'screenshots';

async function shot(url: string, path: string) {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto(url, { waitUntil: 'networkidle' });
  await p.waitForTimeout(400);
  await p.screenshot({ path, fullPage: true });
  await b.close();
}

(async () => {
  await shot(DESIGN, `${OUT}/orders.design.png`);
  await shot(IMPL,   `${OUT}/orders.impl.png`);
})();
```

### 2.3 并排比对

- 两图**同尺寸（同视口宽度）并排**查看（IDE 内并排 / 图像工具左右对照）；
- 逐项对照 `visual-checklist.md`：布局/间距/颜色/字号/层级——直接目视差异；
- 局部差异用截取放大（元素级 `element.screenshot()`）存证；
- 通道 A 且设计稿 HTML 与实现页同源组件栈时，可叠加半透明（opacity）观察对齐偏差（可选技巧）。

### 2.4 交互/长文案脚本补充

```ts
// 点击验证：示例
await p.click('text=提交');            // 看是否有反应（跳转/loading/校验）
await p.hover('a[href*="detail"]');   // hover 态截图
await p.locator('tbody tr').first().click();
```

```ts
// 超长文案注入：把目标文本位替换为长文案后截图
await p.locator('h2').fill? 不适用 —— 用 page.evaluate 改 DOM 文本:
await p.evaluate(([sel]) => {
  document.querySelectorAll(sel).forEach(el => {
    el.textContent = '这是一个用于测试极端超长中文文案是否会撑破当前容器布局的说明性长句子……';
  });
}, ['h2.card-title, td.name, .btn']);
await p.screenshot({ path: 'screenshots/orders.longtext.png' });
```

---

## 三、browser-use / 其它浏览器工具（降级链路）

- Playwright 不可用时，用 browser-use（或 agent-browser 等）打开实现页与设计稿页，截图并人工目测比对；
- 能力差异：可能无法执行精确的 DOM 注入长文案 → 超长文案专项改为「页面内已有真实长数据页优先走查 + 提示用户如需要极端用例提供可构造数据的入口」；
- 交互点击：能用 AI 点击就逐一点，至少验证主要按钮/链接。

---

## 四、视口与设备

- 默认按用户确认的视口（通常 1440×900 桌面 + 375×812 移动各一轮）；
- 有 browser-use / agent-browser 时可在移动视口模拟截图；
- 同一页在不同视口都记录截图，比对时同视口对照（防「桌面一致、窄屏崩」漏检）。

---

## 五、截图命名与归档

- 命名规则：`<页面名>_<问题简述>_<序号>.png`，如 `orders_按钮色值不符_01.png`、`orders_表格长文案溢出_02.png`；
- 归档：`.spec/页面还原评审/screenshots/`（独立模式）或 Testing 场景随轻量清单交付；
- 报告内引用：`![orders 长文案溢出](screenshots/orders_表格长文案溢出_02.png)`。

---

## 六、常见错误对照

| 错误 | 纠正 |
|---|---|
| 全无浏览器工具仍硬跑并称「已走查」 | 铁律五：预检报错等安装，禁止静默降级 |
| 设计稿与实现页视口不同就并排比对 | 同视口截图再比对 |
| 只截整页不截局部 | 关键差异截元素级局部放大 |
| 超长文案靠人工改不了 DOM | Playwright evaluate 注入；无此能力则用真实长数据页 + 向用户说明 |
| 截图乱命名无归档 | 按 §五 命名入 screenshots/ |
