---
title: DMS eye visibility and localization reliability
status: working
type: experiment
created: 2026-07-25
updated: 2026-07-25
confidence: medium
tags: [dms, eye, visibility, keypoints, detection]
related: []
---

# DMS eye visibility and localization reliability

## Research question

在 IR DMS 场景中，如何可靠判断眼部是否可见、定位是否可信，从而避免把反光、侧脸、模糊和遮挡造成的坏 ROI 继续交给闭眼分类器？

## Observations

当前工程观察包括：侧脸时密集关键点可能漂移；遮挡与反光会形成外观上似眼的局部结构；单纯降低眼部检测阈值可以召回目标，也可能放大假阳性；最终疲劳误差由定位、可见性、分类和时序共同决定。

## Competing approaches

1. 单一眼部 YOLO 检测置信度；
2. heatmap 关键点及峰值/分布不确定性；
3. 人脸几何、头姿、关键点可见性、ROI 清晰度的组合判定；
4. 显式训练 visibility/occlusion 任务；
5. 时序一致性与个体自校准。

## Evaluation design

建立按反光、侧脸、模糊、手/遮阳板遮挡、正常可见分层的数据；分别评价定位误差、可见性 AUROC/F1、坏 ROI 拦截率、正常 ROI 保留率，以及最终闭眼事件的误报/漏报变化。所有方案必须在相同样本和阈值选择协议下比较。

## Current conclusion

“检测到眼睛”与“ROI 足以支持闭眼判断”不是同一命题。组合判定可能更稳健，但尚不能在缺少分层标注和消融实验时认定其优于显式可见性模型。

## Next discriminating step

先定义可见性与可用性的标注口径，并对现有检测置信度、关键点置信度/峰值、清晰度和头姿特征做同一数据集上的基线与校准，再决定是否训练新模型。
