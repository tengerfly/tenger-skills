# bash heredoc / re.sub 转义吞噬 → 源码字符串字面量断行

> 归属：`bug-patterns/` 错误模式池 ｜ 日期：2026-09-15 ｜ 来源：会话记录挖掘（rollout 签名：heredoc 转义×49 / Unterminated string×27）
> 依据：learning-assistant 会话 rollout `model-io-sess_369efc48-*.jsonl`（learn.service 批量补丁三轮返工实录）
> 原则：存「一类会再犯的错误」+ 防复发规则。

## 基本信息

| 字段 | 值 |
|---|---|
| 根因类型 | 环境依赖 |
| 受益 skill | Backend-Dev / Frontend-Dev |
| 等级 | P1（生成的源码带真实换行进字符串字面量，编译失败且肉眼难查） |
| 建议落点层级 | 错误表加行 |
| 状态 | 已提炼（落点见文末） |

## 现象（同类 bug 长什么样）

- 用 `python - <<'EOF'`（bash heredoc）生成含 `\\n` 的代码替换时，写入源码的字符串字面量被折成两行：`.join('` + 真实换行 + `');` → TS 报 `Unterminated string literal`；
- `re.sub(pat, replacement, s)` 的 replacement 含 `\n`/`\g` 等序列被 re 模块二次解释，替换结果与预期字符不符。

## 根因（证据链摘要）

当转义内容经过「bash heredoc → python 字符串字面量 → re.sub 替换串」多层处理时，`\\n` 在每层都被解释一次：heredoc 引号不总是阻止处理，python 源码里 `\\n` 是反斜杠+n，但 re.sub 的**替换串**会把 `\n` 解释为换行——多层语义叠加后写出的内容与意图差一层转义。

## 防复发规则（核心，给目标 skill 的可执行规则）

- [ ] 脚本中构造「反斜杠+字母」类字面量一律用 `chr(92)+'n'` 拼接，不写裸 `\\n`
- [ ] `re.sub` 的替换串含反斜杠时改用 lambda：`re.sub(pat, lambda m: repl_text, s)`
- [ ] 生成源码的脚本跑完后立即编译（tsc / node --check）；编译报 Unterminated/意外换行时优先查刚写入的字面量

## 提炼回填（Skill-Optimizer 模式③ 填）

| 字段 | 值 |
|---|---|
| 提炼落点 | `Backend-Dev/SKILL.md` 常见错误对照表新增行（chr(92) 构造 / lambda 替换 / 即改即编译） |
| 决策记录 | `Backend-Dev/CONTEXT.md` D-09 |
| 忽略理由 | — |
