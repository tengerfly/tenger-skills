# 评审上下文隔离（Review Context Isolation）

> 目的：让评审者只拿到「产物 + 判据」，看不到产出者的思考过程。同一个上下文里刚写完再自审，会被自己的推理路径锚定——查不出自己的错，评审会退化成确认（Vibe Coding 心法 4：review 独立性 = 干净上下文 + 不参考生成过程）。
> 地位：本文件是 `shared/` 公共契约，优先级高于各 Skill 正文（`shared/skill-contract.md` §1）。适用于所有评审/审计类 Skill 及其编排方。

## 1. 适用范围

| 类别 | Skill | 强制？ |
|---|---|---|
| 链上评审 | `prd-review`、`prototype-review`、`ui-ux-review`、`tech-review`、`code-review`、`fidelity-review` | 是 |
| 周期审计 | `quality-inspection` | 是 |
| 编排方 | `workflow`、`prd-workflow`、`auto-test`（内嵌 Fidelity-Review 时） | 派发与收账，不得代做评审 |
| 参照 | `fact-check`（核验对象是本会话产出时参照；核验外部公开事实不强制）；`skill-optimizer` 模式④「七维自洽体检」在**同一会话刚改过被体检 skill** 时参照隔离 | 建议 |
| 不适用 | `post-release-review`、`product-analytics`、`defect-triage` 等非产物评审动作 | — |

「评审」指会产出分级问题清单、评审报告、巡检报告或 Gate 建议的动作；「自查」指产出方在自身上下文中做的自检。两者不得混称。

## 2. 铁律

1. **产出上下文不得评审自己的产物**：参与过被审产物创作、修订、内部自检、评审调度的会话/子代理，不得作为该产物的评审者。同一会话里「换一个角色再看一遍」不算隔离。
2. **评审判断只发生在隔离上下文**：fresh 子代理（首选）或新会话。两者都不具备 ⇒ `BLOCKED`；不得以「自己读一遍」「条件允许时用 subagent」降级，也不得把自查包装成评审。
3. **只给评审包**：评审者只接收 §3 定义的包，不继承产出会话历史、草稿、自检结论、猜想或「我觉得哪里有问题」的引导。评审者可读仓库文件，但不得读取产出会话记录。
4. **只审不改**：评审者不改被审产物；问题进清单交产出方。
5. **子代理汇报不等于证据**：编排方必须核验报告文件与证据产物（截图/命令输出/文件:行定位），不得凭子代理自述判 Gate（`shared/evidence-before-claims.md`）。
6. **用户只要快速自查时**：可以输出「自查（非评审）」，但不得产出评审报告、评审任务清单或 Gate 建议，也不得写进评审归档目录。

## 3. 评审包（review package）

一次评审一个包，落盘到评审归档目录：`.spec/<评审域>/评审包-<reviewId>.md`（reviewId 形如 `REV-YYYYMMDD-NN`）。模板：`shared/templates/review-package.md`。包内只允许：

1. **被审对象**：精确路径 + 版本 + 内容摘要（字段与口径见 `shared/artifact-contract.md` §2、`shared/gate-policy.md` §6 第 6 条）；代码评审给批次 + commit/工作区状态。
2. **判据集**：PRD/AC、原型、设计稿 + design-system、TDD/FTDD、批准范围、上游 Gate 状态等引用路径（按评审域）。
3. **清单与模板**：本 Skill 的 references 清单、`known-issue-patterns.md`、报告/清单模板路径。
4. **边界**：批次/端/页面/模块/维度、评审轮次 n/3、只审不改要求。
5. **上轮已确认问题（F1）**：只给已确认项 + 修复判据 + 上轮结论，不给产出方辩解或自查结论。
6. **输出契约**：报告落点、编号/分级口径、证据要求（截图/命令/定位）、Gate 建议格式。
7. **隔离声明**：评审者须在报告 §0.5 填 `isolationMode`、`reviewerRef`、`packageDigest`、`parentExecution`（有 run-log 时）。

**禁止进包**：产出过程对话/摘要、草稿版本、产出方自检结论、未确认的猜测清单、可能诱导评审者的「已知问题」提示（F1 已确认项除外）。

包摘要：PowerShell `Get-FileHash -Algorithm SHA256` 或 `sha256sum`，写进报告 §0.5。

## 4. 隔离执行阶梯（按宿主能力）

| 档 | 条件 | 做法 | 记录 |
|---|---|---|---|
| **L1 子代理（首选）** | 宿主提供 fresh 子代理/子任务工具（DSH `subagent`；Claude Code `Task`；等价工具） | 每个评审单元派 1 个 fresh 子代理；只给评审包 + 单元指令；并行/串行均可，但每个子代理不共享上下文 | `isolationMode: subagent` + `reviewerRef` |
| **L2 新会话** | 无子代理能力，但可开新会话/新 Agent 实例 | 编排方写包 + `dispatch-prompt.md`，由用户在新会话执行；主会话停住，不自行评审。**例外（用户直接在新会话发起评审、且本会话未参与被审产物产出）**：本会话可作 new-session 评审者并按包模板自填评审包（此处「自填包」是评审者自备输入，不视为代替产出方做评审调度），§0.5 记 `parentExecution` 与包摘要；若本会话参与过产出/修订/自检/调度，必须另交新会话 | `isolationMode: new-session` + sessionRef |
| **L3 均无** | 宿主无任何隔离执行能力 | `BLOCKED`：owner=宿主/用户，requiredInput=隔离执行能力，clearCondition=具备后重跑；可先出「自查（非评审）」，不得出评审报告/Gate | 见 Gate |

**多评审单元**：每个已在 Skill 中声明的独立维度/角色/批次各派 1 个独立子代理，互不可见；汇总由独立汇总子代理完成（只输入各单元报告 + 汇总模板）。单单元评审可由该评审者直接产出汇总。若评审 Skill 被编排方作为单个隔离子代理整体调用、而宿主不支持嵌套子代理：单单元评审可继续；多单元评审必须回到编排器分别派发，无法拆分 ⇒ `BLOCKED`（缺多单元隔离能力）。

**常见派发计划**（Skill 正文另有本域细节）：

| Skill | 评审单元（各 1 个独立子代理） | 汇总者 |
|---|---|---|
| `prd-review` | 1 个评审单元，覆盖四份 checklist（按角色拆分时：前端/后端/测试各 1） | 单单元由评审者直接出汇总；角色拆分时由产品专家总审子代理汇总 |
| `prototype-review` | 4 维：页面与载体完整性 / 文案与字段一致性 / 交互与流程闭环 / 原型自身实现质量 | 独立汇总子代理 |
| `ui-ux-review` | 4 维：载体与结构零改动 / 文案与字段一致性 / 视觉规范一致性 / 视觉呈现与可交付质量 | 独立汇总子代理 |
| `tech-review` | 每个批次 1 个（⑩-后 / ⑩-前；单批即 1 个） | 单批由评审者直接出汇总；双批由独立汇总子代理 |
| `code-review` | 每个批次 1 个代码评审者；⑬-前 另派 1 个 Fidelity-Review 评审者 | 单批由评审者直接出汇总；⑬-前 由独立汇总子代理合并 |
| `fidelity-review` | 1 个还原度评审者 | 评审者直接出报告（无跨单元汇总） |
| `quality-inspection` | 1 个巡检审计者（可按检查面再拆，默认 1） | 审计者直接出报告 |

## 5. 编排方程序（workflow / prd-workflow / 各评审 Skill 的编排形态）

1. **开工前判断角色**：本上下文是否参与产出/修订/自检/评审调度？是 ⇒ 不得进入评审步骤，转派发；否 ⇒ 可作为编排方。
2. **固定基线**：按 `shared/gate-policy.md` §6 核对上游 `status/version/gate/allowDownstream`；作废或关闸 ⇒ `BLOCKED`，不打包、不评审。
3. **建包**：写评审包 + `dispatch-prompt.md`（含单元角色、报告落点、只审不改、不得读产出会话）。
4. **派发**：按 §4 能力阶梯；单单元或多单元。
5. **收产物**：核验报告文件 + 证据产物（截图/命令/定位），不采信口头「完成/通过」。
6. **汇总**：多单元交独立汇总子代理；缺包/缺报告/缺证据 ⇒ 该单元「未验证」，不得计为已查。
7. **出 Gate**：按 `shared/gate-policy.md` / `shared/anti-deadloop.md`；报告缺 §0.5 隔离记录或隔离证据不符 ⇒ Gate 只能 `BLOCKED`（缺评审隔离证据）。
8. **留痕**：有 `scripts/` 时跑 `python scripts/tsr.py --project-root <项目> --execution-id <E> --node <节点> --skill <skill> --role review --actor subagent --parent-execution <主 executionId> node-start/node-end ...`；报告 §0.5 填全；`execution` / `workflow.yaml` 的 `evidenceRefs` 指向报告。

## 6. 报告硬性记录：§0.5 评审上下文隔离记录

所有评审汇总报告/单维度报告必须包含（模板已内置）：

| 字段 | 值 |
|---|---|
| `isolationMode` | subagent / new-session |
| `reviewerRef` | 全部评审单元的评审者 id（多单元逗号分隔；subagent id / 新会话 id） |
| `packageDigest` | sha256:… |
| `parentExecution` | 主 executionId（有 run-log 时） |
| `producedByContextInvolved` | false（必须为 false；true ⇒ BLOCKED） |
| `verifiedArtifacts` | 报告与证据文件路径 |

缺本节、`producedByContextInvolved: true`、或 `reviewerRef`/`packageDigest` 为空 ⇒ 报告不得 `PASS`/`CONDITIONAL`，Gate 记 `BLOCKED`（缺评审隔离证据）。这是结构判据，与「上游闸门核对」同级。

## 7. 反模式

| 反模式 | 为什么错 | 正确做法 |
|---|---|---|
| 同一会话写完就「我再看一遍」 | 被自己的推理路径锚定，查不出自己的错 | 派 fresh 子代理 / 新会话 |
| 「条件允许时用 subagent」 | 给了不隔离的合法出口 | 隔离是硬性前置，非增强 |
| 同一子代理里换「评审者角色」 | 上下文未变，只是换称呼 | 新子代理 |
| 把产出会话摘要/自检结论贴给评审者 | 锚定污染，评审变成确认 | 只给评审包 |
| 把多维度塞进一个子代理 | 维度互相锚定，失去独立性 | 每单元一个子代理 |
| 采信子代理「已评审通过」的口头汇报 | 无证据，可能是幻觉 | 核验报告 + 证据文件 |
| 宿主不支持子代理就自己读一遍 | 用同上下文冒充隔离 | 新会话，或 `BLOCKED` |
| 用「轻量任务」跳过隔离 | 轻量只裁程序性前置，不裁评审独立性 | 一旦调用评审 Skill 即适用 |
| 把上一轮问题清单全量喂给评审者 | 复盘会围绕旧问题打转，新增检出被抑制 | 只给 F1 已确认项 + 修复判据 |

## 8. 与现有契约的关系

- `shared/evidence-before-claims.md`：子代理/并行评审结论必须由主线核验产物；
- `shared/anti-deadloop.md`：轮次上限 3、复核只验本轮、P0/P1 冻结；隔离评审不改变轮次规则；
- `shared/gate-policy.md`：Gate 三值、上游闸门、§6 字段与留痕；
- `shared/receiving-review.md`：产物方接收评审的响应纪律；
- `shared/execution-profiles.md`：轻量不强制独立评审 Skill，但一旦调用评审 Skill，本契约不降级。
