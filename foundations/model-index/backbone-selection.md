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
related: [README.md, comparison-axes.md, families/yolo/README.md, families/yolo/architecture.md, families/turingvit/README.md]
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

## 3. 用结构分面覆盖候选，不建立单层分类树

ResNet、CSP、EfficientNet、HRNet、RepVGG 和 Swin 不是同一维度上的互斥类别：它们分别强调连接路径、缩放策略、分辨率组织、部署变换或 token 组织。一个实现可能同时命中多个分面，因此全面性由“选型变量是否覆盖”判断，而不是由模型名单长度判断。

| 分面 | 需要辨别的取值 | 它改变的选型问题 |
|---|---|---|
| 空间组织 | 层级下采样、持续高分辨率、单尺度 token、层级/金字塔 token | 局部细节、全局上下文、输出 stride 和激活内存如何权衡 |
| 基础计算块 | 标准卷积、depthwise / inverted bottleneck、channel shuffle、ghost feature、大核卷积、attention、SSM | 目标 runtime 的真实算子覆盖、带宽、融合和量化代价 |
| 特征与梯度路径 | residual、dense、CSP、ELAN | 梯度传播、特征复用和计算冗余如何组织 |
| 多尺度接口 | 单输出、C2–C5 / P2–P5、并行多分辨率 | neck、head 或 decoder 能否直接消费，适配层成本是否被计入 |
| 缩放与搜索 | 深度/宽度缩放、compound scaling、设计空间或 NAS | 容量收益是否与搜索硬件、输入分辨率和训练配方绑定 |
| 部署变换 | 结构重参数化、算子融合、量化友好设计 | 训练图与推理图是否一致可追溯，转换后精度和延迟是否仍成立 |
| 预训练关系 | supervised、MAE、DINO、CLIP 等 | 权重、数据和学习目标如何影响迁移；它们不是架构类别 |

### 3.1 代表对象映射

| 代表对象 | 主要分面组合 | 进入候选时要验证什么 | 维护边界 |
|---|---|---|---|
| ResNet / ResNeXt / DenseNet | 层级 CNN；residual、grouped 或 dense path | 成熟 control 是否足够；深度、宽度或连接方式是否解决真实误差 | 只在重复比较需求出现后建设 family |
| MobileNet / ShuffleNet / GhostNet | depthwise、shuffle 或 cheap feature generation | 低 FLOPs 是否在目标 NPU 上转化为低延迟；SE、激活和 layout 是否受支持 | 不再用“MobileNet 类”代表全部轻量机制 |
| EfficientNet / EfficientNetV2 / RegNet | 轻量块或标准卷积 + scaling / search | 搜索硬件、输入尺度和训练 recipe 改变后，效率结论是否仍成立 | 缩放/搜索策略与基础计算块分开记录 |
| ConvNeXt | 层级下采样 + 大核 depthwise + 现代训练配方 | 架构收益能否与训练 recipe 分离；LayerNorm/layout 的部署成本 | 不把 GPU 结果直接外推至端侧 NPU |
| CSP / ELAN 系实现 | CSP 或 ELAN 路径 + 多尺度检测接口 | 检测误差是否真由路径组织改善，projection / neck 代价是否固定 | YOLO 中的 CSPDarknet、C2f、ELAN、GELAN 版本事实只在 [YOLO Architecture](families/yolo/architecture.md) 维护 |
| RepVGG / MobileOne / FastViT / RepViT | 结构重参数化，可再叠加 CNN 或 hybrid block | 分支融合是否正确；训练图、导出图、INT8 图和板端结果是否一致 | 作为部署变换分面，不建立互斥“Rep 类”总目录 |
| ViT | 单尺度 patch token + 全局 attention | 小数据、细粒度定位、高分辨率成本和中间节点适配 | visual encoder 能被改造成 backbone，不等于可以直接比较 |
| Swin / PVT / PVTv2 | 层级或金字塔 token + 局部/稀疏 attention | 稠密任务接口、window/reshape/LayerNorm 和目标 runtime 覆盖 | PVT 补足金字塔 Transformer，不把 Swin 当作唯一形式 |
| HRNet | 并行多分辨率 + 重复融合 | 定位收益是否来自持续高分辨率；峰值内存和带宽是否可接受 | 不由关键点结果外推到所有任务 |
| VMamba 等视觉 SSM | 层级表示 + 状态空间计算 | 工具链、算子、量化和目标硬件证据是否足够 | 当前仅为前沿观察，资格为 relation-only，不进入工程实测候选 |

映射只用于防漏和提出假设，不给 family 做静态优缺点排名。具体实现、权重、输出节点和许可证未确定前，比较资格不高于 relation-only；需要 projection、fusion 或节点改造时，按 controlled-adaptation 评价完整组合。

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
- [完整 YOLO family](families/yolo/README.md) 与一个独立 backbone 不能直接排名。

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

## 10. 变更驱动的维护反馈闭环

本条目不是一次性完成的静态指南。每次新增模型、替换实现、记录实测结果或修正分类，都可能暴露新的维护要求；修改者必须在同一次变更中完成影响检查，不能只增加事实而让维护方式滞后。

| 变更触发器 | 必查影响 | 权威落点 | 何时更新本文 |
|---|---|---|---|
| 新增或重命名 backbone / encoder 候选 | 分面、比较资格、接口与许可证是否明确 | 对象事实回 family / registry；通用机制回 mechanisms | 只有选型变量、Gate、采用门或撤销条件发生变化时 |
| YOLO 新版本或内部模块变化 | 是通用机制还是 YOLO 版本实现，是否形成重复事实源 | 版本、C2f/ELAN/GELAN 等采用事实回 YOLO；本文只保留选型关系 | 该变化改变检测 backbone 的候选或验证方式时 |
| 新 runtime、芯片或 INT8 结果 | unsupported op、fallback、量化边界、计时口径是否改变 | 原始结果回 Engineering / Research 案例 | 结果足以修改 Gate 0/3、风险或撤销条件时 |
| 新预训练权重或训练方法 | 收益来自架构、数据、目标还是优化协议 | learning paradigm / 权重来源及具体实验 | 需要改变三臂实验、冻结策略或证据归因时 |
| 新任务、输入或下游消费者 | 原有输出节点、stride 和适配成本是否仍成立 | 任务事实回 tasks，组合事实回案例 | 产生新的任务起点、接口快照字段或区分性实验时 |
| 发现重复、冲突或长期维护成本 | 权威来源、交叉引用和责任边界是否仍清楚 | 保留一个事实源，其他位置改为关系 | 维护边界本身需要修正时 |

每次修改结束前回答六个问题：

1. 这次事实变化是否产生新的维护责任？
2. 哪个文件是唯一权威来源，是否出现复制维护？
3. 比较资格、接口快照、Gate、采用门或撤销条件是否要改？
4. TODO、registry、related links 和 family 边界是否仍一致？
5. 新结论来自公开资料、第三方结果、本人实测还是受限观察？
6. 若无需调整维护方式，PR 中是否明确记录“检查过但无影响”，避免无人判断？

只有真实变更反复触发同一种检查，才把它固化为新字段、模板或自动化；不因一次偶发现象预建空结构。维护反馈本身也接受撤销：若新增规则长期不再区分决策或只制造填写负担，应简化或删除，并保留理由。

## 11. 当前最有价值的三组验证

这不是排期，而是把契约落到常见视觉问题的最小可执行单元：

1. 小 ROI 分类：标准残差 CNN vs 轻量 CNN，固定输入与分类头，验证 stem/downsampling、预训练和 INT8 的实际影响。
2. 局部关键点：HRNet 类高分辨率路线 vs 轻量层级 CNN + 同一 heatmap decoder，先固定坐标与 visibility 链路。
3. 轻量检测：保留当前检测器为完整方案基线；只有误差归因指向特征表征后，才在同一 neck/head 下替换具体 backbone。

这三组分别检验全局/局部分类表征、高分辨率定位表征和多尺度检测表征，足以反向验证本文是否可用；不需要先建立所有 family 页面。

## 12. 事实、推断与未知项

### 第一方事实支持

- ResNet 以残差学习缓解深层网络优化困难；
- MobileNetV3 使用硬件感知搜索和轻量结构，原始目标硬件是移动 CPU；
- EfficientNet 讨论宽度、深度、分辨率的联合缩放，EfficientNetV2进一步引入训练感知搜索与 Fused-MBConv；
- ConvNeXt 是在现代训练和架构设计下重新审视纯 ConvNet；
- ViT 将图像转换为 patch sequence，并依赖大规模预训练展示迁移能力；
- Swin 使用层级结构和 shifted windows 面向通用视觉 backbone；
- HRNet 通过并行多分辨率分支和重复融合维持高分辨率表示。
- CSPNet 以跨阶段部分连接处理梯度信息与计算冗余；它是特征/梯度路径机制，不是与 CNN、Transformer 并列的唯一类别；
- ShuffleNetV2 明确把内存访问和平台特性纳入高效网络设计，GhostNet 用廉价操作生成更多特征图；二者不能被 depthwise 一项完全代表；
- RepVGG 通过结构重参数化把训练期多分支转换为推理期简单结构，因此训练图与部署图必须分别核验；
- PVT 使用逐级缩小的金字塔表示面向稠密预测，说明层级 Transformer 不只有窗口注意力；
- VMamba 提供视觉状态空间路线的第一方机制证据，但当前仓库尚无目标 NPU 工具链与量化证据。

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

## 13. Primary sources

- [ResNet: Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385)
- [MobileNetV3: Searching for MobileNetV3](https://arxiv.org/abs/1905.02244)
- [EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks](https://arxiv.org/abs/1905.11946)
- [EfficientNetV2: Smaller Models and Faster Training](https://arxiv.org/abs/2104.00298)
- [ConvNeXt: A ConvNet for the 2020s](https://arxiv.org/abs/2201.03545)
- [Vision Transformer: An Image is Worth 16×16 Words](https://arxiv.org/abs/2010.11929)
- [Swin Transformer](https://arxiv.org/abs/2103.14030)
- [HRNet: High-Resolution Representations for Labeling Pixels and Regions](https://arxiv.org/abs/1904.04514)
- [CSPNet: A New Backbone that can Enhance Learning Capability of CNN](https://arxiv.org/abs/1911.11929)
- [ShuffleNet V2: Practical Guidelines for Efficient CNN Architecture Design](https://arxiv.org/abs/1807.11164)
- [GhostNet: More Features from Cheap Operations](https://arxiv.org/abs/1911.11907)
- [RepVGG: Making VGG-style ConvNets Great Again](https://arxiv.org/abs/2101.03697)
- [Pyramid Vision Transformer](https://arxiv.org/abs/2102.12122)
- [VMamba: Visual State Space Model](https://arxiv.org/abs/2401.10166)
- [TorchVision feature extraction](https://docs.pytorch.org/vision/main/feature_extraction.html)
