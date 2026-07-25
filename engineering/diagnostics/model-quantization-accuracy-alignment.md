---
title: Model quantization and accuracy alignment
status: working
type: case
created: 2026-07-25
updated: 2026-07-25
confidence: medium
tags: [onnx, rknn, int8, accuracy, deployment]
related: []
---

# Model quantization and accuracy alignment

## Problem

建立从 ONNX 到基于 RKNN Toolkit2 的 INT8 RKNN 的可复现精度验证方法，区分模型转换、量化、预处理、运行时和后处理分别造成的偏差。目标芯片暂以 RV1126B 场景为工作上下文，但方法应尽可能可迁移。

## Goal, constraints, and evaluation

- 同一输入和同一预/后处理下比较 ONNX 与板端 RKNN；
- 同时覆盖中间层数值相似度与最终检测框、分数、类别；
- Run ID、模型版本、转换配置、量化数据集和实体文件可追溯；
- 量化模式、输入尺寸、NV12/RGB、mean/std、容差和 RKNN API 版本尚需在实施前确认。

## Competing explanations

精度下降可能来自：图优化/算子替换、校准集分布、量化参数、输入色彩与范围、布局/缩放、运行时版本、输出反量化或后处理。不能在看到最终 mAP 下降后直接归因于“INT8 精度差”。

## Discriminating evidence

建议按阶段冻结变量：输入字节校验 → FP32 ONNX 基线 → 转换后非量化/模拟量化（若工具链支持）→ INT8 层级 dump → 原始输出 → 后处理结果 → 数据集级指标。每阶段保存哈希和配置。

## Current conclusion

这是需求和诊断框架，不是已完成方案。只有确定工具链可观测能力、板端 dump 成本和评价容差后，才能收敛实现边界。

## Open questions

确认芯片/SDK 版本、模型类型与输出、量化方案、标准输入、评测集、层级 dump 能力、容差和交付 manifest；随后设计最小垂直切片。
