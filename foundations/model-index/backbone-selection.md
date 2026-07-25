---
status: working
type: model-index
rigor: standard
created: 2026-07-25
updated: 2026-07-25
confidence: medium
provenance: public-first-party-sources
evidence_status: partial
owner_review: pending
ip_review: not-applicable
tags: [backbone, visual-encoder, transfer-learning, dense-prediction, edge-ai, quantization]
related: [README.md, comparison-axes.md, families/yolo/README.md, families/turingvit/README.md]
---

# Backbone selection under task and deployment constraints

本文解决的不是“哪个 backbone 最强”，而是：在任务、数据、输入、下游接口和目标硬件已经明确时，如何判断瓶颈是否真的在 backbone，并用最小实验选出当前条件下更合适的特征提取方案。

比较资格、指标口径和证据等级以 [Backbone / visual encoder comparison contract](comparison-axes.md) 为准。本文负责把契约落实为选型、实验和撤销流程，不维护跨论文排行榜。

## 1. 先重构问题：选择对象是系统，不是名称

一个 backbone 候选只有放进下面这条链路后才有意义：

input and preprocessing
→ feature extractor
→ selected output nodes
→ projection / fusion
→ neck, head or decoder
→ loss and post-processing
→ runtime and hardware

更换 backbone 会同时改变输出层级、stride、通道数、归一化、预训练权重、优化难度、适配层、算子图和量化误差。若这些变量没有固定或计入，实验只能说明“两个系统不同”，不能说明某个架构普遍更优。

每次启动比较前必须回答：

1. 当前业务误差是什么：分类混淆、定位偏差、小目标漏检、遮挡失效，还是板端超时？
2. 有什么证据表明误差来自表征，而不是标签、ROI、输入像素、head、loss、后处理或数据分布？
3. 下游真正需要的是全局 embedding、单尺度高语义特征、特征金字塔，还是持续高分辨率特征？
4. 目标硬件、runtime、精度、峰值内存和功耗预算是什么？
5. 比较的是架构、预训练、模型容量还是完整方案？一次实验原则上只承诺回答其中一个问题。

## 2. 先排除“换 backbone 也解决不了”的问题

| 观察 | 先检查 | 只有出现什么证据才考虑 backbone | 可推翻 backbone 假设的结果 |
|---|---|---|---|
| 小目标或局部目标漏检 | 有效像素、裁剪、标签一致性、正样本分配、输出 stride、阈值和后处理 | 相同数据与 head 下，更高分辨率或更合适的层级特征稳定提高召回 | 修正标签、ROI、P2/P3 接入或阈值后问题消失 |
| ROI 分类混淆 | ROI 是否包含目标、类别边界、模糊/遮挡、类别不平衡和时间泄漏 | 固定输入和分类头后，不同表征产生稳定且可重复的困难样本差异 | 提高 ROI 质量或重定义标签后，候选差异消失 |
| 关键点漂移 | 标注噪声、坐标变换、heatmap/回归表征、可见性监督和 decoder | 固定输出表征与 decoder 后，高分辨率特征明显降低定位误差 | 更正坐标链或 visibility 后即可恢复 |
| PC 与板端精度不同 | 预处理、导出图、量化、算子替换、布局和后处理 | 层级 dump 显示误差从 backbone 内部开始并随层累积 | backbone 输出一致，误差首次出现在后续模块 |
| 延迟超预算 | 计时边界、CPU fallback、数据搬运、后处理和线程调度 | profiler 证明 backbone 是主要且可优化的耗时/内存来源 | 瓶颈位于预处理、NMS、拷贝或 unsupported op |

这一步的目标是避免“可见的模型名称”吸走注意力。backbone 是高成本变量，只有在更便宜的解释无法说明现象时才进入实验。

## 3. 候选机制地图：用来提出假设，不用来裸排名

| 候选路线 | 主要结构变量 | 适合检验的假设 | 常见适配代价 | 首要风险 |
|---|---|---|---|---|
| ResNet 类残差 CNN | 分阶段下采样、残差块、标准卷积 | 成熟卷积基线是否已经足够；更深/更宽是否带来可复现收益 | 通道投影、选择 C2–C5 输出 | 不是所有硬件上都最快；深度增加可能只增加容量而未解决任务瓶颈 |
| MobileNet 类轻量 CNN | depthwise + pointwise、倒残差、SE、硬件感知搜索 | 严格延迟/内存约束下，是否能保留足够局部表征 | neck 通道补偿、算子融合检查 | 低 FLOPs 不保证低延迟；depthwise、SE 或激活可能在目标 NPU 上不友好 |
| EfficientNet / EfficientNetV2 类 | 宽度、深度、分辨率联合缩放；MBConv/Fused-MBConv | 资源增加时，平衡缩放是否优于只加深或加宽 | 输入分辨率与输出层级需重新核对 | 原论文效率与搜索硬件、训练协议绑定；复用缩放系数不等于复现其 Pareto 前沿 |
| ConvNeXt 类现代 CNN | 大核 depthwise、stage ratio、LayerNorm、现代训练配方 | 在保留卷积层级结构时，现代化设计能否改善迁移 | LayerNorm/layout、算子融合与内存检查 | 训练 recipe 与架构贡献容易混淆；桌面 GPU 结果不能外推到端侧 NPU |
| Plain ViT | patch token、全局 self-attention、单一或少量尺度 | 全局关系与大规模预训练是否解决 CNN 未覆盖的误差 | 中间 token 选择、特征金字塔、position interpolation | 小数据、细粒度定位和高分辨率计算可能需要较强适配；通常不是稠密任务的即插即用替换 |
| Swin 类层级 Transformer | 局部窗口、shifted window、分阶段层级 | 需要层级特征与较大上下文时，窗口注意力是否有增益 | window/shape 约束、neck 对接、导出替换 | window partition、reshape、LayerNorm 和 attention 的真实 NPU 覆盖必须实测 |
| HRNet 类高分辨率网络 | 并行多分辨率分支、重复跨尺度融合 | 定位精度是否受持续高分辨率表征限制 | 多分支输出聚合、较高激活内存 | FLOPs 不能充分表达多分支带宽和峰值内存；不应因关键点结果好就推断所有任务都更优 |
| 新型 linear/hybrid encoder | 线性注意力、混合卷积/attention、动态分辨率 | 高分辨率全局建模能否在目标部署条件下降低成本 | 自定义算子、动态 shape、projection | 第一方理论复杂度或特定 GPU kernel 不能替代目标 runtime 证据 |

这张表只建立“机制—假设—风险”关系。具体实现、权重、输出节点和许可证未确定前，资格均不高于 relation-only。

## 4. 按任务建立第一组候选，而不是建立全家族排行榜

### 4.1 小尺寸图像或 ROI 分类

首轮至少保留两个机制不同、工具链成熟的基线：

- 标准残差 CNN：用于判断一个简单、稳定的卷积基线能达到什么水平；
- 轻量 CNN：用于估计严格部署预算下的精度—延迟损失。

ConvNeXt 或 plain ViT 只有在出现明确假设时加入，例如现有 CNN 对全局结构或长距离关系稳定失效，且预训练与部署预算允许。不能因为 ImageNet top-1 更高就自动进入候选。

对于 64×64、96×96 等小输入，要重新核对 stem 和总下采样：沿用为 224×224 设计的 stride 可能过早丢失局部信息。这里比较的关键往往是有效特征尺寸，而不是参数量。

### 4.2 目标检测

先把当前检测器中的具体 backbone 实现、输出节点、stride、neck 和 head 冻结为基线。只有错误归因显示表征不足，才替换特征提取部分。

- 小目标问题先检查目标像素、标签、P2/P3 接入和正样本分配；
- 候选必须提供与 neck 对接的明确多尺度输出；
- 若新增 projection、upsample 或 fusion，比较资格是 controlled-adaptation；
- 完整 YOLO 与一个独立 backbone 不能直接排名。

### 4.3 2D landmark / keypoint localization

至少区分两条系统路线：

- 持续或恢复高分辨率特征 + heatmap decoder；
- 轻量层级 CNN + heatmap decoder。

若同时把 heatmap 改为坐标回归，实验结论属于完整方案比较。PFLD 之类的回归系统不能直接充当 HRNet backbone 的对照组；要归因 backbone，必须固定输出表征和 decoder。

### 4.4 Visual encoder / VLM 场景

全局图文对齐表示与稠密预测特征不是同一种消费契约。CLIP、plain ViT 或其他 visual encoder 若要进入检测/关键点，需要明确中间节点、token 到 feature map 的空间对应、projection 和 neck。改造后的结果属于“encoder + adaptation”，不能回写为裸 encoder 排名。

[TuringViT](families/turingvit/README.md) 当前只作为高分辨率 visual encoder / backbone 候选关系；代码、权重和目标硬件复现缺失时不进入实测排名。

## 5. 必须冻结的接口事实

每个候选在训练前保存一张接口快照：

| 项目 | 要记录的事实 |
|---|---|
| 实现身份 | family、variant、仓库、revision、权重 ID/哈希、许可证 |
| 输入 | shape、颜色、范围、resize/crop/pad、normalization、batch |
| stem | kernel、stride、padding；小输入是否修改 |
| 输出节点 | 名称、层级、shape、layout、dtype、通道、stride |
| 空间对应 | feature cell 与输入坐标的对应；padding 和插值规则 |
| 消费者 | neck、head、decoder 或 projector 的确切版本 |
| 适配层 | projection、upsample、fusion、pooling 及其参数/计算/内存 |
| 导出图 | exporter、opset、静态/动态 shape、图优化和替换算子 |
| 运行图 | NPU/CPU 子图划分、fallback、量化边界和布局转换 |

“框架能返回 intermediate features”只说明可以取张量，不说明该张量的语义、尺度和部署接口已经可替换。

## 6. 把架构收益与预训练收益拆开

预训练模型通常值得优先使用，但不能把最终收益全部归因于 backbone 架构。至少记录：

- 预训练数据、任务、输入分辨率和权重版本；
- classifier/head 被删除或替换的方式；
- 哪些层冻结，何时解冻，各参数组学习率；
- normalization 是否冻结或重新估计；
- 输入通道、颜色和 domain shift；
- 训练预算、增强、随机种子和重复次数。

### 最小三臂实验

A. 预训练权重 + 全量微调：backbone 使用较小学习率，作为迁移主基线。  
B. 预训练权重 + 短暂冻结 warm-up + 解冻：检验早期 head 不稳定是否会破坏特征。  
C. 随机初始化：在预算允许时作为架构/预训练归因对照，而不是默认生产方案。

“先冻结 15 epoch，再训练 300 epoch”可以是一个候选 protocol，但不能成为所有数据集和模型的固定规则。冻结退出应由可观察条件决定，例如：

- 新 head 的 loss 和梯度已经稳定；
- 冻结验证集指标进入平台期；
- 解冻后没有出现预训练特征被大步长迅速破坏；
- 剩余训练预算足以让 backbone 真正适应目标域。

若 B 优于 A，只能说明当前优化过程受益于 warm-up；若 A 与 B 接近，不应继续为冻结阶段增加复杂度。若 C 接近预训练方案，需要检查 domain gap、权重映射、输入归一化或数据规模，而不是直接宣布预训练无效。

## 7. 四级实验漏斗

### Gate 0：接口与部署可行性

在训练前完成：

1. 构建候选并导出最小图；
2. 验证输入输出 shape、节点和数值；
3. 在目标 runtime 编译；
4. 检查 unsupported op、CPU fallback、静态 shape、内存和布局转换；
5. 用少量公开/自建样本做 FP32/FP16 层级对齐。

无法稳定导出或关键算子回退的候选先降级，不用完整训练来证明编译器问题。

### Gate 1：低成本任务筛选

使用同一小规模、无泄漏的数据子集和同一 head/decoder：

- 固定输入、增强、优化器、训练步数和随机种子；
- 至少一个成熟 CNN control；
- 记录训练稳定性、收敛速度、验证误差类型和初步延迟；
- 只淘汰明显不合适候选，不在短训结果上宣布最终排名。

### Gate 2：受控完整训练

仅让通过 Gate 1 的少量候选进入：

- 相同 train/val/test split；
- 相同数据与任务输出定义；
- 相同或明确折算的训练预算；
- 至少 3 个种子，或明确说明单次试验的不确定性；
- 报告总体指标和关键 slice，而不是只报均值；
- 保存最佳与最终 checkpoint 的判定规则。

如果候选需要不同训练 recipe，先做共同协议比较，再单独做各自合理调优；两组结果不能混成一个结论。

### Gate 3：量化与目标硬件验收

对 FP32/FP16 胜出者执行：

- ONNX/目标格式图一致性；
- 代表性校准集与量化配置；
- 层级相似度和首个显著偏差层；
- 最终任务精度、P50/P95/P99、峰值内存和完整链路时延；
- NPU/CPU 子图、Q/DQ、transpose 和数据搬运分析。

最终采用必须由目标硬件结果决定。FLOPs、参数量、桌面 GPU FPS 和编译成功只能作为前置证据。

## 8. 最小实验矩阵

| Variable group | 必须固定或报告 | 允许变化 |
|---|---|---|
| Problem | task、label、split、slice、metric、error cost | 无 |
| Input | resolution、preprocess、batch、sampling | 只有被明确设为研究变量时 |
| System | neck/head/decoder、loss、postprocess | controlled-adaptation 时允许，并计入候选系统 |
| Training | optimizer、schedule、augmentation、steps、seed | 第二阶段可为各候选单独调优，但须另表 |
| Backbone | implementation、weights、output nodes、freeze policy | 当前主变量 |
| Deployment | hardware、runtime、precision、threads、timing boundary | 无 |
| Evidence | raw logs、config、commit、weight hash、export artifacts | 无 |

建议用两个表保存结果：

1. common-protocol：用于尽量接近架构归因；
2. best-valid-system：用于回答最终工程采用。

两者回答的问题不同，不能只保留对候选有利的一个。

## 9. 采用门与撤销条件

只有同时满足以下条件才形成采用承诺：

- 在目标任务的关键 slice 上有可重复收益；
- 收益不是由输入、预训练数据、head 或额外适配成本暗中引入；
- 目标 runtime 无关键 CPU fallback；
- 量化后的任务损失、P95/P99 和峰值内存仍在预算内；
- 训练、导出、转换和调试成本可由团队持续维护；
- 至少一个机制不同的候选已经被公平反证。

决策记录至少写：

- 当前采用对象和完整组合；
- 为什么不是其余候选；
- 未固定变量与残余风险；
- 证据路径；
- 触发重新评估的条件。

典型撤销触发器包括：关键 slice 收益消失、量化误差越界、runtime 升级后出现 fallback、输入范围变化、预训练权重许可变化，或适配层成本抵消了 backbone 收益。

## 10. 当前最有价值的三组验证

这不是排期，而是把契约落到常见视觉问题的最小可执行单元：

1. 小 ROI 分类：标准残差 CNN vs 轻量 CNN，固定输入与分类头，验证 stem/downsampling、预训练和 INT8 的实际影响。
2. 局部关键点：HRNet 类高分辨率路线 vs 轻量层级 CNN + 同一 heatmap decoder，先固定坐标与 visibility 链路。
3. 轻量检测：保留当前检测器为完整方案基线；只有误差归因指向特征表征后，才在同一 neck/head 下替换具体 backbone。

这三组分别检验全局/局部分类表征、高分辨率定位表征和多尺度检测表征，足以反向验证本文是否可用；不需要先建立所有 family 页面。

## 11. 事实、推断与未知项

### 第一方事实支持

- ResNet 以残差学习缓解深层网络优化困难；
- MobileNetV3 使用硬件感知搜索和轻量结构，原始目标硬件是移动 CPU；
- EfficientNet 讨论宽度、深度、分辨率的联合缩放，EfficientNetV2进一步引入训练感知搜索与 Fused-MBConv；
- ConvNeXt 是在现代训练和架构设计下重新审视纯 ConvNet；
- ViT 将图像转换为 patch sequence，并依赖大规模预训练展示迁移能力；
- Swin 使用层级结构和 shifted windows 面向通用视觉 backbone；
- HRNet 通过并行多分辨率分支和重复融合维持高分辨率表示。

### 当前推断

- 成熟残差 CNN 适合作为 control，不等于它在任何硬件上都最优；
- 轻量 CNN 更值得优先进入端侧候选，不等于低 FLOPs 必然低延迟；
- HRNet 对定位任务有合理机制假设，不等于它能绕过标签、坐标和 decoder 问题；
- Transformer 或 linear attention 可能改善全局建模，不等于能在固定功能 NPU 上高效执行。

### 必须由本人实验回答

- 哪类表征真正改善目标数据的关键错误 slice；
- 固定协议下架构贡献和预训练贡献各占多少；
- 目标芯片对 depthwise、LayerNorm、attention、reshape 和动态 shape 的真实代价；
- INT8 首个显著误差层与最终任务损失；
- 训练与部署收益是否足以覆盖长期维护成本。

## 12. Primary sources

- [ResNet: Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385)
- [MobileNetV3: Searching for MobileNetV3](https://arxiv.org/abs/1905.02244)
- [EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks](https://arxiv.org/abs/1905.11946)
- [EfficientNetV2: Smaller Models and Faster Training](https://arxiv.org/abs/2104.00298)
- [ConvNeXt: A ConvNet for the 2020s](https://arxiv.org/abs/2201.03545)
- [Vision Transformer: An Image is Worth 16×16 Words](https://arxiv.org/abs/2010.11929)
- [Swin Transformer](https://arxiv.org/abs/2103.14030)
- [HRNet: High-Resolution Representations for Labeling Pixels and Regions](https://arxiv.org/abs/1904.04514)
- [TorchVision feature extraction](https://docs.pytorch.org/vision/main/feature_extraction.html)
