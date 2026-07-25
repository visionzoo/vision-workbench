# Data and training

## Evidence rule

训练信息只记录对应作者明确披露的内容。预训练数据、额外数据、蒸馏教师、增强策略或训练预算没有披露时写 `not disclosed`，不能根据代码默认值或相邻版本推断。

## Version-level record

每个可比较训练记录至少包含：

```yaml
model:
source_revision:
initialization:
training_datasets:
validation_dataset:
image_size:
epochs_or_schedule:
batch_and_hardware:
optimizer:
augmentation:
label_assignment:
distillation:
official_weights:
undisclosed:
```

## What official sources establish

- YOLOv1–v3 的训练数据、预训练与增强应以各自论文和 Darknet 页面为准；不能把现代 Ultralytics 默认训练参数回填到原始版本。
- YOLOv4、YOLOX、YOLOv6、YOLOv7、YOLOv9 和 YOLOv10 的论文与作者仓库分别给出训练 recipe、配置或权重入口；跨仓库配置名相同不代表 recipe 等价。
- Ultralytics 各型号的支持任务、训练命令、数据格式和预训练权重以对应版本文档和发布时的源码为准；当前文档可能随包版本更新，复现时必须冻结 package version 和配置。
- “在 COCO 上报告指标”不自动证明只使用 COCO 训练；必须检查论文、模型卡和仓库是否披露额外数据或预训练。

## Transfer to private datasets

官方 recipe 是基线而不是通用最优解。迁移时至少重新验证：

- 类别频率、目标尺寸和遮挡分布；
- 输入分辨率与有效目标像素；
- mosaic、mixup、随机裁剪对任务语义的影响；
- anchor、label assignment 与正样本数量；
- 冻结/解冻、学习率和 batch size 的耦合；
- 训练预处理与部署预处理的一致性。

私人数据集上的经验进入 `research/experiments/` 或 `engineering/cases/`，只把跨任务复现稳定的结论回写 Foundations。
