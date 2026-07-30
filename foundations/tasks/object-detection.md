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
updated: 2026-07-30
---

# 目标检测

## 任务定义

目标检测同时回答“图里有什么”和“东西在哪里”。常见任务级输出是：

```text
box + class + confidence
```

网络可能输出稠密候选，也可能直接输出一组最终结果。raw tensor 不是任务定义；标签分配、损失、decode 和结果选择共同把网络输出变成可评测对象。

## 任务契约

- **输入**：颜色、range、尺寸、resize/crop/letterbox、normalization；
- **标注**：框格式、类别、忽略区、遮挡、截断和漏标规则；
- **输出**：坐标格式、分数含义、类别激活、是否 decode、是否包含结果选择；
- **匹配**：预测与标注如何按类别和 IoU 配对；
- **验收**：任务指标、切片、失败样本和错误成本。

缺少其中一项时，不同实现可能在计算“同名指标”时评测不同问题。

## 主要 Oracle

- AP/mAP 必须带数据集、split、IoU 范围、最大检测数和 evaluator；
- precision、recall、F1 必须带 score、IoU 和匹配规则；
- 小目标、遮挡、场景、类别和设备域需要分层；
- 延迟区分模型执行与包含预处理、拷贝、decode、结果选择的视频链路；
- 部署还需观察内存、功耗、温度和连续运行稳定性。

单图视觉效果、loss、张量相似度和转换器报告都不是任务级 Oracle。

## 从任务现象进入排查

| 现象 | 首先确认 | 然后进入 |
|---|---|---|
| 小目标漏检 | 目标像素、标签完整性和尺寸分层召回 | 多尺度特征与标签分配 |
| 框位置偏 | resize/letterbox 和坐标还原 | 回归表示、decode 与网络层首个分歧 |
| 重复框多 | 输出是稠密候选还是 one-to-one | 分数、尺度拼接与结果选择 |
| PC 与板端不同 | 输入输出契约和任务指标确有差异 | 相同语义的中间状态、量化与 runtime |
| 换数据集后掉点 | 类别、尺寸、遮挡、颜色和背景分布 | 数据、预训练失配和训练监督 |

这张表只决定先取什么证据，不直接判定根因。

## 与其他条目的关系

- family 对象与实现事实：[YOLO](../model-index/families/yolo/README.md)、[DETR](../model-index/families/detr/README.md)；
- 跨模型运行机制：[目标检测的核心因果链](../mechanisms/object-detection-core.md)；
- 跨架构演变与比较边界：[目标检测架构演变](../mechanisms/object-detection-architecture-evolution.md)；
- 工程诊断：[模型量化与精度对齐](../../engineering/diagnostics/model-quantization-accuracy-alignment.md)。

本页只维护任务契约和任务级验收。具体分支结构归模型族，真实项目输入、版本、结果和结论归工程案例。本页的任务契约、Oracle 边界和条目关系已于 2026-07-27 通过本人审查；本次只补充 DETR 与跨架构入口，不改变既有接受边界。接受不等于具体模型或工程结果已验证。
