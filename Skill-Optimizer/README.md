# Skill-Optimizer —— Skill 元优化器

> 让 skill 越用越贴合你的需求：记录问题 → 挖掘优化点 → 自洽体检 → 全方位优化沉淀。长期迭代，不参与任何业务交付。

## 这是什么

本仓库各专业 Skill 的「运维 + 迭代器」，独立于 Workflow 链之外，任何时刻可触发。四个模式：

| 模式 | 触发说法 | 干什么 | 产物 |
|---|---|---|---|
| ① 记录（兜底） | 「记个问题」「这个 skill 哪里不好」「复盘这次运行」 | 把问题写入 issue 池 | `issue/<skill>/<日期>/xx.md` |
| ② 挖掘 | 丢聊天记录进 `chats/`（或直接粘贴） | 从记录提取优化点，确认后落 issue | 提取清单 → issue |
| ③ 优化 | 「优化 XX」「精简 XX」「迭代 XX skill」 | 读 issue 做全方位优化 | 各 skill 的 SKILL.md / references / CONTEXT.md |
| ④ 体检 | 「体检 / 检查 XX skill」「XX 自洽吗 / 前后一致吗」 | 六维自洽体检，出问题清单 | 问题清单 → 用户逐条裁决（当场修 / 记 issue / 忽略） |

## 核心机制

### 标准先行（流程固定）

每个模式都有固定标准，执行严格按标准逐项走，保证每次流程一致：

| 模式 | 标准 |
|---|---|
| 记录 | `assets/issue-template.md`（问题字段） |
| 挖掘 | `assets/signal-checklist.md`（四类信号） |
| 优化 | `assets/optimize-checklist.md`（八维度核验） |
| 体检 | `assets/self-audit-checklist.md`（六维自洽检查） |

**标准本身也可被优化**：标准有问题 → 记到 `issue/Skill-Optimizer/` → 优化时先修标准，再用修订后的标准干活。

### 问题池（issue/）

`issue/<skill名称>/<日期目录>/<问题文件>`，唯一事实源。主通道是各 skill 埋点自查上报（规则见 `references/instrumentation-guide.md`），元技能兜底补记。

问题字段：等级 `P0/P1/P2`（与 Testing / Code-Review 同口径）+ 10 个预定义标签 + 优化状态。

### 优化状态机

`待处理 → 处理中 → 已沉淀 / 已忽略`；「已沉淀」强制填沉淀目标 + 沉淀位置（文件 / 决策号 D-xx），让「问题 → 改进」双向可追溯。

### 全方位优化（八维度）

1. **问题修复**：读 issue 池「待处理」项逐条修；
2. **入口·触发精准**：description 覆盖 what + when 与动词/场景/同义表达；
3. **省·上下文体积**：SKILL.md ≤ 500 行硬红线、下沉 references、scripts 封装、assets 不加载；
4. **准·指令写法**：问题引导注意力 + 禁令清单 + 铁律/Red Flag；
5. **稳·流程稳定**：工作流清单 BLOCKING/REQUIRED + 确认节点 + 交付清单 + 参数系统；
6. **简洁不落俗**：反 AI 味套话、删冗余措辞；
7. **术语一致**：与 CONTEXT.md 术语表对齐；
8. **心法注入**：把《Vibe Coding 高效能秘籍》心法落到 skill 执行层（做减法 / 决策规划分离 / review 独立性 / 验收标准前置 / 派活四件套 / 苏格拉底反问 / 自动化兜底）。

维度二~六的判据来源 = `assets/skill-writing-standard.md`（编写规范）；维度八判据来源 = `assets/vibe-principles-mapping.md`（心法映射表）。

### 自我指涉

Skill-Optimizer 自身也进 issue 池可自优化；**优化顺序永远是先优化自己（含先修订标准），再优化其他 skill**。

## 目录结构

```
Skill-Optimizer/
├── SKILL.md                       # 主指令（四模式 + 字段 + 状态机 + 铁律）
├── CONTEXT.md                     # 术语对齐 + 决策日志
├── README.md                      # 本文件
├── assets/                        # 六份标准（4 模式标准 + 1 编写规范 + 1 心法映射）
│   ├── issue-template.md          # 记录模式：问题文件模板
│   ├── signal-checklist.md        # 挖掘模式：信号识别清单
│   ├── optimize-checklist.md      # 优化模式：全方位核验清单（八维）
│   ├── self-audit-checklist.md    # 体检模式：自洽检查清单（六维）
│   ├── skill-writing-standard.md  # 编写规范：优化维度二~六判据来源
│   └── vibe-principles-mapping.md # 心法映射：优化维度八判据来源
└── references/
    └── instrumentation-guide.md   # 埋点规范（各 skill 自查上报规则）

issue/                             # 问题池（仓库根，唯一事实源）
chats/                             # 待挖掘的聊天记录（仓库根）
```

## 快速上手

- **记个问题**：对它说「记个问题：PRD-Design 老是漏问入口」；
- **挖掘记录**：把聊天记录丢进 `chats/`，说「挖掘 chats/ 里的优化点」，提取清单经你确认后落 issue；
- **优化 skill**：说「优化 PRD-Design」，它先自检（含修订标准），再读 issue 做八维度核验，改动留痕到目标 skill 的 CONTEXT.md 决策日志并回填 issue 状态。
- **体检 skill**：说「体检 PRD-Design」或「检查 PRD-Design 自洽性」，它对 skill 全套文件 + 全仓交叉引用做六维自洽体检，产出问题清单后逐条经你裁决（当场修 / 记 issue / 忽略）。
