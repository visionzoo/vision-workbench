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
updated: 2026-07-27
---

# 目标检测的核心因果链

本页保存跨检测器复用的机制。某个 YOLO 分支采用什么模块、节点或源码实现，由 [YOLO family](../model-index/families/yolo/README.md) 维护。

## 1. 输入与可见信息

检测器只能利用进入网络的像素。resize、crop、letterbox、颜色与数值范围会改变目标信息和坐标链；目标在下采样前已经不可分时，增加深层容量不能恢复原始细节。

关键问题：原图目标多大，进入网络后多大，经过各 stride 后还占多少位置，训练与部署输入是否相同。

## 2. 多尺度表征与融合

深层特征语义强但空间分辨率低，浅层特征位置细但语义弱；neck 用 top-down、bottom-up、concat、add 或其他路径融合它们。更多尺度只增加候选分辨率，不保证正样本覆盖或有效语义。

关键问题：各层 stride、shape、channel、来源节点和融合顺序是否一致，目标信息在哪个边界首次消失或偏移。

## 3. 标签分配

标签分配决定哪些位置成为正样本、负责哪个目标，以及监督质量如何进入分类与定位。anchor、中心区域、IoU、动态匹配和 task-aligned 是不同机制，不能只用“anchor-free”代替分配说明。

关键问题：每尺度正样本数、匹配质量、边界/重叠目标和漏标如何影响监督。

## 4. 检测头、回归表示与损失

检测头把多尺度特征变成类别与位置表示。分类和定位可以耦合或解耦；框可以由 anchor offset、point distance、离散分布等形式表达。loss 约束的是训练表示，最终框还依赖 decode。

关键问题：raw output 的 shape 与语义、分类激活、回归单位、stride、loss 组件和权重。

## 5. Decode 与结果选择

decode 把网络表示转换成坐标和分数。NMS 从大量候选中按规则消除重复框；one-to-one 路线把选择更多放进训练和模型图。`NMS-free` 不能只看名称，要看实际 head、导出图和 runtime 输出。

关键问题：DFL/box decode、sigmoid、坐标格式、尺度拼接、NMS 或 one-to-one 选择位于哪里。

## 6. 从现象排查时

| 现象 | 保留的竞争解释 | 首轮证据 |
|---|---|---|
| 漏检 | 有效像素、标签、正样本、分类分数、结果选择 | 目标尺寸分层、正样本统计、raw score、阈值曲线 |
| 框偏 | 输入坐标链、融合对齐、回归/decode、量化 | 固定输入、各阶段坐标、回归输出、首个分歧层 |
| 重复框 | 尺度拼接、类别分数、NMS/one-to-one 语义 | raw candidates 与结果选择前后对比 |
| PC/板端差异 | 预处理、算子、融合、输出解释、量化、runtime | 相同语义节点逐级对齐和任务指标 |

先固定输入和接口，再比较相同语义的阶段；找到首个显著分歧边界后，只在相邻模块内下钻。中间张量和相似度用于定位，最终接受仍由 decode 后输出与任务级 Oracle 决定。

对应任务定义：[目标检测](../tasks/object-detection.md)。本页的机制结构、推断边界和诊断入口已于 2026-07-27 通过本人审查；接受不等于机制已在全部模型与任务中验证。
