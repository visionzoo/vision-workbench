---
status: working
type: model-index
rigor: standard
provenance: public-primary-papers-and-pinned-official-code
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-08-03
updated: 2026-08-03
---

# HRNet

HRNet（High-Resolution Network）在本仓库中是 **architecture family**：它从早期阶段开始并行维护多种空间分辨率，并在各 stage 之间重复交换信息，而不是先把图像压到低分辨率再单次上采样恢复。

本页同时记录官方 HRNet facial landmark heatmap 实现，作为该架构进入 2D 人脸关键点任务的具体组合。HRNet 本身不等于 heatmap，HRNet-W18 + 98 heatmaps 也不等于所有 HRNet 关键点系统。

## 1. 对象身份

```text
high-resolution branch
+ progressively added lower-resolution branches
+ repeated cross-resolution fusion
→ multi-resolution feature set
```

Registry 建议：

- `entity_kind: architecture-family`；
- `usage_scopes: [reusable-module, pretraining-source]`；
- `module_roles: [backbone]`；
- `tasks: []`，因为架构可用于 pose、face alignment、segmentation、detection 等，任务属于具体组合。

当 HRNet 接 heatmap head 时，完整系统为：

```text
face ROI
→ HRNet multi-resolution backbone
→ resize lower-resolution branches to high resolution
→ concatenate
→ convolutional heatmap head
→ K heatmaps
→ decoder / inverse transform
```

## 2. 稳定架构机制

### 2.1 并行多分辨率

传统层级 CNN 通常：

```text
1/4 → 1/8 → 1/16 → 1/32
```

HRNet 则保留高分辨率主分支，并逐步增加低分辨率分支：

```text
stage 2: 1/4, 1/8
stage 3: 1/4, 1/8, 1/16
stage 4: 1/4, 1/8, 1/16, 1/32
```

高分辨率分支保留局部位置，低分辨率分支提供更大上下文。这个组织改变的是 feature topology，不保证某个任务必然更准。

### 2.2 重复跨尺度融合

每个 HighResolutionModule 对各分支分别做 residual blocks，再把其它分支变换到目标尺度后求和：

- 低→高：1×1 channel projection + bilinear interpolation；
- 高→低：一系列 stride-2 3×3 convolution；
- 同尺度：identity；
- 融合后 ReLU。

因此部署时必须核对 interpolation、align_corners、连续 downsampling、branch channel 和 sum 顺序。论文中的 FLOPs 不足以表示目标 NPU 的带宽和激活代价。

## 3. 官方 W18 face alignment 实现

固定官方仓库 revision：

```text
HRNet/HRNet-Facial-Landmark-Detection
@ f776dbe8eb6fec831774a47209dae5547ae2cda5
```

WFLW W18 配置：

- input：256×256；
- keypoints：98；
- heatmap：64×64；
- Gaussian sigma：1.5；
- pretrained：HRNetV2-W18 ImageNet；
- stage channels：18/36/72/144；
- stage 4 保留四个分辨率；
- 最终把后三路 bilinear resize 到第一路大小并 concatenate；
- 1×1 Conv/BN/ReLU + final Conv 输出 98 heatmaps；
- 训练 60 epochs、Adam、初始 LR 1e-4（该配置的历史默认，不是现代最佳实践）。

该 repo 最后公开更新停留在 2020 年，依赖示例是较老的 PyTorch/Python/CUDA。它适合确认架构和原始实验，不适合作为当前工程环境的直接模板。

## 4. Heatmap head 不是 HRNet 固有属性

HRNet 可以输出：

- 最高分辨率 branch；
- 多分辨率 feature list；
- concatenated feature；
- classification pooled feature；
- heatmap、segmentation 或其它 dense head。

因此，以下比较不成立：

```text
HRNet vs PFLD = heatmap vs regression
```

因为它同时改变 feature extractor 和 output representation。要归因 heatmap，需要固定 backbone 或增加轻量 CNN + heatmap control；要归因 HRNet，需要固定 heatmap head、loss、decoder 和输入。

## 5. Heatmap 训练与解码

原始 HRNet face alignment 常用 Gaussian target + MSE 类损失。后续研究表明，关键差异可能来自 head 之外：

- Adaptive Wing Loss：提高前景和困难背景像素权重；
- DARK：分布感知坐标解码与更准确 heatmap 编码；
- UDP：修正 resize/flip/坐标变换的系统偏差；
- HIH：用 integer + decimal heatmap 减少亚像素量化误差；
- boundary/occlusion auxiliary supervision：增加几何或可见性信息。

任何 HRNet 指标必须绑定 loss、heatmap size、sigma、decoder、flip test、bbox、normalization 和 test-time augmentation，不能只写 `HRNet-W18`。

## 6. 公开数据和困难切片

官方 face alignment repo覆盖：

- 300W；
- AFLW；
- COFW；
- WFLW。

WFLW 提供 pose、expression、illumination、makeup、occlusion、blur 子集，对 DMS 研究有两个价值：

1. 强制按困难属性而非总体 NME 分析；
2. 98 点包含更细人脸和眼部轮廓。

但其 RGB in-the-wild 分布不能替代车内 IR、眼镜红外反射、极小眼部、压缩视频和报警时序。

## 7. 工程案例与可迁移教训

### 7.1 官方 WFLW pipeline

这是一个典型 top-down face alignment pipeline：先给 face box，再 affine/crop 到固定输入，最后 inverse transform。可迁移教训是：HRNet 的精度依赖 bbox 与坐标链；它并不自行解决 face detection。

### 7.2 MMPose modern integration

MMPose 把 HRNet 与多种 codec、loss、数据集和 evaluator 组合，说明现代工程中“HRNet”只标识 backbone，完整配置仍需冻结：

```text
backbone + head + codec + loss + data pipeline + evaluator
```

MMPose 的实现/权重可以作为第三方工程候选，但不能反过来定义原始 HRNet family。

### 7.3 Slimming / distillation

已有工作尝试剪枝、蒸馏和轻量 HRNet，说明原始高分辨率激活是实际部署瓶颈。采用任何 `Lite-HRNet`、`HRNet-lite` 或裁剪版本时，应建立独立对象关系，不能把其速度归给原始 W18。

### 7.4 DMS/occlusion

Occluded Stacked Hourglass、Adaptive Wing Loss 等案例说明 heatmap 可同时接 visibility/occlusion 辅助监督。对 DMS，HRNet heatmap 的真正研究价值不是只追求 NME，而是观察：

- 峰值是否多峰/扩散；
- 反光和遮挡下 entropy 是否增加；
- visibility head 是否比 peak threshold 更可靠；
- heatmap 与 `usable_for_eye_state` 是否相关。

## 8. 适用场景

### 优先考虑

- 单实例 ROI 已知；
- 关键点细粒度、局部结构重要；
- 需要空间响应和失败诊断；
- GPU/服务器或目标硬件能承担高分辨率激活；
- 精度上限/研究 baseline 优先于最小延迟；
- visibility/occlusion 辅助 head 可带来业务价值。

### 谨慎

- 严格边缘 NPU 内存/带宽预算；
- 多实例整图且每个实例都要重复 crop；
- 输出点数和 heatmap 很多；
- exporter 对 bilinear resize/concat/动态 shape 支持弱；
- 只需要粗 ROI，不需要细粒度空间分布；
- 训练数据不足以支撑大容量和困难切片。

## 9. 与 PFLD、YOLO26 Pose、RF-DETR Keypoint 的关系

| 对象 | 与 HRNet heatmap 的差异 | 有效比较 |
|---|---|---|
| PFLD | 轻量 direct coordinate ROI model | 同 ROI/schema/data/evaluator 的完整系统；另设同-backbone双 head 归因 |
| YOLO26 Pose | 整图 dense detector + pose，实例分配耦合 | 完整端到端多人/单人 pipeline；不能只比 point AP |
| RF-DETR Keypoint | query/set prediction，显式 findable/visible/covariance | 研究遮挡/uncertainty；对齐实例边界与 schema |
| Lite heatmap CNN | 同样 heatmap、不同 backbone | 最适合分离持续高分辨率是否必要 |

## 10. 导出与量化

### 静态导出

- 固定 input 和 heatmap size；
- 确认四 branch 的 resize target；
- `F.interpolate(..., mode='bilinear', align_corners=False)` 语义一致；
- final concatenate 的 channel 顺序一致；
- decoder 在图内还是图外；
- argmax/top-k 是否由 CPU 实现。

### INT8

- 高分辨率分支激活范围与低分辨率分支不同；
- sum fusion 对 scale 对齐敏感；
- heatmap 峰值相近时量化可能导致 argmax 翻转；
- 输出 MSE 小不代表亚像素坐标和下游 ROI 不变；
- 应比较 raw heatmap、peak margin、decoded point、NME/FR 和下游分类。

### 性能

同时记录：

- model-only latency；
- crop/affine/decoder/inverse transform；
- batch=1 peak memory；
- 每人脸调用次数；
- heatmap 搬运和 CPU argmax；
- GPU/NPU 是否存在 resize fallback。

## 11. 竞争解释与采用门

如果 HRNet 优于 PFLD，可能来自：

- 持续高分辨率；
- heatmap representation；
- 更大容量；
- ImageNet pretraining；
- 更高输入；
- loss/decoder；
- 更好数据配方。

采用前至少有一个实验分离主要变量，否则结论只能是“该完整 HRNet 配置更好”。

DMS 采用门：

1. 细粒度 eye normalized error 和 FR 达标；
2. reflection/side-face/occlusion/blur slice 无不可接受退化；
3. visibility/usable 信号明显优于 PFLD/规则 baseline；
4. 下游 eye-state/event 指标改善；
5. 目标硬件 latency、memory、export、INT8 对齐可接受。

## 12. 停止维护

默认不追踪每个 HRNet 下游论文、MMPose config、人体姿态榜单或第三方权重。只有以下触发更新：

- HRNet architecture/interface 的权威实现变化；
- 本仓真实采用固定 HRNet config；
- 新 codec/loss/decoder 改变关键点选型；
- 目标硬件实验产生可复用结论；
- 多次检索需要拆分 architecture 与 face-alignment implementation。

## 13. 来源

### 第一方

- [Deep High-Resolution Representation Learning for Visual Recognition](https://arxiv.org/abs/1908.07919)
- [HRNet organization](https://github.com/HRNet)
- [HRNet Facial Landmark Detection @ f776dbe8](https://github.com/HRNet/HRNet-Facial-Landmark-Detection/tree/f776dbe8eb6fec831774a47209dae5547ae2cda5)
- [WFLW W18 config](https://github.com/HRNet/HRNet-Facial-Landmark-Detection/blob/f776dbe8eb6fec831774a47209dae5547ae2cda5/experiments/wflw/face_alignment_wflw_hrnet_w18.yaml)
- [HRNet face-alignment model code](https://github.com/HRNet/HRNet-Facial-Landmark-Detection/blob/f776dbe8eb6fec831774a47209dae5547ae2cda5/lib/models/hrnet.py)

### 相关方法与工程框架

- [WFLW / Look at Boundary](https://arxiv.org/abs/1803.03220)
- [Adaptive Wing Loss](https://arxiv.org/abs/1904.07399)
- [DARK](https://arxiv.org/abs/1910.06278)
- [UDP](https://arxiv.org/abs/1911.07524)
- [HIH](https://arxiv.org/abs/2104.03100)
- [MMPose face 2D keypoint model zoo](https://mmpose.readthedocs.io/en/latest/model_zoo/face_2d_keypoint.html)

第三方框架只定义自身配置、权重和结果；其指标不能自动归入原始 HRNet。