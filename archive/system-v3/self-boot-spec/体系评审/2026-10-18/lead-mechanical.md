# 评审 · Lead 机械面报告（2026-10-18）

> 范围：全仓机械核对（不替代 A/B/C/D 四组的七维内容审计）。所有发现均可复核。

## 一、通过项（机械证据）

| 检查 | 结果 | 证据 |
|---|---|---|
| skill-contract 契约章节 | PASS | `python scripts/validate_core.py skill-contract --project-root .` → passed（Phase 0 后复跑） |
| registry ↔ 目录 ↔ frontmatter name | 45/45 一致；registry 46 项 = 45 skill + 1 外部引用层 skill-knowledge（无 SKILL.md，路径 `${SKILLS_KNOWLEDGE_ROOT}`） | 本轮脚本核对 |
| legacyAliases 唯一性 | 无冲突（testing/Testing 同一 skill 的大小写别名属同一项） | 本轮脚本核对 |
| 跨 skill / shared 引用双视图可达 | PASS（checked=539，三类违规 0） | `check-installed-refs.py` |
| SKILL 内相对链接可达 | 0 死链 | 本轮脚本逐文件解析 markdown 相对链接 |
| 编码损坏（U+FFFD / ? 连片 / BOM / 控制字符） | 仅 `skill-knowledge/README.md` 一处（已修） | 本轮全仓 tracked 文本扫描 |
| 本机 4 宿主安装副本 | drift=0 | `install-skills.py --check` 四目标 |
| eval 基线 | 12 套重锚，同锚无回退 | `baseline.py save` + `diff` |
| L2 回流 | 闭环 issue 全部有回流用例且逐条分诊 | `relay.py` |

## 二、发现（P1/P2，待修）

### F-M1（P1）「Testing 仍作备用入口」的旧口径散落 4 处，与「Testing 已归档、唯一入口 auto-test」冲突

统一口径（README.md:17、Test/README.md、workflow/SKILL.md:99）：Testing 已归档、旧请求重定向 auto-test、不启动历史备用流程。但仍残留：
- `Test/auto-test/README.md:7`：「Testing 保留为链外备用，源码不动」
- `Test/auto-test/CONTEXT.md:17`：「Testing 源码保留为链外人工走查备用」
- `shared/baseline-terms.md:38`：「auto-test / Testing / Fidelity-Review…」
- `shared/browser-policy.md:34`：「auto-test / Testing 样式视觉断言」
- `shared/evidence-before-claims.md:3`：「auto-test / Testing」
- `workflow/references/legacy-pipeline.md:11,196`：Testing 标「备用」（legacy 参考文件，建议加「已归档，仅历史」注）
判据：读者/模型看到「备用入口」会启动第二套测试流程，违反唯一入口与已归档事实。修法：上述活跃文件删除 Testing 或改为「已归档（重定向 auto-test）」；legacy 文件加历史注。

### F-M2（P2）README 与说明书里的历史校验数字过期

- `README.md:8`：「2026-09-22 核对：…60 项测试：59 通过、1 跳过…」——已远落后于当前（500+ 项）
- `docs/当前项目介绍与目标对齐说明书.md:296`：「2026-09-21 …36 个测试通过」
判据：同一事实两个来源且与当前实测不符；易被误当现状。修法：改为本轮实测口径或注明「历史核对」，并以最新 validation 报告为权威。

### F-M3（P2）5 个 legacy-adapter skill 未走 v2 必备章节，风格与其余 40 个入口不一致

- `DEV/tech-review`、`Other/essence-distill`、`Other/fact-check`、`Other/source-reading`、`UI/fidelity-review` 的 frontmatter 缺 `metadata.contract-level`，正文是旧式 `一、…七、运行问题埋点` 结构，无 Purpose/Trigger/…/State Changes 章节。
- registry 已把它们登记为 `legacy-adapter`（`shared/legacy-skill-adapter.md` 定义），校验器放行——属「契约允许但风格不一致」。
判据：契约允许 ≠ 一致；跨 skill 引用/宿主展示会出现两种结构。修法（不阻塞）：评估是否统一为 v2 入口（工作量大，需单独排期）或至少在 registry/README 注明 legacy-adapter 例外。

### F-M4（P2）历史记录中的机器绝对路径（不阻塞、本轮不清理）

`issue/`、`.spec/` 历史证据、`Test/Testing/ARCHIVED.md`、`workflow/references/legacy-pipeline.md`、`evolution/进化台账.md` 等仍含 `D:/project/...`、`C:/Users/15136/...`。这些是当时事实/历史资料，按「历史只读」策略保留；活跃执行路径已清零（见 issue 02）。

### F-M5（P2）auto-test 的 contractLevel 仍是 legacy-wrapper（用户敏感点）

- `Test/auto-test/SKILL.md` frontmatter `contract-level: legacy-wrapper`、正文含 `LEGACY BODY BOUNDARY`。这是 12 个包装 skill 的统一机制，非能力降级；但用户刚因 legacy 命名投诉过，建议在 README/CONTEXT 显式解释「legacy-wrapper = 兼容包装机制，不是能力状态」，或评估把 auto-test 升为 v2（需单独评审）。

## 三、未覆盖 / 待补

- 内容级审计由 A/B/C/D 四组进行中；本报告只覆盖机械可判项。
- 行为层 eval 本轮未跑（付费引擎，需授权）；结构层已全量。

## 四、建议修复顺序

1. F-M1（P1，改动小、影响唯一入口口径）→ P2 阶段批量修。
2. F-M2（实测数字更新，和最终 validation 报告一起改）。
3. F-M3/F-M4/F-M5 记入报告与 issue，不阻塞本轮。