# Mechanisms

机制页只解释“哪个环节解决什么问题、代价是什么”。一个机制至少应能解释两个模型或两个任务中的现象，否则先留在具体模型页。

当前条目：

- [目标检测的核心因果链](object-detection-core.md)：输入、多尺度表征、标签分配、输出表示、decode 与结果选择；
- [目标检测架构演变](object-detection-architecture-evolution.md)：候选空间、特征组织、监督分配、输出表示、结果选择和语义接口六个轴如何跨 R-CNN、dense detector、DETR 与开放词汇检测演变；
- [Keypoint output representations](keypoint-output-representations.md)：direct coordinate、heatmap、dense pose 与 query/set prediction 怎样改变监督、visibility、不确定性、解码和部署。

具体 PFLD、HRNet、YOLO26 Pose 与 RF-DETR Keypoint 的版本和实现事实仍归各自 family 页面。
