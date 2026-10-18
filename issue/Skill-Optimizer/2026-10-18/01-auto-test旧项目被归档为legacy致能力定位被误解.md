# auto-test 旧独立项目被归档为 legacy，活跃能力定位被误解

> 归属 skill：`Skill-Optimizer`（体系结构/能力定位；涉及 `auto-test`） ｜ 日期：2026-10-18 ｜ 来源：用户

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P1 |
| 标签 | `术语文案` / `流程缺陷` |
| 优化状态 | 处理中（本轮已并入 Test/auto-test/project 并移除 legacy 命名，待用户复看确认） |

> 定级理由：用户因此直接质疑「auto-test 被改成了 legacy」，并要求「把整个体系全部修复」。能力仍在，但对外呈现把「旧独立项目归档」说成了「auto-test 本身变成 legacy」，会让用户与后续执行者误判主能力状态。

## 现象

- 2026-10-18 会话中，用户指令是「tenger-skills 里边很多乱的 删除冗余的文件 然后把 auto-test 也移入到 tenger-skills 文件夹下」。
- 该会话把旧独立项目 `D:/project/agent-project/auto-test` 整体归档到 `docs/auto-test-legacy/`，提交信息写「归档旧 auto-test 项目到 docs/auto-test-legacy」，归档 README 写「被本仓 Test/auto-test/ 取代」「只读参考，不参与 skill 注册与校验」。
- 活跃能力实际一直是 `Test/auto-test/`（SKILL.md 18.9KB，比旧骨架 11.4KB 更全）；旧目录里真正独有的只是：企业级 AI 自动化测试平台项目计划（v0.1 待评审）、竞品分析、旧问题日志、旧 skill 骨架。
- 2026-10-18 22:57 用户追问「auto-test 你给改成了 auto-test-legacy 是怎么回事」，要求整个体系修复、可直接在其他地方使用。

## 跟踪与证据

- 原问题 ID / 来源：新增；关联上一会话第 3 轮与提交 `b0b78b6`
- 发现时间 / 相关步骤：2026-10-18 22:57 用户会话开场
- 证据：
  - `git show --stat b0b78b6` 显示只新增 docs/auto-test-legacy/**，未改动 Test/auto-test/
  - `docs/auto-test-legacy/README-legacy.md`：「被本仓 Test/auto-test/（更新、更完整）取代」「只读参考，不参与 skill 注册与校验」
  - `governance/skill-registry.yaml` 中 auto-test（path=Test/auto-test，status=active）自始未变
- 责任方 / 下一动作 / 修复判据：旧项目资料作为 auto-test 体系一部分并入 `Test/auto-test/project/`，删除 legacy 目录与旧 skill 骨架；判据 = 仓内不再有 auto-test-legacy 命名，README/手册把「活跃技能 = Test/auto-test」与「project/ = 平台项目研究资料」分开说清，用户复看不再误解。
- 根因与归属：已确认——归档用了 legacy 标签，且交付说明没有把「旧独立项目归档」与「活跃技能未变」分开说清；本质是项目研究资料与可执行 Skill 混为一谈。
- 复核证据 / 未验证项：待本轮合并完成后回读目录与文档；用户侧确认未做。
- 回退方式：git revert 本轮提交即可恢复 docs/auto-test-legacy（旧 skill 骨架在 git 历史中）。

## 期望 vs 实际

- **期望**：用户说「把 auto-test 移入 tenger-skills」时，得到的是 auto-test 作为体系一部分（活跃技能 + 项目研究资料各归其位），没有「auto-test 被降级成 legacy」的对外呈现。
- **实际**：唯一可见的新目录叫 docs/auto-test-legacy，并被描述为「只读、不参与注册与校验」，与用户意图相反。

## 修复方向

1. 旧项目独有的计划/竞品分析/问题日志迁入 `Test/auto-test/project/`，配 README 说明来源、状态（平台计划待评审）与「执行入口是 ../SKILL.md」。
2. 删除 `docs/auto-test-legacy/`（含旧 skill 骨架；git 历史可追溯），全仓清除 legacy 命名。
3. `Test/auto-test/README.md` / `CONTEXT.md` 记 D-02；`Test/README.md` 同步真实状态（Testing 已归档、非备用入口）。
4. 使用手册/README 补「auto-test 体系组成」与「可直接安装到其他宿主/机器」的路径。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 本轮进行中：Test/auto-test/project/、Test/auto-test/CONTEXT.md D-02、Test/README.md |
| 忽略理由 | — |