# Skill 体系优化计划

> 版本：v1.0（计划稿，未执行）
>
> 日期：2026-09-17
>
> 依据文档：《Skill体系优化路线图-基于Anthropic-Agent-Skills.md》
>
> 性质声明：本文只输出具体优化计划，不修改任何 Skill 与代码。所有任务在拍板后按阶段独立执行、独立提交。

---

## 1. 计划目标

把当前「Skill 文档集合 + 自然语言工作流协议」升级为「可发现、可执行、可验证」的工程系统，补齐三类基础设施：

1. **统一 Skill 契约**：输入、输出、前置、门禁、停止条件、失败处理结构化。
2. **统一产物契约**：PRD、原型、TDD、评审、测试报告、PIPELINE 可追踪、可校验、可版本化。
3. **真实运行验证**：用真实项目场景验证触发、资源加载、产出和下游消费。

总原则：先建立契约和验证 → 少量 Skill 试点 → 渐进式迁移。不批量重写 18 个 Skill。

## 2. 现状基线（2026-09-17 已核实）

| 项 | 现状 |
|---|---|
| Skill 数量 | 18 个含 SKILL.md 的 Skill（产品调研 3、原型设计 5、技术方案 3、开发质量 4、运行治理 3） |
| 命名 | 目录使用大写连字符（PRD-Design、Backend-Dev 等），不符合 canonical 小写规范 |
| 公共规则 | `shared/` 已有 anti-deadloop、browser-policy、evidence-before-claims、receiving-review、socratic-grilling-core、baseline-terms、dev-common + templates |
| 其他目录 | `bug-patterns/`、`issue/`、`chats/` 已存在 |
| governance/ | 不存在（skill-registry、四张矩阵均未建立） |
| scripts 层 | 不存在，确定性检查均由 Agent 自然语言完成 |
| verification/ | 不存在，未做过真实场景运行验证 |
| asset-library/ | 不存在（资产仍分散在各 Skill 的 references/assets 中） |
| 资产生成物污染 | 已确认 `DEV/frontend-dev/assets/frontend-template-vue3/` 下存在 node_modules/、coverage/、dist/ |
| 双副本 | 本仓库为源；`.zcode\skills` 安装副本需在每次改动后同步（既有约定） |

## 3. 优化点清单（路线图差距分析 → 计划任务）

| 编号 | 优化点 | 级别 | 对应阶段 |
|---|---|---|---|
| O-01 | Skill 名称不符合 canonical 小写规范，需兼容迁移 | P0 | Phase 0 |
| O-02 | description 过重（100~400 字符混入流程/编号/门禁/路径），需四段化 | P1 | Phase 1 |
| O-03 | compatibility 只写宿主名单，不写真实运行时依赖 | P1 | Phase 1 |
| O-04 | SKILL.md 入口重（3~11KB），公共规则重复、案例未下沉 | P1 | Phase 1 |
| O-05 | README/CONTEXT/执行入口职责不清 | P1 | Phase 1 |
| O-06 | 确定性检查未脚本化（frontmatter/名称/引用/manifest/PIPELINE/生成物） | P1 | Phase 0~4 渐进 |
| O-07 | 真实评测体系缺失（scenarios/runs/reports） | P1 | Phase 3 |
| O-08 | 资产中混入 node_modules/coverage/dist 生成物 | P1 | Phase 0 |
| O-09 | 状态和生命周期标记不统一（完成/定稿/初版/无状态行） | P2 | Phase 0 建矩阵，Phase 1 落字段 |
| O-10 | WorkFlow/Testing/bug-fix/skill-optimizer/Frontend-Dev 职责过重，需按模式拆分而非堆主文件 | P2 | Phase 1 试点、Phase 5 展开 |
| O-11 | Skill 清单未升级为 Skill Graph（节点声明输入输出依赖门禁） | 体系 | Phase 1 契约、Phase 4 状态机 |
| O-12 | 阶段间靠聊天上下文传递，未 Artifact First + manifest | 体系 | Phase 2 |
| O-13 | 治理矩阵缺失（状态/契约/产物/缺口四张表） | 体系 | Phase 0 |
| O-14 | Workflow 依赖 ⑧⑨⑩ 类编号，缺稳定节点 ID 与统一状态机 | 体系 | Phase 4 |
| O-15 | 资产未分层（Method/Pattern/Template/Adapter/Evidence），相似资产复制风险 | 体系 | Phase 5 |
| O-16 | 遗留项目无接入方法（Baseline/Characterize/Boundary/Golden Slice/Extract + L0~L4 分级） | 体系 | Phase 3 场景二、Phase 5 提炼 |
| O-17 | BugFix 缺运维闭环字段（版本/部署/回滚/监控/复盘） | 体系 | Phase 6 |

---

## 4. 分阶段执行计划

### Phase 0：建立基线（第 1 周）

**目标**：知道每个 Skill 当前「写了什么、能不能跑、谁依赖谁」。

| 任务 | 具体动作 | 产出物 |
|---|---|---|
| T0.1 | 建立 `governance/skill-registry.yaml`：18 个 Skill 逐一登记 `legacy_name`（现目录名）→ `canonical_name`（小写连字符，如 prd-design、backend-dev、ui-ux-review、skill-optimizer），含旧目录、新目录、owner、一句话职责；**本轮只登记映射，不动目录** | governance/skill-registry.yaml |
| T0.2 | 建立状态矩阵：每个 Skill 标注 documentation / structure / smoke / real-run 四态验证状态（初始全部 real-run: not-run，如实标注，禁止把「文档完成」写成「验证通过」） | governance/SKILL-STATUS-MATRIX.md |
| T0.3 | 建立契约矩阵与产物矩阵：Skill 触发条件、输入、输出、前置依赖、评审者、门禁、停止条件、回退方式、证据位置、已知风险；产物侧列 PRD/原型/设计稿/TDD/FTDD/评审报告/测试报告/PIPELINE 的生产者与消费者 | governance/SKILL-CONTRACT-MATRIX.md、governance/ARTIFACT-MATRIX.md |
| T0.4 | 建立 Workflow 缺口清单：主链 14 节点中缺门禁、缺产物、缺停止条件的位置 | governance/WORKFLOW-GAP-LIST.md |
| T0.5 | 盘点各 Skill 的 references/、assets/ 清单和外部依赖（Node/pnpm/浏览器工具等），登记进 registry | registry 附表 |
| T0.6 | 清理生成物：`DEV/frontend-dev/assets/frontend-template-vue3/` 移除 node_modules/、coverage/、dist/，替换为锁版本清单（package.json + lockfile 说明）+ 可重复安装命令；同步检查 frontend-template-react；检查其余 assets 目录 | 清理后资产 + dependencies 清单 |
| T0.7 | 脚本化起步：实现 `build_skill_registry` 与 `scan_generated_files` 两个校验脚本（scripts/ 只做确定性检查） | scripts/ |

**验收**：任何人可通过矩阵回答任一 Skill 的触发条件、输入、输出、门禁和当前验证状态；核心资产中无生成物。

### Phase 1：统一 Skill 契约（第 2~3 周，三试点）

**目标**：用契约把 Skill 变得可发现、可执行；只动 Workflow、Backend-Dev、Testing 三个试点。

| 任务 | 具体动作 | 产出物 |
|---|---|---|
| T1.1 | 建立契约 schema：skill-contract.schema.yaml（id/type/trigger/inputs/outputs/dependencies/review/gate/stop_conditions/evidence）、artifact-contract.schema.yaml、workflow-node.schema.yaml | shared/contracts/ |
| T1.2 | 三试点 frontmatter 重构：name 沿用 canonical 映射；description 四段化（能力/触发/输入/边界），流程、门禁细则、输出路径全部移出 description；compatibility 改为真实运行时依赖（如 Testing 写「需要浏览器自动化与本地 dev server」），无特殊依赖则删除该字段 | 3 个 SKILL.md 的 frontmatter |
| T1.3 | SKILL.md 瘦身：按标准模板（Purpose / When to use / When not to use / Inputs / Outputs / Preconditions / Workflow / Pattern selection / Quality gate / Stop conditions / Evidence / References）重组正文；保留真正影响执行的部分，不机械复制全部章节；重复出现的 P0/P1 规则、浏览器策略、证据规则改为显式指针——在正文中写明「何时读取 shared/ 哪个文件」 | 3 个瘦身后 SKILL.md |
| T1.4 | 案例与检查清单下沉：大段案例、详细检查清单移入 references/；SKILL.md References 节列出本次任务可能需要的文件及触发条件 | references/ 增量 |
| T1.5 | 职责声明落地：每个试点补 README（人的说明）/CONTEXT（决策与迁移记录，不作为隐式必读）/SKILL.md（唯一执行入口）分工，影响 Agent 决策的规则不得只存在于 README/CONTEXT | 3 组文件 |
| T1.6 | 生命周期字段统一：metadata 中加 lifecycle / maturity / verification / runtime / owner / last_verified 六个正交字段，替换「完成/定稿/初版」等口语状态 | registry + 三试点 metadata |

**验收**：三个试点均能明确说明输入、输出、前置、停止条件、失败处理和证据位置。

### Phase 2：统一产物契约（第 3~4 周）

**目标**：阶段间传递可持久化产物，而非聊天记录。

| 任务 | 具体动作 | 产出物 |
|---|---|---|
| T2.1 | 制定 manifest.yaml 模板：artifact（id/type/version/path）+ lifecycle（status/created_by/created_at）+ review（skill/status/rounds/p0/p1/p2）+ downstream.allowed | shared/contracts/ 模板 |
| T2.2 | 第一批覆盖六类产物：PRD、TDD/FTDD、代码评审报告、测试报告、PIPELINE（原型/设计稿第二批） | 6 个 manifest 模板 |
| T2.3 | 定义下游消费规则：下游 Skill 开工前只读产物 + manifest 判断可否开始（status=approved 且 p0=0），写入试点 Skill 的 Preconditions | 规则条目 |
| T2.4 | 校验脚本：`validate_artifact_manifest`（manifest 必填字段与 schema 合法性） | scripts/ |

**验收**：下游 Skill 不需要阅读完整聊天历史，仅凭产物和 manifest 就能判断能否开始。

### Phase 3：建立真实运行验证（第 5~6 周）

**目标**：用真实场景暴露契约问题，不靠「文件存在、章节齐全」自证质量。

| 任务 | 具体动作 | 产出物 |
|---|---|---|
| T3.1 | 建立 verification/ 目录：scenarios/（场景定义）、runs/（运行记录）、reports/（结论） | verification/ |
| T3.2 | 定义四个 Golden Scenarios：① 从零构建小型全栈功能；② 接手已有项目新增一个功能；③ 纯前端修改并通过视觉与功能检查；④ 从线上日志定位并修复一个 Bug | 4 份 scenario 定义 |
| T3.3 | 定义异常场景：输入缺失、资源缺失、工具不可用、评审反复不通过——验证安全停止与澄清行为 | 异常场景定义 |
| T3.4 | 逐场景执行：记录触发是否正确、references/assets 是否被正确找到、产物是否符合契约、下游能否消费、失败是否留证 | runs/ 记录 |
| T3.5 | 场景二（遗留项目）按五步法执行：Baseline→Characterize（特征测试/接口快照）→Boundary→Golden Slice→Extract；旧代码按 L0~L4 分级，最多记为 Case/Evidence | 遗留项目接入报告 |

**验收**：每个场景都有输入、运行记录、产物、评审结果、失败点和改进结论。

### Phase 4：强化 Workflow（第 7~8 周）

**目标**：把自然语言编排升级为可校验、可恢复的状态机；先 validator，后 dispatcher，不做平台。

| 任务 | 具体动作 | 产出物 |
|---|---|---|
| T4.1 | 引入稳定节点 ID：prd-design / prd-review / prototype-design / ui-ux-design / backend-tech-design / frontend-tech-design / backend-dev / frontend-dev / code-review / testing，替换 ⑧⑨⑩ 类编号（registry 中 legacy 编号保留映射） | 节点 ID 表 |
| T4.2 | 统一状态机：NOT_STARTED / BLOCKED / READY / RUNNING / WAITING_REVIEW / CHANGES_REQUESTED / RECHECKING / APPROVED / RELEASED / SKIPPED / WAIVED / FAILED / ABORTED | 状态机定义 |
| T4.3 | PIPELINE 作为项目唯一状态源：增加暂停、跳过、豁免、失败、回滚的记录格式；明确人工决策点与自动校验点 | PIPELINE 规范 |
| T4.4 | 校验脚本：`validate_pipeline_state`（状态合法迁移、门禁前置检查）；dispatcher 明确后置，不先做复杂引擎 | scripts/ |

**验收**：同一项目中断后，可仅依据 PIPELINE 和产物 manifest 恢复工作。

### Phase 5：资产分层与检索（第 9~10 周）

**目标**：建立五类资产分层，遏制相似资产无限复制。

| 任务 | 具体动作 | 产出物 |
|---|---|---|
| T5.1 | 建立 Method / Pattern / Template / Adapter / Evidence 目录与登记格式（与《AI工程资产沉淀执行计划》的 asset-library 目录规范对齐，两计划共用一套分层） | 资产目录骨架 |
| T5.2 | Pattern 增加适用条件、requires、provides、conflicts、ordering；Adapter 增加语言、框架、版本和运行依赖 | 首批 Pattern/Adapter 契约 |
| T5.3 | 资产生命周期：Draft / Experimental / Validated / Stable / Deprecated / Retired | 生命周期规范 |
| T5.4 | 优先沉淀 10~20 个高频、跨项目、已验证资产（从各 Skill assets/ 与真实项目中提炼），不追求一次建大库 | 首批分层资产 |
| T5.5 | 复杂 Skill 按模式拆分评估：WorkFlow/Testing/bug-fix/skill-optimizer/Frontend-Dev 逐个判断——主 Skill 留路由与共同流程，模式细节进 references，确定性检查进 scripts；仅当职责、触发、输入输出、生命周期真正不同时才拆独立 Skill | 拆分评估结论 |

**验收**：AI 先检索候选资产再说明选择理由；无候选时显式标记「需要新方案」，不把临时代码伪装成稳定资产。

### Phase 6：补齐 BugFix 与运维闭环（第 11 周）

| 任务 | 具体动作 |
|---|---|
| T6.1 | 在 Bug-Fix 现有「日志→复现→根因→修复→回归→沉淀」链路上增加字段：版本、部署环境、变更记录、发布批次、回滚方案、监控指标、影响范围、观察窗口、事故复盘 |
| T6.2 | 建立追溯要求：一个线上问题可追溯到受影响版本、修复提交、验证结果和后续 Pattern / Anti-Pattern |

**验收**：线上问题全链路可追溯；反模式回写 bug-patterns/ 并关联修复模式。

### Phase 7：持续运行与 Skill 演进（第 12 周及以后）

每个真实项目结束后固定执行八步：

```text
更新 PIPELINE → 保存运行证据 → 记录失败与返工 → 判断是否产生 Case
→ 判断是否产生 Pattern / Anti-Pattern → 判断是否需要更新 Skill
→ 运行回归场景 → 发布新版本
```

**验收**：Skill 的每次重要修改都有变更原因、影响范围、验证场景和回滚方案。

---

## 5. 第一批执行清单（Phase 0~3 内的优先序）

| 序 | 动作 | 说明 |
|---|---|---|
| A | 先做治理文件 | governance/ 五件套（registry + 四矩阵），不先批量改 Skill |
| B | 三个试点 Skill | Workflow（调度/状态/交接）、Backend-Dev（输入输出/资产选择/落地）、Testing（真实运行/证据/门禁） |
| C | 先加校验再迁移 | frontmatter 校验、canonical name 校验、引用路径校验（validate_resource_links）、manifest 校验、PIPELINE 校验、生成物扫描 |
| D | 先做四个 Golden Scenario | 不先建几十个 Pattern，用真实场景暴露契约问题 |
| E | 每次只迁移一个闭环 | 第一个闭环：Backend-Tech-Design → Backend-Dev → Code-Review → Testing；完成后再扩展前端、设计和 BugFix |

## 6. 验证指标

**结构指标**：全部 Skill frontmatter 合法；canonical name 唯一可映射；资源引用无死链；核心规则不依赖 README/CONTEXT 隐式加载；核心资产无生成物。

**执行指标**：正确 Skill 触发率；输入缺失安全停止率；manifest 完整率；下游首次消费成功率；PIPELINE 中断恢复成功率；评审返工轮次与 P0/P1 重复率。

**工程指标**：构建/测试/Lint 通过率；相似功能重复造轮子比例；Pattern 跨项目复用次数与复用后缺陷数；BugFix 日志到根因平均时长；线上问题回溯至 Skill/Pattern/Adapter/Evidence 的可达率。

不追求「生成代码行数」「单次对话完成率」类短期指标。

## 7. 明确不做的事情

1. 不一次性重命名、重写全部 18 个 Skill；
2. 不把历史代码直接纳入资产库；
3. 不把每个项目差异复制成新 Pattern；
4. 不让 AI 在无候选资产和验证证据时宣称「已沉淀」；
5. 不先做 Web 管理平台、向量数据库、自动 dispatcher；
6. 不把 README/CONTEXT/聊天记录/日志塞进 SKILL.md；
7. 不写不能改变模型决策的绝对化规则；
8. 不用「文档完成」替代「真实项目验证通过」。

## 8. 风险与执行注意事项

| 风险 | 应对 |
|---|---|
| 双副本漂移（本仓库为源，`.zcode\skills` 为安装副本） | 每个阶段改动 Skill 后按既有约定同步安装副本，纳入各阶段验收项 |
| 矩阵维护成本高，建完即过期 | 矩阵生成尽量脚本化（build_skill_registry），文档只留人工判断字段 |
| 试点周期被真实项目挤占 | Golden Scenario 直接复用真实项目充当（场景②③），不单独造项目 |
| 命名迁移破坏外部引用 | Phase 0 只登记映射不改目录；目录移动放到链接、脚本、引用全部更新之后单独执行 |
| 与《AI工程资产沉淀执行计划》重叠 | Phase 5 资产分层直接复用该计划的 asset-library 目录与 schema，两计划一套资产分层、不各建一套 |

## 9. 时间线总览

```text
第 1 周     Phase 0  基线：registry + 四矩阵 + 生成物清理 + 2 个脚本
第 2~3 周   Phase 1  契约：schema + WorkFlow/backend-dev/Testing 三试点
第 3~4 周   Phase 2  产物：六类 manifest + 下游消费规则
第 5~6 周   Phase 3  验证：verification/ + 四个 Golden Scenario + 异常场景
第 7~8 周   Phase 4  Workflow：稳定 ID + 13 态状态机 + validator
第 9~10 周  Phase 5  资产：五分层 + 10~20 个首批资产 + 复杂 Skill 拆分评估
第 11 周    Phase 6  BugFix 运维闭环
第 12 周起  Phase 7  持续演进：八步复盘 + 回归场景 + 版本化发布
```

---

## 10. 最终验收标准（第一阶段完成的判定）

- 每个 Skill 有稳定 ID、清晰 description 和真实 compatibility；
- SKILL.md 是自包含执行入口，详细内容按需加载；
- 输入、输出、门禁、停止条件、证据位置可查；
- 关键产物有 manifest 和版本；
- Workflow 使用稳定节点 ID 和明确状态机；
- 至少四个真实场景完成 forward testing；
- 至少一条闭环可中断后恢复；
- 至少 10 个资产完成五分层；
- 遗留项目有基线、特征测试、边界和 Golden Slice；
- BugFix 可追踪到发布、回滚、监控和复盘；
- Skill/Pattern 更新能通过回归场景验证。
