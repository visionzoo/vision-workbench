---
status: working
type: model-index
rigor: standard
provenance: public-primary-papers-and-pinned-official-code
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-07-30
updated: 2026-07-30
---

# MobileNet

MobileNet 在这里指 Google 从 **MobileNetV1 到 MobileNetV4** 持续提出的移动视觉架构谱系。它作为 `architecture-family` 维护，可在具体组合中承担 `backbone` 或 `visual-encoder` 角色；它不是“所有轻量网络”的总称，也不是一个可以脱离实现、输入、消费者和目标硬件直接比较的抽象标签。

> 当前判断：MobileNet 值得独立维护，不是因为它拥有很多版本，而是因为它连续改变了空间卷积与通道混合的分工、瓶颈中的信息流、硬件感知搜索目标，以及卷积与注意力在移动模型中的组合方式。真正的工程问题不是“哪一代更新”，而是这些变化在当前任务接口和 runtime 上是否形成可测收益。

## 1. 家族边界

### 1.1 纳入什么

本条目维护：

- MobileNetV1、V2、V3、V4 的架构身份与主要机制；
- V3 Large / Small 以及官方 EdgeTPU 分支；
- V4 Conv / Hybrid 主要配置和面向 dense prediction 的官方配置关系；
- Google 第一方代码中可定位的 MobileNet MultiMAX 等相邻硬件搜索分支；
- 作为 backbone / visual encoder 时必须冻结的接口和部署事实。

### 1.2 不纳入什么

以下对象不能因为都强调移动端或轻量化就并入 MobileNet：

- ShuffleNet、GhostNet、EfficientNet、MobileOne、RepViT 等独立架构谱系；
- MnasNet、NetAdapt 等搜索或平台适配方法本身；
- 任意第三方仓库中名称带 `mobilenet` 的改造；
- 完整检测、分割或关键点系统中的 neck、head、decoder 与任务结果；
- 某个芯片上的转换、量化和延迟结论。

这些对象可以作为来源关系、替代候选或工程案例出现，但不在本页复制其事实。

## 2. 版本演变不是简单升级表

| 分支 | 主要重构 | 核心问题 | 不能由此直接推出 |
|---|---|---|---|
| MobileNetV1 | depthwise convolution + pointwise convolution；width / resolution multiplier | 怎样显著减少标准卷积的计算，并用宽度和输入分辨率控制容量 | depthwise 在任意 NPU 上都更快；缩小宽度只损失少量精度 |
| MobileNetV2 | inverted residual、expansion、depthwise、linear bottleneck；shortcut 连接窄表示 | 怎样在低维瓶颈间保留信息，同时把非线性计算放到扩展空间 | V2 block 在所有小输入或量化条件下都优于 V1 |
| MobileNetV3 Large / Small | platform-aware NAS + NetAdapt；SE、hard-swish；面向不同资源区间的独立结构 | 怎样把搜索目标和实际移动 CPU latency、任务适配结合 | 论文中的移动 CPU 排名可外推到固定功能 NPU |
| MobileNetV3 EdgeTPU | 面向 EdgeTPU 约束重构 block 与算子组合 | 怎样让搜索空间匹配特定加速器 | `EdgeTPU` 名称意味着其他 NPU 也适配 |
| MobileNet MultiMAX | 多硬件架构搜索与共享设计空间 | 怎样减少每种硬件都单独设计网络的成本 | 一个模型会在所有硬件上同时最优 |
| MobileNetV4 Conv | Universal Inverted Bottleneck（UIB）统一多种卷积 block；多硬件搜索 | 怎样在不同移动硬件上形成更通用的纯卷积候选 | V4 Conv 的论文 latency 在目标 runtime 上成立 |
| MobileNetV4 Hybrid | UIB 与 Mobile Multi-Query Attention（MQA）组合 | 怎样在移动预算下引入全局交互 | attention/MQA 已被目标编译器原生高效支持 |
| MobileNetV4 ConvMediumSeg | 官方代码中面向 dense prediction 调整的输出和 stage 配置 | 怎样提供更适合稠密任务的多层特征 | 分类配置可以无修改直接充当检测/分割 backbone |

这里的版本变化同时涉及 block、搜索空间、激活、注意力、输入分辨率、训练与蒸馏配方。跨论文精度或 latency 差值不能单独归因于某个 block。

## 3. 四条稳定机制主线

### 3.1 空间计算与通道混合分离

标准卷积同时处理空间邻域和跨通道组合。V1 将其拆为：

```text
input
→ depthwise spatial convolution
→ pointwise 1×1 channel mixing
→ output
```

理论乘加量下降只说明算术工作减少。真实延迟还取决于 kernel 实现、并行度、内存访问、layout、融合和张量尺寸；因此 `MAdds/FLOPs 更低` 只能成为候选证据，不能成为硬件采用结论。

### 3.2 Inverted residual 与 linear bottleneck

V2 的典型 block 是：

```text
thin input
→ pointwise expansion
→ depthwise spatial filtering
→ linear pointwise projection
→ thin output
```

残差连接位于窄瓶颈之间，而主要非线性计算发生在扩展空间。`linear bottleneck` 的含义不是取消全部激活，而是避免在低维输出瓶颈上继续使用会破坏信息的非线性截断。

进入工程时必须固定：expansion ratio、stride、shortcut 条件、最后一层激活、宽度取整和输出 stage。仅说“使用 inverted residual”不足以绑定实现。

### 3.3 硬件感知搜索与任务适配

V3 不只是给 V2 加 SE 和 hard-swish。其设计把平台 latency 纳入搜索和后续适配，并分别形成 Large / Small；论文还针对检测和分割系统调整网络尾部与任务结构。

这带来两个边界：

1. 搜索结果与目标硬件、runtime 和搜索空间绑定；
2. 完整任务收益包含 backbone、任务适配和训练配方，不能只回写为 MobileNet block 的普遍优势。

### 3.4 UIB、纯卷积与 Hybrid 路线

V4 用 UIB 表达不同位置的 depthwise operations 与 expansion/projection 组合，使多个既有 inverted-bottleneck 形态进入统一搜索空间；Hybrid 变体再加入面向移动约束的 MQA。

因此 V4 不是单一 block：

```text
V4 family
├─ Conv: conv / fused-IB / UIB combinations
└─ Hybrid: Conv path + selected Mobile MQA blocks
```

对目标 NPU，V4 Conv 与 V4 Hybrid 应分别判定比较资格。若 attention、reshape、normalization 或动态行为发生 fallback，Hybrid 的论文复杂度不能替代实际运行证据。

## 4. 官方来源也需要绑定版本与责任

### 4.1 来源优先级

本页采用以下责任划分：

1. **论文**：定义架构问题、机制和作者报告的实验条件；
2. **固定 revision 的官方代码与配置**：定义可定位实现、block spec、endpoint 和可构建配置；
3. **官方概览文档**：用于导航和解释，不覆盖代码中已存在但概览尚未同步的实现；
4. **第三方实现**：只定义该第三方的映射和权重，不自动继承官方实现身份。

### 4.2 已发现的不同步

在 TensorFlow Models 固定 revision `4d7bdd8c170ee90850f2f9ccef0f6d19b817de35` 中：

- `official/vision/modeling/backbones/mobilenet.py` 已包含 MobileNetV1、V2、V3、V4 的 block specs；
- 同 revision 下存在 V4 Conv Small/Medium/Large、Hybrid Medium/Large 和 ConvMediumSeg 配置；
- `official/vision/modeling/backbones/backbones.md` 的 MobileNet 概览仍只写 V1–V3。

因此，概览页不能作为版本完整性的唯一 Oracle。这个发现只要求本条目绑定来源责任和 revision；一次不同步尚不足以新增全仓库规则或自动检查。

## 5. 作为 backbone / visual encoder 的接口合同

使用具体 MobileNet 之前，至少冻结：

| 对象 | 必须确认的事实 |
|---|---|
| 实现身份 | family、variant、官方/第三方仓库、revision、权重 ID/哈希、许可证 |
| 输入 | shape、颜色、range、resize/crop/pad、normalization、batch |
| 缩放 | width multiplier、resolution、channel rounding、最小通道约束 |
| Stem | kernel、stride、padding；小输入时是否修改 |
| Block | block 类型、expansion、kernel、stride、SE、activation、attention/MQA |
| 输出 | endpoint 名称、stage、shape、layout、dtype、channel、stride |
| 消费者 | classifier、neck、head、task decoder 或 projector 的确切实现 |
| 适配 | projection、上采样、融合、额外输出层及其参数/延迟/内存 |
| 导出与运行 | exporter、opset、静态/动态 shape、融合、fallback、量化边界 |

分类器最终 embedding、检测器需要的多尺度 feature maps、关键点需要的高分辨率特征不是同一消费契约。能够从框架取出中间 tensor，不表示该 tensor 已经具备可替换的空间语义与部署接口。

## 6. 部署与量化时优先核查什么

### 6.1 Depthwise 不天然等于低延迟

优先观察：

- depthwise kernel 是否由 NPU 原生执行；
- channel 数、对齐和 feature-map 尺寸是否导致低利用率；
- depthwise + pointwise + BN + activation 能否融合；
- NHWC/NCHW 转换和中间张量搬运；
- 模块 latency 与完整链路 P50/P95/P99。

多硬件 MobileNet 研究明确把硬件和软件栈差异视为设计变量，这本身就是对“低 MAdds 普遍更快”的反证。

### 6.2 激活、SE 和 attention 是独立风险

- V3 的 hard-swish、SE 在不同量化器和编译器上可能采用不同 lowering；
- V4 Hybrid 的 MQA、reshape、softmax/normalization 需要单独检查算子支持和内存；
- 替换激活或移除 SE 后得到的是改造系统，不能继续引用原版指标身份。

### 6.3 输入和缩放会改变完整系统

width multiplier 和 resolution multiplier 同时改变容量、feature shape、下游接口、激活内存和任务可见信息。对 64×64、96×96 等 ROI 输入，默认 stem/downsampling 可能过早压缩局部结构；这必须通过目标任务实验回答，不能由 ImageNet 结果推断。

### 6.4 INT8 接受仍由任务 Oracle 决定

编译成功、张量有限、层级相似度较高只支持定位和筛选。最终仍需：

- 固定 FP32/量化 artifact 与输入；
- 找到首个语义一致的显著偏差边界；
- 检查 per-channel/per-tensor、对称性、校准集和排除层；
- 回到分类、检测或关键点任务指标以及完整链路性能。

## 7. 当前选型入口

| 真实目的 | 首轮候选 | 原因 | 采用前的反证 |
|---|---|---|---|
| 建立最小历史/兼容基线 | V1 | 机制简单，便于检查 depthwise/pointwise 工具链 | 更低算术量是否真的降低目标 runtime latency |
| 成熟轻量 CNN control | V2 | 实现和预训练生态成熟，block 接口清楚 | 小输入、量化和输出 stage 是否适合当前消费者 |
| 移动 CPU 或成熟通用部署候选 | V3 Small / Large | 有明确资源区间和硬件感知设计 | 原论文 CPU 条件是否与目标平台相符；SE/h-swish 成本 |
| 特定 EdgeTPU 路线 | V3 EdgeTPU | 搜索空间面向该加速器 | 非 EdgeTPU 平台不得因名称直接采用 |
| 现代多硬件纯卷积候选 | V4 Conv | UIB 与多硬件搜索提供新的 block 组合 | 官方实现、权重、endpoint、目标 runtime 与 INT8 证据 |
| 卷积 + 全局交互候选 | V4 Hybrid | 在移动架构中引入 MQA | attention 路径是否原生执行，收益是否覆盖内存与调试成本 |
| 检测/分割 backbone | 先看具备明确多层 endpoint 的固定配置 | 稠密任务需要空间层级而非分类输出 | projection/neck 成本、输出 stride、目标尺寸和任务 slice |

这张表只决定先检查谁，不形成跨任务排名。正式比较继续使用 [Backbone / visual encoder comparison contract](../../comparison-axes.md) 和 [Backbone selection under task and deployment constraints](../../backbone-selection.md)。

## 8. 避免白白维护的停止规则

本 family 先且只维护一个 `README.md`。满足以下触发条件前，不拆出 `variants.md`、`deployment.md`、`sources.md` 或单独机制页：

- 同一页面已经承担至少两个会独立更新、且反复妨碍检索或审查的阅读目的；
- 有第二次真实查询或工程修改证明某项信息需要独立权威位置；
- 新机制能够解释至少两个模型族或两个任务，而不只是 MobileNet 版本事实；
- 本人需要在固定任务/硬件上反复执行同一比较或诊断。

以下变化默认不触发维护：

- 第三方框架新增一个别名、权重或排行榜条目；
- 新论文只报告更高指标，但没有改变家族身份、接口、比较资格或采用/撤销条件；
- 另一个轻量网络变得流行；
- 当前没有任务或硬件决策需要的参数表扩充。

当内容长期不改变选型、验证或排查动作，或与 `backbone-selection.md` 总是同步修改，应合并为关系引用而不是保留重复事实。Git 历史保存被替代内容，不为过时版本建立归档页。

## 9. 当前边界与待区分问题

### 当前已支持的判断

1. MobileNet v1–v4 构成可追溯的架构谱系，但每代改变的不只模型规模；
2. “轻量”“低 FLOPs”“mobile”都不能独立授权部署采用；
3. architecture、搜索目标、官方实现、预训练权重、任务适配和硬件结果必须分开归因；
4. V4 Conv 与 Hybrid 在目标 runtime 上需要分别验证；
5. 本页的信息审查不会自动激活训练、下载、导出、量化或板端实验。

### 尚未解决

- 哪个具体实现和权重最适合作为本人的公开可复现 MobileNet control；
- 在 64×64 眼部 ROI、目标检测 backbone 和关键点定位中，最佳 stem 与输出节点是否相同；
- 海思、RKNN 等目标 runtime 对 depthwise、hard-swish、SE、UIB 和 MQA 的真实执行与 INT8 稳定性；
- V4 的收益有多少来自架构、搜索、训练/蒸馏数据和输入设置；
- MobileNet 相对标准残差 CNN、其它轻量 CNN 和结构重参数化候选的真实维护收益。

这些问题只有在固定任务、实现、数据、消费者、runtime 和 Oracle 后才进入实验。

## 10. 第一方来源

访问日期：2026-07-30。论文结果只支持作者披露的条件，不代表本人复现或目标硬件结论。

| ID | 来源 | 主要责任 |
|---|---|---|
| M001 | [MobileNetV1](https://arxiv.org/abs/1704.04861) | depthwise separable convolution、width/resolution multiplier |
| M002 | [MobileNetV2](https://arxiv.org/abs/1801.04381) | inverted residual、linear bottleneck、任务适配示例 |
| M003 | [MobileNetV3](https://arxiv.org/abs/1905.02244) | platform-aware NAS、NetAdapt、Large/Small、SE、hard-swish |
| M004 | [MobileNetV4](https://arxiv.org/abs/2404.10518) | UIB、Mobile MQA、Conv/Hybrid、多硬件搜索与训练配方 |
| M005 | [Discovering Multi-Hardware Mobile Models via Architecture Search](https://arxiv.org/abs/2008.08178) | 硬件/软件依赖、MultiMAX 与多硬件搜索边界 |
| M006 | [MnasNet](https://arxiv.org/abs/1807.11626) | platform-aware NAS 的相邻方法关系，不定义 MobileNet family 全部版本 |
| M007 | [NetAdapt](https://arxiv.org/abs/1804.03230) | 平台适配方法关系，不作为独立 MobileNet 版本 |
| M008 | [TensorFlow Models MobileNet implementation at `4d7bdd8`](https://github.com/tensorflow/models/blob/4d7bdd8c170ee90850f2f9ccef0f6d19b817de35/official/vision/modeling/backbones/mobilenet.py) | 固定 revision 的 V1–V4 block specs、endpoints 与相邻分支实现 |
| M009 | [TensorFlow Models MobileNet configs at `4d7bdd8`](https://github.com/tensorflow/models/tree/4d7bdd8c170ee90850f2f9ccef0f6d19b817de35/official/vision/configs/experiments/image_classification) | V4 Conv / Hybrid 配置身份 |
| M010 | [TensorFlow Models backbone overview at `4d7bdd8`](https://github.com/tensorflow/models/blob/4d7bdd8c170ee90850f2f9ccef0f6d19b817de35/official/vision/modeling/backbones/backbones.md) | 官方概览及其与同 revision 代码不同步的证据 |
