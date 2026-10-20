# 测试方法学（Testing Methods）

> 用途：定测试策略时的理论弹药。金字塔见 `decision-rules.md` §一。

---

## 一、测试金字塔（Unit 70 / Integration 20 / E2E 10）

- 反「冰淇淋反模式」：E2E 最多、单元最少 = 慢、脆、难定位。
- 单元：函数/hook/纯逻辑，mock 依赖；集成：多组件+真实 DB；E2E：关键链路。

## 二、TDD（Red-Green-Refactor）

- 先写失败测试（红）→ 最小实现跑绿 → 重构。与本 Skill 的「验收闭环」同源：先定验收标准，再验证。
- 适用：开发类 skill 已测试先行；本 Skill 用于「补测」时按此循环。

## 三、BDD（Given-When-Then）

- Cucumber/SpecFlow/behave；业务可读验收标准。与 PRD 的 Gherkin AC 同构，可直接承接。

## 四、测试四象限（Marick）

| 象限 | 导向 | 目的 |
|---|---|---|
| Q1 技术导向·支持团队 | 单元测试 | 指导开发 |
| Q2 业务导向·支持团队 | 验收/场景测试 | 支撑产品 |
| Q3 业务导向·评价产品 | 探索/可用性测试 | 批判产品 |
| Q4 技术导向·评价产品 | 性能/安全/负载 | 批判技术 |

> 判断「该不该测」：先定位象限，再定方法。

## 五、风险驱动测试

- 影响面 × 失败概率排序，先测高风险模块；与 SKILL.md 的 P0/P1/P2 分级同源。

## 六、Page Object 模式（E2E 可维护性骨架）

```
pages/LoginPage.ts 封装元素定位与操作；测试只调 page.login()，不散落 selector
```

## 七、测试数据管理

- 工厂函数 + Faker 造数据；避免共享可变状态；落库后单测/集成可复用。
- 不硬编码测试数据，保证可重复执行。

> 出处：TheJambo/awesome-testing、TesterHome《测试质量进阶》。
