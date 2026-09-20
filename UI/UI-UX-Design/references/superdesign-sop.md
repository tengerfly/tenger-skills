# Superdesign SOP 吸收版（本 skill 场景化）

> 来源：官方 superdesign-skill 仓库 `references/SUPERDESIGN.md`（v0.14.0 时代）+ CLI `--help` 实测。本文件只保留**本 skill 场景要用的规则**，官方原文以 https://github.com/superdesigndev/superdesign-skill 为准。
> 官方规则可能随版本更新——执行前若命令行为与本文不符，以 `--help` 实测为准并记 issue。

## 一、场景路由（官方三分 → 本 skill 场景）

| 官方场景 | 判定 | 本 skill 处理 |
|---|---|---|
| A. 已有渲染 UI（改既有页面设计） | 被开发项目已有前端代码且在渲染 | **默认不接**（属前端阶段）；确要接 → 按「INIT 硬门禁」走官方 A 案：init 六文件 → 像素级复刻 → branch 变体 |
| B. 已有代码库的新页面 | 有代码库但页面未渲染 | 本 skill 正常接（以布局清单为真相源） |
| C. 无代码库新项目 | 设计稿阶段（常态） | **本 skill 默认场景（D-09）**：不做像素级复刻（无实然 UI），以布局清单产基线复刻，直接出稿 |

**INIT 说明**：官方的 init（`.superdesign/init/` 六文件：代码库分析产物）只在场景 A 需要。场景 C 跳过 init——没有代码可分析，fabricate 一个反而制造假上下文。

## 二、命令调用总规范

- 一律 `superdesign <command>`（CLI 已全局安装；官方文档的 `npx --yes @superdesign/cli@latest` 等价）；命令行为存疑时先 `superdesign <command> --help`，**禁止凭记忆猜参数**；
- 默认输出即 agent 优化格式（带 `help[]` 下一步提示）；需要完整机器载荷才加 `--json`；列表类命令需要展开截断字段加 `--full`；
- JSON 参数（`--pages` / `--props`）传**字面合法 JSON**，替换值而非括号键名；
- `create-project` 默认自动开浏览器——agent 场景一律加 `--no-open`（画布 URL 仍会打印）。

## 三、命令陷阱清单（--help 不会告诉你的）

| 陷阱 | 规则 |
|---|---|
| `create-design-draft` 多个 `-p` 被**静默丢弃** | 只接受一个 -p；只报成功但变体全丢。变体一律走 `iterate-design-draft --mode branch` |
| `--context-file` 支持 `path:start:end` 行段 | 同文件多段自动合并；~900 行阈值裁剪的唯一合法方式 |
| `extract-website` 服务端爬取，耗时 60-120s | 无载荷选择器默认 `--design-md`；`extract-brand-guide` 已被官方弃用，不要用 |
| `iterate-design-draft` 的 `--device` 从源稿继承 | 除非刻意换视口，不要重传 |
| `create-project --device` 只作用于 template 首稿 | 后续每稿自带 --device |
| `--reference-id` 传的是**画布图片节点 id / 品牌资产 key** | 仅 prompt 里写本地图片路径 ≠ 模型看得见；图片必须先 upload-asset |
| `revert-design-draft` 本身可逆 | 回退前当前 head 会先入版本历史，可放心试；版本号用 `get-design` 查 |
| prompt 里出现广告词式形容词 | 复刻/基线场景禁止美学形容词（premium/elegant…），会被渲染成假页面；美学语言只进变体方向 -p |

## 四、上下文与载荷（PAYLOAD BUDGET）

- **每次生成必带**：`--context-file .superdesign/design-system.md`（D-07 铁律）；
- **~900 行阈值**：超 900 行的文件必须行段裁剪——页面/组件裁到实际渲染分支，CSS 裁到 `:root` token 块，配置裁到相关段；
- **400 过载** = 上下文超限。正确处理：裁大文件到渲染段，**重试同一调用**；错误做法：瘦成「最小上下文」重试——模型收不到真实页面会凭 design-system 发明一个通用假页（假页面比失败更糟）。

## 五、资产路由（upload-asset）

| purpose | 用途 | 传给生成的方式 |
|---|---|---|
| `reference` | 临时视觉参考（截图、竞品图） | `--reference-id <nodeId>`，上画布不入品牌库 |
| `brand` | 持久品牌资产（logo、品牌字体） | `--reference-id <assetKey>` + prompt 明示「logo 位必须用该资产，禁止首字母/emoji/自造 SVG 替代」 |
| `content` | 最终内容图（要出现在稿里的图） | 用返回公网 `url` 嵌入 HTML + `--reference-id <nodeId>` |

- 稳定 key 上传（内容 hash 去重）；HTML 内图片只允许 `https://` 公网 URL 或 `data:`，**禁止**相对路径 / file:// / 本机绝对路径；
- **logo 后置校验**：含 logo 位的稿子出稿后必须 `get-design` 检查 HTML——logo 位必须是真 logo URL 或含 logo 的组件引用；发现替代品 → 最小直编修正后 `import-design-draft --into`，不开新分支不花额度。

## 六、直编契约（import-design-draft 硬性校验）

- 单个完整文档：`<!DOCTYPE html>` … `</html>`（片段拒绝）；
- 页面稿单屏；Tailwind utility 类做样式（CDN 缺失自动注入）；
- 图标 `<iconify-icon>` 且 `<head>` 自带其 CDN script（不自动注入）；
- `<body>` 无 class，布局全在单个根 `<div>`；
- 每个 `<a>` 唯一描述性 id，不嵌套；链接只允许完整 https URL 或 `#hash` 占位，禁止相对路径；
- 违反渲染契约 → 拒绝并给修复指引；轻问题 → `warnings[]` 返回，必须处理后重传。

## 六·附 直编闭环铁律（一类问题，2026-09-05 沉淀 · 学径案例）

> 类别：**「只改了本地 .spec/设计稿/*.html 却没 import 回传云端草稿」**（含迭升新增模块/分类/面板后的整体直编）。共同症状：本地文件已是新版（截图存证也在），但用户从**可点击的评审入口**（主态页「设置」等宿主入口/头像菜单，其 `<a>` 指向 `p.superdesign.dev/draft/<id>`）点进去看到的是云端旧稿 → 误判「新模块没生成」。根因：评审/宿主入口的单一事实源是**云端草稿 URL**，本地 HTML 只是工作副本；改完不回传，云端永远落后。

### 闭环流程（每次更新云端都最新 · 用户拍板 2026-09-05）

**目标状态：每次本地设计稿更新后，云端立即是最新页面——「待回传」不跨会话、不留「本地新/云端旧」中间态。**

1. **本地直编/迭升完成** → 保存 `.spec/设计稿/*.html`；
2. **自动本地打开确认**：起本地静态服务（或直接打开 HTML）渲染该稿，请用户查看确认「没问题」——让用户在本地看到最新版，而非看旧云稿产生误判；
3. **用户确认 OK → 立即回传云端**（同一轮内完成，不搁置）：
   `import-design-draft --into <draftId> --html-file <本地文件> --generated-by <模型>`
4. **回传后核版本**：`get-design --draft-id <id>` 确认 version 已递增为最新；
5. **README 状态如实**：稿源对照表更新为已回传版本（如 v2 已回传），**禁止以「本地已改 / 待回传」当定稿交付**；凡标注「待 import 回传」即未闭环——要么本轮完成回传，要么显式挂起为遗留项并同步告知用户（云端仍是旧版）；
6. **迭升后查引用链**：单稿迭升（如设置弹框扩分类）后，除该稿外还要核查**宿主页入口链接**（哪些页面点进来）、README 稿源对照、关联专稿是否引用了旧版云端 URL 或漏了最新内容——用户实际看到的是「入口云稿 → 目标云稿」整条链，任一环旧都算遗漏。

> 实现提示：本地静态服务可用 `python -m http.server <port>`（中文路径下更稳）或用 agent-browser / Playwright 直接打开 file:// 截图给用户；用户确认入口 = 「本地最新稿截图 / 本地服务 URL」，不是云端旧稿。

## 七、版本、回退与跨会话续跑

- 每稿有版本历史；`get-design` 输出自带 currentVersion/versions；
- 回退：`revert-design-draft --draft-id <id> --to-version <n>`（免额度、可逆）；从历史版本续改：`iterate ... --from-version <n>`；
- **续跑约定（本 skill）**：步骤 9 归档时把 projectId / 各页 draftId+version 写入 `.spec/设计稿/README.md`；`.superdesign/resume.json` 若由官方流程生成则同样有效。跨会话续做先读归档 README 或 resume.json 找回 id，找不到再 `fetch-design-nodes --project-id` 兜底；**禁止重复 create-project**；
- 模型选择：`list-models` 查看可选模型；重要页面可换更强的模型并告知用户（模型影响质量/速度/成本）。演示稿（presentation）不走本 skill。
