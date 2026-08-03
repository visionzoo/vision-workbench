---
status: working
type: model-index
rigor: standard
provenance: public-primary-papers-and-pinned-official-code
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-07-31
updated: 2026-07-31
---

# CLIP (OpenAI reference family)

本条目中的 CLIP 指 OpenAI 在 2021–2022 年公开的 **paired image–text model family**：一个图像编码器、一个文本编码器、共享嵌入空间、可学习温度和一组官方 checkpoint。它既不是 ViT/ResNet 架构族，也不是所有“CLIP-like”视觉语言对齐方法的总称。

> 本仓库只维护 OpenAI reference family 的对象身份、接口和使用边界。OpenCLIP、SigLIP、ALIGN、EVA-CLIP、MetaCLIP、DFN、LiT、CoOp/CoCoOp、开放词汇检测器和通用 VLM 只建立关系，不并入同一版本树。

## 1. 为什么是 model family

CLIP 的权威对象不是单独的 image encoder，也不只是一个 contrastive loss，而是可直接加载和组合的配对模型：

```text
image encoder
+ text encoder
+ image/text projections
+ normalized shared embedding space
+ learned logit scale
+ tokenizer and preprocessing
+ checkpoint identity
```

同一 family 内的图像编码器可以是 Modified ResNet 或 Vision Transformer；因此不能把 CLIP 归入 ViT family。反过来，同一 ViT 架构也可以使用监督学习、DINO、MAE 或其它方法预训练，不能仅凭 backbone 名称推断 CLIP 能力。

在本仓库中：

- `entity_kind` 是 `model-family`；
- CLIP 可以作为固定图文匹配/零样本分类方案，也可以拆出 image encoder 作为 `visual-encoder`；
- image encoder 单独使用时只保留视觉表征，不自动保留文本对齐、prompt 语义或零样本能力；
- contrastive vision-language alignment 是学习范式，不等于每个使用 cosine similarity 的模型都属于 CLIP。

## 2. 家族边界

### 核心 OpenAI checkpoint

固定官方代码当前登记九个模型：

| 官方名称 | 图像侧 | 主要接口差异 |
|---|---|---|
| RN50 | Modified ResNet | attention pooling，基础 CNN 版本 |
| RN101 | Modified ResNet | 更深 CNN |
| RN50x4 | scaled Modified ResNet | 宽度/分辨率/计算按复合规则扩展 |
| RN50x16 | scaled Modified ResNet | 更大 CNN checkpoint |
| RN50x64 | scaled Modified ResNet | 最大官方 CNN checkpoint |
| ViT-B/32 | Vision Transformer | patch 32 |
| ViT-B/16 | Vision Transformer | patch 16 |
| ViT-L/14 | Vision Transformer | 更大 ViT，patch 14 |
| ViT-L/14@336px | Vision Transformer | 固定 336 输入 checkpoint |

这些名称同时约束 architecture、输入分辨率、projection 和 checkpoint；不能把 `ViT-L/14@336px` 当成对任意 `ViT-L/14` 临时修改 resize 的同义词。

### 只建立关系

以下对象可能继承思想、接口或权重兼容性，但不是 OpenAI CLIP 的后续官方版本：

- OpenCLIP 及其独立训练 checkpoint；
- Hugging Face、TorchVision 或其它框架实现；
- ALIGN、LiT、SigLIP、EVA-CLIP、MetaCLIP、DFN 等独立训练谱系；
- prompt learning、adapter、LoRA 和其它适配方法；
- Grounding DINO、OWL-ViT、开放词汇检测/分割等下游系统；
- 将 CLIP image encoder 嵌入通用 VLM、视频模型或机器人系统的组合。

它们只有在改变本条目的官方 artifact identity、加载接口、许可或本人的实际比较合同后才回写本页。

### 明确排除

- ViT、ResNet 架构本身；
- 通用 contrastive learning；
- 自监督 [DINO](../dino-self-supervised/README.md)；
- 文本生成式 VLM；
- 任意名称中包含 `CLIP` 的第三方项目。

## 3. 最小因果链

```text
image
→ RGB / resize / center crop / normalize
→ RN or ViT image encoder
→ image projection
→ L2-normalized image embedding
                                ┐
                                ├→ exp(logit_scale) × cosine similarity
                                ┘
text
→ BPE tokenizer / context length 77
→ causal Transformer
→ EOT representation
→ text projection
→ L2-normalized text embedding
```

训练时，配对图文在 batch 内形成相似度矩阵，并对 image→text 与 text→image 两个方向施加对称 contrastive objective。推理时，官方模型只返回 image/text embeddings 或相似度 logits；“类别概率”“检索结果”“开放词汇检测框”都由额外候选集合和消费逻辑定义。

## 4. 零样本分类不是裸模型输出

CLIP 的零样本分类至少还需要：

```text
class taxonomy
+ class names / descriptions
+ prompt templates
+ tokenizer
+ text embedding aggregation
+ image preprocessing
+ similarity and temperature
+ optional calibration / rejection
```

因此，下列变量都是系统输入，而不是无关文案：

- 类别是否互斥、是否覆盖背景和 unknown；
- 同义词、上位词、细粒度词和否定表达；
- prompt 模板及模板集成方式；
- 语言、拼写、缩写和领域术语；
- 每次运行的候选类别集合；
- softmax 是在固定闭集上计算，还是需要阈值/拒识。

改变候选类别集合会改变归一化后的概率和错误结构。不能只保存模型 hash，却不保存 prompt 与 taxonomy。

## 5. 官方输入输出合同

### 5.1 图像输入

固定官方 loader 返回与 checkpoint 绑定的 transform：

```text
Resize(input_resolution, bicubic)
→ CenterCrop(input_resolution)
→ RGB
→ ToTensor
→ Normalize(
    mean=(0.48145466, 0.4578275, 0.40821073),
    std=(0.26862954, 0.26130258, 0.27577711)
  )
```

真实采用时至少冻结：

- resize/crop 语义；
- RGB 通道和数值范围；
- interpolation；
- input resolution；
- 是否以 letterbox、ROI crop 或非方形输入替代官方合同。

预处理改变后，官方 checkpoint 仍能运行不等于语义保持不变。

### 5.2 文本输入

官方 tokenizer 使用固定词表/BPE，所有公开模型的 `context_length` 为 77。文本编码取 EOT token 位置，经 text projection 得到 embedding。

必须保存：

- 原始文本与规范化后的实际字符串；
- tokenizer revision；
- truncate 策略；
- token IDs 或其 hash；
- prompt 顺序和类别 ID 映射；
- 语言和领域词表。

### 5.3 相似度输出

官方 `forward`：

1. 分别编码 image/text；
2. 对两个 embedding 做 L2 normalization；
3. 计算 `exp(logit_scale) × image_features @ text_features.T`；
4. 返回 image→text 和 text→image 两个 logits 矩阵。

README 中的概率是对候选文本 logits 额外做 softmax 的结果。它不是模型固有、跨 taxonomy 可比较的置信度。

## 6. 从真实需求选择消费方式

| 需求 | 第一候选 | 必须固定 | 首个反证 |
|---|---|---|---|
| 固定闭集零样本分类 | image + cached text embeddings | taxonomy、prompt、preprocess、temperature | 监督分类器在同域显著更稳 |
| 小样本分类 | frozen image features + linear/小型 head | split、probe、特征归一化、调参预算 | 收益来自更大预训练数据而非对齐 |
| 图文检索 | paired embeddings + ANN/精确检索 | gallery、文本粒度、距离、recall protocol | 领域词汇或细粒度实例区分失败 |
| 难例聚类/素材筛选 | image embeddings 或 image–text score | 人工 Oracle、阈值、采样和失败切片 | 可视化相似但任务标签不可分 |
| 开放词汇检测/分割 | CLIP 作为语义接口的完整下游系统 | region adapter、prompt、base/novel evaluator | 结果被 detector/adapter 主导 |
| VLM 视觉编码器候选 | 固定 CLIP image encoder + projector | token/feature接口、projector、训练数据 | 全局 embedding 缺少空间信息 |
| 端侧固定词表分类 | 仅部署 image encoder，预计算文本向量 | embedding hash、归一化、量化误差 | NPU 算子/内存或量化破坏排序 |

本页不把这些使用方式自动激活为实验。

## 7. 与 DINO、监督预训练和 CLIP-like 模型比较

### CLIP vs DINO

CLIP 使用 image–text supervision，DINO 使用无人工类别标签的视觉自蒸馏。有效比较必须固定：

```text
same downstream consumer
+ comparable image architecture/capacity
+ same task data and split
+ same input
+ same adaptation budget
+ explicit pretraining data/availability
+ same evaluator and hardware
```

若 CLIP 用零样本 prompt、DINO 用线性 probe，比较的是两个完整消费方案，不只是预训练方法。

### CLIP vs 监督预训练

至少保留三臂：

1. frozen visual feature + 相同 probe；
2. 相同 adapter/head 与训练预算；
3. 各自最合理的完整系统。

不能把“CLIP 在某个零样本 benchmark 上有效”推广成私有域 ROI 分类、细粒度状态识别或检测 backbone 必然更好。

### OpenAI CLIP vs OpenCLIP / SigLIP 等

只有在 architecture、checkpoint、training data、loss、tokenizer、preprocess、embedding dimension、prompt 和 evaluator 对齐后，才有资格做受控比较。第三方 API 名称兼容不等于 checkpoint 或数值兼容。

## 8. 部署、导出和量化检查

先决定部署的是哪条图：

```text
A. image encoder only
B. text encoder only
C. paired encoders + similarity
D. paired encoders + fixed taxonomy classifier
E. CLIP as a submodule of a larger detector/VLM
```

### image encoder

- RN 与 ViT 的算子、feature topology 和内存行为不同；
- ViT 要核对 patch embedding、positional embedding、LayerNorm、attention 和 projection；
- RN 版本包含 modified stem、anti-aliasing 和 attention pooling，不能按普通 torchvision ResNet 映射；
- 导出全局 embedding 不等于导出可供 dense task 使用的中间 feature。

### text encoder

- context length 77、causal mask、EOT 选择和 text projection 必须保持；
- 固定词表可离线预计算 text embeddings，并把 tokenizer/text encoder 移出设备；
- prompt 或 taxonomy 一旦改变，缓存必须失效并重新生成；
- 缓存至少保存 checkpoint、tokenizer、prompt、类别顺序、dtype、normalization 和 embedding hash。

### similarity 与量化

量化验证不能只看单个 top-1：

- image embedding cosine drift；
- text embedding cosine drift；
- pairwise similarity matrix；
- top-k/ranking stability；
- margin 较小样本的翻转率；
- `logit_scale`、normalization 和 softmax 前后差异；
- 任务级 slice 指标和 reject 行为。

若只部署 image encoder，应把“预计算的 text embedding + classifier semantics”作为独立版本化制品，而不是散落在业务代码中的常量。

## 9. 风险与适用边界

OpenAI model card 将公开 CLIP 定位为研究输出，不把未经特定领域测试的通用部署列为目标用途；它还明确指出：

- 性能和偏差会随 class design 变化；
- 对细粒度分类和计数等任务存在限制；
- 训练和评测主要面向英语；
- 监控和人脸识别使用被列为 out-of-scope；
- 400M 图文训练集未公开，无法完整复现数据身份。

这些是采用门，不是附录。对 DMS、人员相关图像或任何生产系统，必须建立任务级 taxonomy、偏差、拒识、稳定性和责任边界；本页不把官方 benchmark 当作部署许可。

## 10. 当前结论

当前可以成立：

- OpenAI CLIP 是一个可追溯的 paired image–text `model-family`；
- 图像架构、文本编码器、preprocess、tokenizer、prompt、checkpoint 和 similarity 共同定义系统；
- image encoder 可以作为 visual encoder 使用，但单独拆出后不能声称保留完整 CLIP 能力；
- prompt/taxonomy 是版本化接口；
- OpenAI CLIP 与 OpenCLIP、SigLIP 等只能建立关系，不能共享一棵官方版本树。

当前不能成立：

- CLIP 对私有视觉任务普遍优于监督或 DINO 预训练；
- 零样本概率是可跨 taxonomy 比较的校准置信度；
- 任意 ViT/RN checkpoint 都能替换官方 CLIP image encoder；
- 官方论文结果已在本人数据、runtime 或目标 NPU 上复现；
- CLIP 可未经专项验证进入生产或人员相关判断。

因此条目保持 `working / partial / owner_review: pending / medium`。

## 11. 停止维护与拆页规则

默认不因以下变化更新本页：

- 又出现一个名字包含 CLIP 的论文或仓库；
- OpenCLIP/Hugging Face 新增 checkpoint 或别名；
- benchmark 排名变化；
- 新增下游 prompt、adapter、检测器或 VLM；
- 没有进入本人决策的新模型规模。

只有以下变化触发维护：

1. OpenAI 官方 checkpoint、加载接口、model card 或许可发生实质变化；
2. 本人真实任务需要选择 CLIP、DINO、监督预训练或其它对齐方法；
3. 导出、量化或设备实验产生可复用证据；
4. 两类内容出现独立更新频率，且单页已造成至少两次检索/审查返工。

真实实验进入 `engineering/`、`research/` 或独立项目；本页不保存权重、日志、排行榜或运行产物。

## 12. 第一方来源

| ID | Source | 主要责任 |
|---|---|---|
| C01 | [Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020) | 400M 图文对、对称 contrastive learning、zero-shot transfer 与论文评测边界 |
| C02 | [OpenAI CLIP introduction](https://openai.com/index/clip/) | 官方问题定义、方法概览、限制与 broader impacts |
| C03 | [openai/CLIP @ d05afc4](https://github.com/openai/CLIP/tree/d05afc436d78f1c48dc0dbf8e5980a9d471f35f6) | 当前可定位 reference implementation |
| C04 | [`clip/clip.py`](https://github.com/openai/CLIP/blob/d05afc436d78f1c48dc0dbf8e5980a9d471f35f6/clip/clip.py) | 九个 checkpoint、SHA、preprocess、tokenizer/load API |
| C05 | [`clip/model.py`](https://github.com/openai/CLIP/blob/d05afc436d78f1c48dc0dbf8e5980a9d471f35f6/clip/model.py) | RN/ViT image encoder、text encoder、projection、normalization 与 logit contract |
| C06 | [OpenAI CLIP model card](https://github.com/openai/CLIP/blob/d05afc436d78f1c48dc0dbf8e5980a9d471f35f6/model-card.md) | intended/out-of-scope use、数据披露、限制、偏差和语言边界 |

通用比较资格见 [comparison-axes.md](../../comparison-axes.md)，选型与实验门见 [backbone-selection.md](../../backbone-selection.md)。
