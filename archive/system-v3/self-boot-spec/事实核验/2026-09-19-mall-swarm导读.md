# Fact-Check · mall-swarm 导读核验（第 1 轮）

- 核验对象：`.spec/源码学习/macrozheng__mall-swarm/导读.md`
- 证据源：L3 本地克隆（mall-swarm master@04c442f，全部锚点本会话亲读/grep）
- TL;DR：**承重断言全 ✅；2 处精确性失准（auth 文件数 7→6、宣传出处归属）当轮修正**。修正后可采纳。

## 承重断言判定表

| # | 断言 | 判定 | 证据 |
|---|---|---|---|
| 1 | 九模块：底座三+业务三+新增 gateway/auth/monitor | ✅ | pom.xml:13-21 |
| 2 | 网关路由：discovery locator + 显式 lb:// + StripPrefix=1 | ✅ | mall-gateway application.yml:15-40 |
| 3 | SaReactorFilter 全拦截+白名单 | ✅ | SaTokenConfig.java:40-45 |
| 4 | 双账号按路径分流（portal 会员/admin 管理员） | ✅ | SaTokenConfig.java:50-53 |
| 5 | 权限判定读 Redis hash PATH_RESOURCE_MAP + AntPathMatcher + checkPermissionOr | ✅ | SaTokenConfig.java:56-73 |
| 6 | auth 是 Feign 薄聚合（6 个 Java 文件），clientId 区分 | ✅（修正后） | find 计数=6；AuthController.java:34-46 |
| 7 | auth 的 service 是 @FeignClient("mall-admin") 代理登录 | ✅ | auth UmsAdminService.java:16-20 |
| 8 | 真实登录在业务服务 StpUtil.login | ✅ | mall-admin UmsAdminServiceImpl.java:89-104 |
| 9 | 双账号 StpLogic TYPE=memberLogin + JWT 风格 | ✅ | StpMemberUtil.java:44-49 |
| 10 | 权限规则集中制：admin 写 Redis hash、网关只读 | ✅ | UmsResourceServiceImpl.java:85-86；AuthConstant.java:37 |
| 11 | MQ 三件套+10min cron 原样保留 | ✅ | portal component 三文件；OrderTimeOutCancelTask.java:24 |
| 12 | 监控 Spring Boot Admin | ✅ | mall-monitor pom.xml:28,32 |
| 13 | ⚠️ Sentinel/Seata 代码中不存在（宣传提及） | ✅(⚠️边界已标) | 全仓 grep 无依赖无代码；README:93 列 Seata、仓库简介列 Sentinel——导读已精确标注出处 |
| 14 | config/ 为 Nacos 配置样例（五组 dev/prod） | ✅ | config/ 目录结构与文件实读 |

## 反证搜索记录

- 「Sentinel/Seata 不存在」：`grep -rliE "sentinel" .`（排除 README）与 pom/代码双查无命中；README 与仓库简介的提及已单独取证并写入导读
- 未证实清单：无
