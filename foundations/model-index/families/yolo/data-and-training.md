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

## What first-party sources establish

- YOLOv1–v3 的训练数据、预训练与增强应以各自论文和 Darknet 页面为准；不能把现代 Ultralytics 默认训练参数回填到原始版本。
- YOLOv4、Scaled-YOLOv4、YOLOR、YOLOX、PP-YOLO 系列、YOLOv6/7/9/10/12/13、DAMO-YOLO、Gold-YOLO 等由各自论文与作者仓库给出 recipe、配置或权重入口；跨仓库配置名相同不代表 recipe 等价。
- Ultralytics YOLOv5、YOLOv8、YOLO11、YOLO26 的支持任务、训练命令、数据格式和预训练权重以对应 release 的文档、源码和配置为准；当前在线文档可能更新，复现时必须冻结 package version 和配置。
- YOLO-World、YOLOE、YOLOE-26 属于开放词汇路线，必须额外记录检测、grounding、图文等预训练数据，文本编码器/词汇构建、prompt 模式和是否进行词汇重参数化；不能套用闭集 COCO 训练记录。
- YOLO-NAS 等含 NAS、蒸馏或专有搜索过程的模型，应区分已发布网络/权重与未公开的搜索过程；无法复现的部分明确写 `not disclosed`。
- “在 COCO 上报告指标”不自动证明只使用 COCO 训练；必须检查论文、模型卡和仓库是否披露额外数据或预训练。
- 第三方框架迁移的权重不能沿用上游训练描述而不记录迁移、转换或再训练过程。

## Transfer to private datasets

第一方 recipe 是基线而不是通用最优解。迁移时至少重新验证：

- 类别频率、目标尺寸和遮挡分布；
- 输入分辨率与有效目标像素；
- mosaic、mixup、随机裁剪对任务语义的影响；
- anchor、label assignment 与正样本数量；
- 冻结/解冻、学习率和 batch size 的耦合；
- 开放词汇模型的 prompt、负类别、词汇缓存和域内文本表达；
- 训练预处理与部署预处理的一致性。

私人数据集上的经验进入 `research/experiments/` 或 `engineering/cases/`，只把跨任务复现稳定的结论回写 Foundations。
