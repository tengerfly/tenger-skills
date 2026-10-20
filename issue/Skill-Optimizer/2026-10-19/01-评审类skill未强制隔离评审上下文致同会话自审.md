# 评审类 Skill 未强制隔离评审上下文，产出会话可自审（P0）

> 归属 skill：`Skill-Optimizer`（体系规则；逐 Skill 落点见修复方向） ｜ 日期：2026-10-19 ｜ 来源：用户

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P0 |
| 标签 | `流程缺陷` / `工具依赖` |
| 优化状态 | 处理中（规则、模板、7 个 Skill 与编排层已改；行为层 fresh 派发验证待跑） |

## 现象

- 用户指出：PRD 审核、UI 审核、代码审核等评审类 Skill，可能在产出该产物的同一会话里直接评审，未隔离上下文。
- 实际盘点（2026-10-19 改前）：
  - `DEV/code-review/SKILL.md:81`、`DEV/tech-review/SKILL.md:67` 只写「独立上下文（subagent / 新会话）」「条件允许可用不同模型交叉审查」——是可选项，不是硬性前置；同会话自审没有阻断。
  - `PRD/prd-review/SKILL.md`、`UI/prototype-review/SKILL.md`、`UI/ui-ux-review/SKILL.md`、`UI/fidelity-review/SKILL.md`、`Other/quality-inspection/SKILL.md` 正文没有评审者必须隔离的要求。
  - `workflow`、`prd-workflow` 可直接在产出会话内调度评审，无派发/隔离证据要求。
- 后果：评审者拿到整个会话与生成过程，被产出者的推理路径锚定；「自查」被当成「独立评审」，评审退化成确认（依据：`docs/vibe-coding-学习笔记.md:105,666`；`docs/对比-Superpowers与本体系统.md` §2③ 明确记录本仓无评审包/上下文隔离）。

## 跟踪与证据

- 原问题 ID / 来源项目与版本：本仓直接建 issue，路径即稳定标识。
- 发现时间 / 相关步骤：2026-10-19，用户直接提出；涉及所有评审类 Skill 的入口与 Procedure。
- 责任方 / 下一动作 / 修复判据：见「修复方向」。
- 根因与归属：已确认——评审独立性只有「立场隔离」口号，没有「执行上下文隔离」的硬性规则、派发计划和报告证据字段；宿主能力差异被用来默认降级为同上下文自审。
- 复核证据 / 未验证项：结构层 `skill-contract` / `refs` 校验通过；独立 fresh 验收（`.spec/体系评审/2026-10-19/评审上下文隔离改造-独立验收.md`）结论「结构层 PASS」，原 P1 F-01 已闭环；真实项目 fresh 子代理派发与「产出上下文不自审」行为验证未跑。
- 回退方式：回退本轮涉及的 `shared/review-context-isolation.md`、`shared/templates/review-package.md`、报告模板 §0.5、7 个评审/审计 Skill 的隔离节与派发计划、`workflow` / `prd-workflow` 的 REQUIRED 段；保留 issue 事实。

## 期望 vs 实际

- **期望**：评审判断只由未参与产出/修订/自检的隔离上下文（fresh 子代理首选，新会话次选）作出；评审者只拿评审包；每评审单元独立子代理、汇总独立；报告记录隔离证据；无隔离能力 ⇒ BLOCKED，不得同会话自审。
- **实际**：见「现象」；code-review / tech-review 的「独立上下文」是可选项，其余 Skill 无要求；workflow 无派发强制。

## 修复方向

1. **公共契约**：新增 `shared/review-context-isolation.md`（适用范围、铁律、评审包、L1 子代理 / L2 新会话 / L3 BLOCKED、常见派发计划、报告 §0.5、反模式）；新增 `shared/templates/review-package.md`。
2. **报告硬性位**：`shared/templates/review-summary-template.md` 与 `review-dimension-template.md` 加 §0.5「评审上下文隔离记录」；缺记录 / `producedByContextInvolved` 非 false ⇒ Gate 只能 BLOCKED。
3. **7 个评审/审计 Skill**：`prd-review`、`prototype-review`、`ui-ux-review`、`fidelity-review`、`tech-review`、`code-review`、`quality-inspection` 正文加隔离节 + 派发计划 + Procedure REQUIRED + 错误表行；本地报告模板加 §0.5；CONTEXT 记 D-xx。
4. **编排层**：`workflow/SKILL.md` §4 与 `PRD/prd-workflow/SKILL.md` 步骤 7/8 加 REQUIRED 派发；`Test/auto-test/SKILL.md` L2 内嵌 Fidelity-Review 改为派发独立评审子代理；`UI/ui-ux-design` 内部门禁声明「自查 ≠ 独立评审」。
5. **文档**：`docs/对比-Superpowers与本体系统.md` §2③/§3/§5/§6.2 标注决策修订（评审隔离优先于宿主无关；无子代理走新会话，均无才 BLOCKED）。
6. **验收判据**：① 7 个 Skill 均有隔离节与派发计划；② grep「条件允许可用不同模型」「独立上下文（subagent / 新会话）」等可选措辞，改为硬性或清零；③ workflow / prd-workflow 有 REQUIRED；④ summary/dimension/inspection 模板含 §0.5；⑤ `python scripts/validate_core.py skill-contract --project-root .` 与 `python scripts/check-installed-refs.py --project-root . --quiet` 通过；⑥ 行为层 fresh-agent 场景（产出上下文调评审 → 必须先派发）待跑。

## 双向落点（来源 = 评审闭环时必填）

| 方向 | 目标 skill | 落点 |
|---|---|---|
| A · 防复发 | `workflow` / `prd-workflow` / 产出方 Skill（prd-design、prototype-design、ui-ux-design、backend-dev、frontend-dev） | 编排层 REQUIRED 派发；产出方明确「自查 ≠ 独立评审」，不得自证通过 |
| B · 检出力 | `Skill-Optimizer` | `references/known-issue-patterns.md` 加「评审自审（reviewer = producer）」模式，含检出方法（比对报告 §0.5、执行 actor、包摘要） |

> 规则见仓库根 `shared/anti-deadloop.md` §4；P0 必须双向沉淀。本轮 B 方向已落一条模式，A 方向落编排层与产出方说明。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | `shared/review-context-isolation.md` + 7 个评审/审计 Skill + `workflow` / `prd-workflow` |
| 沉淀位置 | 各 Skill 隔离节 / Procedure / 报告模板 §0.5 / CONTEXT D-xx；清单见「修复方向」 |
| 忽略理由 | — |
