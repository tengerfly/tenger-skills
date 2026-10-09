# 跨 skill 引用在副本视图必断（分类层 + 大小写），并把两份共享约定提升进 shared/

> 归属 skill：仓库级（连带 `Skill-Optimizer` 资产归属变更）｜ 日期：2026-10-08 ｜ 来源：用户 + 体检

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P0 |
| 标签 | `接口契约` / `产物格式` / `边界不清` / `工具依赖` |
| 优化状态 | 已沉淀 |

## 现象

`UI-UX-Review` 七维体检收尾时顺带发现：skill 有两套目录布局——源仓「`<分类>/<Skill-Name>/`」两层，安装副本「`<skills 根>/<skill-id>/`」一层且目录名小写（`sync-skills.sh` 按 registry id 落名）。跨 skill 引用是按源仓写的，所以在副本视图：

| 类别 | 实测处数 | 含义 |
|---|---|---|
| 源仓可达、副本不可达 | 25 | **宿主今天就读不到**（含 12 个 SKILL.md 的埋点章节指向 Skill-Optimizer 两份约定） |
| 两视图都不可达 | 20 | 回退层数写错、分类层写错、tail 漏 `references/` 段 |
| 仅大小写不符 | 13 | Windows 可用，大小写敏感 FS 上全断 |
| 两视图大小写精确可达 | **0** | 一处都没有 |

放大到全仓：跨 skill 引用 58 处、带分类层的 43 处（含 6 处目录级路由被误写成相对路径）。

## 跟踪与证据

- 原问题 ID / 来源项目与版本：承接 `issue/UI-UX-Review/2026-10-08/01`（同一轮体检的连带发现）；无宿主报错，纯静态可达性实测
- 发现时间 / 相关步骤 / 脱敏证据：2026-10-08；两视图可达性脚本逐级比对目录实名（模拟区分大小写 FS），`checked=425  分类层=0  源仓不可达=0  副本不可达=0 RESULT: PASS` 为修复后状态
- 责任方 / 下一动作 / 修复判据：仓库级；判据 = `scripts/check-installed-refs.py` 三项归零并已接入 `scripts/validate-reference-integrity.ps1`
- 根因与归属：已确认——两个视图层数天然差一，任何单条 `../` 字符串不可能同时满足；仓内只有 `shared/` 配了三落点，故跨 skill 共享资产不放 `shared/` 就必然断
- 复核证据 / 未验证项：规则与门禁已落地；**副本实际内容需重新同步四端后才生效**（本轮已同步 Qoder 一次，早于本批改动）
- 回退方式：`git revert` 本批两个提交（`e287044` 目录小写化、本批 shared 提升），文件移动是 `git mv`，历史保留

## 期望 vs 实际

- **期望**：一条跨 skill 引用写出来，源仓与宿主副本都能解析；共享约定只有一个权威位置
- **实际**：引用按源仓写、副本按 id 扁平落名，两边互不成立且无人检测；两份被 16 个 skill 共用的约定（埋点规范、issue 模板）藏在单个 skill 私有目录里

## 修复方向

（本次已全部执行）

1. **统一到小写 id**：22 个 skill 目录 `git mv` 成 registry id，registry `path` 字段同步；`validate_core.py:93` 要求 frontmatter `name == id`、id 必须小写 kebab，副本目录本就小写 → 宿主侧零改动、零加载风险
2. **共享资产提升**：`Other/skill-optimizer/references/instrumentation-guide.md` → `shared/instrumentation-guide.md`；`Other/skill-optimizer/assets/issue-template.md` → `shared/templates/issue-template.md`；48 处引用按各文件到仓根层数重算，不留副本
3. **写法归一**：`shared/skill-contract.md` 新增 §1.4——只允许「`shared/` 相对路径」与「`<skill-id>/内部路径` 逻辑引用」两种形式，禁止带分类层的跨 skill 相对路径；6 处目录级路由提及改为 skill id
4. **门禁固化**：`scripts/check-installed-refs.py`（两视图可达性 + 禁用形式扫描，历史池与测试夹具豁免）接入 `validate-reference-integrity.ps1`；`scripts/rewrite-cross-refs.py` 留作按 registry 修错的工具
5. **不改写历史**：`issue/`、`bug-patterns/` 池内旧路径保持当时事实

## 双向落点

| 方向 | 目标 | 落点 |
|---|---|---|
| A · 防复发 | `shared/skill-contract.md` | §1.4 Cross-skill references（两种合法写法 + 禁止写法 + 归档池边界） |
| B · 检出力 | `scripts/` | `check-installed-refs.py` 门禁接入 `validate-reference-integrity.ps1`；`rewrite-cross-refs.py` 修复工具 |

## 沉淀记录

| 字段 | 值 |
|---|---|
| 沉淀目标 | 仓库级 + `Skill-Optimizer` |
| 沉淀位置 | `Other/Skill-Optimizer/CONTEXT.md` D-38；提交 `e287044`（目录小写化）与本批（shared 提升 + 门禁）；`docs/工程体系使用手册.md` 同步章节 |
| 忽略理由 | — |
