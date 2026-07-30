---
status: working
type: model-index
rigor: standard
provenance: public-primary-papers-and-official-repositories
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-07-30
updated: 2026-07-30
---

# DETR

DETR 在这里指以 **direct set prediction、object queries、bipartite matching 和 Transformer-style task decoder** 为共同谱系的检测器家族。它不是所有“使用 Transformer 的检测器”的总称，也不是由单一组织连续维护的一条版本线。

> 本条目的 `DINO` 仅指检测器 **DETR with Improved deNoising anchOr boxes**；Meta 的自监督 DINO 属于自监督视觉表征方法，不能因同名混入本家族。

## 1. 家族身份

原始 DETR 由 Facebook AI Research 提出。Deformable DETR、DAB-DETR、DN-DETR、DINO、RT-DETR、LW-DETR、D-FINE、Grounding DINO、RF-DETR 等后续分支来自不同组织，代码、训练配方、backbone、query 定义、decoder、输出语义和部署支持均可能不同。

这个家族的稳定共同点是：

```text
image
→ backbone / visual encoder
→ single-scale or multi-scale visual features
→ optional encoder / projector / feature fusion
→ query initialization
→ task decoder
→ per-query class / box outputs
→ one-to-one set supervision
→ final prediction set
```

并非每个分支都具有相同组件：

- 原始 DETR 使用 CNN backbone 和标准 Transformer encoder-decoder；
- Deformable/real-time 分支通常重构多尺度特征交互；
- 一些分支弱化或替换 encoder，只保留浅层 decoder；
- open-vocabulary 分支把固定分类权重替换为文本或跨模态语义接口；
- 实际 exporter/runtime 可能在图外保留 top-k、threshold、decode，甚至重新加入 NMS。

## 2. 核心范式改变

传统 dense detector 通常在大量 anchor/point 上产生 many-to-one 候选，再依赖 NMS 消除重复框。DETR 把检测写成固定容量的集合预测：

```text
many candidates
+ heuristic assignment
+ duplicate removal
        ↓
fixed queries
+ bipartite one-to-one matching
+ set loss
```

这个改变把“同一目标只能由一个最终预测负责”的约束前移到训练。其收益是输出接口更直接、可减少 anchor 与 NMS 设计；代价是匹配稳定性、query 初始化、多尺度特征、训练收敛和 decoder 计算成为新的主要问题。

## 3. 分支演变不是版本升级表

| 分支 | 主要问题 | 核心变化 | 仍不能直接推出 |
|---|---|---|---|
| DETR | 去掉 anchor/NMS 与复杂检测流水线 | learned queries、global set loss、bipartite matching | 训练快、小目标强、部署简单 |
| Deformable DETR | 标准 attention 对高分辨率特征昂贵，收敛慢 | 多尺度 reference points + sparse deformable sampling | 目标 runtime 原生支持采样算子 |
| DAB-DETR | query 缺少清晰空间含义 | 用动态 box coordinates 表达并逐层更新 query | 与 anchor-based detector 等价 |
| DN-DETR | 早期 bipartite matching 不稳定 | noisy GT reconstruction 辅助任务 | 推理时需要 denoising branch |
| DINO | 进一步提高收敛、query 初始化和框优化 | contrastive denoising、mixed query selection、look-forward-twice | 自监督 DINO 的权重或结论可直接迁移 |
| RT-DETR | DETR 难以进入实时部署 | efficient hybrid encoder、uncertainty-minimal query selection、可调 decoder 层数 | 任意硬件都比 YOLO 更快 |
| RT-DETRv2 | 多尺度采样和部署灵活性 | scale-selective sampling、可选 discrete sampling、训练改进 | 所有 exporter/runtime 已支持相同图 |
| LW-DETR | 降低实时 DETR 结构复杂度 | ViT encoder + projector + shallow DETR decoder | ViT 在边缘设备自动占优 |
| D-FINE | 提升实时 DETR 定位精度 | fine-grained distribution refinement + localization self-distillation | 分布式回归在目标 NPU 上零成本 |
| Grounding DINO | 从闭集走向语言条件检测 | language-guided query selection、cross-modality decoder | 任意 prompt 都有稳定类别定义 |
| OVLW-DETR | 开放词汇 DETR 的部署成本 | 文本类别 embedding 对齐与轻量 DETR | 文本编码器、词表和权重可跨实现混用 |
| RF-DETR | 为目标数据域寻找 specialist accuracy-latency Pareto | 预训练 specialist detector + weight-sharing NAS | 2025 论文结果已被本人或目标硬件复现 |

表中的后续工作解决的是原始 DETR 暴露出的具体瓶颈。它们并不构成唯一主线，也不能只按发布日期视为全面替代。

## 4. 四个不能省略的机制

### 4.1 Query

query 是 decoder 的检测槽位及其内容/位置状态，不是“完全没有空间先验”。不同分支可能使用：

- 纯 learned content query；
- reference point；
- explicit box coordinates；
- encoder-selected proposal/query；
- language-guided query；
- denoising query（仅训练）。

需要核对 query 数、初始化、位置表示、逐层更新和 top-k 选择。query 数不足会限制最大输出容量；query 数增加也会增加 decoder 和 matching 成本。

### 4.2 Bipartite matching

Hungarian matching 为每个 GT 选择唯一 prediction，未匹配 query 学习 no-object。matching cost 与最终 loss 不一定完全相同，通常组合类别与框代价。

它解决重复责任，但会引入：

- 早期预测相近时的匹配切换；
- small/crowded objects 的负责 query 不稳定；
- no-object 比例和 loss 权重敏感；
- auxiliary decoder loss 与最终层目标不完全一致。

DN-DETR/DINO 的去噪训练说明，DETR 的训练效率不仅由 attention 决定，也由 matching 的优化稳定性决定。

### 4.3 Multi-scale visual features

原始 DETR 主要使用低分辨率单尺度特征，小目标表现和训练效率受限。后续分支通过 FPN-like multi-scale features、deformable sampling、hybrid encoder 或 ViT multi-level aggregation修正。

因此“DETR 有全局注意力”不能替代下面的核查：

- 输入后目标有效像素；
- 各 level stride、shape、channel；
- encoder 内交互与跨尺度 fusion 的位置；
- decoder 每个 query 实际采样哪些 level；
- 导出后 reference point、sampling offset 和 interpolation 语义。

### 4.4 One-to-one output contract

`one-to-one` 与 `NMS-free` 是训练和推理接口合同，不是模型名称属性。至少确认：

```text
training matcher
→ auxiliary many-to-one branch?
→ exported head
→ decode / top-k / threshold
→ runtime output
→ external NMS?
```

如果训练时存在 auxiliary one-to-many 分支，导出时必须确认保留的是哪条 head。即使最终无需 NMS，坐标解码、top-k、阈值与 resize 还原仍属于结果生成链。

## 5. 选分支时先问什么

| 需求 | 当前先看 | 为什么 | 采用前必须确认 |
|---|---|---|---|
| 理解集合预测的最小基线 | 原始 DETR + 固定官方实现 | 范式最清楚，便于理解 query/matching | 训练预算、小目标切片、输出合同 |
| 通用闭集高精度 | DINO / Deformable 系 | 多尺度、query 初始化和去噪机制成熟 | 预训练数据、backbone、训练 schedule |
| 实时闭集检测 | RT-DETRv2、LW-DETR、D-FINE、RF-DETR 候选 | 已直接优化 accuracy-latency 与部署 | 目标 runtime 算子、batch=1 latency、端到端链路 |
| 开放词汇或短语 grounding | Grounding DINO / OVLW-DETR | 语言进入 query/decoder 或类别 embedding | prompt 定义、文本编码器、base/novel evaluator |
| 资源受限边缘 NPU | 先做 operator viability，再与成熟 YOLO baseline 比较 | 论文 FLOPs 不能反映 attention/sampling 支持 | export graph、量化、内存、decoder 与后处理 latency |
| 拥挤或重复框问题 | one-to-one DETR 与 assignment/quality-aware dense detector 同时保留 | 问题可能来自 matching，也可能来自 score/NMS | crowd split、query capacity、result-selection 前后错误 |

选择 DETR 不应从“Transformer 更先进”出发，而应从当前系统的候选、匹配、重复抑制、多尺度、语义和部署瓶颈出发。

## 6. 与 YOLO 的有效比较

DETR 与 YOLO 只能在完整 detector 层级比较；不能把 `decoder` 与 `YOLO head`、`ViT encoder` 与完整 YOLO、或跨论文 AP/FPS 直接排名。

最小比较合同：

- 同一 dataset/split、类别、输入和 evaluator；
- 尽量对齐预训练数据、参数规模、训练预算和 augmentation；
- 固定 batch、precision、runtime、硬件和 warmup；
- 同时记录 model-only 与 end-to-end latency；
- 检查 YOLO 的 NMS 与 DETR 的 top-k/decode 是否计入；
- 按 small/medium/large、crowd/occlusion、类别和域切片；
- 记录导出成功率、算子 fallback、峰值内存、量化和稳定性。

若无法对齐预训练或训练预算，只能得出“完整候选系统在该条件下的结果”，不能归因为 CNN、Transformer、one-stage 或 one-to-one 单一因素。

## 7. 工程排查入口

| 现象 | DETR 特有候选解释 | 首轮证据 |
|---|---|---|
| 漏检 | query capacity、query selection、matching、no-object score、多尺度采样 | matched query、各 decoder layer recall、query score、采样点 |
| 重复框 | 实际导出 head 不是 one-to-one、auxiliary branch 泄漏、top-k/score 解释错误 | raw per-query output、head identity、selection 前后结果 |
| 框逐层漂移 | reference point/update、iterative refinement、坐标归一化或 sampling offset | 各 decoder layer boxes、reference points、首个分歧层 |
| 小目标差 | 输入像素、feature level、sampling、query selection | 尺度切片、level contribution、采样位置 |
| PC/板端差异 | attention/sampling/grid_sample、LayerNorm、softmax、量化、输出解释 | 固定输入、相同语义节点、算子 fallback、最终任务指标 |
| 开放词汇不稳定 | prompt tokenization、text embedding、region-text alignment、词表缓存 | 固定 prompt、embedding hash、base/novel 和 synonym 测试 |

通用输入、标签、输出和任务 Oracle 见 [目标检测](../../../tasks/object-detection.md)，跨检测器因果链见 [目标检测核心机制](../../../mechanisms/object-detection-core.md)。

## 8. 当前边界

- 本轮建立的是公开第一方证据支持的信息基线，没有统一训练、COCO 复测、目标硬件或 INT8 实验；
- RT-DETR、LW-DETR、D-FINE、RF-DETR 的论文速度不能跨硬件或跨实现直接比较；
- Grounding DINO/OVLW-DETR 的开放词汇能力不能代表固定私有域的 prompt 稳定性；
- 没有选择仓库的固定 DETR implementation revision，也没有确认目标 NPU 的算子支持；
- 因此条目保持 `working / partial / pending / medium`，下一步应由本人先审查范围，再激活一个有任务与硬件 Oracle 的受控比较。

## 9. 第一方来源

| ID | Source | 主要责任 |
|---|---|---|
| D001 | [DETR paper](https://arxiv.org/abs/2005.12872) / [official repository](https://github.com/facebookresearch/detr) | direct set prediction、object queries、bipartite matching |
| D002 | [Deformable DETR](https://arxiv.org/abs/2010.04159) / [official repository](https://github.com/fundamentalvision/Deformable-DETR) | multi-scale deformable attention |
| D003 | [DAB-DETR](https://arxiv.org/abs/2201.12329) / [official repository](https://github.com/SlongLiu/DAB-DETR) | dynamic box queries |
| D004 | [DN-DETR](https://arxiv.org/abs/2203.01305) / [official repository](https://github.com/FengLi-ust/DN-DETR) | query denoising |
| D005 | [DINO](https://arxiv.org/abs/2203.03605) / [official repository](https://github.com/IDEA-Research/DINO) | improved denoising、query selection、box refinement |
| D006 | [RT-DETR](https://arxiv.org/abs/2304.08069) / [official repository](https://github.com/lyuwenyu/RT-DETR) | real-time hybrid encoder and query selection |
| D007 | [RT-DETRv2](https://arxiv.org/abs/2407.17140) | selective sampling and deployment-oriented improvements |
| D008 | [LW-DETR](https://arxiv.org/abs/2406.03459) / [official repository](https://github.com/Atten4Vis/LW-DETR) | lightweight ViT + shallow DETR |
| D009 | [D-FINE](https://arxiv.org/abs/2410.13842) / [official repository](https://github.com/Peterande/D-FINE) | distribution refinement and localization self-distillation |
| D010 | [Grounding DINO](https://arxiv.org/abs/2303.05499) / [official repository](https://github.com/IDEA-Research/GroundingDINO) | language-conditioned open-set detection |
| D011 | [OVLW-DETR](https://arxiv.org/abs/2407.10655) | deployment-oriented open-vocabulary DETR |
| D012 | [RF-DETR](https://arxiv.org/abs/2511.09554) / [official repository](https://github.com/roboflow/rf-detr) | specialist real-time DETR and weight-sharing NAS |

跨家族的架构演变、anchor-free/assignment 与开放语义关系见 [目标检测架构演变](../../../mechanisms/object-detection-architecture-evolution.md)。
