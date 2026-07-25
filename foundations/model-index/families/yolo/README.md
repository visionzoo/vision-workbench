---
status: working
type: model-index
rigor: standard
provenance: official-papers-repositories-documentation-and-owner-use
evidence_status: partial
owner_review: accepted
ip_review: not-applicable
confidence: medium
created: 2026-07-25
updated: 2026-07-25
---

# YOLO

YOLO 是实时目标检测模型家族，但不是一条由单一组织连续维护的版本线。YOLOv3 之后，不同编号和命名分支来自不同作者或组织，代码、许可和版本含义也不同。

## 在 Foundations 里的位置

- 角色：`task-model`
- 主要任务：[目标检测](../../../tasks/object-detection.md)
- 核心机制：[多尺度、标签分配、检测头、结果选择](../../../mechanisms/object-detection-core.md)
- 真实工程记录：见 [Deployment](deployment.md) 中的回链

## 本人经验

已确认有 YOLO 训练、导出和部署的实际使用经验。因此本条目可以记录“本人经验”，但不在没有独立材料的情况下写具体项目、设备和指标。官方资料仍只表示第一方定义或报告，不能用本人使用经验替代来源。

## 各页面分工

| 页面 | 只负责什么 |
|---|---|
| [Variants](variants.md) | 版本归属、维护方和主来源；这是谱系的唯一维护位置 |
| [Architecture](architecture.md) | 结构和机制发生了什么变化 |
| [Data and training](data-and-training.md) | 官方披露的训练信息和迁移时要重查的条件 |
| [Evaluation](evaluation.md) | 指标与比较口径 |
| [Deployment](deployment.md) | 导出、量化和板端检查 |
| [Ecosystem implementations](ecosystem-implementations.md) | 高质量第三方复现、移植和改造 |
| [Limitations](limitations.md) | 已知限制和未完成项 |
| [Sources](sources.md) | Source ID 与原始链接 |

其他页面不再各自维护完整版本名单。新增分支时，先改 `variants.md` 和 `sources.md`；只有结构、训练、评测或部署确实有新内容时，才改对应页面。

## 当前状态

- 主要分支和高价值生态改造已经分开；
- 第一方来源与本人经验已经分开；
- 尚未逐个冻结所有仓库 revision、权重哈希和完整指标条件；
- 尚未完成统一硬件复测；
- 任务、机制、来源和工程回链已经补齐；本人已确认目录分工和维护成本可以接受。
- 这次验收只表示 YOLO 可以作为后续模型族的建设样板，不表示所有分支、指标和部署结论都已独立复测。

## 维护成本复盘

上一次补分支时同时改了 8 个页面，说明谱系信息重复得太多。本轮改成：

- 新增分支必改：`variants.md`、`sources.md`；
- 有新机制时才改 `architecture.md`；
- 训练、评测、部署有实质差异时才改对应页面；
- README 不再保存版本名单。

这样增加普通分支通常只改 2 个文件，不会再把整个目录一起翻一遍。
