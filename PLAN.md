# 体系收敛计划 v4：AI Coding + 评审验收环（核心是评审）

> 状态：**计划稿 v2（已吸收「体系核心是评审体系」这一判断）· P1 已完成（2026-10-20）** ｜ 日期：2026-10-20 ｜ 分支：`converge/ai-coding-loop` ｜ 回滚快照：tag `pre-converge-20261020`
> 一句话：**执行层变薄，评审验收层变厚，问题记录反哺闭环**——教模型的钱少花，判断模型做没做对的钱多花。

## 0. 一页结论

| 项 | 内容 |
|---|---|
| 目标 | 一套帮你 AI Coding 的开发体系：开发中记录问题 → 反哺 Skill → 越用越好用；**核心资产是评审与验收能力** |
| 核心判断 | LLM 越强，「教它怎么写代码」越贬值；「判断它写没写对、能不能收」越值钱。体系的护城河＝判据 + 证据 + 独立评审 + 真实缺陷模式 |
| 做法 | 执行类 Skill 压薄（每篇≤100 行，不教框架细节）；评审/验收/测试证据压厚；冻结治理层；用 2 个真实任务验证 |
| 验收 | ① 核心环独立完成真实交付；② 问题卡→Skill 改动→下次验证闭环跑通；③ 能算出：一次验收通过率、缺陷逃逸率、复发率 |
| 暂不做 | v3 重构、继续加规则/评测、全量清 65 条 issue、自举 Gate 验收循环 |

## 1. 本心复述与偏移诊断

**你的本心**：① 一套帮你 AI Coding 的开发体系；② 开发中遇到的问题记录在案；③ 用记录反哺 Skill，越用越好用；④ **体系核心是评审体系，模型越强越要加强「把控收官」。**

**偏移事实**：45 个 `SKILL.md` 共 6,049 行，体系自身治理/验证/证据材料 61,383 行（10 倍）；近 40 次提交 29 次只动体系自身；自举 Gate `BLOCKED` 29 天；真实编码交付只发生在 10-18 的 R41–R43。

**为什么会偏**：每遇到一个问题就加一层机制；只进不出；用测试数/Gate 状态代替交付指标；把「管控」做成了「自我验证」，而不是「验收你的交付物」。

## 2. v4 三层结构：执行薄 / 评审厚 / 反哺闭环

```text
tenger-skills/
├── README.md              # 一页：是什么、怎么用（≤150 行）
├── WORKFLOW.md            # 一条主链 + 何时停（≤100 行）
├── skills/                # 核心 10 个 Skill（4 薄教 + 4 厚收 + 2 入口/修复）
├── shared/                # 4 份：Skill 写法 / 评审契约 / 验收契约 / 问题记录与反哺
├── issue/                 # 问题卡（30 秒一张）
├── bug-patterns/          # 真实缺陷模式 → 评审检出清单（长期资产）
├── loop-log.md            # 每个真实任务一行复盘 + 验收指标
├── scripts/               # validate_lite（≤5 秒）+ install-skills（core profile）
└── archive/               # 冻结区（只读）：治理/评测/自举记录/元 Skill/旧 docs/旧 issue
```

**五条原则**：
1. **教学变薄**：执行类 Skill 只写「交付标准 + 停等点 + 证据要求」，不教框架细节（模型已会）；每半年审计再删一次。
2. **评审变厚**：判据、证据标准、独立评审、缺陷模式库是长期资产，随真实缺陷积累而升值。
3. 记录要轻（30 秒一张卡），反哺要小（每次≤3 处、每处≤10 行）。
4. 冻结优于保留，删除优于冻结；archive 只读 + tag 快照，随时回滚。
5. 门禁只防「假完成」；评审强度按任务风险分级，不让评审拖死交付。

## 3. Skill 处置：10 核心 + 6 按需 + 29 冻结

### 3.1 核心 10（默认安装）

| # | Skill | 类型 | 由哪些现有 Skill 合并/精简 | 目标篇幅 |
|---|---|---|---|---|
| 1 | `workflow` | 入口 | workflow（精简） | ≤120 行 |
| 2 | `onboarding` | 入口 | project-onboarding（精简） | ≤100 行 |
| 3 | `requirements` | 薄教 | idea-intake + product-discovery + product-definition + feature-decision + prd-design + prd-review | ≤100 行 |
| 4 | `tech-design` | 薄教 | backend-tech-design + frontend-tech-design（方案自检并入） | ≤100 行 |
| 5 | `backend-dev` | 薄教 | backend-dev（精简） | ≤100 行 |
| 6 | `frontend-dev` | 薄教 | frontend-dev（精简） | ≤100 行 |
| 7 | `auto-test` | 厚收·证据 | auto-test（精简为 L0-L2 + 可复现声明） | ≤150 行 |
| 8 | `review` | **厚收·评审** | code-review + tech-review 的评审部分 | ≤180 行 |
| 9 | `acceptance` | **厚收·验收** | 新增：DoD + 证据核验 + 交付结论（收编 workflow 的 Gate 部分） | ≤150 行 |
| 10 | `bug-fix` | 修复 | bug-fix（精简） | ≤100 行 |

> 核心中的「厚收」3 个（auto-test / review / acceptance）是体系最值钱的部分，优先写、可以写厚；「薄教」4 个原则上压到 100 行以内。

### 3.2 按需 6（默认不装，`--profile on-demand`）

`ui-design`（原型+UI+还原度合并）、`release`（发布计划+部署+验证合并）、`incident`、`refactor`、`oss-radar`、`fact-check`。

### 3.3 冻结 29

其余全部（产品研究/竞品/蓝图/原型评审/UI 评审/旧技术评审/信号采集/分诊/运行/发布旧版/质量巡检/optimizer/evolver/lifecycle/source-reading/essence-distill/competitive-analysis/product-analytics/post-release-review 等），移入 `archive/frozen-skills/`，不删除、不维护、不安装、不校验。

### 3.4 历史资产去向（只读，不迁移、不清理）

| 旧资产 | 去向 |
|---|---|
| 旧 65 条 issue | `archive/issue-v3/` 只读；新问题池从 0 开始 |
| 旧 `docs/` 计划/研究/说明书 | `archive/docs-v3/`；根目录只留 README/WORKFLOW/本计划 |
| `governance/`、`evals/`、自举 `.spec/`、551 测试、四宿主漂移核对 | `archive/system-v3/`，需要时手动跑 |
| 45 个旧 Skill 全文 | `archive/frozen-skills/` + 原分支与 tag |

## 4. 评审验收体系（本体系的核心资产，写厚）

### 4.1 为什么它是核心

LLM 能力越强，产出越像样，「教怎么写」的边际价值越低；但模型也越会「说得像真的」，**判断真假的成本反而上升**。所以体系应该把投入从「教」转向「收」：判据、证据、独立评审、缺陷模式。

### 4.2 评审强度按风险分级（默认自动判定，可手动覆盖）

| 档位 | 适用 | 最少做什么 | 时限 |
|---|---|---|---|
| 轻量 | 文案/样式/单文件小改 | 自检 + 1 次快速评审（可同会话新上下文） | ≤10 分钟 |
| 标准 | 一般功能开发 | 独立代码评审（fresh 上下文）+ 测试证据 + 验收清单 | 按任务定 |
| 完整 | 生产/发布/迁移/权限/资金 | 全部 + 独立评审 + owner 签收 + 回滚验证 | 不省 |

### 4.3 判据（Definition of Done）

- 需求 AC 逐条对应；
- 无未解决 P0/P1；
- 证据齐全且可复现（命令/测试/构建/运行/截图/日志/sha256）；
- 变更可回滚（改了什么、怎么退）；
- 风险与遗留项显式登记。

### 4.4 证据标准（防「AI 说得像真的」）

每条结论必须挂证据；证据形态只认：可复现命令与输出、测试报告、构建产物、真实运行/截图、日志、文件 sha256。**口头描述、模型自述、旧截图都算未验证。**

### 4.5 独立评审（保留旧体系的精华）

- 评审者不参与产出（fresh 上下文/新会话）；
- 只给评审包（任务、被审对象、判据），不给产出过程与自检结论；
- 报告必须记录隔离信息与评审者 id（简化版 §0.5）；
- 复核只验已确认项，最多 3 轮；P0 未清不得放行。

### 4.6 结论与处置

评审/验收结论三值：**ACCEPT 放行 / FIX 可修后复验 / REJECT 阻塞**。高风险任务加「owner 签收」；有条件接受必须由 owner 明确记录风险（不默认放行）。

### 4.7 长期增强（随模型变强，越积越值钱）

1. 判据库：从每次真实缺陷提炼 checklist；
2. 缺陷模式库 `bug-patterns/`：评审者的检出清单；
3. 缺陷逃逸复盘：验收后 2 周内冒出的 P0/P1 必须回填「评审为什么没抓到」；
4. 每半年审计一次：教学类 Skill 还能删什么；评审判据要补什么。

### 4.8 教学层变薄规则

执行类 Skill 只写：何时做、交付什么、验收标准、何时停、证据要求；不写框架教程、不写大段代码模板（除非模型反复做错）。每篇≤100 行，超了先删。

## 5. 问题记录与反哺环

**记录**：`issue/NNN-slug.md`，30 秒一张卡：类型（review/acceptance 发现的 **skill** 问题、**project** 问题、**env** 问题、**process** 卡点）、归属 Skill、现象、证据、影响、建议改动、状态。**评审与验收发现的问题，是反哺的最主要来源。**

**反哺规则（防膨胀）**：
1. 触发：同一问题第 2 次出现，或单次卡 >30 分钟 → 必须改 Skill；
2. 窗口：每 2 周一次批改，每次 ≤3 处、每处 ≤10 行；
3. 验证：下次真实任务记 `verifiedBy`；4 周未验证 → 回滚该改动；
4. 范围：只改 `skills/` 与 `shared/` 四份规则。

**闭环状态**：`open → fixed → verified → closed`；无法验证的保持 open。

**度量（每月）**：
- 一次验收通过率 = 首次 ACCEPT 任务数 / 总任务数；
- 缺陷逃逸率 = 验收后 2 周内新发现的 P0/P1 数 / 已交付任务数；
- 复发率 = 同类问题再次出现次数 / 已修复问题数；
- 反哺有效率 = 修复后该类问题减少条数 / 已修复问题数；
- loop-log 每任务一行：日期｜任务｜时长｜返工｜介入｜评审发现数｜一次通过？｜新增问题｜修复｜复发｜Skill 改动。

## 6. 阶段计划（D0 = 2026-10-20）

| 阶段 | 时间 | 任务 | 产出 | 验收标准 |
|---|---|---|---|---|
| **P0 准备** | D0（今天）✅ | 提交当前分支、tag、切分支、计划入库 | 分支 + tag + 计划 | 已完成 |
| **P1 冻结瘦身 + 评审底座** | D1–D3（10-21～23）✅ 2026-10-20 提前完成 | ① archive 迁移；② 厚收三件套（评审/验收/问题反哺契约）；③ 核心 10（厚收 3 + 薄教 4 + 入口 2 + bug-fix）；④ README + WORKFLOW；⑤ `validate_lite.py` + installer core profile；⑥ issue 模板 + loop-log（原 P2 项提前） | 可安装的 v4 骨架（根 10 项、10 Skill + 4 shared、installer core、validate_lite、issue/loop-log） | 已达成：根目录 10 项；install=10 Skill+4 shared；validate_lite 52 项 PASS / 0.80s（≤5 秒）；评审/验收模板可用；copy 安装后 `--check` drift=0 |
| **P2 闭环跑通** | D4–D5（10-24～25） | ① issue 模板 + loop-log；② 反哺规则接入 workflow/review；③ 用 1 个历史小任务回放：评审→验收→问题卡→修 Skill→复验 | 闭环样本 | 任务走完；2–5 张问题卡；至少 1 条 fixed→verified；一次验收通过率有数（0 或 1） |
| **P3 真实试点** | W1–W2（10-27～11-06） | 用核心 10 做 2 个你指定的真实小任务；记录 loop-log；执行 1 次批改窗口 | 2 份任务记录 | 交付成功；3 个指标：时长/返工/介入；验收指标有数 |
| **P4 对比决策** | W3–W4（11-09～11-20） | 与旧体系同题对比；决定按需能力装回/继续冻结/回滚 | 一页决策记录 | 决策明确 |

## 7. 门禁策略（从 25 分钟降到 5 秒）

`validate_lite.py` 查 6 件事：① `skills/*/SKILL.md` frontmatter 与必需小节；② `skills/` 与 `shared/` 引用可达；③ 问题卡必填字段/状态枚举；④ loop-log 表头；⑤ 评审/验收报告必需字段（AC、证据、隔离、结论三值）；⑥ installer `--dry-run` core 清单。
不再作为日常门禁：551 全量测试、12 套 eval、goal-plan 机读执法、自举 Gate、四宿主漂移——随旧结构进 `archive/system-v3/`，需要时手动跑。CI 只跑 validate_lite + installer 冒烟。

## 8. 风险与回滚

| 风险 | 应对 |
|---|---|
| 评审过重拖慢交付 | 风险三档 + 轻量档 10 分钟上限；评审超时先交付再补评审记录 |
| 评审形式化/假绿 | 证据标准只认可复现物；独立上下文；高风险 owner 签收；缺陷逃逸复盘 |
| 模型变强后教学 Skill 过时 | 每半年审计删除；执行类≤100 行 |
| 核心 10 能力不足（UI/发布/事故） | 按需 6 随时装回，不重建治理层 |
| 精简改坏可用性 | 原分支 + tag 原样保留；archive 只读，随时回滚 |
| 旧宿主安装副本 | 默认不动；CodeBuddy 已按用户指令切到 v4 core（旧 v3 安装先备份、后删除，见 §11）。其他宿主（.dsh / .qoder-cn / .zcode 等）仍保留 v3 安装，后续按需逐个切换 |

## 9. 交付物与 Done 定义

**交付物**：① 本计划；② v4 目录与归档；③ 核心 10 Skill（含评审/验收厚资产）；④ shared 4 份；⑤ validate_lite + installer core profile；⑥ issue 模板 + loop-log + 反哺规则；⑦ 2 个真实任务记录（含验收指标）；⑧ 一页决策记录。

**v4「可用」Done**：新会话只装 core profile，拿一句真实需求走完 需求→方案→开发→测试→**独立评审→验收→交付**，全程不碰旧治理文件；同时产生问题卡，并在下一次任务验证至少 1 条反哺。

## 10. 待你确认的 6 个决策点（默认值已给）

| # | 决策 | 默认 |
|---|---|---|
| 1 | 核心 10 名单（4 薄教 + 2 入口 + auto-test/review/acceptance 3 个厚收 + bug-fix） | 按 §3.1 |
| 2 | UI 设计 / 发布 / 事故是否放按需 | 按需（默认不装） |
| 3 | 评审强度三档（轻量/标准/完整）自动判定 | 按 §4.2 |
| 4 | 反哺批改窗口频率与上限 | 每 2 周、每次≤3 处 |
| 5 | 首批 2 个真实试点任务 | 由你指定 |
| 6 | 历史资产处理 | archive 只读保留（可回滚），不删除 |

确认方式：2026-10-20 用户在新会话确认「按默认执行、开工」，6 项均按默认值执行；P1 已于同日完成。

## 11. 执行记录

| 日期 | 阶段 | 动作 | 提交 / 证据 |
|---|---|---|---|
| 2026-10-20 | P0 | 分支、tag、计划入库 | `4b0e04c` / tag `pre-converge-20261020` / `0f6c3cf`、`051dbc3` |
| 2026-10-20 | P1-① | 旧体系整体冻结进 `archive/`（只读）：45 个旧 Skill、65 张旧问题卡、旧治理/评测/自举/脚本/共享契约、学习资料；新增 `archive/README.md`（映射 + 回滚方式） | `ed165c0` |
| 2026-10-20 | P1-②③ | 厚收三件套 + 核心 10 Skill：`shared/` 4 份 521 行；`skills/` 10 份 595 行（42–87 行/份） | `e4a8756` |
| 2026-10-20 | P1-④⑤⑥ | README（80 行）+ WORKFLOW（56 行）、`validate_lite.py`、installer core profile、CI、issue 模板 + loop-log（11 列） | `e4a8756`、`d483be0` |
| 2026-10-20 | 宿主切换 | CodeBuddy 切到 v4 core：旧 45 Skill + 42 份旧 shared 先备份（2445 + 42 文件）再删除；`--profile core` 安装 10 Skill + 4 shared，`--check` drift=0（62 文件） | 宿主 `~/.codebuddy/skills`；备份 `D:\project\agent-project\.backups\codebuddy-v3-20261020`（仓外）；源修订 `92d737e` |

### P1 验收对照

| P1 验收标准 | 结果 | 证据 |
|---|---|---|
| 根目录 ≤10 项 | ✅ 恰好 10 项 | README.md / WORKFLOW.md / PLAN.md / loop-log.md + skills/ shared/ issue/ bug-patterns/ scripts/ archive/ |
| install 只装 10+4 | ✅ | `python scripts/install-skills.py --list --profile core` → 10 个 skill + 4 份 shared；copy 安装到仓外临时目录后 `--check` drift=0 |
| validate_lite ≤5 秒 | ✅ 0.80s（含解释器启动实测约 2–4s） | `python scripts/validate_lite.py` → 52/52 PASS，exit 0 |
| 评审/验收模板可用 | ✅ | `skills/review/templates/review-report.md`（6 节 + 三值）；`skills/acceptance/templates/acceptance-report.md`（5 节 + sha256 + 签收） |

### 未做（按计划留到后续）

- 按需 6（ui-design / release / incident / refactor / oss-radar / fact-check）未实现，installer 暂只提供 `--profile core|all`；等 P2/P3 有真实任务再按需写，不预先造。
- P2 闭环回放（历史小任务走评审→验收→问题卡→改 Skill→复验）、P3 两个真实试点任务、P4 对比决策均未开始。
- 旧宿主安装副本保持不动；`archive/` 与 tag 可整体回滚（见 §8、§3.4）。

