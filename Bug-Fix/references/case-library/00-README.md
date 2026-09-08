# Bug 修复 / 日志定位案例库（Case Library）索引

> 定位：诊断 bug、定位日志时**按需加载**的方法论与范本参考。本 Skill 铁律（先复现/证据链三段/根因 Gate/只诊断委托）与 `references/root-cause-guide.md` 优先，本库补「系统调试方法 + 日志定位专项 + 同行范本」。

## 一、目录

| 文件 | 内容 | 何时读 |
|---|---|---|
| `debugging-methods.md` | 4 阶段/假设驱动/5-Whys/三次上限/反模式/常见根因 | 收敛根因、生成假设时 |
| `log-locating.md` | 日志定位 9 项专项 + Commit-Then-Instrument 干净清理 | 分析日志、插桩时 |
| `agent-skill-samples.md` | 同类调试 Skill 结构样本 | 优化本 Skill 结构时 |

## 二、统一案例字段

> 场景 → 问题 → 方法/工具 → 可借鉴点 → 出处 → 注意事项。

## 三、使用原则

1. **先根因后修复**：NO FIXES WITHOUT ROOT CAUSE，绝不只修症状——与本 Skill 铁律「证据链三段」一致。
2. **Commit-Then-Instrument**：插桩日志用 `git restore .` 干净清理，绝不手删（防留悬挂括号/破坏缩进）。
3. **借鉴不照搬**：同行范本的 9 阶段/红绿验证只作参考，本 Skill 只诊断委托、不改码不深度测试的边界不变。
