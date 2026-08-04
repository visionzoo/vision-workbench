# Mechanisms

机制页只解释“哪个环节解决什么问题、代价是什么”。一个机制至少应能解释两个模型或两个任务中的现象，否则先留在具体模型页。

当前条目：

- [目标检测的核心因果链](object-detection-core.md)：输入、多尺度表征、标签分配、输出表示、decode 与结果选择；
- [目标检测架构演变](object-detection-architecture-evolution.md)：候选空间、特征组织、监督分配、输出表示、结果选择和语义接口六个轴如何跨 R-CNN、dense detector、DETR 与开放词汇检测演变；
- [Keypoint output representations](keypoint-output-representations.md)：direct coordinate、heatmap、dense pose 与 query/set prediction 怎样改变监督、visibility、不确定性、解码和部署；
- [Bernoulli inclusion sampling](bernoulli-inclusion-sampling.md)：独立包含概率怎样形成随机大小训练子集，以及它与固定大小、分层、分组和重要性采样的边界。

具体模型的版本与实现事实仍归各自 family 页面；具体数据集上的采样收益、训练结果和失败证据归对应 experiment 或 engineering case。
