# 「Testing 仍作备用入口」旧口径散落活跃文档，与唯一入口 auto-test 冲突

> 归属 skill：`auto-test`（口径一致性）＋ `Skill-Optimizer`（跨文件同步） ｜ 日期：2026-10-18 ｜ 来源：体检

## 基本信息

| 字段 | 值 |
|---|---|
| 等级 | P1 |
| 标签 | `术语文案` / `流程缺陷` |
| 优化状态 | 处理中（P2 阶段统一修） |

## 现象

统一口径（README.md:17「Testing 已归档，不再作为备用 Skill 被发现」、Test/README.md、workflow/SKILL.md:99「旧 Testing 请求重定向 auto-test，不启动历史人工测试流程」）已确立，但活跃文件中仍残留「Testing 作备用」表述：

- `Test/auto-test/README.md:7`：「Testing 保留为链外备用，源码不动」
- `Test/auto-test/CONTEXT.md:17`：「Testing 源码保留为链外人工走查备用」
- `shared/baseline-terms.md:38`：「auto-test / Testing / Fidelity-Review…」
- `shared/browser-policy.md:34`：「auto-test / Testing 样式视觉断言」
- `shared/evidence-before-claims.md:3`：「auto-test / Testing」
- `workflow/references/legacy-pipeline.md:11,196`：Testing 标「备用」（legacy 只读参考，可加历史注）

## 跟踪与证据

- 证据：`git grep -n Testing -- README.md Test/auto-test shared workflow`（2026-10-18 本轮）；来源=Lead 机械面评审 F-M1
- 影响：读者/模型看到「备用入口」可能启动第二套测试流程，违反唯一入口；跨应用安装后同样生效。
- 根因与归属：已确认——2026-09-22 归档 Testing 时只改了部分入口，shared 与 auto-test 自身说明未同步。

## 期望 vs 实际

- **期望**：活跃文件只保留「Testing 已归档，旧请求重定向 auto-test，不启动历史流程」。
- **实际**：5 处活跃文件仍把 Testing 写成备用/可用入口。

## 修复方向

1. Test/auto-test/README.md 与 CONTEXT.md 改为「Testing 已归档（归档见 Test/Testing/ARCHIVED.md），旧请求重定向 auto-test，不启动第二套流程」。
2. shared/baseline-terms.md、shared/browser-policy.md、shared/evidence-before-claims.md 删除「/ Testing」。
3. workflow/references/legacy-pipeline.md（legacy 只读）加「Testing 已归档，仅历史」注。
4. 修完复跑 check-installed-refs 与 skill-contract；改 shared 需重锚 eval 基线。

## 沉淀记录（优化模式回填）

| 字段 | 值 |
|---|---|
| 沉淀目标 | 未沉淀（处理中） |
| 沉淀位置 | 待 P2 修复：上述 5 个活跃文件 + 1 个 legacy 注 |
| 忽略理由 | — |