# Governance schemas

这里保存治理文件的机器可读约束说明。当前 PowerShell 校验器采用无第三方依赖的结构检查，后续可在确定 YAML 解析运行时后升级为完整 JSON Schema 校验。

- `artifact-manifest.schema.yaml`：项目 `.spec/manifest.yaml` 的最小字段；
- `workflow.schema.yaml`：项目 `.spec/workflow.yaml` 的状态、Gate 和生命周期；
- `traceability.schema.yaml`：项目 `.spec/traceability.yaml` 的链接字段。

本目录只描述结构，不承载项目私有数据。