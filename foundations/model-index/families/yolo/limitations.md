# Limitations

## Family-level limitations

- 密集单阶段检测通常仍受小目标、严重遮挡、模糊、域偏移和标注质量影响；具体程度必须由目标数据验证。
- 多尺度特征并不自动解决低有效像素或不可见目标，输入分辨率提升也可能受算力和训练分布限制。
- NMS-based 分支对置信度、IoU 和类别处理敏感；NMS-free 分支则依赖其匹配、训练和导出实现，不能只凭名称判断行为。
- 官方 COCO 结果不能直接预测 IR、车载、工业或自定义类别表现。

## Evidence and naming limitations

- YOLO 没有统一版本治理机构；相邻编号可能来自不同团队。
- 部分分支主要由源码和文档定义，结构说明可能随 release 改变。
- 官方训练数据、预训练来源、增强细节或导出限制有时未完全披露。
- 聚合网站和第三方博客常把不同 evaluator、硬件和计时范围的数字放在同一表中。

## Deployment failure conditions

- 预处理颜色、range、padding 或 normalization 不一致；
- exporter/runtime/opset 组合变化；
- head decode、DFL、NMS 或 end-to-end 节点不受目标 NPU 支持；
- calibration set 与现场分布不一致；
- INT8 对分类分数、定位分布或小目标产生不可接受损失；
- 只验证单图视觉效果，没有任务级、分层和端到端 Oracle。

## Unknowns in this sample

- 尚未冻结所有来源的具体 commit、release 和权重哈希；
- 尚未逐版本录入完整官方训练 recipe 和指标元组；
- 尚未完成统一硬件、统一 runtime 的独立复测；
- 尚未验证八文件结构对长期维护是否过重。

这些未知项是下一轮核验对象，不应用推断补齐。
