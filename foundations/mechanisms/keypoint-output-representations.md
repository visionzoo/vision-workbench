---
status: working
type: mechanism
rigor: standard
provenance: public-primary-papers-and-pinned-official-code
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-08-03
updated: 2026-08-03
tags: [keypoint, heatmap, coordinate-regression, set-prediction, uncertainty, visibility]
related: [../tasks/2d-landmark-localization.md, ../model-index/families/pfld/README.md, ../model-index/families/hrnet/README.md, ../model-index/families/yolo/README.md, ../model-index/families/detr/README.md]
---

# Keypoint output representations

关键点网络最终都要给出坐标，但“怎样表示坐标”会改变监督密度、空间先验、遮挡处理、解码误差、部署图和可解释信息。本文只维护跨模型可复用的输出表征机制，不维护某个模型的版本事实。

## 1. 总体因果链

```text
image / ROI
→ feature representation
→ instance assignment
→ keypoint representation
→ supervision and loss
→ decode
→ inverse coordinate transform
→ visibility / uncertainty / downstream decision
```

四个候选的差异不仅在 backbone：

| 候选 | 实例分配 | 关键点表征 | 主要训练信号 | 推理输出 |
|---|---|---|---|---|
| PFLD | 外部 face ROI | direct coordinate vector | coordinate + pose/data-imbalance regularization | 固定坐标向量 |
| HRNet heatmap | 外部 face ROI | per-point 2D heatmap | dense heatmap loss | heatmap → coordinate |
| YOLO26 Pose | dense detector assignment + one-to-one branch | anchor-relative coordinate + visibility；训练期 sigma/RLE | box/cls/pose/kobj/RLE | instance boxes + decoded keypoints |
| RF-DETR Keypoint | Hungarian set matching + class-conditioned keypoint queries | x/y/findable/visible/Gaussian precision/class contribution | matching + location/BCE/Gaussian NLL | query instances + keypoints/confidence |

若同时改变实例分配与关键点表征，只能比较完整系统，不能把差异归因给 heatmap 或 regression。

## 2. Direct coordinate regression

### 2.1 表示

```text
feature vector → [x1, y1, x2, y2, ..., xK, yK]
```

坐标可在 ROI 内归一化，也可回归 offset。PFLD 通过轻量卷积、多尺度特征拼接和全连接层直接输出全部人脸点。

### 2.2 优势

- 输出尺寸与点数线性相关，不随 heatmap 分辨率平方增长；
- 不需要 argmax、soft-argmax 或亚像素 decoder；
- 常规 Conv/FC 算子易进入 ONNX、NCNN 和多数 NPU；
- 适合单实例、固定 schema、严格延迟和内存约束。

### 2.3 代价

- 全局向量压缩了空间分布，无法直接观察多峰与模糊峰；
- 遮挡点仍可能输出一个看似正常的坐标；
- crop 偏移和尺度误差会系统性影响所有点；
- 单独坐标 loss 容易被平均误差主导，困难姿态和少数切片需额外加权；
- 若需要 visibility、不确定性或拓扑约束，必须增加独立 head/loss。

### 2.4 适用与反证

适用于：稳定 ROI、固定少量/中量点位、部署预算严格、下游只需要坐标。

反证：在遮挡/反光样本中，坐标误差相近但下游可用性明显不同；或 crop jitter 导致误差显著增大。此时应增加 visibility/uncertainty、改善 ROI 合同，或引入空间分布基线，而不是只加宽网络。

## 3. Heatmap regression

### 3.1 表示

对每个关键点生成二维响应：

```text
K × H_hm × W_hm
```

训练标签通常是在 GT 坐标附近绘制 Gaussian。推理可用 argmax、局部偏移、Taylor refinement、soft-argmax 或分布期望恢复坐标。

### 3.2 为什么有效

- 将一个坐标监督扩展为局部空间监督；
- 卷积输出保持空间对应，适合局部结构定位；
- 峰值位置、宽度、多峰和响应分散可用于诊断；
- 持续高分辨率 backbone 可在较浅空间网格上保留细节。

### 3.3 不能把 heatmap 当作天然概率

MSE/Adaptive Wing 等 heatmap loss 并不自动得到 calibrated probability。峰值受 Gaussian sigma、loss、输出分辨率、图像质量和网络容量共同影响。两个模型的峰值不可在未校准时直接设同一 visibility 阈值。

### 3.4 编码与解码误差

热图路线有三类误差：

1. **representation quantization**：原图连续坐标压到离散网格；
2. **transform bias**：resize、crop、flip、像素中心不一致；
3. **decoder bias**：整数 argmax 或启发式 quarter-offset。

DARK 说明分布感知解码和无偏 Gaussian 编码能在不换 backbone 时改善结果；UDP 说明坐标变换与翻转偏差会造成不公平比较；HIH 则把整数位置与小数 offset 分成两级 heatmap，以减少亚像素量化误差。

### 3.5 资源代价

例如 98 个 64×64 FP32 heatmap 单样本约为：

```text
98 × 64 × 64 × 4 bytes ≈ 1.53 MiB
```

这只是最终输出，不含高分辨率中间激活。INT8 可减小数据量，但 argmax、峰形、近邻差异和亚像素 decoder 可能受量化影响，不能只比较输出 MSE。

## 4. Dense detector + pose head

### 4.1 系统形式

```text
multi-scale features
→ box/class assignment
→ per-location pose channels
→ selected instance
→ keypoint decode
```

常规 Ultralytics Pose 的每个关键点可包含 `x/y/visible`。关键点与检测实例共享正样本分配和框面积归一化，因此漏框、错框、assignment 和关键点误差耦合。

### 4.2 YOLO26 Pose 的具体变化

在固定 Ultralytics revision `81d076f8c38a49126cc1d5be369c8c107ec69789` 中：

- `Pose26` 保留 box/class/pose head，并支持 one-to-many 与 one-to-one 两套分支；
- 每点预测坐标与可见性；
- 训练期额外预测 `sigma_x/sigma_y`；
- `PoseLoss26` 使用传统 location/visibility loss，并增加 RealNVP/RLE residual likelihood；
- 推理 `fuse()` 会移除 sigma head 与 flow model，部署输出仍是坐标/visibility，不直接输出训练期 sigma。

因此，不能把“训练使用不确定性损失”写成“部署模型输出可解释置信区间”。需要不确定性时，应明确保留哪个 head、怎样导出及如何校准。

### 4.3 适用与反证

适用于：整图多人、实例发现与关键点必须一体化、已有 YOLO 数据/工具链、可接受较大输入。

反证：系统已有单人稳定 face ROI，关键点只占小区域；整图模型大部分计算用于无关背景和人体结构。此时应以 ROI 模型为控制，证明一体化方案对漏框、遮挡或工程简化有真实收益。

## 5. Query / set-based keypoint prediction

### 5.1 系统形式

```text
visual features
→ instance queries
→ Hungarian matching
→ matched instance feature
→ class-conditioned keypoint queries
→ structured keypoint slots
```

GroupPose 类方法让每个实例 query 派生一组关键点 query，适合表达人体/对象内部结构。RF-DETR Keypoint Preview 当前采用类似结构，并允许不同类别拥有不同关键点数量。

### 5.2 RF-DETR 当前槽位语义

固定 revision `f50258b07d51efc23771a9418dc13f20de71866b` 的每个关键点槽位有 8 个值：

```text
0 x
1 y
2 findable logit      # annotator could find, v > 0
3 visible logit       # fully visible, v == 2
4 log Lxx
5 Lxy
6 log Lyy
7 class contribution
```

位置 loss 按目标面积归一化；findable 与 visible 分开 BCE；Cholesky 参数定义二维 Gaussian precision，并进入 NLL；关键点成本也可影响 matching。

### 5.3 优势

- 明确区分“能标注”和“完全可见”；
- 二维协方差可表达各向异性定位不确定性；
- 不同类别可有不同点位 schema；
- instance set matching 减少重复实例责任歧义。

### 5.4 风险

- 不确定性参数可能数值发散，源码专门处理 non-finite 值；
- matching cost、instance query 与 keypoint query 同时影响收敛；
- query 数、decoder 深度、resolution、patch/window 共同决定 latency；
- 当前模型为 Preview，接口和 checkpoint 可能变化；
- attention/decoder、动态 schema 和后处理对端侧 NPU 不一定友好。

## 6. Visibility 与不确定性对照

| 信号 | 回答的问题 | 常见误读 | 必要校验 |
|---|---|---|---|
| Heatmap peak | 模型在某位置响应多强 | 等同于可见概率 | reliability curve、slice calibration |
| Heatmap entropy/width | 响应是否分散 | 等同于定位误差 | 与 GT error、模糊/遮挡分层相关性 |
| YOLO keypoint visible logit | 训练标签下点是否存在/可见 | 等同于下游 ROI 可用 | 对 `usable` 单独标注与校准 |
| YOLO26 training sigma | RLE 中残差尺度 | 推理天然输出 uncertainty | 检查 fuse/export 是否保留 |
| RF-DETR findable | 标注者能否定位 | 等同于完全可见 | 与 visible 分开评估 |
| RF-DETR visible | `v==2` | 等同于眼状态可判定 | 与 DMS usable Oracle 对照 |
| RF-DETR covariance | 二维坐标分布尺度/方向 | 等同于真实误差概率 | NLL、coverage、calibration、数值稳定 |

## 7. 受控比较设计

### 7.1 比完整系统

若目标是选择可上线方案，允许四条路线保持各自最合理实现，但结论必须写成：

```text
candidate system + fixed data + fixed runtime/hardware + fixed evaluator
```

不能说“Transformer 比 CNN 更准”或“heatmap 普遍更稳”。

### 7.2 分离输出表征

若目标是研究 heatmap vs coordinate：

- 固定 ROI、数据、backbone capacity、augmentation 和训练预算；
- 用同一 backbone 配 direct regression head 与 heatmap head；
- 或至少加入轻量 heatmap baseline，避免 HRNet vs PFLD 同时改变 backbone；
- visibility head 独立对齐。

### 7.3 分离实例发现

- 同一人工/固定 face ROI 上比较 PFLD 与 HRNet；
- YOLO/RF-DETR 先在同一外部 ROI 模式下评估 keypoint decoder，若实现不支持则标记 full-system-only；
- 另行测整图 detector+keypoint 的漏框和端到端成本。

## 8. 导出与量化

### Direct regression

检查 FC/reshape、坐标范围、输出顺序、FP16/INT8 的小数精度和 inverse transform。

### Heatmap

检查高分辨率输出、upsample、concat、argmax/top-k、峰值相邻差、decoder 是否在图内，以及 INT8 后峰位翻转。

### YOLO Pose

检查 one-to-one/one-to-many 导出分支、框与 keypoint anchor/stride、visibility sigmoid、top-k/NMS、custom `kpt_shape`、RLE sigma 是否被移除。

### RF-DETR Keypoint

检查 decoder、query selection、findable/visible sigmoid、协方差参数、class-specific padded keypoint layout、Hungarian matcher只在训练还是有推理依赖，以及目标 runtime 对 attention/LayerNorm/reshape 的支持。

最小数值对齐不只比较坐标：

- raw keypoint tensor；
- decoded coordinates；
- visibility/findable logits；
- heatmap peak/entropy 或 covariance；
- instance box/query identity；
- top-k/ranking；
- task-level slice metrics。

## 9. 当前判断

- PFLD、HRNet heatmap、YOLO26 Pose 与 RF-DETR Keypoint 是四种系统路线，不是四个同层 backbone；
- 对 DMS 单脸眼部，ROI 模型应作为首要控制；
- heatmap 是空间证据强但资源重的基线；
- YOLO26 Pose 适合一体化多实例，并通过 RLE改善训练，不代表推理输出完整 uncertainty；
- RF-DETR Keypoint 的 findable/visible/covariance 最贴近遮挡研究，但 preview 和部署风险最高；
- 最终采用必须由相同 DMS Oracle 和目标硬件实验决定。

## 10. 主要来源

- [PFLD](https://arxiv.org/abs/1902.10859)
- [HRNet facial landmark implementation](https://github.com/HRNet/HRNet-Facial-Landmark-Detection)
- [Adaptive Wing Loss](https://arxiv.org/abs/1904.07399)
- [DARK](https://arxiv.org/abs/1910.06278)
- [UDP](https://arxiv.org/abs/1911.07524)
- [HIH](https://arxiv.org/abs/2104.03100)
- [Ultralytics Pose26 head @ 81d076f8](https://github.com/ultralytics/ultralytics/blob/81d076f8c38a49126cc1d5be369c8c107ec69789/ultralytics/nn/modules/head.py)
- [Ultralytics PoseLoss26 @ 81d076f8](https://github.com/ultralytics/ultralytics/blob/81d076f8c38a49126cc1d5be369c8c107ec69789/ultralytics/utils/loss.py)
- [RF-DETR keypoint head @ f50258b0](https://github.com/roboflow/rf-detr/blob/f50258b07d51efc23771a9418dc13f20de71866b/src/rfdetr/models/heads/keypoints.py)
- [RF-DETR Keypoint Preview variant @ f50258b0](https://github.com/roboflow/rf-detr/blob/f50258b07d51efc23771a9418dc13f20de71866b/src/rfdetr/variants.py)
- [Group Pose](https://arxiv.org/abs/2308.07313)
