# tenger-skills

> 一套帮你 AI Coding 的 Skill 体系：开发中记录问题 → 反哺 Skill → 越用越好用。
> v4 核心判断：LLM 越强，「教它怎么写代码」越不值钱，「判断它写没写对、能不能收」越值钱。
> 所以：执行层变薄，评审验收层变厚，问题记录反哺闭环。

## 是什么

- 10 个 Skill：2 个入口（workflow / onboarding）+ 4 个薄教（requirements / tech-design / backend-dev / frontend-dev）+ 3 个厚收（auto-test / review / acceptance）+ 1 个修复（bug-fix）。
- 4 份公共契约：Skill 写法、评审、验收、问题记录与反哺（`shared/`）。
- 三个反馈资产：问题卡 `issue/`、缺陷模式库 `bug-patterns/`、每任务一行的 `loop-log.md`。
- 体系最值钱的不是「教模型写代码」，是判据、证据、独立评审和真实缺陷模式。

## 安装（2 条命令）

先 `git clone` 本仓并进入目录（Windows/macOS/Linux，Python 3.10+，仅标准库）：

```bash
python scripts/install-skills.py --profile core --target ~/.dsh/skills
python scripts/install-skills.py --check --target ~/.dsh/skills
```

第一条装 core（10 个 Skill + 4 份 shared），第二条只读核对副本是否等于源仓，不一致 exit 1。装到别处换 `--target`（如 `~/.claude/skills`）。体系本地校验：`python scripts/validate_lite.py`，exit 0 即通过。

## 用起来（3 步）

1. **说清楚**：给项目路径、目标、范围、终点；终点默认「实现并验证」，不含发布。
2. **让 [workflow](skills/workflow/SKILL.md) 带路**：它判轻量/标准/完整三档，按主链调度专业 Skill，产物落项目 `.spec/tasks/<日期>-<slug>/`。
3. **看验收再收工**：结论 ACCEPT 才算完，FIX/REJECT 不算；顺手记一张问题卡、在 loop-log 记一行。

主链与每步产物见 [WORKFLOW.md](WORKFLOW.md)。

## 核心 10 个 Skill

| # | Skill | 类型 | 一句话职责 |
|---|---|---|---|
| 1 | `workflow` | 入口 | 判档、调度、交接、收口 |
| 2 | `onboarding` | 入口 | 新/旧项目盘点与可验证基线 |
| 3 | `requirements` | 薄教 | 澄清目标/场景/可测 AC |
| 4 | `tech-design` | 薄教 | 选型、接口、数据、回滚 |
| 5 | `backend-dev` | 薄教 | 按 AC 与契约实现后端 |
| 6 | `frontend-dev` | 薄教 | 按原型/契约实现前端 |
| 7 | `auto-test` | 厚收 | L0-L2 可复现证据链 |
| 8 | `review` | 厚收 | 独立评审 + 三值结论 |
| 9 | `acceptance` | 厚收 | DoD 核对 + owner 签收 |
| 10 | `bug-fix` | 修复 | 先复现再修 + 回归 |

## 评审验收是核心资产

- 三档：轻量（小改：自检 + 快速评审）/ 标准（独立评审 + 测试证据 + 验收）/ 完整（标准全部 + owner 签收 + 回滚验证）。
- 三值结论：`ACCEPT` 放行 / `FIX` 可修后复验 / `REJECT` 阻塞。
- 独立评审：评审者不参与产出，只拿评审包（任务、被审对象、判据/AC），报告写隔离信息。
- 证据只认可复现物；模型自述、口头描述、旧截图 = 未验证。
- 判据与缺陷模式随真实缺陷升值：见 [bug-patterns/README.md](bug-patterns/README.md)。
- 细节：[shared/review-contract.md](shared/review-contract.md)、[shared/acceptance-contract.md](shared/acceptance-contract.md)。

## 问题记录反哺

- 记录：抄 [issue/000-template.md](issue/000-template.md) 记一张卡（30 秒），状态 open → fixed → verified → closed。
- 反哺触发：同一问题第 2 次，或单次卡 >30 分钟 → 改 Skill；每 2 周批改，每次 ≤3 处、每处 ≤10 行。
- 验证：下次真实任务记 `verifiedBy`；4 周未验证 → 回滚该改动。
- 规则见 [shared/issue-loop.md](shared/issue-loop.md)；每任务在 [loop-log.md](loop-log.md) 记一行复盘。

## 目录

```text
README.md  WORKFLOW.md  PLAN.md  loop-log.md
skills/        核心 10 个 Skill（workflow / onboarding / 4 薄教 / 3 厚收 / bug-fix）
shared/        4 份公共契约
issue/         问题卡（30 秒一张）
bug-patterns/  真实缺陷模式 → 评审检出清单
scripts/       validate_lite + installer core profile
archive/       冻结区（只读，v3 全量）
```

## 回滚

- 回滚快照：tag `pre-converge-20261020`；旧分支 `refactor/skill-system-v3`；旧体系只读在 [archive/](archive/README.md)。
- 整仓回滚：`git checkout pre-converge-20261020`（或从该 tag 新建分支）。
- 只要旧资产：直接从 `archive/` 复制，不必回滚分支。