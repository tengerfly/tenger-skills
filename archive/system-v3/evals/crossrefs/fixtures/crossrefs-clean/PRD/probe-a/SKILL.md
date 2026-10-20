# Probe A（合规引用写法）

## Purpose

夹具条目：只用于复刻 §1.4 的两种合法写法，让 `crossrefs` 判据有可判绿的现场。

## 引用

- 共享约定按到仓根层数写：见 `../../shared/problem-recording.md`（技能根内两级 `../`，两视图同一串可达）。
- 指向别的 skill 的私有资产写逻辑引用，不带 `../`：见 `probe-b/references/x.md`（按 registry id 定位，不做文件系统解析）。
- 占位写法不是真引用，不该被算进违规：`../../shared/<文件>.md`。
