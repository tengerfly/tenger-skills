---
name: Skill-Optimizer
description: Skill 元优化器（长期迭代）。记录 skill 问题、从聊天记录挖掘优化点、按八维优化/精简 skill、对 skill 做七维自洽体检、从 bug-patterns/ 池提炼错误模式反哺方案/开发 skill。触发：记问题/复盘/挖掘聊天/优化/精简/迭代/体检某 skill、检查自洽一致性、错误池提炼/反哺、沉淀 bug 模式到方案开发。
compatibility: Claude Code / Agent SDK / OpenCode
---

# Skill-Optimizer（Skill 元优化器）

> 定位：本仓库各专业 Skill 的运维 + 迭代器。只做四件事——记录、挖掘、优化、体检。评审闭环管「这一次交付物」，本 skill 管「每一次都犯的方法论问题」。

## 一、模型：双问题池 + 四个模式

| 模式 | 触发 | 做什么 | 产物 |
|---|---|---|---|
| ① 记录 | 记问题/复盘运行 | 问题写入 issue 池 | `issue/<skill>/<日期>/<序号>.md` |
| ② 挖掘 | 提供 chats/ 或粘贴聊天 | 提取优化点 | 提取清单 → 确认后落 issue |
| ③ 优化 | 优化/精简/迭代 XX | 按八维优化并沉淀；含从 bug-patterns/ 提炼防复发规则 | SKILL.md / references / CONTEXT 改动 |
| ④ 体检 | 体检/检查 XX 自洽 | 七维自洽体检 | 问题清单 → 用户逐条裁决 |

**标准先行**：每模式有固定标准——记录 `assets/issue-template.md`、挖掘 `assets/signal-checklist.md`、优化 `assets/optimize-checklist.md`、体检 `assets/self-audit-checklist.md`，编写规范 `assets/skill-writing-standard.md`。执行严格按标准，不凭感觉。

**自我指涉**：本 skill 自身也是优化对象，问题（含六份标准的问题）记 `issue/Skill-Optimizer/`；**先优化自己（先修标准再干活），再优化其他 skill**。

## 二、双问题池

**问题池（skill 自身方法论问题，`issue/`）**——记录 skill 怎么干活的问题，消费方 = 本 skill 模式③ 优化 skill 自身：

- 路径 `issue/`，结构 `issue/<skill>/<日期目录>/<序号>-<标题>.md`，序号当日从 01 递增。
- 每文件字段：标题、归属 skill、来源（埋点/挖掘/体检/用户）、等级（P0/P1/P2）、标签（10 枚举）、现象、期望 vs 实际、修复方向、状态（待处理/处理中/已沉淀/已忽略）、沉淀目标/位置（已沉淀必填）。

| 等级 | 含义 |
|---|---|
| P0 | 方法论硬伤/每次必犯/阻塞 |
| P1 | 明显影响/高频 |
| P2 | 轻微/建议 |

标签：触发识别、流程缺陷、边界不清、术语文案、产物格式、接口契约、工具依赖、性能体积、正面参考、反面参考。

状态机：待处理 → 处理中 → 已沉淀（填沉淀目标+位置）或已忽略。

**错误模式池（真实 bug 错误模式，`bug-patterns/`）**——记录各被修项目暴露的「会再犯的一类错 + 防复发规则」，消费方 = 方案/开发 skill（经本 skill 模式③ 提炼）：

- 写入方：Bug-Fix 收尾沉淀（有预防价值才沉，用户确认后落池），各项目修复都直接写入本池。
- **位置 = 本 skill 源仓库根集中池**：`D:\project\agent-project\tenger-skills\bug-patterns\<日期>\<序号>-<标题>.md`——池只此一处，用户在本仓库即可统一提炼，无需去各项目拉取。模板见 `Bug-Fix/assets/pattern-card-template.md`，状态 `待提炼 → 已提炼/已忽略`。
- 分工：问题出在「skill 怎么干活」→ `issue/`；问题出在「写出的代码/方案有哪类坑」→ `bug-patterns/`。池规则详见 `bug-patterns/README.md`。

## 三、模式① 记录

1. 定位目标 skill（未点名先确认）。
2. 提炼：现象、期望 vs 实际、等级、标签、修复方向。
3. 写 issue 文件。
4. 向用户确认等级/标签/归属。

## 四、模式② 挖掘

1. 输入：读 `chats/`（.md/.txt/.json/.html）或用户粘贴。
2. 扫信号：负面（不对/重来/怎么又/别乱发挥/反复返工/纠正/质疑）、正面（好/就这样/思路对/以后都这样）、返工循环、触发痕迹（哪个 skill 被调起、产出、断在哪步）。
3. 提炼：信号聚合 → 现象 + 期望 vs 实际 + 归属 + 等级 + 标签 + 修复方向。
4. **确认后才落盘**。
5. 写入 `issue/<skill>/<日期>/`。

## 五、模式③ 优化

顺序：先优化 Skill-Optimizer 自己（含标准）→ 再优化目标 skill。

八维核验（判据：维度二~六 skill-writing-standard、维度八 vibe-principles-mapping）：
① 问题修复——读目标 issue 待处理/处理中逐条修；
② 触发精准——description 覆盖 what + when 与动词/场景/同义表达；**含量化 eval**：生成触发样本（该触发/不该触发/边界）→ 盲测 → 假阳/假阴分析 → ≤5 轮迭代调优；
③ 上下文体积——SKILL.md ≤ 500 行硬红线，长内容下沉 references，可执行代码进 scripts；L1~L4 四级加载见编写规范 §二；
④ 指令写法——问题引导、禁令清单、铁律/Red Flag；
⑤ 流程稳定——BLOCKING/REQUIRED 标记、Gate、交付检查、参数系统；
⑥ 简洁不落俗——删 AI 味套话、冗余；
⑦ 术语一致——对照 CONTEXT.md；
⑧ 心法注入——对照 vibe-principles-mapping 落到执行层。

流程：
1. 读目标 issue 列待修问题；
2. 按 optimize-checklist 八维核验；
3. 只动有依据处；
4. **old-vs-new 能力审计**：改动前记录目标 skill 能力清单，改动后对比——确认无「丢功能 / 引入未声明行为 / 声称支持却没实现」，每项变更可追溯到 issue/核验发现；
5. 在目标 skill 的 CONTEXT.md 追加 D-xx（改了什么、依据哪条 issue）；
6. 回填 issue 状态：解决 → `已沉淀` + 沉淀目标/位置；不处理 → `已忽略` + 理由。

### 模式③-附加：错误模式池提炼（目标 = 方案/开发 skill）

优化对象为方案/开发 skill，或用户点名「提炼 bug-patterns」时，读本仓库集中池 `bug-patterns/` 中 `待提炼` 案例，翻译成目标 skill 的防复发规则：

1. 读 `bug-patterns/` 待提炼案例（本仓库根，一处即可），按受益 skill 归类，清单交用户确认（提炼哪几条、落哪层）。
2. 按**层级升级**落点：目标 skill「常见错误对照表」加行 → 高频/跨案例模式沉淀 references 防复发清单（如 `frontend-error-patterns-guide.md`，命名对齐该 skill 惯例）→ 重大模式进方案 skill 的 Gate/预检项。
3. 提炼=给目标 skill 加「可执行的防复发检查项」，不是贴案例（案例卡仍在池里可溯源）；粒度=一类问题。
4. 改后在目标 skill CONTEXT.md 记 D-xx；回填案例卡状态 `已提炼`（落点 + 位置）；不提炼 → `已忽略` + 理由。

## 六、模式④ 体检

按 `assets/self-audit-checklist.md` 七维：
① 术语/命名一致（同指异名、与 CONTEXT 冲突、旧术语残留）；
② 逻辑闭环（悬空引用、断头、Gate 未落地、枚举数量前后不一致）；
③ 文句质量（病句、错别字、占位符未替换）；
④ 声明-流程一致（声明的依赖/前置有对应检测→阻塞→报错步骤）；
⑤ 跨位置同步（关键事实/编号/引用多文件 grep 比对）；
⑥ 简洁不落俗；
⑦ 安全审计（危险指令/硬编码凭据/依赖/外联风险，带脚本的 skill 重点查）。

范围（默认）：目标 skill 全套文件 + 全仓交叉引用（根 README/Workflow/其他 skill/issue）。

流程：定位 → 按七维机械 grep + AI 通读 → 问题清单（等级+位置+现象+修复方向+判据）→ **逐条交用户裁决**（当场修→记 D-xx；记 issue→来源填体检；忽略→说明）→ 小结确认。

## 七、沉淀约定（全局强约束）

1. **粒度 = 一类问题**：沉淀类别级通用判据/检查项/防复发规则，不是单点案例；单点只作附注。自问能否防「这一类」再犯。
2. **落点 = 先 tenger-skills 源仓库，再同步 CodeBuddy 副本**：任何沉淀先写 `D:\project\agent-project\tenger-skills`；同步到 `C:\Users\15136\.codebuddy\skills\` 同名文件，用哈希校验。`issue/` 与 `bug-patterns/` 双池都在源仓库根（集中池），不外发部署（部署副本只含 skill 文件，不含数据池）。

## 八、铁律

1. **标准先行**：先加载对应标准逐项执行；标准缺失/有问题先修标准。
2. **改动有依据**：每个改动可追溯一条 issue 或核验发现，不凭空重构。
3. **先己后人**：先优化 Skill-Optimizer 自己（含标准）。
4. **沉淀留痕**：每次改动在目标 skill CONTEXT.md 记 D-xx。
5. **字段必填**：等级、标签、状态三字段。
6. **确认后落盘**：挖掘清单未经用户确认不落盘。
7. **零加戏**：只处理确认过的问题与发现，不擅自重写风格/增删功能。

## 九、常见错误对照表

| 错误 | 纠正 |
|---|---|
| 凭感觉大改无依据 | 每个改动回溯 issue/体检发现 |
| 跳过自优化 | 先优化自己 |
| 不写决策日志 | 追加 D-xx |
| 挖掘未确认就落盘 | 先列清单确认 |
| 问题缺三字段 | 必填 |
| 已沉淀不填目标/位置 | 必须可追溯 |
| 体检只口头说 | 按七维出清单，每条带位置/方向/判据 |
| 当场修没记 D-x | 留痕 |
| 改完不同步检查 | 旧词/编号/术语全仓清零 |
| 提炼把案例整段贴进 skill | 只提炼可执行防复发规则，案例留 bug-patterns 池 |
| 提炼无用户确认 | 先列清单（哪几条、落哪层）确认 |
| 提炼后不回填案例卡 | 状态 `已提炼` + 落点/位置 |
| 错把 bug-patterns 当 issue | 归 skill 自身问题走 issue/；归代码坑走 bug-patterns/ |

## 十、资源清单

- `assets/issue-template.md`、`signal-checklist.md`、`skill-writing-standard.md`、`vibe-principles-mapping.md`、`optimize-checklist.md`、`self-audit-checklist.md`
- `references/instrumentation-guide.md`
- `issue/`：skill 自身问题池（源仓库根）；`bug-patterns/`：错误模式集中池（源仓库根，池规则 `bug-patterns/README.md`、案例卡模板 `Bug-Fix/assets/pattern-card-template.md`）；`chats/`：待挖掘目录

## 十一、运行问题埋点

收尾按 `references/instrumentation-guide.md` 自查上报 `issue/Skill-Optimizer/<日期>/<序号>-<标题>.md`（来源=埋点；字段/等级/标签按其规范，模板 `assets/issue-template.md`）。不确定不记，不打断主流程。