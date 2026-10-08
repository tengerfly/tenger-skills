# Essence-Distill 设计上下文

## 为什么造（2026-09-20）

用户读的书、GitHub 仓库、学习材料越来越多，缺一个「压强器」：全文摘要平均用力留不下精华，书摘金句有句无观点，AI 直接总结又容易脑补且不可回查。需要一个 skill：把材料里的精华蒸馏成**高密度、条条可溯源**的文档——每条能回原文、AI 的引申单独标注、丢弃显式留痕。

注意：用户口中的「蒸馏」**不是 ML 训练数据蒸馏**，是内容精华提取。

## 用户原始诉求（2026-09-20）

1. 「写一个蒸馏数据的 skill……不是说蒸馏数据，而是给一本书、一个 GitHub 仓库、一份学习资料等，把里边的精华内容蒸馏出来」
2. 先去 GitHub 调研已有同类 skill，再沉淀我们的（调研记录见下）

## GitHub 同类 skill 调研（2026-09-20，各取所长）

| 来源 | 做法 | 采纳点 |
|---|---|---|
| [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill)（书/长视频/播客 → 可执行 Agent Skills，v2.5） | 「书」泛指一切长内容；无文本凭记忆蒸馏=禁止；三重验证（来源充分性/可执行性/任务增益）；覆盖率硬门（关键任务清单逐条给去向，不虚报零遗漏）；rejected/ 审计留痕；断点续跑 | 无文本不蒸馏、三道筛、覆盖率自查、丢弃留痕 |
| [JuneYaooo/lineage-skill](https://github.com/JuneYaooo/lineage-skill)（视频/PDF/转写 → source-backed 学习 skill） | 出处七分类（direct_source / source_grounded_synthesis / mentor_inference / unsupported…）；「Preserve evidence before synthesis」；冲突原文保留各自条件，never flatten disagreement | 推断/原文区隔、冲突并存铁律 |
| obsidian-second-brain 的 `/obsidian-distill` | 「压缩≠摘要」；编号可引用块 B1/B2…；每条关键主张带 `(src: B3)`；不可追溯的断言不收录且**显式报告丢弃** | B 块锚点体系、丢弃台账 |
| [jwynia/agent-skills](https://github.com/jwynia/agent-skills) 的 summarization | 「summarize 有很多种」——按目的/受众/场景选形态 | 三档位（速览/学习/行动） |
| Actionable Book Summarizer（Claude Code skill） | 把书蒸馏成 50~100 条高影响**可执行**忠告 | 行动档「每条带怎么用」 |
| arXiv《Repo-To-Skill》 | 仓库材料蒸馏进上下文预算 | 「压缩比/密度优先」意识 |

未采纳：cangjie 的「蒸馏成可执行 Agent Skill」产物形态（用户要的是精华**内容**，且 skill-factory 是另一条重产线，边界写进 SKILL 铁律 10）；lineage 的学习者状态/教练闭环（属教学产品，非本 skill 范围）。

## 关键决策

| 决策 | 理由 |
|---|---|
| 产物 = 精华文档，不做可执行 skill 输出 | 用户诉求是「精华内容」；skill-factory 另有成熟外部方案（cangjie-skill），混进来体积失控 |
| 三档位按目的选，默认学习档 | jwynia：目的决定形态；「帮我蒸馏」九成是想真掌握 |
| 每条精华 = 主张+展开+锚点+边界（+行动）的固定卡格式 | 「锚点」承接全仓「证据先于断言」血统；「边界」防把有条件的话抄成无条件真理 |
| 三道筛 V1 可溯源 / V2 含金量 / V3 属于原文 | 分别挡「不可回查」「正确废话」「AI 脑补」三大病 |
| 覆盖率自查用「关键问题清单」而非「章节清单」 | 蒸馏按读者目的裁剪，不是按作者目录搬运；「材料未回答」也是合法结论 |
| 丢弃台账 + 推断区作为附录三件套强制件 | obsidian/lineage 实证：静默丢弃和推断混写是蒸馏品两大信任杀手 |
| B 块锚点作为无页码文本的兜底体系 | 转写/长文没有页码行号，B 块编号是最小可用锚点 |
| 仓库类与 Source-Reading 分工：思想/决策/最佳实践 vs 逐行实现走读 | 同一仓库两种学习诉求都成立，互不替代；克隆 playbook 直接复用不重写 |
| 压缩比写进交付头部 | 密度可审计，防「蒸馏比原文还长」 |

## 与既有 skill 的关系

- **Source-Reading**：仓库输入的分工（见上）；本 skill 复用其 `references/clone-playbook.md`。
- **Fact-Check**：辨外部说法真假归它；本 skill 只保证「忠于原文」，原文本身是错的 → 在精华卡「适用边界」标注存疑即可，不越权核伪。
- **OSS-Radar / Competitive-Analysis / Skill-Optimizer**：借实践反哺 / 产品竞调 / 问题埋点，边界同 Source-Reading 约定。

## 待观察点（首跑后回填）

- 三档位行数红线（60/400）是否合手感
- B 块 200~500 字粒度是否合适
- 锚点抽验 ≥3 条的比例是否足以兜住漂移
- 「关键问题清单」由 AI 单方拟定是否够准（要不要用户确认）

## 决策日志

| # | 日期 | 决策 | 来源 | 状态 |
|---|---|---|---|---|
| D-01 | 09-20 | 创建 Essence-Distill v0.1：七步流程 + 三档位 + 三道筛 + 附录三件套；产物为精华文档（非可执行 skill） | 用户诉求 + GitHub 六源调研（本文件） | ✅ |
