# 独立 Skill 维护包：自动化验证报告

## 范围与结果

- 日期：2026-09-22；目标：Skill/skill-lifecycle 及其仓库注册、测试接入和导航文档。
- 模式：auto-test 会话模式，实际执行 Python/Git 命令；没有调用独立测试引擎或真实模型会话。
- 版本：基于 7935eeb 的当前未提交工作区，包含此前用户任务变更；不将全仓已有修改全部归因本次。
- 本次独立回归：12 项，11 通过、1 跳过；跳过原因是 Windows 无创建符号链接权限，并非通过。
- 全仓回归：60 项，59 通过、1 为上述同一符号链接用例跳过，退出码 0。
- 包内结构/引用检查、skill-creator 格式校验、git diff --check：退出码 0。
- 自动化已执行范围通过；真实模型闭环与宿主安装未验证。保留既有 .spec/workflow.yaml 的 BLOCKED，不宣布体系验收通过。

## 分层与命令

| 层次 | 执行内容 | 结论 |
|---|---|---|
| L0 | check_bundle.py，标准库、只读结构/普通 Markdown 文件引用/Python 语法；另运行 quick_validate.py | 通过；不是完整 YAML/Markdown 或隐私扫描器 |
| L1 | unittest discover：独立目录 12 项，全仓 60 项 | 上述通过/跳过数量 |
| 隔离复制集成 | 将包的源码文件复制到仓库外临时目录，用 Python -I -S -B -X utf8 执行完整包内测试；去掉 site-packages 与环境注入 | 退出码 0，不需要本仓共享规则、脚本或第三方包；排除 Python 缓存 |
| L2/L3 | 非 Web 应用，浏览器/API 层不适用；真实模型执行创建→记录→迭代未执行 | 不计通过；tests/behavior-cases.md 提供待执行场景 |
| L4 | 性能/负载/安全专项无本轮信号，未执行 | 不给专项通过结论 |

常用复验命令：

```text
.venv/Scripts/python.exe -I -S -B -X utf8 Skill/skill-lifecycle/scripts/check_bundle.py Skill/skill-lifecycle
.venv/Scripts/python.exe -I -S -B -X utf8 -m unittest discover -s Skill/skill-lifecycle/tests -v
.venv/Scripts/python.exe -B scripts/validate_core.py system --project-root .
git diff --check
```

## 已覆盖

- 仓库外完整包复制后的执行；只读检查前后哈希不变，不执行目标 Python 代码。
- 资源缺失、目录越界（含编码路径）、绝对文件链接、入口元数据错误、未填模板、无效 UTF-8、Python 语法错误的拒绝。
- 包内合法父目录引用可用；目标 Skill 模板填充后可独立结构检查，无维护包引用。
- 工程入口继续加载共享问题规则，独立包加载自身记录规则；不为独立包删除记录义务。

## 发现、修复与限制

初轮全仓失败：旧记录契约测试要求所有入口硬绑定 shared/problem-recording.md。独立包使用包内规则，因此增加显式 recordingPolicy 注册信息，测试核对其存在、真实加载与包内路径边界。原工程入口默认值不变。原始失败日志保留，不以最终通过覆盖历史。

Windows 符号链接回归因权限跳过，不尝试绕过系统权限。外部知识库未配置仍为 warn-and-degrade，未擅自配置。测试会产生 Python 缓存，最终复验使用 -B；分享时排除 __pycache__/ 和 .pyc（可能含本机路径），它们不是发布资源。

真实模型是否按时记录、正确判断偏好范围、等待批准再改写、回退不覆盖他人改动，都尚未实际试跑；本轮没有模型成功率、交互覆盖率或个人适用性结论。未安装、同步或上传本包，没有迁移任何旧问题池和个人偏好。

## 证据与问题

- 日志目录：.spec/auto-test/evidence/portable-skill-20260922/
- 首轮：bundle-check.log、portable-tests.log、skill-format.log、system-validation.log、results.json。
- 最终：copied-package-tests.log、bundle-check-final.log、skill-format-final.log、system-validation-final.log、diff-check-final.log、results-final.json。
- 问题唯一详情：issue/Skill-Optimizer/2026-09-22/01-维护闭环无法独立复制.md。

下一步：接收方选择一个实际目标 Skill，按包内行为场景完成真实使用验证；当前交付的是独立维护工具包及已验证的静态/脚本能力，不是已验证适用于所有人的最终个人 Skill。
