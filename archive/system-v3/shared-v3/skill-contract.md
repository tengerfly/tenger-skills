# Skill Contract v2

This is the common execution contract for every active Skill and legacy wrapper.

## 1. Precedence

When instructions conflict, apply this order:

1. `shared/` contracts;
2. `governance/` registries and schemas;
3. the current Skill `SKILL.md`;
4. the Skill's references and assets;
5. historical or legacy material, which is read-only compatibility input.

A local Skill must not redefine Gate values, lifecycle states, evidence labels, or the current state source.

## 1.1 Execution scope

先按 `shared/execution-profiles.md` 选择执行强度，直接调用原子 Skill 同样适用。其轻量独立执行规定优先限定本契约及领域 Skill 的程序性前置；安全、真实授权、范围、证据诚实和已存在的相关阻塞不降级。标准/完整执行才使用下述正式 execution、artifact、Gate 和状态契约。轻量不伪造这些记录，也不调用正式预检来绕过它们。

消费需求时遵循 `shared/requirements-context.md`，先索引再读已确认版本的相关原文与依赖。只加载本任务需要的 references/assets，不先通读整个 Skill 资源库。

## 1.2 Problem recording

所有执行强度及独立调用均遵循 `shared/problem-recording.md`：失败事实在下一安全节点持久化，详情一事一源、项目索引可发现，恢复/交付核对未决项。未知根因不妨碍记事实；此义务不依赖正式 Envelope，也不授权跨仓写入或解除 Gate。

## 1.3 Workflow visibility

遵循 `shared/workflow-visibility.md`：开工、恢复、阶段交接、等待决策、阻塞和收尾时向用户展示当前位置、当前 Skill、证据、待决定事项与下一步。正式状态以 workflow.yaml 为唯一来源；轻量复用任务摘要，不增加第二套状态或自动审批。

## 1.4 Cross-skill references

源仓布局是「`<分类>/<skill-id>/`」两层，安装副本布局是「`<skills 根>/<skill-id>/`」一层。同一条 `../` 相对路径不可能在两个视图同时成立（层数天然差一，跨分类时更甚）。跨 skill 引用只允许两种写法：

1. **共享约定与模板**——归仓库根 `shared/`（模板放 `shared/templates/`），按当前文件到仓根的层数写 `../`：技能根内两级、`references/` 与 `assets/` 内三级，形如 `../`×n + `shared/<文件>.md`。副本侧由 `shared` 三落点（容器级、skills 根级、技能目录级）承接，两视图同一串均可达。某 skill 的私有资产被两个以上 skill 需要时提升进 `shared/`，不留副本。
2. **指向其他 skill 的私有资产**——写逻辑引用 `<skill-id>/内部路径`（不带 `../`、不带分类层），按 registry id 定位，不做文件系统解析；只是路由或称呼时直接写 skill id。

禁止写法：带分类层的相对路径（形如 `../`×n + `<分类>/<skill-id>/…`）与跨分类的 `../<兄弟skill>/`——副本扁平布局下必断。归档目录（未注册、不随宿主分发）只可写仓内路径并注明不分发，不得写成技能内相对路径。

机器核验：`scripts/check-installed-refs.py`（副本视图可达性 + 禁用形式扫描），已接入 `scripts/validate-reference-integrity.ps1`。

## 2. SKILL.md frontmatter

```yaml
---
name: example-skill
description: One sentence describing the trigger and responsibility.
metadata:
  contract-level: v2 | v1 | legacy-wrapper | legacy-adapter | external-reference
  legacy-alias: null
---
```

`name` is lowercase kebab-case. The entry file is always named `SKILL.md`. Historical names belong in `metadata.legacy-alias`, not in the active `name`.

## 3. Required sections

Every entry Skill contains these headings:

`Purpose`, `Trigger`, `Inputs`, `Preconditions`, `Responsibilities`, `Non-goals`, `Procedure`, `Outputs`, `Evidence`, `Gate`, `Failure Route`, `Downstream Contract`, `State Changes`.

`Procedure` must describe one deterministic path. If an input is missing, route to `Failure Route`; do not invent a second, incompatible process.

## 4. Evidence labels

Use the following labels consistently:

| Label | Meaning | Rule |
|---|---|---|
| `FACT` | Directly observed or explicitly supplied | Preserve source location |
| `EVIDENCE` | A verifiable observation or test result | Link `evidenceRef` |
| `INFERENCE` | Reasoned conclusion from evidence | Show the reasoning boundary |
| `ASSUMPTION` | Temporary premise not yet verified | Mark as open |
| `RECOMMENDATION` | Suggested option | Not an approval |
| `DECISION` | Accepted direction by the user or authorized owner | Link `decisionRef` |
| `OPEN` | Unresolved question or missing input | Must have an owner or Failure Route |

## 5. Execution record

Use `projectId`, never a new local alias such as `project`:

```yaml
execution:
  executionId: EXE-YYYYMMDD-001
  skill: <governance skill id>
  lifecycle: CREATE | CHANGE | DEFECT | REFACTOR | INCIDENT | OPTIMIZE
  projectId: <project-id>
  status: COMPLETED | PARTIAL | BLOCKED
  gate: PASS | CONDITIONAL | BLOCKED
  evidenceRefs: []
  artifactRefs: []
  decisionRefs: []
  nextAction: <explicit action or NONE>
```

## 6. Gate and state rules

Use only `PASS`, `CONDITIONAL`, and `BLOCKED`. Follow `shared/gate-policy.md` and `shared/anti-deadloop.md`; do not create local exceptions. The current state source is `.spec/workflow.yaml`. `.spec/PIPELINE.md` and `.spec/WORKFLOW.yaml` are read-only legacy inputs.

## 7. Wrapper compatibility

A `legacy-wrapper` may retain old references and assets, but it must:

- expose the common sections and contract;
- translate old outputs into the current artifact, evidence, and Gate vocabulary;
- prevent legacy text from overriding the shared contracts;
- keep historical material clearly marked as legacy.
