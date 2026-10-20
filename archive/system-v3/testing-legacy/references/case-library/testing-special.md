# 专项测试（Special Testing）

> 用途：命中专项需求信号时的工具与要点。触发条件见 `decision-rules.md` §三。

---

## 一、性能与负载

| 工具 | 特点 |
|---|---|
| k6 | JS 脚本、云原生（默认推荐） |
| JMeter | 协议广、GUI/CLI |
| Gatling | Scala DSL、高并发 |
| Locust | Python 写压测 |

要点：压测基线 → 测 → 记录 P95/P99 → 与方案阈值比对。

## 二、安全测试

| 工具 | 用途 |
|---|---|
| OWASP ZAP | DAST 漏扫 |
| Semgrep/CodeQL | SAST 静态分析 |
| Nuclei | 模板化漏洞探测 |
| Burp Suite | 渗透测试 |

## 三、契约测试

- Pact：消费者驱动契约（CDC），前后端接口一致性。

## 四、可视化回归

| 工具 | 用途 |
|---|---|
| Percy/Chromatic | 像素级视觉对比 |
| Axe-core | 无障碍自动化（WCAG） |

## 五、AI / LLM 测试（2026 新坑，涉 AI 项目预留）

- promptfoo：Prompt/LLM 输出评估、回归；
- ai-test-generation / ai-bug-triage：LLM 生成与分类测试；
- 要点：AI 输出评估需「输入数据覆盖 + 失败表达 + 降级人工介入」维度（对齐 PRD 涉 AI 五维业务要求）。

> 出处：k6.io、zaproxy.org、pact.io、percy.io、promptfoo.dev。
