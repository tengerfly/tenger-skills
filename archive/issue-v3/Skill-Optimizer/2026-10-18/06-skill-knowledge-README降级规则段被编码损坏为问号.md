# skill-knowledge/README 的「降级规则」整段在提交时被损坏为问号

> 归属 skill：`Skill-Optimizer`（体系文档/引用层） ｜ 日期：2026-10-18 ｜ 来源：体检

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P2 |
| 标签 | `术语文案` / `产物格式` |
| 优化状态 | 处理中（本轮已按上下文重建该节，待复核即可） |

## 现象

`skill-knowledge/README.md` 末尾「外部知识库的降级规则」整节（标题 + 正文）在提交 `a710c0c`（2026-09-21）写入时被破坏：标题与整段正文只剩 `?` 字符，实际语义（`SKILLS_KNOWLEDGE_ROOT` / `governance/knowledge-registry.yaml` / `warn-and-degrade` / `scripts/validate.ps1 -StrictKnowledge`）对读者不可见。

同批 `git show a710c0c -- skill-knowledge/README.md` 可见该 hunk 新增行本身就是问号，说明是写入通道/编码转换造成的损坏，不是后续被别人改坏。

## 跟踪与证据

- 发现：2026-10-18 本轮体系修复中做全仓编码扫描（Node 逐文件 UTF-8 解码 + 问号占比判据）
- 证据：`git show 61d7486:skill-knowledge/README.md` 无损坏（52 行）；`git show HEAD:...` 有 2 行损坏（原第 53/55 行）；`a710c0c` 的 diff 新增行即问号
- 全仓其余 300+ tracked 文本文件无同类损坏（含 yaml/py/ps1/sh/json）
- 影响：引用层 README 的关键降级口径不可读，后续 skill 引用只能靠猜或另找来源；不阻断执行器。
- 根因与归属：已确认——历史写入通道把中文段落编码成 `?`；与 `shared/dev-common.md` §四「源码写入通道与写后校验」属同一类问题（该规则是后补的）。
- 回退方式：按本节文字还原即可；如需原文可查 `61d7486` 版本（该节当时尚不存在）。

## 期望 vs 实际

- **期望**：引用层 README 的降级规则可读、与 `governance/knowledge-registry.yaml`（required: false / missingPolicy: warn-and-degrade）一致。
- **实际**：整段为问号，读者无法获得降级口径。

## 修复方向

1. 本轮：按仓库既有口径重建该节（warn-and-degrade；未取得资产时停止该项或经用户确认替代；`-StrictKnowledge` 严格模式）。
2. 防复发：沿用 `shared/dev-common.md` §四的写后校验（读回、非空、无 `?` 连片、无 U+FFFD）；后续新增写通道时接入同一检查。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 本轮进行中：skill-knowledge/README.md 重建「外部知识库的降级规则」 |
| 忽略理由 | — |