# 同类调试 Skill 结构样本（Agent Skill Samples）

> 用途：优化本 Skill 结构时的借鉴范本（只借鉴组织方式，不搬运内容）。

---

## 一、franzenzenhofer/debug-mode-skill（最完整范本）

- **9 阶段闭环**：Safety → Discover → Hypothesize → Reproduce → Instrument → Analyze → Reset → Fix → Verify。
- **Commit-Then-Instrument** + `git restore .` 干净清理（已融入 log-locating.md）。
- Hypothesis-tagged logs plus red/green verification: a failing assertion is evidence of a failing check; a passing assertion is evidence only for that check.
- 复现策略优先级：独立脚本 → 失败单测 → curl/HTTP → 循环 50 次（竞态）→ 手动。

## 二、doraemonkeys/claude-code-debug-mode（假设驱动范本）

- Bug Report → Hypotheses → Instrument（#region DEBUG 块）→ Reproduce（日志落 .claude/debug.log）→ Analyze → Fix → Verify → Clean Up。

## 三、ferrucc-io/clog（结构化 trace 范本）

- `/reproduce` skill + 本地日志服务器（NDJSON，端口 2999）；`_clog()` 临时插桩 POST 结构化 JSON，语言无关。

## 四、awesome-skills/5-whys-skill（中文触发词范本）

- 触发词含「找根因/排查问题/问题出在哪/深挖原因」；Why Chain 表 + Countermeasures 表。

## 五、oimiragieo/agent-studio debug-log-analysis（取证纪律范本）

- 铁律：先复制副本 → 降噪 → 分类错误 → 交叉引用（前后 ≥10 行）→ 结构化报告；绝不原地操作原始文件。

## 六、skillmd/debug-systematic（4 阶段范本）

- REPRODUCE/ISOLATE/DIAGNOSE/FIX&VERIFY + git bisect + 常见根因表。

> 出处：github.com/franzenzenhofer/debug-mode-skill、awesome-skills/5-whys-skill、github.com/ferrucc-io/clog。
