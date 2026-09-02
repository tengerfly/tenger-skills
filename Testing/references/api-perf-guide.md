# 接口性能测试指南（API Performance Guide）

> 权威细则：如何识别并记录「慢接口」——监听方式、耗时计算、阈值分类、证据留存。

---

## 一、慢接口阈值（默认，【设计假设】可调）

| 等级 | 阈值 | 含义 | 计入问题级别 |
|---|---|---|---|
| 慢 | `> 1000ms` | 明显可感知卡顿 | P2 |
| 很慢 | `> 3000ms` | 严重影响体验 | P1 |
| 严重 | `> 5000ms` | 接近超时、可能引发超时报错 | P1/P0（视是否导致功能失败） |

> 阈值在测试计划的「测试元信息」中登记，用户可自定义覆盖默认值。

## 二、监听方式（优先级 Playwright → 其他）

### 2.1 Playwright `page.on('response')`（推荐）

```ts
import { chromium } from 'playwright';

const slowApis: Array<{ url: string; method: string; duration: number }> = [];

const browser = await chromium.launch();
const page = await browser.newPage();

page.on('response', async (response) => {
  const url = response.url();
  // 只统计业务接口，排除静态资源
  if (!/\.(js|css|png|jpg|svg|woff2?|ico)$/.test(url)) {
    const timing = response.timing();
    // duration = 响应结束 - 请求开始（ms）
    const duration = timing ? timing.responseEnd - timing.startTime : -1;
    slowApis.push({ url, method: response.request().method(), duration });
  }
});

await page.goto('http://localhost:3000');
// ... 走完需要测的流程
```

### 2.2 `performance.getEntriesByType('resource')`（通用）

```ts
const entries = await page.evaluate(() =>
  performance
    .getEntriesByType('resource')
    .filter((e) => e.initiatorType === 'fetch' || e.initiatorType === 'xmlhttprequest')
    .map((e) => ({ name: e.name, duration: Math.round(e.duration) })),
);
```

### 2.3 midscenejs YAML 脚本内取耗时（可选）

```yaml
web:
  url: http://localhost:3000
tasks:
  - name: 收集接口耗时
    flow:
      - javascript: |
          JSON.stringify(
            performance.getEntriesByType('resource')
              .filter(e => e.initiatorType === 'fetch' || e.initiatorType === 'xmlhttprequest')
              .map(e => ({ name: e.name, duration: Math.round(e.duration) }))
          )
        name: api_timing
```

## 三、接口清单来源

- 后端 TDD（`.spec/TDD/VN/`）的「接口清单」；
- 前端 `src/api/` 目录的 fetch 方法（路径 + 方法）；
- 跑测时实际抓到的请求（覆盖清单之外的真实调用）。

## 四、执行与记录

1. **每个接口至少触发一次**：通过走页面流程或直接调用触发；
2. **多次采样**：关键接口刷新/重复触发 3 次，记录「平均耗时 + 最大耗时」（避免单次抖动误判）；
3. **逐条记录**到 `接口性能清单.md`：

| 接口路径 | 方法 | 触发场景 | 平均耗时 | 最大耗时 | 等级 | 证据 |
|---|---|---|---|---|---|---|
| `/api/orders` | GET | 订单列表加载 | 2300ms | 3100ms | 很慢 | `截图/耗时数据` |

4. **慢接口进问题文档**：按等级计入 P1/P2，附触发场景与证据。

## 五、注意事项

- **排除静态资源**：只统计业务接口（fetch/xhr），不统计 js/css/图片等静态资源加载；
- **区分「慢」与「错」**：接口报错（4xx/5xx）是功能/异常问题，走功能测试记录；接口慢（成功但超阈值）走本清单记录；两者不混；
- **标注环境**：本地 dev server 的接口耗时可能与生产有差异（无反向代理/缓存），结论中注明「本地环境实测，生产需复测」。
