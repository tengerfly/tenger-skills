# 问题记录修复核验（2026-09-21）

## 范围与结论

针对问题池 2026-09-21 的 01、02 两条：规则修复和静态接线检查完成，可进入受控真实项目试跑；跨会话恢复、协作中断与运行期去重仍需按 `task-scope-regression.md` 验证，不作全体系独立验收结论。

- 45 个本地活动 Skill 显式接入 `shared/problem-recording.md`，独立调用也执行。
- 下一安全节点记录已观察失败；根因未知不丢事实；轻量复用原摘要，不补全套正式建档。
- auto-test、Code-Review + Fidelity-Review、defect-triage 明确唯一详情、索引写入/更新与路由边界。
- 恢复与交付核对未决项，已修复不等于复核通过；写失败报告未落盘，跨仓未授权先留项目待反馈。
- 不改后台服务、注册表/正式状态机或 Superdesign 设计流程；没有同步安装副本。

## 本次实际验证

1. `.venv/Scripts/python.exe -X utf8 -m unittest discover -s scripts/tests -p test_problem_recording.py -v`：4 项通过。首次执行测试编写问题及修正经过保留在原 01 问题中。
2. `powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/validate.ps1 -ProjectRoot D:/project/agent-project/tenger-skills`：退出 0，36 项测试通过，输出 `system validation passed`。未配置 `SKILLS_KNOWLEDGE_ROOT`，按已有 warn-and-degrade 策略降级。
3. `git -c core.safecrlf=false diff --check`：退出 0。
4. 修复前后 SHA-256 比对一致：Superdesign SOP、原 design-review-gate、archive-readme-template、`.spec/workflow.yaml`。自举 Gate 未被解除。
5. 对 45 个活动入口执行 skill-creator 的 `quick_validate.py`：40 通过、5 个既有格式问题；逐一取 Git HEAD 原文执行同一检查，得到相同错误，非本次引入。详见源仓 `issue/Skill-Optimizer/2026-09-21/03-可选Skill格式校验发现五个既有兼容问题.md`。

## 能证明什么 / 不能证明什么

新增测试只证明入口引用可解析、消费者有索引职责、模板字段齐全和选定冲突规则被替换，不证明 Agent 每次都会落盘。维护过程实际经历一次测试失败 → 在原 issue 追加事实并回读 → 修正测试 → 专项/全量复测成功，证明本次手动执行了该记录流程，不等同后台自动捕获或新会话行为验收。

两个原问题保持「处理中」，附「规则修复完成、真实试跑待复核」说明，不伪造独立评审结果。无后台监听器，不能保证宿主突然退出前来不及保存的信息不丢失。

## 下一步

新项目从当前源仓读取更新后的 Skill 及共享规则；已安装旧副本不自动更新。受控试跑中用最小失败、暂停/恢复、修复复核验证实际记录行为。按证据确认 01/02 验收后再关闭问题；正式体系解除 BLOCKED 仍需原授权验收流程。
