# 体系收敛计划 v4：AI Coding 闭环

> 状态：**计划稿（待你确认后执行）** ｜ 日期：2026-10-20 ｜ 新分支：`converge/ai-coding-loop`（从 `refactor/skill-system-v3` @ `4b0e04c` 切出） ｜ 回滚快照：tag `pre-converge-20261020`
> 一句话：把体系从「自我治理平台」收回成「帮你写代码 + 记录问题 + 反哺 Skill」的三步小闭环。

## 0. 一页结论

| 项 | 内容 |
|---|---|
| 目标 | 一套能让 AI 帮你写代码的开发体系：开发中遇到问题 → 记录 → 反哺 Skill → 下次更好用 |
| 现状 | 45 个 Skill、9 张注册表、68 状态/126 转移、12 套 eval、551 测试（25 分钟）、65 条 issue；体系自身行数是 Skill 正文的 10 倍 |
| 做法 | 冻结治理层；保留 **9 个核心 Skill + 3 份共享规则 + 问题池 + 一张 loop-log**；用 2 个真实任务验证，再决定是否恢复其他能力 |
| 验收 | ① 核心环独立完成一次真实编码交付；② 问题卡 → Skill 改动 → 下次验证 的闭环跑通；③ 月度能算出复发率与反哺有效率 |
| 暂不做 | v3 重构、继续加规则/评测、全量清 65 条 issue、自举 Gate 验收循环 |

## 1. 本心复述与偏移诊断

**你的本心（三句话）**：
1. 创建一套开发体系，帮助我 AI Coding；
2. 开发中遇到的问题要记录（项目问题 + 体系问题）；
3. 用这些记录反哺优化 Skill，让体系越用越好用。

**偏移在哪里（数据）**：
- 45 个 `SKILL.md` 共 6,049 行；治理/验证/证据/台账等体系自身材料 61,383 行（10 倍）；
- 近 40 次提交：29 次只动体系自身，14 次是超过 10 个文件的整层改动；
- 自举 Gate 自 2026-09-21 起 `BLOCKED` 已 29 天；最近两天在「验收体系」，没有真实交付；
- 真实编码交付只发生在 2026-10-18 的 R41–R43 试跑（且那次是体系在驱动项目，不是体系在帮你）。

**为什么会偏**：每遇到一个问题就加一层机制；只进不出、没有冻结；用测试数/eval 数/Gate 状态代替了「交付有没有更快更省事」；你的位置被推到流程末端只为签字。

## 2. v4 目标态结构

```text
tenger-skills/
├── README.md              # 一页：这套东西是什么、怎么用（≤150 行）
├── WORKFLOW.md            # 一条主链 + 何时停（≤100 行）
├── skills/                # 核心 9 个 Skill（默认只装这些）
├── shared/                # 3 份共享规则（写法 / 问题记录与反哺 / 最小质量底线）
├── issue/                 # 问题池（轻量卡：现象/证据/归属/建议/状态）
├── bug-patterns/          # 真实 Bug 模式（保留）
├── loop-log.md            # 每个真实任务一行复盘（时长/返工/介入/问题/反哺）
├── scripts/               # validate_lite.py（≤5 秒）+ install-skills.py（core profile）
└── archive/               # 冻结区（只读）：原 governance/evals/自举 .spec/元 Skill/旧 docs
```

**五条原则**：
1. 只保留一次真实编码交付必须的东西；用不到 → 冻结。
2. 记录要轻（30 秒一张卡），反哺要小（每次≤3 处、每处≤10 行）。
3. 每个机制必须能被真实任务使用并验证；不能被验证的机制不进核心。
4. 冻结优于保留，删除优于冻结；archive 只读 + tag 快照，随时可回滚。
5. 门禁只防「假完成」，不追求「证明体系正确」。

## 3. 45 个 Skill 的处置：9 核心 + 6 按需 + 30 冻结

### 3.1 核心 9（默认安装，必须互相衔接）

| # | 核心 Skill | 由哪些现有 Skill 合并/精简 | 干什么 |
|---|---|---|---|
| 1 | `workflow` | workflow（精简到 ≤120 行） | 入口：判断任务大小、选路径、何时停 |
| 2 | `onboarding` | project-onboarding（精简） | 接管已有项目：跑法/结构/测试/基线 |
| 3 | `requirements` | idea-intake + product-discovery + product-definition + feature-decision + prd-design + prd-review | 需求澄清、范围、轻量 PRD/验收标准、自检 |
| 4 | `tech-design` | backend-tech-design + frontend-tech-design + tech-review | 技术方案（含前后端契约核对） |
| 5 | `backend-dev` | backend-dev（精简） | 后端实现 + 自测 |
| 6 | `frontend-dev` | frontend-dev（精简） | 前端实现 + 还原/自测 |
| 7 | `auto-test` | auto-test（精简为 L0-L2） | 测试唯一入口 |
| 8 | `code-review` | code-review + tech-review 的评审部分 | 方案/代码/交付评审（只审不改） |
| 9 | `bug-fix` | bug-fix（精简） | 问题定位与修复闭环 |

### 3.2 按需 6（默认不装，需要时 `--profile on-demand` 装）

`ui-design`（原型+UI+还原度合并）、`release`（发布计划+部署+验证合并）、`incident`、`refactor`、`oss-radar`、`fact-check`。

### 3.3 冻结 30

其余全部（产品研究/竞品/蓝图/原型评审/UI 评审/旧技术评审/信号采集/分诊/运行/发布旧版/质量巡检/optimizer/evolver/lifecycle/source-reading/essence-distill/competitive-analysis/product-analytics/post-release-review 等）。
处理：移入 `archive/frozen-skills/`，**不删除**、不再维护、不参与安装与校验。

## 4. 问题记录与反哺环（本计划的核心）

### 4.1 记录（30 秒一张卡）

文件：`issue/NNN-<slug>.md`；字段：

```yaml
id: ISSUE-20261020-001
type: skill | project | env | process
skill: frontend-dev          # 归属
severity: P0 | P1 | P2
status: open | fixed | verified | closed
openedAt: 2026-10-20
```

正文四段：现象（1-2 句）／证据（文件:行 / 命令输出 / 截图路径）／影响（卡了多久、返工几次）／建议改动（改哪个 Skill 的哪一条，没有就写「未知」）。

### 4.2 路由

- `project` → 当场修项目（不进 Skill 池）；
- `skill` → 进反哺队列；
- `env` → 记录环境/工具问题，攒够 2 次再处理；
- `process` → 只在「卡了 >30 分钟」时记，避免琐事淹没。

### 4.3 反哺触发与上限（防止再膨胀）

1. **触发**：同一问题第 2 次出现，或单次阻塞 >30 分钟 → 必须改 Skill；
2. **窗口**：每 2 周一次「Skill 批改窗口」，每次 ≤3 处、每处 ≤10 行；
3. **验证**：改完在卡上记 `verifiedBy: <下一次真实任务>`；**4 周内没有验证 → 回滚该改动**；
4. **范围**：只改 `skills/` 与 `shared/` 三份规则，不改 archive。

### 4.4 闭环状态

`open → fixed（Skill 已改 + commit）→ verified（下次任务确认不再犯）→ closed`；无法验证的保持 `open`，不假装闭环。

### 4.5 度量（每月看 2 个数）

- **复发率** = 同类问题再次出现的次数 / 已修复问题数；
- **反哺有效率** = 修复后下一任务中该类问题减少的条数 / 已修复问题数；
- 每任务一行 `loop-log.md`：日期｜任务｜时长｜返工次数｜你介入次数｜新增问题数｜修复数｜复发数｜Skill 改动数。

## 5. 阶段计划（D0 = 2026-10-20）

| 阶段 | 时间 | 任务 | 产出 | 验收标准 |
|---|---|---|---|---|
| **P0 准备** | D0（今天） | 当前分支确认干净并推送（`4b0e04c`）；打 tag `pre-converge-20261020`；切新分支；提交本计划 | 新分支 + 本计划 | 分支存在、工作区干净、计划入库 |
| **P1 冻结瘦身** | D1–D2（10-21～22） | ① 建 `archive/` 并迁入治理/评测/自举记录/元 Skill/非核心 Skill；② 写核心 9 个 Skill；③ 写 shared 3 份；④ README + WORKFLOW；⑤ `validate_lite.py` + installer core profile | 可安装的 v4 骨架 | ① 根目录 ≤10 项；② `install --target <temp>` 只装 9+3；③ `validate_lite` ≤5 秒通过；④ 冒烟：装进临时目录能读懂入口 |
| **P2 闭环跑通** | D3–D4（10-23～24） | ① issue 模板 + loop-log；② 反哺规则写进 `shared/issue-loop.md` 与 `workflow` 引用；③ 用 1 个历史小任务回放一遍 | 闭环样本 | 真实任务走完一次；产出 2–5 张问题卡；至少 1 条走完 fixed→verified |
| **P3 真实试点** | W1–W2（10-27～11-06） | 用核心 9 做 2 个你指定的真实小任务；记录 loop-log；执行 1 次批改窗口 | 2 份任务记录 | 交付成功；3 个指标有数：交付时长/返工次数/你介入次数 |
| **P4 对比决策** | W3–W4（11-09～11-20） | 与 v3 体系在同题上的表现对比；决定保留/补回/回滚 | 一页决策记录 | 决策明确：哪些按需能力装回、哪些继续冻结 |

## 6. 门禁与测试策略（从 25 分钟降到 5 秒）

`scripts/validate_lite.py` 只查 5 件事：
1. `skills/*/SKILL.md` frontmatter 与必需小节齐全；
2. `skills/` 与 `shared/` 的引用路径可达；
3. `issue/` 卡必填字段与状态枚举合法；
4. `loop-log.md` 表头字段完整；
5. `install-skills.py --dry-run` 能列出 core profile 清单。

**不再作为日常门禁**：551 项全量测试、12 套 eval、goal-plan 机读执法、自举 Gate、四宿主漂移核对——全部随旧结构进入 `archive/`，需要时手动跑。
CI（`.github/workflows`）改为只跑 `validate_lite` + installer 冒烟。

## 7. 风险与回滚

| 风险 | 应对 |
|---|---|
| 核心 9 能力不足（UI/发布/事故场景） | 按需 6 随时装回；不重建治理层 |
| 精简改坏真实可用性 | 原分支 `refactor/skill-system-v3` 与 tag `pre-converge-20261020` 原样保留，随时回滚 |
| 反哺再次膨胀 | 触发条件 + 每 2 周≤3 处 + 4 周未验证回滚 |
| 现有宿主安装副本（.dsh/.qoder-cn 等） | 新分支只写独立安装目标；旧副本不动，避免互相污染 |
| 远端默认分支仍是旧的 `codex/skills-condense` | 不改默认分支（需你在 GitHub 设置）；新分支单独推送 |

## 8. 交付物与 Done 定义

**交付物**：① 本计划；② v4 目录与归档；③ 核心 9 Skill；④ shared 3 份；⑤ validate_lite + installer core profile；⑥ issue 模板 + loop-log + 反哺规则；⑦ 2 个真实任务记录；⑧ 一页决策记录。

**v4「可用」定义（Done）**：一个新会话只安装 core profile，拿到一句真实需求，能独立走完 需求→方案→开发→测试→评审→交付，全程不碰旧治理文件；同时产生问题卡并在下一次任务验证至少 1 条反哺。

## 9. 待你确认的 5 个决策（已给默认值）

| # | 决策 | 默认 |
|---|---|---|
| 1 | 核心 9 名单是否按 §3.1 | 按默认 |
| 2 | UI 设计 / 发布 / 事故是否放按需 | 按需（默认不装） |
| 3 | 反哺批改窗口频率与上限 | 每 2 周、每次≤3 处 |
| 4 | 首批 2 个真实试点任务 | 由你指定（建议：最近想做但没做的两个小功能） |
| 5 | 历史资产处理 | archive 只读保留（可回滚），不删除 |

确认方式：回复「按默认执行」，或指出要改的条目。确认后我从 P1 开始执行。