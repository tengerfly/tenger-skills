# ../../issue/Frontend-Dev/2026-09-16/02

| 字段 | 值 |
|---|---|
| 标题 | 用户澄清：正面案例须升级为进主流程的标准 SOP，非案例库被动参考 |
| 归属 skill | Frontend-Dev（元教训归 Skill-Optimizer） |
| 来源 | 用户 |
| 等级 | P1 |
| 标签 | 流程缺陷 |
| 状态 | 已沉淀 |

## 现象

issue 01 沉淀时把两页试做经验落在了 `case-library/`（按需加载的被动参考）。用户澄清本意：「将这种好的流程沉淀成一个标准的 SOP，后续开发都按照这个流程来，能提高质量」——期望是**每次开发默认执行**，案例库落点无法保证被读到。

## 期望 vs 实际

期望：流程成为 SKILL 主流程的强制步骤（Gate/REQUIRED），后续每页默认执行。
实际：playbook 只躺在案例库索引里，主流程无任何引用点，是否遵循取决于模型当次是否想起。

## 修复方向（已执行）

1. SKILL.md 主流程四处强制引用：S1 输入瘦身（REQUIRED）+ 口径表查表、S7 视图模型先行（Ext 扩展+留痕）、§4.7 验收脚本化执行（项目有脚本则 REQUIRED 先跑）、新增 §4.9 口径冲突与口径表；错误对照表加 3 行（口径反复考证 / 绕过脚本手动怼 / 契约缺口静默造字段）；§六资源清单标注 playbook 为 SOP。
2. playbook 头部标注「标准 SOP，主流程强制引用」；案例库索引「何时读」改为「必按此执行」。
3. 元教训落 Skill-Optimizer：沉淀落点分层规则（§七-6）+ ../../issue/Skill-Optimizer/2026-09-16/01。

## 沉淀目标/位置

- `../Frontend-Dev/SKILL.md`（S1/S7/§4.7/§4.9/错误表/§六）
- `../Frontend-Dev/references/case-library/static-page-trial-playbook.md`（头部 SOP 状态）
- `../Frontend-Dev/references/case-library/00-README.md`（索引行）
- `../Frontend-Dev/CONTEXT.md` D-18
- `../../Other/Skill-Optimizer/SKILL.md` §七-6（落点分层）、`../../Other/Skill-Optimizer/CONTEXT.md` D-32
