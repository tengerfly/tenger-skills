# archive/ —— v4 冻结区（只读）

> 这里只读保留旧体系（v3）的全部历史资产。**不维护、不安装、不校验、不进 issue 池。**
> 需要复用旧内容时，只读复制到 `skills/` 或 `shared/` 的新文件里，不要直接改这里。

## 为什么保留

- 回滚：v4 走不通时可以整体退回 v3（见下）。
- 取证：旧交付、评审报告、问题卡是真实缺陷模式的来源，评审判据从这里提炼。
- 对照：P4 要拿 v4 与旧体系同题对比。

## 结构

| 路径 | 内容 | 来源 |
|---|---|---|
| `frozen-skills/` | 45 个旧 Skill 全文（原封不动） | 旧 `DEV/ PRD/ UI/ Other/ Test/ Skill/ workflow/` |
| `frozen-skills/README-*.md` | 原各分类目录的 README（`README-DEV.md` 等） | 同上 |
| `issue-v3/` | 旧问题卡 65 张 + 旧 issue README | 旧 `issue/` |
| `docs-v3/` | 旧计划/研究/手册/说明/聊天记录 + 旧根 README 快照 | 旧 `docs/ chats/ README.md` |
| `system-v3/governance/` | 旧 9 张注册表与 schema | 旧 `governance/` |
| `system-v3/evals/` | 旧 12 套 eval 与基线 | 旧 `evals/` |
| `system-v3/evolution/` | 旧 skill-evolver 偏好库与进化台账 | 旧 `evolution/` |
| `system-v3/self-boot-spec/` | 自举 `.spec/`（Gate、证据、评审、obs） | 旧 `.spec/` |
| `system-v3/scripts-v3/` | 旧校验/测试/评测脚本与 551 项测试 | 旧 `scripts/`（新 `scripts/` 只留 validate_lite + installer） |
| `system-v3/shared-v3/` | 旧 shared 契约与模板 42 份 | 旧 `shared/` |
| `system-v3/testing-legacy/` | 旧 Testing 归档目录 | 旧 `Test/Testing/` |
| `system-v3/skill-knowledge/` | 外部知识库引用层 | 旧 `skill-knowledge/` |
| `system-v3/*.ps1, pyproject.toml, requirements.txt, github-v3-validate.yml` | 旧工具链配置与 CI | 旧根目录 / `.github/` |
| `learning/` | 学习资料（vibe coding HTML 等，本地保留不入库） | 旧 `vibe Coding 高效能秘籍/` |

## 回滚方式

- 回滚快照：tag `pre-converge-20261020`；旧分支 `refactor/skill-system-v3 @ 4b0e04c`。
- 整仓回到 v3：`git checkout pre-converge-20261020`（或从该 tag 新建分支），旧目录原样还在。
- 只要旧资产：从本目录复制，不需要回滚分支。
- v4 不删 archive 内容；若 v4 确认长期可用，再单独决策是否把 archive 移出仓库（本分支不动）。

## 规则

1. **只读**：不改这里任何文件；需要改的是 `skills/` 与 `shared/` 的新版本。
2. **不装**：installer 只发现 `skills/`（`archive/` 在排除名单里），archive 内容不会进宿主。
3. **不校验**：`validate_lite` 不扫描这里。
4. **可取证**：评审要提炼缺陷模式时，从 `frozen-skills/*/references/`、`issue-v3/`、`system-v3/self-boot-spec/` 只读取证。
