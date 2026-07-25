---
status: working
type: task
rigor: standard
provenance: standard-task-definition-and-owner-practice
evidence_status: partial
owner_review: accepted
ip_review: not-applicable
confidence: medium
created: 2026-07-25
updated: 2026-07-25
---

# 目标检测

## 任务是什么

目标检测要同时回答两个问题：图里有什么，东西在哪里。典型输出是：

```text
box + class + confidence
```

检测器可能输出稠密候选框，也可能直接输出一组最终结果。输出形式不同，会影响标签分配、损失、解码、NMS 和部署方式。

## 先把输入输出说清楚

- 输入：颜色空间、数值范围、尺寸、resize/letterbox、normalization；
- 标注：框格式、类别定义、忽略区、遮挡和截断规则；
- 输出：坐标格式、分数含义、类别激活、是否已经 decode、是否包含 NMS；
- 验收：任务级指标和典型失败样本，不能只看几张图。

## 主要指标

- 常用精度指标是 AP/mAP，但必须带数据集、split、IoU 范围和 evaluator；
- 小目标、遮挡和类别不均衡需要单独分层统计；
- 延迟要区分模型执行和完整链路，完整链路还包括预处理、拷贝、解码和 NMS；
- 模型上线前还要看内存、功耗和连续运行稳定性。

## 常见问题

| 现象 | 先查什么 |
|---|---|
| 小目标漏检 | 有效像素、输入尺寸、多尺度特征、正样本分配 |
| 框位置偏 | resize/letterbox、坐标还原、回归损失、量化误差 |
| 重复框多 | 分数定义、类别处理、NMS 或端到端选择 |
| PC 与板端结果不同 | 预处理、输出解释、算子替换、量化和 runtime |
| 换数据集后掉点 | 类别、尺寸、遮挡、颜色和背景分布是否变化 |

## 与其他条目的关系

- 模型族：[YOLO](../model-index/families/yolo/README.md)
- 核心机制：[目标检测的四个核心机制](../mechanisms/object-detection-core.md)
- 工程诊断：[模型量化与精度对齐](../../engineering/diagnostics/model-quantization-accuracy-alignment.md)

这页只保存任务共性。某个 YOLO 版本的结构放在模型族，真实项目结果放在工程或实验记录。
