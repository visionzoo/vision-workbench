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

# DINO (self-supervised)

本条目中的 DINO 指 Meta AI / FAIR 延续的 **self-supervised visual representation method family**：原始 DINO、DINOv2 与 DINOv3。它定义怎样在没有人工类别标签时训练通用视觉表征，不定义某一种固定 backbone 架构。

> 检测器 [DINO](../detr/README.md) 是 **DETR with Improved deNoising anchOr boxes**；两者只共享缩写，不共享权重、训练目标、输出接口或版本谱系。

## 1. 对象身份：方法不是架构

DINO 的长期身份由学习目标、教师—学生更新、视图构造、正则化、数据与蒸馏过程决定：

- 原始 DINO 官方实现覆盖 ViT、XCiT 和 ResNet-50；
- DINOv2 官方基础模型主要是 ViT-S/B/L/g；
- DINOv3 官方套件同时提供 ViT 与 ConvNeXt；
- 同一 ViT 也可使用监督学习、MAE、CLIP 等其它预训练方法。

一个可复现对象至少要绑定：

```text
architecture
+ DINO method version
+ pretraining data
+ size / patch / token contract
+ distillation and adaptation
+ checkpoint hash and license
```

只写“使用 DINO”不足以确定模型。

## 2. 家族边界

### 核心谱系

- **DINO (2021)**：无标签自蒸馏、momentum teacher、multi-crop、centering 与 sharpening；
- **DINOv2 (2023)**：DINO self-distillation、iBOT masked-image modeling、KoLeo regularization、数据筛选、规模化训练与蒸馏；
- **DINOv2 with registers**：在 ViT token 序列加入 register tokens，处理部分高范数 patch artifacts；
- **DINOv3 (2025)**：继续扩展数据与模型规模，引入 Gram anchoring 和高分辨率适配，发布 ViT 与 ConvNeXt backbone 套件。

### 只建立关系

以下不是 DINOv4，也不作为核心版本维护：

- `dino.txt` 等冻结视觉表征后的文本对齐；
- FINO metadata-guided adaptation；
- XRay-DINO、Cell-DINO、Channel-Adaptive DINO 等领域适配；
- CHMv2、深度、分割、跟踪等下游系统；
- Hugging Face、timm 和第三方框架封装；
- 任意使用 DINO 特征的论文、产品或 VLA 系统。

只有它们改变核心方法、官方权重身份、接口或许可时，才回写本页。

### 明确排除

- DETR 检测器 DINO、Grounding DINO；
- ViT、ConvNeXt、ResNet、XCiT 架构本身；
- MAE、MoCo、SimCLR、iBOT、CLIP 等独立方法谱系；
- 无法追溯到 Meta/FAIR 主线的同名模型。

## 3. 演变不是版本排名

| 版本 | 主要问题 | 核心变化 | 不能直接推出 |
|---|---|---|---|
| DINO | 无标签条件下学习可迁移表征 | student/teacher、自蒸馏、multi-crop、centering、sharpening | ViT 必然产生可靠分割；任意规模都稳定 |
| DINOv2 | 扩展为更通用的 frozen visual features | DINO+iBOT+KoLeo、LVD-142M、规模化训练与蒸馏 | 收益只来自 loss；所有领域无需适配 |
| DINOv2 registers | 某些 ViT patch token 出现高范数 artifact | learned register tokens | 所有 ViT、层和任务都需要 registers |
| DINOv3 | 长训练下 dense feature quality 退化并需要更多尺度/架构 | LVD-1689M/SAT-493M、Gram anchoring、高分辨率适配、ViT/ConvNeXt 套件 | 7B 训练可由小规模复现；冻结特征普遍替代专用方案 |
| Adjacent adaptation | 文本、metadata、领域任务需要额外接口 | text alignment、metadata adaptation、task adapters | 它们是核心新版本；收益属于裸 DINO |

跨版本比较必须同时记录 architecture、规模、patch size、registers、训练数据、分辨率、蒸馏、probe 和许可。

## 4. 稳定机制主线

### 4.1 Teacher–student self-distillation

```text
multiple augmented views
→ student predicts teacher distribution
→ teacher follows student by EMA
→ centering / temperature control collapse
→ retain transferable backbone representation
```

teacher 没有人工类别标签，也不是预先固定的监督模型。projection head、temperature schedule、center update、EMA momentum 与 crop 组合共同定义训练行为。

### 4.2 Global/local view 与 token 粒度

Multi-crop 约束不同视图的一致性。ViT 上的 object-like attention 与 patch correspondence 是观察结果，不是损失函数保证。消费特征时至少区分：

- class token；
- patch tokens；
- register tokens；
- 单层或多层组合；
- pooling / normalization；
- resize、crop 与 patch spatial correspondence。

“能返回 token”不等于 token 已适合检测、关键点、分割或跟踪。

### 4.3 DINOv2 是组合式规模化

官方模型卡定义的关键组合是：

```text
DINO self-distillation
+ iBOT masked-image modeling
+ KoLeo regularization
+ curated LVD-142M
+ large ViT training
+ teacher-to-smaller-model distillation
```

因此 DINOv2 的差异同时来自方法、数据、规模、训练工程和蒸馏；不能在无消融时归因给一个“v2 loss”。

### 4.4 Registers 属于接口和权重身份

DINOv2 register 模型的序列是：

```text
CLS + optional registers + patch tokens
```

下游 dense feature 使用必须确认是否移除 registers、如何还原 patch grid，以及 checkpoint 与模型构造是否一致。Registers 是对特定 artifact 的修正，不是所有 ViT 的固定模板。

### 4.5 DINOv3 保存 dense feature

DINOv3 延续 DINO、iBOT 与 KoLeo，并增加 Gram anchoring，以缓解长训练中 dense feature maps 的质量退化；之后进行高分辨率适配和多尺寸蒸馏。

```text
data preparation
→ large-scale pretraining
→ Gram anchoring
→ high-resolution adaptation
→ architecture/size distillation
→ optional task/text adaptation
```

DINOv3 ViT 与 ConvNeXt 共享方法谱系，但 token、feature map、算子和部署接口不同。

## 5. 数据、权重和许可也是身份

| 对象 | 必须冻结 |
|---|---|
| 方法 | DINO / DINOv2 / DINOv2-register / DINOv3 |
| 架构 | ViT、ConvNeXt、ResNet、XCiT；size 与 patch |
| 数据 | 数据集、筛选方式、领域、规模与可披露性 |
| 权重 | 官方/第三方、哈希、distilled、registers |
| 输入 | resize/crop、range、normalization、patch multiple |
| 输出 | CLS、patch、register 或 feature map；层、shape、layout、dtype |
| 适配 | frozen probe、adapter、partial/full fine-tuning |
| 许可 | 代码、基础权重、领域权重、adapter 与衍生发布分别核对 |

许可不能由“同一 GitHub 组织”推定：

- 原始 DINO 仓库已归档，代码为 Apache-2.0；
- DINOv2 基础代码与权重为 Apache-2.0，但同仓领域模型可能另有研究或非商业许可；
- DINOv3 使用独立 DINOv3 License；
- 第三方 Hub 镜像不改变上游许可。

真实采用前必须读取当前模型卡与许可文件。

## 6. 来源责任与时态

1. **论文/技术报告**：定义方法问题、训练组成和报告条件；
2. **固定 revision 的官方代码与模型卡**：定义模型、token/feature 接口、依赖、权重与许可；
3. **官方 README 动态更新**：记录新 adapter 或领域项目，不自动升级为核心版本；
4. **第三方封装**：只定义自身映射和兼容范围。

固定参考点：

- DINO：`7c446df5b9f45747937fb0d72314eb9f7b66930a`，仓库于 2025-08-06 归档；
- DINOv2：`7764ea0f912e53c92e82eb78a2a1631e92725fc8`；
- DINOv3：`6876159a11b4df116f30f667f8c9888617df0751`。

DINOv3 README 在 2026-06-12 增加 FINO metadata-guided training 分支；它是 adjacent release，不是 DINOv4。

## 7. 从真实需求选择消费方式

| 需求 | 第一候选 | 先回答什么 | 不应默认做什么 |
|---|---|---|---|
| 小 ROI 分类 | frozen CLS/pooled feature + linear head | ROI、输入尺寸、域偏移、监督 baseline | 直接全量微调大模型 |
| 检索/聚类/难例发现 | normalized global feature 或 patch aggregation | 距离、索引、slice 与人工 Oracle | 用可视化替代指标 |
| 分割/深度/关键点 | patch/multi-layer features + decoder | patch grid、层选择、spatial alignment、adapter 成本 | 假设最后一层普遍最优 |
| 目标检测 | 固定 DINO backbone + 固定 detector | 多尺度接口、projection、预训练归因、训练预算 | 与完整 YOLO/DETR 直接排名 |
| 视频匹配/跟踪 | frozen patch correspondence baseline | 帧采样、遮挡、漂移、时序 Oracle | 从单帧 attention 推断长期稳定 |
| 文本/开放词汇 | DINO + 独立 text alignment | 文本数据、encoder、alignment head、prompt | 把 DINO 当原生 VLM |
| 端侧部署 | 小型 ViT/ConvNeXt 候选 + operator viability | runtime、precision、memory、fallback | 从参数量或论文 probe 推断板端收益 |

## 8. 与监督预训练、CLIP 的最低比较合同

```text
same downstream architecture and consumer
+ comparable capacity
+ fixed input and task data
+ explicit pretraining data
+ same adaptation budget
+ same evaluator and hardware
```

分别保留：

1. **frozen representation**：相同 probe；
2. **controlled adaptation**：相同 adapter/head 与预算；
3. **best valid system**：允许合理调优，但结论属于完整系统。

DINO 与 CLIP 的数据、监督信号和语义接口不同；结果不能直接推出自监督或视觉语言监督普遍更优。

## 9. 部署与量化检查

### ViT DINO

- patch embedding、positional interpolation、register tokens；
- LayerNorm、attention、softmax、reshape/transpose；
- patch multiple、裁剪行为与 patch-grid 还原；
- 高分辨率 token 数、峰值内存和 latency。

### ConvNeXt DINOv3

- depthwise convolution、LayerNorm layout、stage outputs；
- classification endpoint 与 dense feature maps 的差异；
- 从 ViT teacher 蒸馏不等于运行接口兼容。

### 验收

模型可加载、编译成功和 embedding 相似度只是局部证据。最终仍需固定 artifact 与输入语义，检查首个显著分歧、CPU fallback、下游任务 Oracle、P50/P95/P99 和峰值内存。

## 10. 当前判断与未知项

### 当前判断

- DINO 应作为 method family，而不是 ViT 或“预训练权重”备注；
- DINOv2/v3 不能由单一 loss 解释，数据治理、规模、蒸馏和接口都是核心条件；
- 对当前嵌入式视觉工作，第一步应是 frozen feature baseline 与算子可行性，不是复现大规模自监督训练；
- DINOv3 ConvNeXt 是不同于 ViT 的部署候选，但目标 NPU 上仍无本人证据。

### 竞争解释

下游收益可能来自架构、预训练数据、自监督目标、模型规模、输入分辨率、adapter/head、训练预算或评测偏差；平均指标提高也不保证关键错误 slice 改善。

### 必须实验回答

- 64×64/96×96 ROI 上 patch size 是否过度损失局部信息；
- frozen DINO 相对监督 MobileNet/ResNet 是否改善遮挡、反光等困难样本；
- 哪一层和 token aggregation 适合检测、关键点与难例检索；
- ViT/ConvNeXt DINOv3 在目标 runtime 的 FP16/INT8、内存与 fallback；
- 收益是否覆盖许可、依赖、适配和维护成本。

## 11. 停止维护和拆页规则

不因以下内容更新或拆页：

- 新增一个 DINO 下游论文或排行榜结果；
- Hugging Face/timm 新增别名、镜像或示例；
- 官方增加不改变核心方法、接口或许可的 task adapter；
- 未进入本人决策的领域权重；
- 无受控协议的跨论文性能数字。

只有在以下情况下拆分：

1. 方法演变与权重/工程接口形成两个反复独立更新的阅读目的；
2. 至少两次因单页难以定位同类信息而返工；
3. 某机制需要成为跨两个 family 或任务的权威机制页；
4. 启动真实训练、导出、量化或设备实验时，在 `engineering/` 或独立项目保存制品。

未来若 DINO 名称继续被无共同谱系项目复用，应强化命名消歧，而不是扩大本 family。

## 12. 第一方来源

| ID | Source | 主要责任 |
|---|---|---|
| S01 | [Emerging Properties in Self-Supervised Vision Transformers](https://arxiv.org/abs/2104.14294) / [official DINO repository](https://github.com/facebookresearch/dino) | 原始 DINO、自蒸馏、multi-crop 与 emergent observations |
| S02 | [DINOv2](https://arxiv.org/abs/2304.07193) / [official repository](https://github.com/facebookresearch/dinov2) | 数据筛选、DINO+iBOT+KoLeo、规模化训练与蒸馏 |
| S03 | [Vision Transformers Need Registers](https://arxiv.org/abs/2309.16588) | register tokens 与 high-norm patch artifacts |
| S04 | [DINOv3](https://arxiv.org/abs/2508.10104) / [official repository](https://github.com/facebookresearch/dinov3) / [model card](https://github.com/facebookresearch/dinov3/blob/main/MODEL_CARD.md) | Gram anchoring、高分辨率特征、ViT/ConvNeXt 套件与许可 |
| S05 | [Who Needs Labels?](https://arxiv.org/abs/2606.05107) / [FINO branch](https://github.com/facebookresearch/dinov3/tree/FINO) | metadata-guided adjacent adaptation；不是 DINOv4 |
| S06 | [DINOv2 Meets Text](https://arxiv.org/abs/2412.16334) | post-hoc text alignment；DINO 本身不是原生 VLM |

通用比较资格见 [comparison-axes.md](../../comparison-axes.md)，选型、实验与撤销条件见 [backbone-selection.md](../../backbone-selection.md)。
