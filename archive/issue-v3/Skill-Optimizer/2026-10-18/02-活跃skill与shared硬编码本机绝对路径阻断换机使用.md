# 活跃 skill 与 shared 硬编码本机绝对路径，换机/换宿主即失效

> 归属 skill：`Skill-Optimizer`（体系可移植性；涉及 Skill-Optimizer / Skill-Evolver / Bug-Fix / OSS-Radar / Backend-Dev / Backend-Tech-Design / Frontend-Dev / Frontend-Tech-Design / Code-Review 与 shared/browser-policy.md） ｜ 日期：2026-10-18 ｜ 来源：体检

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P1 |
| 标签 | `工具依赖` / `边界不清` |
| 优化状态 | 处理中（本轮改相对路径/环境变量，待换机实测） |

> 定级理由：用户目标「直接在其他地方直接使用」被这批路径直接阻断——换机器、换用户名、克隆到别的磁盘后，skill 正文里的池路径、同步命令、外部知识库路径全部指向不存在的位置。

## 现象

全仓扫描活跃执行文件（SKILL.md / references / assets / shared）发现 20+ 处本机绝对路径，典型：

- `Other/skill-optimizer/SKILL.md`：bug-patterns 池 = `D:/project/agent-project/tenger-skills/bug-patterns/...`
- `Other/bug-fix/SKILL.md`：「集中沉淀池（写死，勿改）：D:/project/...」
- `Other/skill-evolver/SKILL.md`：`D:/project/.../evolution/`；安装副本同步写 `C:/Users/15136/.codebuddy/skills/Skill-Evolver/`
- `shared/browser-policy.md`：`C:/Users/15136/.dsh/profiles/...`、npx 缓存 hash 路径、硬编码 env 块
- `DEV/backend-dev`、`DEV/backend-tech-design`、`DEV/frontend-dev`、`DEV/frontend-tech-design`、`DEV/code-review`：外部 AI 知识库 = `D:/project/agent-project/skills-knowledge/...`
- CONTEXT 中同类路径：`DEV/backend-dev/CONTEXT.md`、`DEV/frontend-dev/CONTEXT.md`

## 跟踪与证据

- 原问题 ID / 来源：新增；体检命令：`git grep -n -E "[A-Za-z]:[/](project|Users)"`（本轮实测 44 处命中，含历史 docs/issue 记录；活跃路径约 20 处）
- 发现时间：2026-10-18 23:00 本轮体系修复
- 影响面：换机后 Skill-Optimizer 的池写入、Bug-Fix 沉淀、Skill-Evolver 同步、DEV 类知识库检索全部失效；且失效方式多为「悄悄写不进去/找不到目录」，不是报错停机。
- 根因与归属：已确认——体系在单机长期演进中把「本机路径」当成事实写进规范；docs 中早有 P3 记录（`docs/案例库体系方案-草案.md` 安装路径硬编码），本次升级为 P1 并落地修复。

## 期望 vs 实际

- **期望**：活跃执行文件只出现仓库相对路径、环境变量（`$env:SKILLS_KNOWLEDGE_ROOT`、`$HOME`、`~/`）或显式占位符；换机后按文档设一个环境变量即可。
- **实际**：多处写死本机盘符/用户名，换机即断，且历史 docs 里的待办未被执行。

## 修复方向

1. 池路径统一为仓库根相对写法（`../../bug-patterns/`、`../../evolution/`）；安装副本/其它项目运行时的边界写成「写用户指定维护目录，不写源仓」。
2. 安装副本同步改为 `scripts/install-skills.py --target <宿主 skills 目录>`（跨平台），不写死宿主目录。
3. `shared/browser-policy.md` 机器相关路径改占位符 + 发现命令（npx 缓存、profile patch 路径）。
4. DEV 外部知识库统一读 `$env:SKILLS_KNOWLEDGE_ROOT`；未配置按 `skill-knowledge/README.md` 降级并登记，不伪造检索。
5. 受影响 skill 的 CONTEXT.md 记 D-xx；本轮修复后对上述目录再做一次 grep 清零。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 本轮进行中：各 SKILL.md/CONTEXT.md + shared/browser-policy.md |
| 忽略理由 | — |