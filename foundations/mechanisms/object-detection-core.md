---
status: working
type: mechanism
rigor: standard
provenance: yolo-official-sources-and-owner-practice
evidence_status: partial
owner_review: accepted
ip_review: not-applicable
confidence: medium
created: 2026-07-25
updated: 2026-07-25
---

# 目标检测的四个核心机制

这四项基本决定了一个检测器能不能找到目标、框得准不准，以及最后能不能部署。

## 1. 多尺度特征

作用：让不同分辨率的特征分别处理大、中、小目标。

本质：深层特征语义强但分辨率低，浅层特征位置细但语义弱；neck 把两者融合。它不能凭空恢复已经丢失的像素，所以小目标问题首先仍是有效像素问题。

## 2. 标签分配

作用：决定训练时哪些预测位置算正样本，以及每个正样本负责哪个目标。

本质：它直接改变监督信号的数量和质量。anchor、中心区域、IoU、动态匹配和 task-aligned 方法只是不同规则；数据分布变化后，原规则不一定仍合适。

## 3. 检测头

作用：把特征变成框、类别和置信度。

本质：分类和定位需要的特征并不完全相同。耦合头共享更多计算，解耦头把两条路径分开；anchor-free 省掉预设框，但仍要定义位置、尺度和回归形式。部署时必须确认输出张量的真实含义。

## 4. 重复结果处理

作用：从大量候选结果中留下最终目标。

本质：NMS 用人为规则消除重复框，简单但依赖阈值和后处理；端到端方法把“一对一选择”更多放进训练和模型图里，减少后处理，但对训练、导出和 runtime 支持要求更高。`NMS-free` 不能只看模型名称，要看实际导出图。

## 怎么用于排查

```text
漏检 → 先查有效像素和标签分配
框不准 → 查坐标链路、回归形式和量化
重复框 → 查分数解释与结果选择
板端不一致 → 查输出语义、导出图和后处理位置
```

对应模型样板：[YOLO architecture](../model-index/families/yolo/architecture.md)。
