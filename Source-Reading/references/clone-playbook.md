# 取源 Playbook（步骤① 取源时加载）

目标：用最小代价把「走读所需」的源码拿到本地。铁律：克隆到工作区**外**的临时目录（如 `<工作区>/.spec/源码学习/_clones/<owner>__<repo>` 或系统临时目录），绝不混入在研项目。

## 1. 摸底（先 API 后克隆）

```bash
# gh 已认证（5000 次/h）优先；否则免认证 api.github.com（60 次/h）
gh api repos/<owner>/<repo> --jq '{default_branch,language,size,stargazers_count,archived}'
```

关注字段：
- `default_branch`：克隆分支
- `language`：主语言（决定后面看什么构建配置）
- `size`：仓库 KB 数（> 200000 即 200MB → 走大仓策略）
- `archived`：true 时提醒用户「仓库已归档，仍按此版本学」

## 2. 克隆分档

### 常规（单包、< 200MB）
```bash
git clone --depth 1 https://github.com/<owner>/<repo>.git
```

### 大仓（> 200MB 或历史很重）
```bash
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/<owner>/<repo>.git
cd <repo>
git sparse-checkout init --cone
# 先只拿核心，需要时再 add
git sparse-checkout set packages src
git checkout
```

### monorepo（react / vue3 / babel 级）
1. 只检出 `packages/` + 根构建配置：`git sparse-checkout set packages package.json tsconfig.json vitest.config.ts`（按实际微调）
2. 读 `packages/*/package.json` 的 name / main / module / exports，画出包依赖图（谁依赖谁）
3. 逐章需要哪个包再 `git sparse-checkout add packages/<name>`

### 指定 tag/分支
```bash
git clone --depth 1 --branch <tag_or_branch> <url>
```
用户给了版本必须用它（锚点以它为准），并写进总览页头部。

## 3. 瘦身（走读不需要的目录，sparse-checkout 时不 add 它们）

默认排除：`tests/ test/ __tests__/ e2e/ cypress/ docs/ examples/ examples/ benchmarks/ fixtures/ .github/`

判断某目录要不要：看根 README 与构建配置的入口字段；测试目录**不排除命名规则**——实现文件常以 `.test.ts` 同级存放（vue/react 模式），此时保留、只走读非测试文件。

## 4. 常见坑

| 坑 | 处置 |
|---|---|
| 克隆巨慢/断流 | 确认已用 `--depth 1`；仍慢加 `--filter=blob:none`；网络不通时告知用户并停（唯一停机条件） |
| 行号与网上教程对不上 | 正常——以本次克隆版本为准，锚点自己核实，总览页标注版本 |
| blobless 克隆后读老文件内容为空 | `git sparse-checkout add` 补目录；不要 `git fetch --unshallow`（拉全史无必要） |
| 找不到入口 | 顺序查：package.json 的 `main/module/exports/bin` → 构建配置入口 → README 快速开始 |
| 链接库/生成代码混在源码里 | 看 build 脚本区分「手写源码」与「构建产物」，走读只看手写源码 |

## 5. GitHub 限流应对（与 OSS-Radar playbook 同源）

`gh api` → 免认证 `api.github.com` → WebSearch 兜底。摸底只需 1~2 次调用，一般碰不到限流。
