# 测试决策规则与选型（Testing Decision Rules）

> 用途：写测试计划/选测试框架时的「测什么、先测哪层、用哪个框架、专项何时上」决策库。与 `test-case-guide.md` 分工：case-guide 管「用例怎么写」，本文件管「策略怎么定、框架怎么选」。
> 写法范式（借鉴 peterhdd/qaskills）：`When + 场景 → 动作 + 量化阈值 + 理由`。本 Skill 的铁律（全状态/全点击/三态/慢接口阈值）优先级高于本文件，冲突以 SKILL.md 铁律为准。

---

## 一、测试金字塔（先测哪层、每层占比）

| 层级 | 占比 | 测什么 | 工具 |
|---|---|---|---|
| 单元 Unit | ~70% | 函数/hook/纯逻辑，mock 依赖 | Vitest/Jest/pytest/JUnit |
| 集成 Integration | ~20% | 多组件协作、真实 DB 事务 | Testing Library/Supertest/真实库 |
| E2E | ~10% | 关键用户链路 | Playwright/Cypress |

> ⛔ 反「冰淇淋反模式」：E2E 最多、单元最少 = 慢且脆。先写单元，E2E 只覆盖关键链路。本 Skill 的「全状态/全点击」是验收视角的 E2E 覆盖，不改变金字塔占比原则。

## 二、框架选型（When…use…）

| 场景 | 动作 | 理由 |
|---|---|---|
| 前端 JS/TS 单测 | Vitest（Vite 项目）/ Jest（老项目） | Vitest 快、原生 ESM |
| 后端 Node 单测 | Jest + Supertest（接口） | 与 NestJS 生态贴合 |
| Python | pytest + httpx | 生态最广 |
| Java | JUnit 5 + REST Assured | 企业标准 |
| Go | 内置 testing + testify | 无第三方负担 |
| E2E 跨浏览器 | Playwright（默认，auto-wait、CLI 省 token） | Cypress 组件测试友好 |
| 移动端 | Appium | 跨平台 |

## 三、专项测试触发（按需求关键词开关）

| 需求信号 | 专项 | 工具 |
|---|---|---|
| 高并发/大流量/性能要求 | 性能测试 | k6（JS 脚本）/JMeter（协议广）/Locust（Python） |
| 敏感数据/对外接口/合规 | 安全测试 | OWASP ZAP（DAST）/Semgrep（SAST） |
| 前后端接口对接 | 契约测试 | Pact（消费者驱动 CDC） |
| 视觉还原要求 | 可视化回归 | Percy/Chromatic（像素）/Axe-core（无障碍） |
| 涉 AI 生成功能 | AI 测试 | promptfoo（LLM 输出评估/回归） |

> 契约测试与可视化回归本 Skill 默认不主动展开，命中对应需求信号才启用；AI 测试是 2026 新坑，涉 AI 项目建议预留。

## 四、写代码时是否补测试（与 backend-dev / frontend-dev 的路由）

- 开发类 skill 产出的每个功能点自带单测（它们测试先行）；本 Skill 不重复写单测。
- 本 Skill 的边界：**可运行项目的验收/E2E/回归/样式/性能**；单元/集成测试归开发自测，本 Skill 只在「开发未测、需补」时按金字塔补关键层，并在计划中说明原因。
- 慢接口阈值：>1000ms 慢 / >3000ms 很慢 / >5000ms 严重（SKILL.md 铁律，可调）。

## 五、覆盖率与门禁

| 项 | 阈值 |
|---|---|
| 单测行覆盖 | ≥80%（团队标准可调） |
| 覆盖率趋势 | 只能升不能降（coverage-as-ratchet） |
| CI 门禁 | typecheck + lint + 单测 + build + e2e 全绿才合入 |

> 覆盖率是下限不是目标；「像用户一样测试」（Testing Library），不测实现细节。
