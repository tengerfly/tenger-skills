# 大厂真实架构案例索引（Real Cases）

> 用途：找同类业务架构参考时的轻索引。只存「主题 + 一句话价值 + 链接」，细节按需去原出处查。引用许可以各仓库 LICENSE 为准。

---

## 一、海外大厂（英文，架构演进参考）

| 主题 | 一句话价值 | 出处 |
|---|---|---|
| Netflix Microservices | 微服务 + 混沌工程（Mastering Chaos）先驱 | pin0513/awesome-software-design |
| Uber 4000+ 微服务 | 领域导向（DDD）拆 4000+ 服务的边界治理 | 同上 |
| Spotify 2000+ 微服务 | Backstage + C4 模型管服务图谱 | 同上 |
| Figma 实时协作 | CRDT 解决多人实时编辑的一致性 | 同上 |
| Discord Cassandra→ScyllaDB | 高写入场景存储选型演进 | 同上 |
| Shopify Modular Monolith | 模块化单体的成熟实践 | 同上 |
| Stripe API 版本兼容 | 公共 API 版本化与兼容策略 | 同上 |
| Cloudflare Pingora | Rust 重写 Nginx 的性能实践 | 同上 |
| GitHub 迁微服务 | 单体拆微服务的渐进路径 | 同上 |

## 二、中文大厂 / 实战（重点中文案例子库）

| 主题 | 一句话价值 | 链接 |
|---|---|---|
| 后端架构全景图 + 高并发「六板斧」 | 缓存/降级熔断/限流/异步/分库分表/弹性扩容 + 2025 技术栈模板 | juejin.cn/post/7576086446460059683 |
| 高并发电商微服务实战 | gRPC vs REST 权衡、Redis 购物车、K8s + OpenTelemetry 可观测 | blog.csdn.net/gitblog_00755/article/details/158597892 |
| 微服务技术栈选型三套 | 初创/高并发/金融级（Spring Cloud Alibaba / gRPC+K8s / Seata+OceanBase） | cloud.baidu.com/article/5084233 |
| 高可用高并发全链路 | DDD 划边界、ShardingSphere 分库分表、RocketMQ 削峰 + 幂等 + 死信 | cloud.baidu.com/article/4088741 |
| 仿小红书 Java 微服务 | Spring Cloud + UniApp 多端内容社区端到端样例 | cloud.tencent.com/developer/article/2578299 |

## 三、中文社区与书单（按需深挖）

| 资源 | 价值 |
|---|---|
| 掘金 · 后端/架构（juejin.cn） | 高并发、云原生实战文最密集 |
| 腾讯云开发者社区 / 百度智能云技术站 | 微服务/IM/电商架构样例 |
| 阿里中间件 / 美团技术团队 / 字节跳动技术博客 | 一线大厂真实架构演进 |
| 《大型网站技术架构》《亿级流量网站架构核心技术》《凤凰架构》 | 中文语境架构决策参考 |

> 沉淀原则：按「业务场景 → 技术挑战 → 选型决策 → 架构图 → 关键代码 → 踩坑」记录，配真实链接；只借鉴决策，不照搬架构（见 `00-README.md` 使用原则）。
