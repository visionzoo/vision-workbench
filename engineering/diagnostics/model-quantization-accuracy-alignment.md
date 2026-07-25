---
title: Model quantization and accuracy alignment
status: working
type: diagnostic
rigor: standard
created: 2026-07-25
updated: 2026-07-25
confidence: low
provenance: conversation-draft
evidence_status: unverified
owner_review: pending
ip_review: pending
tags: [onnx, rknn, int8, accuracy, deployment]
related: [foundations/model-index/families/yolo/deployment.md]
---

# Model quantization and accuracy alignment

## Evidence boundary

本条目由历史对话重构，仅用于保存待确认的问题空间；没有导入原始模型、转换配置、运行日志、板端 dump 或评测结果。下文中的芯片、工具链、目标和诊断路线均待本人核对，不能作为已验证事实或实施承诺。

## Problem

候选问题表征：建立从 ONNX 到量化后设备模型的可复现精度验证方法，区分模型转换、量化、预处理、运行时和后处理分别造成的偏差。RV1126B 与 RKNN Toolkit2 只是当前对话中的候选上下文；实际兼容性必须根据精确 toolkit、runtime、driver 和 SDK 版本验证。

## Goal, constraints, and evaluation

以下是待确认目标，不是已接受需求：

- 同一输入和同一预/后处理下比较 ONNX 与板端输出；
- 同时考虑中间层数值相似度与最终检测框、分数、类别；
- Run ID、模型版本、转换配置、量化数据集和实体文件可追溯；
- 量化模式、输入尺寸、NV12/RGB、mean/std、容差和 API 版本尚未确认。

## Competing explanations

若最终精度出现下降，候选原因包括：输入不一致、图优化/算子替换、校准集分布、量化参数、色彩与范围、布局/缩放、runtime/driver 兼容性、输出反量化或后处理。不能从最终 mAP 差异直接承诺“量化导致”。

## Discriminating action

第一步不是实现整套系统，而是由本人确认真实工具链与输入/输出契约，并取得同一原始输入、ONNX 原始输出和板端原始输出。只有工具链确实支持相应观测时，才考虑逐层 dump；“非量化转换模型”或“模拟量化”也不能在未核实能力前当作必有阶段。

## Required environment record

```yaml
target_soc: rv1126b # conversation candidate; confirm exact identifier
toolkit_version:
runtime_version:
driver_version:
sdk_provenance:
model_commit_or_hash:
preprocess_contract:
postprocess_contract:
```

## Foundation link

模型级部署检查见 [YOLO deployment](../../foundations/model-index/families/yolo/deployment.md)。该页保存通用检查项；本页只在取得真实工具链和原始证据后记录具体诊断。

## Current conclusion

尚无技术结论。当前仅确认：要避免把最终检测差异直接归因于量化，必须先锁定输入、版本和输出解释；其余路线等待原始证据与本人确认。
