---
title: DMS eye visibility and localization reliability
status: working
type: research-question
rigor: standard
created: 2026-07-25
updated: 2026-07-25
confidence: low
provenance: conversation-draft
evidence_status: unverified
owner_review: pending
ip_review: pending
tags: [dms, eye, visibility, keypoints, detection]
related: []
---

# DMS eye visibility and localization reliability

## Evidence boundary

本条目由历史对话重构，没有附带原始图像、标注规范、模型版本、日志或评测结果。下列“观察”是待本人和 IP 审查的对话线索，不是已验证数据，也不应被外推为 DMS 系统的一般事实。

## Research question

候选问题：在 IR DMS 场景中，如何判断眼部是否可见、定位是否足以支持后续闭眼判断，从而识别由反光、侧脸、模糊或遮挡造成的不可用 ROI？

## Conversation-derived cues

待核对线索包括：侧脸时关键点可能漂移；遮挡与反光可能干扰局部结构；降低检测阈值可能同时改变召回和假阳性；最终事件误差可能由定位、可见性、分类和时序共同作用。上述陈述尚未绑定样本、版本或指标。

## Competing hypotheses

1. 眼部检测置信度已足以判断 ROI 可用性；
2. heatmap 关键点的峰值或分布不确定性提供额外区分力；
3. 人脸几何、头姿、关键点可见性和清晰度的组合更有效；
4. 显式 visibility/occlusion 任务优于规则组合；
5. 主要误差其实来自下游分类或时序，而非可见性判断。

## Candidate evaluation

先定义“可见”与“可用于闭眼判断”是否为同一标签，并确定人工一致性。若 IP 边界允许，再在合法数据上按反光、侧脸、模糊、遮挡和正常样本分层，比较定位误差、可见性指标、坏 ROI 拦截率、正常 ROI 保留率及最终事件误差。阈值选择和测试集必须隔离，避免用同一数据选阈值又报告结果。

## Next discriminating action

先由本人确认问题、材料权属和标注口径，再用现有输出建立最小基线。只有基线显示可见性是主要误差来源，才承诺训练新模型；否则应回到定位、分类或时序等竞争解释。

## Current conclusion

尚无关于最佳方案的结论。当前仅保留一个待验证区分：“检测到眼睛”与“ROI 足以支持闭眼判断”可能不是同一命题。
