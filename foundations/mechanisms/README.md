# Mechanisms

机制页只解释“哪个环节解决什么问题、代价是什么”。一个机制至少应能解释两个模型或两个任务中的现象，否则先留在具体模型页。

当前条目：

- [目标检测的核心因果链](object-detection-core.md)：输入、多尺度表征、标签分配、输出表示、decode 与结果选择；
- [目标检测架构演变](object-detection-architecture-evolution.md)：候选空间、特征组织、监督分配、输出表示、结果选择和语义接口六个轴如何跨 R-CNN、dense detector、DETR 与开放词汇检测演变；
- [Keypoint output representations](keypoint-output-representations.md)：direct coordinate、heatmap、dense pose 与 query/set prediction 怎样改变监督、visibility、不确定性、解码和部署；
- [Visual degradation modeling](visual-degradation-modeling.md)：受控、链路驱动和学习式退化怎样服务鲁棒训练、压力测试与恢复数据构造，以及何时会破坏标签或掩盖输入链路错误。

具体模型、实现版本和设备结果仍归 model family 与 engineering 条目；DMS 中退化和增强的受控实验见 [DMS degradation and enhancement validation](../../research/experiments/dms-degradation-and-enhancement-validation.md)。
