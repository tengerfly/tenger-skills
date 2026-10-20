# 测试框架速查（Testing Frameworks）

> 用途：按语言/类型选测试框架。详细决策见 `decision-rules.md` §二。

---

## 一、单元测试

| 语言 | 框架 | 特点 |
|---|---|---|
| JS/TS | Vitest | Vite 原生、快、ESM |
| JS/TS | Jest | 老牌、生态广 |
| Python | pytest | fixture/参数化强 |
| Java | JUnit 5 | 企业标准 |
| Go | testing + testify | 零第三方 |
| Rust | cargo test | 内置 |

## 二、API / 集成测试

| 工具 | 适用 |
|---|---|
| Supertest | Node/Express/NestJS 接口 |
| REST Assured | Java REST |
| Postman/Newman | 接口集合 + CI |
| httpx/requests | Python 接口 |
| Pact | 消费者驱动契约 |

## 三、E2E / UI

| 工具 | 特点 |
|---|---|
| Playwright | 跨浏览器、auto-wait、CLI 省 token（默认） |
| Cypress | 组件/集成友好、时间旅行 |
| Selenium | 老牌、Java 生态 |
| Appium | 移动端 |

## 四、覆盖率与报告

- Vitest/Jest 自带；`c8`/`nyc` 统计；coverage-as-ratchet（只升不降）。
- Allure/ReportPortal 报告大盘。

> 出处：jestjs.io、vitest.dev、playwright.dev 等官方文档。
