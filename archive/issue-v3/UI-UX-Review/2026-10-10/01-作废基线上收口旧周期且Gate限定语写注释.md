# 在已作废基线上收口旧评审周期，并把 Gate 的限定条件写进注释（下游读不到）

> 归属 skill：`UI-UX-Review` ｜ 日期：2026-10-10 ｜ 来源：用户（业务项目 `knowledge-bases` 追问暴露）+ 本 skill 自查

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P1 |
| 标签 | `流程缺陷` / `产物格式` / `边界不清` |
| 优化状态 | 已沉淀（2026-10-10 源仓规则层落地 A/B 两端；**尚未经真实一轮收口 fresh 复跑验证**） |

> 定级理由：判据结论本身正确（31 条全闭有实测支撑），错在**Gate 语义越界 + 限定语放错位置**——明显影响下游判断且极易复发（任何一次「旧基线收口」都会再犯）。

## 现象

2026-10-10 设计评审第三轮（末轮 3/3）：

1. 复核方（本 skill）在 **14:52** 收口一个已于 **10:53** 被 `DEC-20261010-PRODUCT-DIRECTION` 作废的基线（PRD v0.2 → `APPROVED_SUPERSEDED`），并把 Gate 记为 **`PASS`**，只在注释/正文里加限定：`allowDownstream: true   # 限定：仅对基线 PRD v0.2 成立；不得当作 v0.3 现行需求的实现依据`。
2. 而同一时刻，上游 `PRD-20261010` v0.3.2 的第 2 轮评审记录（13:57）已写明 `gate: BLOCKED`、`allowDownstream: false # 不放行 prototype-design`、`round: 2/3`。**复核方出 Gate 时没有读它。**
3. 用户一句「PRD-review 没有走完，怎么就走设计阶段了？」才把这条问出来。核对后确认：设计阶段本身没越序开工（都发生在 10:53 前），**失守点正是这次收口给出的 `PASS`**。
4. 同轮更正：报告 §一 改判 `BLOCKED`（新增 §1.1 时序核查节）、`manifest.yaml` 的 `gate: PASS → BLOCKED`、**`allowDownstream: true → false`**、`workflow.yaml` 第三轮 outcome 同步改判并新增 `BLK-DESIGN-01`。

**关键机制错在**：`gate-policy.md` §3 已写「`allowDownstream: false` 即使记了 Gate 也挡下游」，而下游（`consumedBy: Frontend-Tech-Design, Frontend-Dev, Fidelity-Review`）读的是 `gate` / `allowDownstream` **字段**，不读我写在注释和段落里的限定语。限定语放注释 = 没有限定。

## 根因

1. **把「判据全闭」当成「可放行」**：本 skill 的轮次判据只覆盖「本清单 D-01~D-31 是否闭合」，收口动作天然导向 PASS；缺一道「出 Gate 前先核对上游闸门是否仍有效」的前置。
2. **限定语义落在不可被消费的位置**：用注释/正文表达「这个 PASS 只对旧基线成立」，而不是把结论压进 `gate` 与 `allowDownstream` 两个字段。
3. **基线有效性不在评审输入校验里**：`§二 输入与前置` 只要求「PRD / 布局清单 / design-system / 设计稿 / 浏览器工具」存在，**不要求这些输入仍是现行批准版本**；PRD 是覆盖式改同名文件，mtime 与版本号是唯一线索，而评审流程没有把它列为必查项。
4. 同事件族另一条（不在本条重复建档，只回链）：修复方把自述结论写进评审方单一事实源并自写 Gate（`设计评审/任务清单.md` §五 曾被写成「第二轮 Gate：PASS」，与当时复核报告的 CONDITIONAL 互斥）——详情源见项目侧 `knowledge-bases/.spec/问题日志.md` 2026-10-10 两行与 `第三轮复核报告.md` §7.1，归属 `UI-UX-Design` 防复发。

## 期望 vs 实际

- **期望**：评审周期收口时，若所依据的上游基线已 `SUPERSEDED` 或其现行版本 `gate != PASS` / `allowDownstream: false`，本周期 Gate 只能记 `BLOCKED`（命名缺失输入 + owner + 清除条件），`allowDownstream` 同步置 `false`；「判据全闭」作为事实单独记录，不得借注释承载放行范围。
- **实际**：记了 `PASS` + `allowDownstream: true`，限定语写在注释里；靠用户追问才改判。

## 修复方向（本轮未改 skill 规则，仅登记；待用户在源仓裁决）

1. **Gate 前置核对（主修）**：`UI-UX-Review` 的 Gate 步骤加 REQUIRED 预检——出 Gate 前逐条读 `manifest.yaml` 中本评审的上游 artifact（PRD / 原型 / design-system）的 `status`、`version`、`gate`、`allowDownstream`；任一为 `SUPERSEDED` / 非 `PASS` / `false` → 本周期只能 `BLOCKED`，并在报告与 manifest 写 `blockedBy`。
2. **禁止用注释承载放行范围**：`shared/gate-policy.md` 补一条（或本 skill 引用）——限定条件必须落在字段上（`gate` / `allowDownstream` / `blockedBy`），注释与正文只作解释；`allowDownstream: true` 不得与「基线已作废」并存。
3. **报告模板加固定小节**：`assets/summary-template.md` / 复核报告结构加「**上游闸门核对**」表（上游 artifact id｜当时版本｜mtime｜gate｜allowDownstream｜结论）与「**时序核查**」（基线作废时刻 vs 被审产物 mtime），无此表则 Gate 只能记「未验证」。
4. **基线漂移检出成为常规动作**：判据若引用上游原文（如 `prd/overview.md:41`），复核时必须对该字符串做四路 grep（`.spec/prd/` + `.spec/features/` + `.spec/archive/` + `.spec/TDD/`）确认原文仍在；不在则判「基准漂移」，改由同源 v-x 基线文档回证并登记 openItem，不得静默沿用旧结论。
5. **旧基线收口 ≠ 放行**：收口语固定写成「本周期判据全闭（轮次 n/3）；放行状态 BLOCKED，缺 <上游批准 + 增量>」，避免「PASS」字样被下游截读。

## 跟踪与证据

- 原问题 ID：项目侧 `BLK-DESIGN-01`（`knowledge-bases/.spec/workflow.yaml` `blockedItems`）；评审详情源 `.spec/设计评审/第三轮复核报告.md`（§一 Gate 更正 + §1.1 时序核查 + §7.1 台账纠正）
- 发现时间 / 相关步骤：2026-10-10 14:52 收口、15:0x 用户追问后改判；步骤=第三轮复核出 Gate
- 脱敏证据：`manifest.yaml` `DESIGN-REVIEW-20261010` 更正前后（`gate: PASS → BLOCKED`、`allowDownstream: true → false`、新增 `blockedBy` 两条 + `gateCorrectionNote`）；`需求评审/PRD-20261010-评审-第2轮.md` 执行记录 `allowDownstream: false`（13:57）；mtime 时间线见报告 §1.1 表
- 责任方 / 下一动作 / 修复判据：`UI-UX-Review`（规则由用户在源仓落地）；判据=构造「上游 `allowDownstream: false`」场景跑一次收口，产出必须为 `BLOCKED` 且 `allowDownstream: false`，且报告含「上游闸门核对」表
- 根因与归属：**已确认**；归属评审方 Gate 步骤（本条）+ 编写方回填规则（回链 `UI-UX-Design`，见根因 4）
- 复核证据 / 未验证项：本轮未改 skill；改判后的台账一致性已用 `yaml.safe_load` 复验（`gate=BLOCKED`、`allowDownstream=False`、`blockedItems` 含 `BLK-DESIGN-01`/`BLK-GATE-ORDER-01`）。**未验证**：云端 draft version 递增（Superdesign MCP 未连接，`README.md:33` 与 `workflow.yaml` 版本号互斥）
- 回退方式：规则改动单列提交；若某次收口确需对旧基线给 PASS，须以显式 DEC 记录授权，不改默认判据

## 双向落点

| 方向 | 目标 | 落点 |
|---|---|---|
| A · 防复发 | `UI-UX-Design`（产出方） | ① 交付/返工收尾必须声明所依据的上游版本与 mtime（现 `README.md:14` 只写「PRD v0.2 APPROVED」，无版本指纹）；② **禁止自写评审 Gate**——回填评审任务清单仅限状态列与修复说明并标回填方（本事件实况见根因 4 回链） |
| B · 检出力 | `UI-UX-Review` `references/known-issue-patterns.md` | 新增两条模式：①「**基准漂移**：判据引用的上游原文被覆盖式修订后消失」，检出方法＝四路 grep + PRD 版本行 mtime 与复核报告 mtime 比对；②「**收口放行越界**：Gate 为 PASS 但上游存在 `allowDownstream: false` / 基线 SUPERSEDED」，检出方法＝出 Gate 前逐条读上游 manifest artifact 的四字段并列表 |

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | B · 检出力（本条主体）：`UI-UX-Review` 主流程 Gate 前置核对；A · 防复发（回链根因 4）：`UI-UX-Design`；公共口径统一落 `shared/gate-policy.md` §6，各 skill 只引用不复制 |
| 沉淀位置 | `UI/ui-ux-review/SKILL.md`——§二 输入表加「上游闸门有效性」行、步骤 1 改「资产解析、上游闸门核对与浏览器预检」并加 REQUIRED、步骤 6 改「汇总 + 出 Gate」（核对表 + 时序核查 + 收口语固定）、§二 输出清单补承接位、§五 错误表 +2 行；`UI/ui-ux-review/assets/summary-template.md` 新增 **§〇**；`UI/ui-ux-review/references/known-issue-patterns.md` **模式 10**（基准漂移）与**模式 11**（收口放行越界）——以上记 `UI/ui-ux-review/CONTEXT.md` **D-19**。A 方向：`UI/ui-ux-design/SKILL.md` 步骤 9 加「上游基线指纹」与「回填边界（编写方不得自写 Gate）」两条 REQUIRED、§五 错误表 +2 行、`assets/archive-readme-template.md` §一 加承接行——记 `UI/ui-ux-design/CONTEXT.md` **D-37**。跨端同一判据：`shared/gate-policy.md` §6.4「限定只落字段」 |
| 忽略理由 | 不适用 |

> 与原「修复方向」的两处偏离／补充：③ 原建议 2「禁止用注释承载放行范围」不单独在本 skill 复述，统一收进 `shared/gate-policy.md` §6.4（本仓约定：中央约定唯一权威，下游只引用），SKILL 与模板各引一处；⑤ 原建议 4「基线漂移检出成为常规动作」落为案例库**模式 10** 的检出方法（四路 grep + mtime 比对）并挂进步骤 6 的时序核查，未另立第五套 grep 规则。**边界收口（同轮续修）**：原落差「只有 `ui-ux-review` 有核对表、其余评审节点只继承 §6 文字判据」已补齐——公共基线 `shared/templates/review-summary-template.md` 新增 **§0** 上游闸门核对与本轮 Gate，`tech-review`／`code-review`／`prd-review`／`prototype-review` 四节点主流程各加**同一条** REQUIRED 开工前闸门核对并挂 §0 指针（汇总记 `Skill-Optimizer` **D-41**，各节点 D-10／D-17／D-12／D-09）。`fidelity-review` 按公共模板「单报告无需汇总」口径未挂 §0，其基线有效性由 Code-Review／auto-test 的核对覆盖——**该覆盖是否足够尚未验证**，留作观察项。
