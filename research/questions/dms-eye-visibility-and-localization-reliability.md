---
title: DMS eye visibility and localization reliability
status: working
type: research-question
rigor: standard
created: 2026-07-25
updated: 2026-08-11
confidence: medium
provenance: conversation-draft-plus-public-research-structure
evidence_status: unverified
owner_review: pending
ip_review: pending
tags: [dms, eye, visibility, keypoints, detection]
related: [small-scale-eye-information-preservation-and-openness-measurement.md, ../experiments/upper-face-roi-information-preservation.md, ../experiments/dms-eye-keypoint-model-selection.md, ../../foundations/tasks/2d-landmark-localization.md, ../../foundations/mechanisms/keypoint-output-representations.md]
---

# DMS eye visibility and localization reliability

## Evidence boundary

本条目由历史对话重构，没有附带原始图像、标注规范、固定模型、日志或评测结果。公开文献能帮助建立竞争解释和实验合同，但不能验证用户数据上的结果。下列“观察”仍是待本人和 IP 审查的线索，不应被外推为 DMS 系统的一般事实。

## Scope relationship

本条目是 [R1](small-scale-eye-information-preservation-and-openness-measurement.md) 的 observability 子问题，只回答 findable、visible、usable 和定位可靠性。它不单独维护 ROI/重采样/网络分层的信息保真链，也不能用“关键点可用”代替连续开合度与部署验收。

## Research question

在 IR DMS 场景中，如何判断眼部是否可见、定位是否足以支持后续闭眼判断，从而识别由反光、侧脸、模糊、遮挡或 ROI 偏移造成的不可用输入？

这个问题包含三个不同标签：

1. landmark 是否可标注 / findable；
2. landmark 是否可见 / visible；
3. 眼部是否足以支持眼状态判断 / usable_for_eye_state。

三者不能用一个“关键点置信度”代替。

## Conversation-derived cues

待核对线索包括：

- 侧脸时关键点可能漂移；
- 遮挡、反光和模糊可能干扰局部结构；
- 降低检测阈值可能同时改变召回和假阳性；
- 人脸/眼 ROI 的 crop 与坐标还原可能制造系统偏移；
- 最终事件误差可能由定位、可见性、分类和时序共同作用。

这些陈述尚未绑定样本、版本或指标。

## Competing hypotheses

1. 现有眼部检测置信度已足以判断 ROI 可用性；
2. PFLD-style direct regression 已达到足够定位精度，新增 heatmap 只增加成本；
3. heatmap 的峰值、峰间 margin、entropy 或空间方差提供额外区分力；
4. 显式 findable/visible/occlusion head 优于峰值阈值；
5. RF-DETR 类二维 covariance 能提供更有效 uncertainty，但复杂度不适合部署；
6. 人脸几何、头姿、关键点 visibility、清晰度和反光的组合更有效；
7. 一体化 YOLO/RF-DETR keypoint 能减少上游 face ROI 失效；
8. 主要误差其实来自下游分类、时序或标签，而非定位/可用性。

## Public evidence that changes the experiment

- PFLD 说明 direct coordinate ROI 模型可以非常轻，但传统输出本身没有空间分布或显式 occlusion；
- HRNet/heatmap、DARK、UDP、HIH 说明编码、解码、亚像素与坐标链可能和 backbone 同等重要；
- Occluded Stacked Hourglass 表明在驾驶员安全场景显式预测 occlusion 可能改善定位与下游解释；
- YOLO26 Pose 当前训练使用 keypoint visibility 与 RLE uncertainty，但标准推理 fuse 会移除 sigma/flow 分支；
- RF-DETR Keypoint Preview 当前源码把 findable、visible 和二维 Gaussian 参数分开，但仍是 Preview，部署与校准未由本人验证。

这些是候选机制，不是本场景结论。

## Candidate evaluation

实验由 [DMS eye keypoint model selection](../experiments/dms-eye-keypoint-model-selection.md) 统一维护，核心顺序是：

1. 先定义并复核 `findable / visible / usable`；
2. 固定 ROI、schema、split、坐标链和 evaluator；
3. 优先比较 PFLD direct regression 与 HRNet heatmap；
4. 只有现有 ROI 是主要瓶颈或显式 uncertainty 有决策价值时，才训练 YOLO26/RF-DETR；
5. 同时评价定位、visibility/usability、视频 jitter、下游眼状态/事件和目标硬件。

阈值选择和测试集必须隔离，避免用同一数据选阈值又报告结果。同一视频相邻帧不得跨 split。

## Next discriminating action

由本人确认：

- 数据权属与可披露边界；
- eye landmark schema；
- `usable_for_eye_state` 标注口径；
- 现有 face/eye ROI 是否稳定；
- 当前 baseline 与目标硬件门限。

随后先完成小规模双人标注一致性、坐标链单元测试和 PFLD/HRNet Gate 1–2。只有结果显示关键点/可用性是主要误差源，才承诺更复杂模型或完整设备实验。

## Current conclusion

当前可确认的只有任务结构：

- “检测到眼睛”“关键点可标注”“点可见”和“ROI 足以判断闭眼”不是同一命题；
- 四个候选处于不同系统边界，不能直接用论文 AP/NME 排名；
- 需要把关键点指标与最终眼状态/疲劳事件连接起来。

尚无最佳模型结论。
