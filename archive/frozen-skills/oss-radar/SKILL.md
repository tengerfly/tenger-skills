---
name: oss-radar
description: "开源情报雷达（GitHub 优秀实践采集→提炼→反哺）。采集 GitHub 上优秀的开源 skill 与同域工程项目，提炼人家的优秀实践点，反哺本仓自有 skill 与在研项目；支持增量采集与无人值守定时巡逻。触发：采集开源情报、跑一轮雷达、扫描/巡逻 GitHub、调研开源 skill、调研某项目的开源实现、看看别人怎么做的、借鉴优秀实践、反哺优化我们的 skill、出开源情报报告、写技术方案前先调研同类项目（TDD/FTDD 前置调研）。边界：产品/商业层竞品分析走 Competitive-Analysis，本 skill 只管工程实现层与 skill 层。"
metadata:
  contract-level: legacy-wrapper
  legacy-alias: "OSS-Radar"
  compatibility: "Claude Code / Agent SDK / OpenCode"
---


# OSS-Radar（开源情报雷达）

> IRON LAW：每条发现必须是完整三元组——**出处**（repo + 文件/链接）+ **优秀点** + **建议落点**；缺任一项不进报告、不进情报库。
> 定位：本仓库的「外部输入口」。Skill-Optimizer 管内部迭代（issue 池/体检/聊天挖掘），本 skill 管外部输入（GitHub 开源情报）。只采不改：反哺改动一律写成任务清单，经确认交 Skill-Optimizer / 对应开发 skill 落地。

## 问题记录与恢复（执行必需）

发现失败、阻塞或用户纠正时，在下一安全节点按 `../../shared/problem-recording.md` 记录；根因未明不丢事实。恢复/交付前核对未决项，沿用已有详情与唯一索引。此规则优先于旧的仅收尾埋点/不确定不记表述，不增加轻量任务的正式建档要求。

## 一、模型：双泳道 × 双模式 × 六步

**双泳道**（watchlist 里每条采集目标归属其一）：

| 泳道 | 对象 | 提炼重点 | 反哺对象 |
|---|---|---|---|
| A · skill 泳道 | 优秀开源 skill / agent skill 集 | 触发描述、渐进披露分层、指令写法、流程稳定（Gate/防死循环）、脚本化、安全兜底 | 本仓各 skill（经 Skill-Optimizer 模式③） |
| B · 项目泳道 | 与在研项目同域/同栈的开源项目 | 架构与模块边界、选型与理由、测试基建、工程化（CI/lint/规范）、可复用组件与模式 | 在研项目（对应方案/开发 skill）；本轮报告（`.spec/开源情报/`）可直接作 Workflow ⑧⑨ 技术方案的前置调研输入 |

**双模式**：交互模式（用户在场，反哺清单确认后可继续推进）与无人值守模式（定时巡逻，行为差异见 §四）。

**六步**：⓪ 装载 watchlist → ① 发现 → ② 采集 → ③ 提炼 → ④ 反哺产出 → ⑤ 台账回写。

## 二、数据目录与 watchlist

数据目录 = 当前工作区 `.spec/开源情报/`：

| 文件 | 作用 |
|---|---|
| `watchlist.md` | 配置 + 台账：关注 topics/repos、两泳道反哺对象路径、`last_run`、已扫 repo 清单 |
| `YYYY-MM-DD-<主题>.md` | 本轮报告（TL;DR + 发现清单 + 待拍板区） |
| `情报库.md` | 累积情报（按条目追加合并，重复只补强不重记） |
| `任务清单.md` | 反哺任务单一事实源（P0/P1/P2 + 状态机，对齐 issue 池约定） |

初始化：watchlist 不存在时——交互模式按 `assets/watchlist-template.md` 问用户两件事（①关注哪些 topics/repos；②两泳道反哺对象路径）；无人值守模式直接按模板写默认清单（默认 topics 见 references）继续跑，不停等。

**REQUIRED**：每轮开始必读 watchlist，结束必回写 `last_run` 与新增已扫 repo；watchlist 缺失 = 第一步先建。

## 三、流程

### ⓪ 装载
读 watchlist，定本轮范围（默认全泳道；用户点名「只扫 X」按点名来）。无人值守 → 全程叠加 §四。

### ① 发现（拉候选清单）
1. 渠道优先级：`gh api`（本机已认证，5000 次/h）→ `api.github.com` 免认证（核心 60 次/h、search 10 次/分）→ WebSearch / web_reader 兜底。端点、查询语法、限流应对见 `references/github-api-playbook.md`（**此步加载**）。
2. 查询 = watchlist topics/关键词 + 增量限定（`pushed:>last_run`）。
3. 配额自守：单轮 search ≤ 5 次；候选满 20 条即停，先到先得。
4. 分诊：候选按相关度 + 星数/近期活跃排序 → 深读池 ≤ 6 个，其余只记名字进台账「待扫池」。

### ② 采集（深读池）
每 repo 只取：README、（skill 类）SKILL.md、目录树（git trees API）、≤ 3 个关键文件。只摘「点」不当搬运工：原文片段 ≤ 10 行作证据，出处（repo + 路径 + 链接）随手记。

### ③ 提炼
逐 repo 出发现条目，每条 = 三元组 + 两个附加字段：

- 三元组：出处 / 优秀点 / 建议落点（IRON LAW）
- 可移植性：直接搬（约定/清单/规则可改写落仓）｜需改造（须对齐本仓术语与流程）｜仅启发（方向性参考）
- 等级：P0 直接影响在研项目质量或本仓 skill 硬伤级缺口 / P1 明显增益 / P2 建议

提炼自问（问题化，不给泛泛评价）——skill 泳道：人家的 description 凭什么能命中？它的 L1~L4 分层比我们省在哪？它把哪类重复劳动固化成了脚本/清单？防死循环/防跑飞机制是什么？项目泳道：模块边界为什么能这么切？测试基建怎么搭？哪些组件/模式可直接进组件库？

### ④ 反哺产出
1. 写本轮报告（结构见 `assets/report-template.md`，**TL;DR REQUIRED**）。
2. 合并进 `情报库.md`（与既有条目查重）。
3. 更新 `任务清单.md`：每条 P0/P1 写成可执行任务（目标 skill/项目 + 改什么 + 依据哪条发现）。
4. 交互模式：把 P0/P1 反哺清单呈给用户，确认后——skill 类 **REQUIRED SUB-SKILL：** 交 `Skill-Optimizer` 模式③执行，项目类交对应方案/开发 skill。**本 skill 自己不改任何自有 skill/项目文件。**

### ⑤ 台账回写
watchlist：`last_run = 本轮日期`；深读过的 repo 进已扫清单（附一句话结论）；待扫池保留。不回写 = 下轮重复劳动，视为本轮未完成。

## 四、无人值守模式（自动化定时调用）

判定：由定时/自动化任务唤起，或用户明说「不用等我 / 无人值守跑」。行为差异只有三条：

1. **不停**：任何确认点（初始化、反哺确认）都不等待——按 watchlist 默认值继续，待确认项写进报告「待拍板」区。
2. **不改**：只产出报告/情报库/任务清单三类文件，绝不修改自有 skill 与项目代码。
3. **可读**：报告开头 TL;DR（本轮看了什么、最有价值 ≤3 条发现、待拍板几条），让用户 30 秒扫完。

接入方式：用自动化定时任务（cron）创建，prompt 示例：「运行 OSS-Radar skill：按 `<工作区>/.spec/开源情报/watchlist.md` 增量采集，产出本轮报告并更新台账；无人值守模式，不等确认。」频率建议 1~2 周/轮——开源情报不需要日报，频了只稀释提炼质量。

## 五、铁律

1. **三元组完整**：无出处或无落点的发现不进报告、不进情报库。
2. **只采不改**：反哺改动只进任务清单，经确认由对应 skill 执行；本 skill 不动自有文件。
3. **配额自守**：单轮 search ≤ 5 次、深读 ≤ 6 repo；超限收敛本轮范围，不硬刷。
4. **台账必回写**：last_run 与已扫清单缺回写 = 本轮未完成。
5. **无人值守不停等**：缺配置写默认值继续，缺输入降级范围继续；唯一停机条件 = 网络全通道不可用（写进报告）。
6. **不搬版权物**：只摘观点/结构/判据，整段代码与文档不入库，用出处链接代替。

## 六、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 采集一堆 repo 只罗列不提炼 | 每个深读 repo 必须产出 ≥1 条三元组，或明确「无可借鉴」一句话结论 |
| 发现无落点（「人家做得真好」完事） | 建议落点必填到具体 skill/项目与位置 |
| 每轮从头扫老 repo | 靠台账增量：`pushed:>last_run` + 已扫清单排除 |
| search 限流即卡死 | 降级链：gh → 免认证 → WebSearch/web_reader；配额内收敛 |
| 无人值守时停下问问题 | 按默认继续，待确认项写报告「待拍板」区 |
| 把发现直接改进自有 skill | 只进任务清单，确认后交 Skill-Optimizer（模式③） |
| 整段搬运人家 README/代码进情报库 | 摘点 + 链接，片段 ≤ 10 行 |
| 报告流水账无 TL;DR | TL;DR 置顶，P0/P1 发现置顶 |

## 七、资源清单

- `references/github-api-playbook.md`：GitHub REST/Search 端点、限流数字、查询语法、增量与降级技巧——步骤①②执行时加载
- `assets/watchlist-template.md`：watchlist 初始化模板（含台账区）——⓪ 首次建清单时加载
- `assets/report-template.md`：本轮报告结构 + 发现/任务条目格式——④ 产出时加载
- 关联 skill：`Skill-Optimizer`（反哺执行方，交互模式确认后调用）；`Competitive-Analysis`（边界：产品/商业层归它）

## 八、运行问题埋点

本 skill 自身的问题（限流策略失效、提炼空转、watchlist 设计缺陷、误触发）按 Skill-Optimizer 约定上报 `../../issue/OSS-Radar/<日期>/<序号>-<标题>.md`（来源=埋点）。归因未明先留事实，按共享记录规则处理；不为经验提炼阻塞主流程。

## Contract Compatibility Layer

Use the common Gate contract: PASS requires no unresolved P0/P1; residual P0 is BLOCKED; residual P1 may only be an authorized CONDITIONAL with exceptionId, owner, dueAt, remediation, allowDownstream, and approvalRef. There is no force-pass rule.


> LEGACY BODY BOUNDARY: The preceding body, references, and assets are retained for capability compatibility. When any wording conflicts, the contracts in `../../shared/` and the sections below win.

## Purpose

Preserve the mature capability of `OSS-Radar` while exposing it through the v2 Skill contract.

## Trigger

Run when the user explicitly requests this capability or when the `workflow` orchestrator routes a compatible stage to this wrapper.

## Inputs

- the user's request and confirmed scope;
- current project artifacts, evidence, decisions, and `.spec/workflow.yaml`;
- the retained legacy body, references, assets, and scripts in this directory.

## Preconditions

- read `../../shared/skill-contract.md`, `../../shared/gate-policy.md`, and `../../shared/anti-deadloop.md`;
- read `.spec/manifest.yaml` and `.spec/workflow.yaml` when a project is available;
- verify scope, authorization, repository boundaries, and required upstream artifacts;
- do not overwrite unrelated or uncommitted files.

## Responsibilities

- execute the retained domain capability within its stated scope;
- translate legacy outputs into the current artifact, evidence, decision, and Gate vocabulary;
- record execution, traceability, residual issues, and the next action;
- route work outside this wrapper to the responsible domain Skill.

## Non-goals

- do not silently change product decisions, scope, or acceptance criteria;
- do not invent missing facts, evidence, approvals, or test results;
- do not use legacy Gate values or legacy state files as current truth;
- do not delete retained compatibility material.

## Procedure

1. Read the request, current state, manifest, and upstream handoff.
2. Load only the retained legacy resources needed for this execution.
3. Execute the domain action and keep assumptions separate from evidence.
4. Validate the output against its repair or acceptance criteria.
5. Register artifacts, evidence, decisions, and open items.
6. Write the execution record and `.spec/workflow.yaml`.
7. Emit exactly one Gate and one explicit next action.

## Outputs

- the domain artifact, report, code change, test evidence, or routed task defined by the retained capability;
- `artifactRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, `gate`, and `nextAction`;
- a failure route when the wrapper cannot complete safely.

## Evidence

Use direct source files, command output, test results, screenshots, dated external sources, or explicit user decisions. Label conclusions as `FACT`, `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, `RECOMMENDATION`, `DECISION`, or `OPEN`. A recommendation is not approval.

## Gate

Use only `PASS`, `CONDITIONAL`, or `BLOCKED`. `PASS` requires complete inputs and artifacts with no unresolved P0/P1. Residual P0 is always `BLOCKED`. Residual P1 is never `PASS` and may be `CONDITIONAL` only with `exceptionId`, `risk`, `owner`, `dueAt`, `remediation`, `allowDownstream`, and `approvalRef`. Three review rounds are the maximum; never force-pass or start an automatic fourth round.

## Failure Route

If evidence, authorization, scope, or an upstream Gate is missing, set `BLOCKED`, name the missing item and owner, and route to the responsible upstream Skill. If the issue is outside this wrapper's boundary, stop and route it rather than improvising.

## Downstream Contract

Downstream Skills may consume only manifest entries whose status and Gate allow downstream use. They must read `sourceRefs`, `evidenceRefs`, `decisionRefs`, `openItems`, and `nextAction`; they must not infer approval from chat context or file existence.

## State Changes

Record the old state, new state, actor, timestamp, reason, evidence references, Gate, and next action in `.spec/workflow.yaml`. The exact state names come from `governance/state-registry.yaml` in the source repository; an installed copy without that repository must use the state names already present in the project `.spec/workflow.yaml` and must not invent new states.
