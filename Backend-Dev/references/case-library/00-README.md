# 后端开发案例库（Case Library）索引

> 定位：写后端代码时**按需加载**的落地参考。与 Backend-Tech-Design 的 case-library 分工：那份管「架构/设计/选型」，本份管「编码落地/代码模式/规范」。
> 来源：khalidbelk/awesome-backend、futurice/backend-best-practices、skillmd backend-developer、中文大厂实战。已精编浓缩。

## 一、目录

| 文件 | 内容 | 何时读 |
|---|---|---|
| `language-patterns.md` | Go/Java/Node 代码规范（目录结构+代码模式） | 写具体语言代码时 |
| `api-security.md` | API 设计 + 鉴权决策树 + 安全编码 | 写接口/鉴权/安全时 |
| `quality-engineering.md` | 测试/日志/CI-CD/可观测 | 搭工程质量时 |
| `agent-skill-samples.md` | 同类后端开发 Skill 结构样本 | 优化本 Skill 结构时 |

## 二、统一案例字段

> 场景 → 技术栈 → 问题 → 解法/关键代码 → 出处 → 适用边界。

## 三、使用原则

1. **编码规范回溯到 TDD**：TDD 选型/契约优先，case-library 只补 TDD 未覆盖的通用写法。
2. **不越层**：四层架构铁律优先，案例代码只借鉴模式，不破坏分层。
3. **借鉴不照搬**：语言/ORM 案例按实际选型等价映射。
