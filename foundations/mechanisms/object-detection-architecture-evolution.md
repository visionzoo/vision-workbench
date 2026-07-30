---
status: working
type: mechanism
rigor: standard
provenance: public-primary-papers-and-official-repositories
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-07-30
updated: 2026-07-30
---

# 目标检测架构演变：从候选框流水线到集合预测与开放语义

本文回答的不是“按年份列模型”，而是：**目标检测系统中的哪些职责被共享、学习、删除或重新定义了**。同一时期的检测器会组合不同路线，因此不能把历史压缩成“二阶段 → 单阶段 → Transformer”的单线替代关系。

具体模型版本由 [YOLO family](../model-index/families/yolo/README.md) 和 [DETR family](../model-index/families/detr/README.md) 维护；本页只维护跨模型可复用的架构演变、比较边界与选型问题。

## 1. 先定义这里的“架构”

检测架构不只等于 backbone。至少包含六个相互耦合的对象：

```text
image
├─ candidate space：外部 proposal / dense anchor or point / learned query
├─ shared representation：逐区域重复计算 / 全图共享特征 / 多尺度或 token 表征
├─ supervision：固定规则 / 自适应 many-to-one / bipartite one-to-one
├─ output representation：class + box / quality-aware score / box distribution / query set
├─ result selection：级联筛选 / NMS / learned duplicate suppression
└─ semantic interface：固定类别权重 / region-text embedding / text or visual prompt
```

backbone、neck、head、decoder 只是这些职责在网络图中的实现位置。架构名称相同，也可能因标签分配、输出语义、训练数据、预训练和 runtime 后处理不同而成为不同系统。

## 2. 五条真正稳定的演变轴

| 演变轴 | 早期形态 | 中间形态 | 当前代表形态 | 真正解决的问题 |
|---|---|---|---|---|
| 候选生成 | sliding window、外部 region proposal | RPN、dense anchor、default box | point / keypoint、learned object query | 在巨大位置空间中决定“哪里值得预测” |
| 特征计算 | 每个候选独立提取或分类 | 全图共享 CNN 特征、ROI 特征 | FPN/PAN、多尺度 deformable attention、ViT/hybrid encoder | 避免重复计算，同时保留尺度与上下文 |
| 监督与匹配 | 手工正负规则、固定 IoU 阈值 | adaptive / dynamic many-to-one assignment | Hungarian one-to-one + denoising / auxiliary matching | 决定每个 GT 由谁负责，以及重复预测如何被抑制 |
| 输出与排序 | objectness、class、box 分离 | quality-aware classification、分布式回归 | query-level class/box set、迭代 refinement | 让分数更能表达定位质量，并稳定框回归 |
| 类别语义 | 固定闭集分类权重 | 视觉语言蒸馏、region-text 对齐 | 文本/视觉提示、开放词汇或 prompt-free vocabulary | 从“识别训练时类别”扩展到“按语义描述查找对象” |

这五条轴不是同步前进的。例如 FCOS 去掉 anchor box，但仍使用 dense locations、FPN 和 NMS；原始 DETR 使用 learned queries 与 one-to-one matching，却仍使用 CNN backbone；开放词汇 YOLO 仍可保留 dense one-stage 几何结构。

## 3. 主要阶段及其因果关系

### 3.1 Region-based：先减少候选，再识别

R-CNN 把 region proposal 与 CNN 表征结合，但每个候选重复计算；Fast R-CNN 把整图卷积共享给全部 proposal；Faster R-CNN 再用共享特征上的 RPN 学习候选区域。FPN 进一步把高层语义沿 top-down 路径送到不同空间尺度。

这一阶段留下的长期机制不是“二阶段一定更准”，而是：

```text
共享整图特征
+ 稀疏候选
+ proposal-level refinement
+ 可插拔 ROI task head
```

它适合候选数量可控、需要区域级精修或扩展实例任务的系统，但 proposal、ROI 操作和多阶段调度会增加实现与部署复杂度。

### 3.2 Dense one-stage：把候选铺到特征图上

YOLOv1 把检测重构为单次整图预测；SSD 在多个分辨率特征图上使用 default boxes；RetinaNet 说明 dense detector 的关键障碍之一是极端前景—背景不平衡，并用 Focal Loss 抑制易负样本。

这一阶段真正完成的是：

```text
proposal generation
→ regular dense prediction over feature maps
```

它减少了显式 proposal/ROI 流程，但没有消除候选设计、正负样本定义、框解码和 NMS。现代 YOLO 的高效率还来自 backbone/neck/head、训练配方、算子实现和部署生态，不能只归因于“单阶段”。

### 3.3 Anchor-free：从框模板转向点、角点或距离

CornerNet 用成对角点表达框；FCOS 从特征点回归到四条边。它们减少了 anchor 数量、尺度和宽高比超参数，但没有消除空间先验：stride、FPN level、中心采样、回归范围和匹配规则仍然决定监督。

ATSS 的受控比较进一步表明，在其设置下，anchor-based 与 anchor-free 的主要性能差异很大程度来自正负样本选择，而不是“从 box 回归还是从 point 回归”本身。因此：

> `anchor-free` 是候选几何描述，不是完整架构，也不能替代标签分配说明。

随后 GFL、VarifocalNet、TOOD、OTA/SimOTA 等工作把重点转向定位质量、分布式框表示、分类—定位对齐和动态匹配。现代 dense detector 的核心竞争已从“有没有 anchor”转为“谁负责 GT、分数如何排序、框不确定性如何表达”。

### 3.4 DETR：把检测改写为集合预测

DETR 用固定数量的 object queries、Transformer encoder-decoder、bipartite matching 和 set loss 直接输出预测集合，把重复框消除更多地放到训练目标中。其范式变化是：

```text
dense candidates + heuristic duplicate removal
→ fixed-size prediction set + one-to-one responsibility
```

原始 DETR 的慢收敛和小目标问题说明，删除手工组件并不等于删除结构先验。Deformable DETR 引入多尺度稀疏采样；DAB-DETR 把显式 box coordinates 作为 query；DN-DETR 用去噪任务缓解早期匹配不稳定；DINO 组合 query 初始化、去噪和迭代框优化。

这条谱系实际上经历了“去先验 → 重新引入可学习或显式空间先验”的回摆。详细分支与来源见 [DETR family](../model-index/families/detr/README.md)。

### 3.5 Real-time DETR：端到端开始进入部署竞争

RT-DETR 通过高效 hybrid encoder 和 query selection 把 DETR 推向实时检测；RT-DETRv2 继续处理多尺度采样与部署算子；LW-DETR 采用 ViT encoder、projector 和浅层 decoder；D-FINE 重新设计 DETR 的分布式框回归；RF-DETR 则把 specialist detector 的 accuracy-latency 组合纳入权重共享 NAS。

这说明“CNN 负责实时、Transformer 负责高精度”的旧二分已经失效，但不能反向推出 DETR 已普遍优于 YOLO。真实部署仍取决于：

- attention、sampling、grid_sample 等算子是否被目标 runtime 原生支持；
- decoder 层数、query 数和多尺度特征的实际 latency；
- 模型图内外是否仍有 decode、threshold 或 NMS；
- 训练预算、预训练数据和输入分辨率是否一致；
- FPS 是否包含预处理、数据拷贝和结果输出。

### 3.6 Open-vocabulary / promptable：类别头变成语义接口

ViLD 用视觉语言教师把开放词汇知识蒸馏到区域检测器；GLIP 联合 grounding 与 detection；Grounding DINO 把语言引导的 query selection 和跨模态 decoder 引入 DINO；YOLO-World 与 YOLOE 则把开放词汇、文本/视觉提示和实时 dense detector 结合。

这不是简单地把 `Linear(num_classes)` 换成文本 embedding。系统同时改变了：

```text
category source
+ region-text alignment
+ pretraining data
+ prompt encoder / vocabulary cache
+ zero-shot / base-novel evaluation
+ runtime dependency
```

闭集专用检测器在固定类别、有限硬件和稳定数据域中仍可能更简单、更快、更可控；开放词汇能力只有在类别变化、长尾、快速迁移或语义查询确实产生价值时才值得承担额外复杂度。

## 4. 需要纠正的六个常见叙事

1. **“二阶段被单阶段淘汰”**：两者是候选与精修组织方式，不是时间上的胜负关系。
2. **“anchor-free 没有先验”**：它仍依赖 point、stride、level、center/range 和 assignment。
3. **“DETR 就是纯 Transformer”**：原始 DETR 使用 CNN backbone，许多实时 DETR 是 CNN/Transformer hybrid。
4. **“NMS-free 等于无后处理”**：仍可能有 decode、top-k、threshold、坐标还原，导出器或 runtime 也可能重新加入 NMS。
5. **“开放词汇只改分类头”**：语义空间、数据、对齐、提示接口和评测协议都发生变化。
6. **“新架构指标更高，因此适合迁移”**：跨论文 AP/FPS 混入了数据、预训练、输入、训练预算、实现和硬件差异，不能直接归因架构。

## 5. 从任务约束反推架构

| 真实约束 | 优先检查的路线 | 先保留的反例 |
|---|---|---|
| 低功耗 NPU、INT8、算子受限 | 成熟 dense CNN one-stage；再测试 one-to-one YOLO 或 real-time DETR | 理论 FLOPs 低但 attention/sampling/runtime 慢 |
| 拥挤、遮挡、重复框难消 | one-to-one set prediction、quality-aware score、crowd-aware assignment | query 数不足、匹配不稳或召回下降 |
| 小目标 | 输入有效像素、P2/P3、多尺度特征、采样与分配 | 换更大 backbone 但目标在早期已不可分 |
| 固定少量类别 | 闭集 specialist detector | 开放词汇模型引入无用语义与 runtime 成本 |
| 类别经常变化或长尾 | Grounding / open-vocabulary detector | prompt 变化造成定义漂移，novel 类定位不稳定 |
| 数据少但有通用预训练 | 强预训练 + 受控微调 | 收益来自预训练数据而非 detector architecture |
| 需要跨平台部署 | 固定导出图、算子、decode 与 end-to-end latency | 论文 FPS 或框架内 benchmark 无法复现 |

选型时先固定任务、数据、输入和硬件 Oracle，再决定候选空间。不能从“YOLO / DETR / open-vocabulary”名称直接跳到采用结论。

## 6. 架构比较的最小受控协议

### 6.1 固定非目标变量

- dataset、split、类别和忽略规则；
- 输入尺寸、resize/letterbox、颜色与 normalization；
- 预训练来源和训练数据可见范围；
- augmentation、epoch/iteration、optimizer 与 batch；
- evaluator、score/IoU、max detections；
- runtime、precision、batch、硬件、warmup 和 latency 范围。

### 6.2 记录架构语义

- candidate：proposal、anchor、point 还是 query；
- matching：many-to-one 还是 one-to-one，正样本如何决定；
- representation：box offset、point distance、distribution 或 iterative refinement；
- selection：NMS、top-k、one-to-one，位于模型内还是外；
- semantics：fixed classes、text embedding、visual prompt 或 built-in vocabulary。

### 6.3 观察能区分机制的证据

- 每个 GT 的负责候选/query 数和匹配稳定性；
- 各尺度/各 decoder layer 的 recall 与定位误差；
- classification score 与 IoU 的相关性；
- result selection 前后的候选数、重复框和漏检；
- small/medium/large、crowd/occlusion、base/novel 等切片；
- 导出算子、峰值内存和端到端 latency breakdown。

只有任务级指标、目标硬件结果和机制证据共同支持时，才把收益归因于架构变化。

## 7. 当前结论与边界

- 目标检测没有收敛为单一架构；dense CNN、region-based detector、DETR 和 open-vocabulary detector 在不同约束下并存。
- 更稳定的长期主线是：**减少重复计算 → 改善多尺度表征 → 重构正样本责任 → 对齐分类与定位 → 学习结果去重 → 开放类别语义**。
- `one-stage / two-stage`、`anchor-based / anchor-free`、`CNN / Transformer` 都只是分面，不能单独决定性能或工程价值。
- 本页只基于公开第一方论文和仓库建立信息基线，没有进行统一数据、统一训练或统一硬件复测；因此保持 `working / partial / medium`，等待本人审查。

## 8. 第一方证据

| ID | 负责支持的事实 | 第一方来源 |
|---|---|---|
| ODA001 | region proposal + CNN | [R-CNN](https://arxiv.org/abs/1311.2524) |
| ODA002 | shared full-image convolution for proposals | [Fast R-CNN](https://arxiv.org/abs/1504.08083) |
| ODA003 | learned RPN sharing convolutional features | [Faster R-CNN](https://arxiv.org/abs/1506.01497) |
| ODA004 | top-down multi-scale semantic pyramid | [FPN](https://arxiv.org/abs/1612.03144) |
| ODA005 | unified single-pass regression | [YOLOv1](https://arxiv.org/abs/1506.02640) |
| ODA006 | multi-scale default-box dense detection | [SSD](https://arxiv.org/abs/1512.02325) |
| ODA007 | foreground-background imbalance and Focal Loss | [RetinaNet](https://arxiv.org/abs/1708.02002) |
| ODA008 | paired-keypoint anchor-free detection | [CornerNet](https://arxiv.org/abs/1808.01244) |
| ODA009 | per-pixel point-to-box regression | [FCOS](https://arxiv.org/abs/1904.01355) |
| ODA010 | assignment as the main anchor-based/free difference under controlled settings | [ATSS](https://arxiv.org/abs/1912.02424) |
| ODA011 | joint quality/class score and distributed box representation | [GFL](https://arxiv.org/abs/2006.04388) |
| ODA012 | classification-localization task alignment | [TOOD](https://arxiv.org/abs/2108.07755) |
| ODA013 | optimal-transport global assignment | [OTA](https://arxiv.org/abs/2103.14259) |
| ODA014 | vision-language distillation for open vocabulary | [ViLD](https://arxiv.org/abs/2104.13921) |
| ODA015 | unified grounding and detection pretraining | [GLIP](https://arxiv.org/abs/2112.03857) |
| ODA016 | language-conditioned DINO detector | [Grounding DINO](https://arxiv.org/abs/2303.05499) |
| ODA017 | real-time open-vocabulary YOLO | [YOLO-World](https://arxiv.org/abs/2401.17270) |
| ODA018 | text, visual and prompt-free open-vocabulary interfaces | [YOLOE](https://arxiv.org/abs/2503.07465) |

DETR 内部演变的第一方来源统一维护在 [DETR family](../model-index/families/detr/README.md)，YOLO 分支身份与实现来源统一维护在 [YOLO sources](../model-index/families/yolo/sources.md)。
