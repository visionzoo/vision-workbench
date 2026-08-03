---
status: working
type: task
rigor: standard
provenance: public-primary-sources-and-explicit-engineering-cases
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-08-03
updated: 2026-08-03
tags: [keypoint, landmark, pose, face-alignment, visibility, evaluation]
related: [../mechanisms/keypoint-output-representations.md, ../model-index/backbone-selection.md, ../../research/questions/dms-eye-visibility-and-localization-reliability.md]
---

# 2D landmark / keypoint localization

本任务回答：在二维图像中，为一个或多个实例定位具有固定语义的点，并给出足以支持下游决策的可见性、置信度或不确定性信息。人脸关键点、人体姿态、手部关节和工业结构点共享部分数学形式，但实例发现、点位定义、遮挡语义、评价尺度和部署接口可能完全不同。

本页不维护模型版本，也不把所有“输出坐标”的网络视为可直接比较。具体输出表征见 [Keypoint output representations](../mechanisms/keypoint-output-representations.md)，PFLD、HRNet、YOLO Pose 和 RF-DETR Keypoint 的事实分别回到各自模型权威条目。

## 1. 先确定系统边界

关键点系统至少有四种边界：

```text
A. 已知 ROI → 单实例关键点
B. 检测器 → ROI → 单实例关键点
C. 整图 → 多实例框 + 关键点
D. 整图 → query / set-based 实例 + 关键点
```

PFLD 与经典 HRNet face alignment 通常属于 A 或 B；YOLO Pose 和 RF-DETR Keypoint 属于 C 或 D。若系统已有稳定人脸框，把整图多人姿态模型与 ROI 模型直接比较，会同时改变实例发现、裁剪、有效像素、关键点 head 和后处理，结论只能属于完整系统，不能归因于关键点表征。

每次比较前必须冻结：

- 输入是整图、人脸 ROI、上半脸 ROI 还是眼部 ROI；
- ROI 来自人工框、固定规则还是某个检测器；
- 一个图像允许几个实例，漏框和错框是否计入；
- landmark schema、点位顺序、左右定义与缺失点规则；
- 输入 resize、crop、padding、翻转和坐标还原；
- 输出是像素坐标、归一化坐标、heatmap、offset、query 还是分布参数；
- visibility、occlusion、findable 与“可用于下游任务”分别如何定义。

## 2. 输出合同

一个可复现结果至少要绑定：

```text
image / ROI identity
+ transform chain
+ instance identity
+ landmark schema
+ coordinates and coordinate frame
+ visibility / findability / confidence semantics
+ decoder and threshold
+ model/checkpoint/runtime identity
```

推荐的基础记录格式：

```text
instance:
  bbox_xyxy: [x1, y1, x2, y2]
  bbox_source: detector|manual|fixed-roi
keypoints:
  schema_id: eye12-v1
  coordinates: [[x, y], ...]
  coordinate_frame: original-image
  visibility: [0|1|2, ...]
  confidence: [float, ...]
  uncertainty: optional
transform:
  crop, resize, padding, flip, inverse-map
```

`confidence` 不能只写一个数值。它可能是 heatmap 峰值、关键点存在概率、可见概率、query score、预测分布尺度或人为组合分数，语义不同，阈值不能混用。

## 3. Visibility 不是一个词

常见标注至少涉及三种命题：

1. **annotated / findable**：标注者能否确定该点；
2. **visible**：该点是否在图像中完整可见；
3. **usable**：该点及其局部 ROI 是否足以支持下游判断。

COCO 式 `v=0/1/2` 常表示未标注、已标注但遮挡、可见。RF-DETR Keypoint 当前源码进一步分别学习 `findable` 和 `visible`。Ultralytics Pose 的第三维则作为关键点存在/可见 logit 训练。Heatmap 峰值低可能来自遮挡，也可能来自模糊、裁剪偏移、域偏移或模型容量不足。DMS 中“眼角可标注”仍不保证眼睑纹理足以判断睁闭眼，因此必须另设 `usable_for_eye_state` Oracle。

## 4. 四类输出表征

| 路线 | 典型对象 | 原始输出 | 主要优势 | 主要风险 |
|---|---|---|---|---|
| Direct coordinate regression | PFLD | 固定长度坐标向量 | 输出小、解码简单、端侧友好 | 缺少空间分布；对 crop/遮挡敏感；置信度需另建 |
| Heatmap regression | HRNet face alignment | 每点二维 heatmap | 保留空间证据；易观察峰值、扩散和多峰 | 激活/输出大；下采样与解码产生量化偏差 |
| Dense detector + pose head | YOLO26 Pose | 框、类别、每点坐标/visibility；训练期可含 sigma | 一次完成多实例定位与关键点；工具链完整 | 对单 ROI 可能结构过重；框分配和关键点误差耦合 |
| Query / set prediction | RF-DETR Keypoint Preview | 实例 query + keypoint query；坐标、findable、visible、协方差参数 | 显式结构、遮挡和不确定性；无需重复实例抑制假设 | preview 接口；decoder/matching复杂；边缘部署证据不足 |

四条路线只能在统一系统合同下比较。更详细的因果链、训练/推理差异和量化风险见机制页。

## 5. 坐标链是首要故障源

关键点的误差可能在模型前后产生：

```text
original image
→ detector bbox
→ bbox expansion / aspect-ratio correction
→ crop / affine transform
→ network input
→ output representation
→ decoder
→ inverse affine
→ original image / downstream ROI
```

首轮验证必须使用合成点或可解析几何图，逐步检查：

- `x/y` 与 `row/column` 是否交换；
- resize 是否使用像素中心、align-corners 或半像素语义；
- bbox 是否 inclusive/exclusive；
- padding、letterbox、旋转、翻转和左右点交换是否一致；
- heatmap 到输入的倍率是否用 `W/heatmap_W` 还是 `(W-1)/(heatmap_W-1)`；
- 导出/runtime 是否改变 interpolation、round、top-k 或 sigmoid。

UDP 与 DARK 的研究表明，即使网络不变，编码、解码和坐标变换偏差也会显著改变结果；因此“换模型”前先冻结坐标链。

## 6. 评价指标

### 6.1 几何定位

人脸关键点常用 Normalized Mean Error：

```text
NME = mean_i ||p_i - g_i||_2 / d
```

归一化尺度 `d` 必须明确，可能是 inter-ocular、inter-pupil、bbox size、bbox diagonal 或其它尺度。不同定义的 NME 不能直接比较。

同时记录：

- median / mean / P90 / P95 normalized error；
- AUC of CED；
- failure rate at an预先固定阈值；
- 每个点、每个区域和每个实例尺度的误差；
- 原图像素误差与 ROI 归一化误差。

人体姿态常用 COCO OKS AP。OKS 绑定实例面积和每点 sigma；把 COCO OKS AP 直接用于眼部 12 点，需要重新定义 sigma 并验证其业务含义，不能照搬 17 点人体参数。

### 6.2 Visibility / usability

- findable / visible classification AP、AUROC、F1；
- 在正常 ROI 保留率固定时的坏 ROI 拦截率；
- 在坏 ROI 漏放率固定时的正常 ROI 误杀率；
- calibration、ECE 或 reliability curve；
- 遮挡、反光、模糊和侧脸分别报告。

### 6.3 时序稳定性

单帧 NME 好不代表视频可用。至少记录：

- 静态片段的逐点 jitter；
- 帧间速度/加速度异常；
- 左右点交换、峰值跳转和短时失踪率；
- 检测框抖动与关键点自身抖动的分解；
- 平滑前后定位误差与事件延迟。

### 6.4 下游任务

DMS 的最终 Oracle 应包含：

- 眼 ROI 成功提取率；
- 睁闭眼分类帧级误差；
- 疲劳事件误报、漏报和触发延迟；
- 正常、侧脸、眼镜反光、遮挡、运动模糊、低照度/IR 过曝切片；
- 模型、预处理、解码、后处理和端到端延迟；
- 峰值内存、模型大小、导出/量化成功率和数值漂移。

## 7. 数据与切片

### 人脸公开基准

| Dataset | 价值 | 不能替代 |
|---|---|---|
| 300W | 经典 68 点与 common/challenging split | IR DMS、细粒度眼睑 visibility |
| AFLW | 大姿态、较稀疏点位 | 精细眼部结构 |
| COFW | 遮挡人脸与 occlusion 研究 | 当前车型、摄像头与反光分布 |
| WFLW | 98 点；pose/expression/illumination/makeup/occlusion/blur slices | 车内 IR 与下游闭眼判定 |

WFLW 的分层评测很适合验证“总体平均值掩盖侧脸/遮挡失败”的问题，但公开图像分布和 DMS IR 域仍需分开。

### DMS 最小验证集

建议同一身份或同一视频只进入一个 split，防止相邻帧泄漏。每个样本至少带：

- face/eye size、yaw/pitch/roll 或可复核几何标签；
- glasses/reflection、blur、occlusion、illumination；
- landmark、visibility、usable-for-eye-state；
- downstream eye-state/event label；
- 标注者和复核状态。

先测标注一致性。若“可用于闭眼判断”在人之间都无法稳定一致，模型比较不会产生可靠结论。

## 8. 适用场景初筛

| 场景 | 首轮候选 | 理由 | 不应默认选择 |
|---|---|---|---|
| 单驾驶员、已有稳定人脸 ROI、严格 NPU 预算 | PFLD + 一个轻量 heatmap control | 隔离关键点任务；部署链简单 | 直接上整图 126M query 模型 |
| 细粒度眼睑、需要可视化空间证据 | HRNet-W18 heatmap 或轻量 heatmap | 可观察峰值/多峰/扩散，便于 visibility 分析 | 只用 argmax 峰值当 calibrated confidence |
| 多人整图、同时需要框与人体 17 点 | YOLO26 Pose | 一体化检测与 pose、完整训练/导出生态 | 将 COCO 权重直接当人脸眼部模型 |
| 多类别不同点位、遮挡与不确定性研究 | RF-DETR Keypoint Preview | class-conditioned keypoint queries、findable/visible/Gaussian NLL | 在 preview 阶段直接承诺端侧生产 |
| 只做最终眼状态，不需要通用 landmark | 专用眼部检测/分类与最小结构点 | 减少无关输出与标注成本 | 因“关键点模型先进”扩大任务 |

## 9. 真实工程案例与可迁移教训

### PFLD mobile pipeline

PFLD 论文展示的是 `face detector → detected face → PFLD 0.25X`，并报告 Snapdragon 845 上单脸超过 140 FPS、约 2.1 MB。这个结果说明 ROI 回归可以非常轻，但它不包含当前检测器、摄像头、预处理、多人调度和目标 NPU 的端到端成本。社区存在 PyTorch→ONNX→NCNN 移植，证明算子链较简单；社区权重、点位和预处理必须逐项核对，不能替代论文身份。

### HRNet WFLW face alignment

HRNet 官方人脸关键点仓库的 W18 配置使用 256×256 输入和 98×64×64 heatmap，并提供 WFLW 各困难切片。仓库基于较老的 PyTorch/CUDA 环境，适合作为架构与评测参考，不应直接视为现代部署工程。真正落地需重新固定 framework revision、decoder、导出图和目标 runtime。

### YOLO Pose production-style pipeline

Ultralytics Pose 把实例框、类别、关键点和可见性统一到一个整图模型，并提供训练、验证、预测与导出入口。它适合多人/整图系统；对 DMS 单脸小眼部，必须证明整图实例发现带来的价值足以覆盖更大的模型、输入和关键点分配成本。

### RF-DETR Keypoint preview

当前实现为每点预测 `x/y/findable/visible/Cholesky uncertainty/class contribution`，并把关键点成本纳入 set matching。它提供了强研究基线，尤其适合遮挡与不确定性；但官方明确称为 Preview，API、checkpoint 和性能均可能变化。当前公开 T4 TensorRT FP16 数字不能外推到 RKNN/海思、INT8 或车内 IR。

### Driver-occlusion research

Occluded Stacked Hourglass 在驾驶员安全语境中同时输出人脸 landmark heatmap 与 occlusion，说明显式遮挡监督可能比单一坐标置信度更贴近头姿、眨眼和打哈欠等下游任务。它不是本次四候选之一，但提供了一个重要反例：若核心目标是“可用性”，只提高定位 NME 可能不够。

## 10. 深度分析与来源地图

### 第一方与论文

- [PFLD paper](https://arxiv.org/abs/1902.10859) / [author project](https://sites.google.com/view/xjguo/fld)
- [HRNet facial landmark repository](https://github.com/HRNet/HRNet-Facial-Landmark-Detection)
- [WFLW / Look at Boundary](https://arxiv.org/abs/1803.03220)
- [Adaptive Wing Loss](https://arxiv.org/abs/1904.07399)
- [DARK](https://arxiv.org/abs/1910.06278)
- [UDP](https://arxiv.org/abs/1911.07524)
- [HIH: Heatmap in Heatmap](https://arxiv.org/abs/2104.03100)
- [YOLO26 technical report](https://arxiv.org/abs/2606.03748) / [Ultralytics Pose docs](https://docs.ultralytics.com/tasks/pose/)
- [RF-DETR paper](https://arxiv.org/abs/2511.09554) / [keypoint docs](https://rfdetr.roboflow.com/learn/run/keypoints/)
- [Group Pose](https://arxiv.org/abs/2308.07313) for query-based pose relations

### 可作为工程案例、不能替代第一方定义

- [GiantPandaCV PFLD architecture analysis](https://cloud.tencent.com/developer/article/1647254)
- [PFLD PyTorch / ONNX / NCNN community implementation index](https://paperswithcode.com/paper/pfld-a-practical-facial-landmark-detector)
- [ncnn/pnnx conversion guide](https://github.com/Tencent/ncnn/wiki/use-ncnn-with-pytorch-or-onnx)
- [MMPose face 2D keypoint model zoo](https://mmpose.readthedocs.io/en/latest/model_zoo/face_2d_keypoint.html)
- [RF-DETR keypoint fine-tuning guide](https://rfdetr.roboflow.com/learn/train/)
- [Occluded Stacked Hourglass summary](https://trid.trb.org/View/1493271)

来源进入结论前必须标记为论文、官方实现、厂商报告、第三方复现、社区案例或本人实验。转载文章可帮助理解代码路径，但不能独立证明精度、速度或适用性。

## 11. 本任务当前结论

可以成立：

- 关键点选型首先是系统边界与输出表征选择，而不是模型名排名；
- ROI 回归、heatmap、多实例 dense pose 和 query set prediction 应分别建立控制变量；
- visibility/findable/usable 必须拆开；
- 坐标链、heatmap 编解码和下游 Oracle 与 backbone 同等重要；
- 公开 COCO/WFLW 结果不能直接回答 DMS IR 眼部可用性。

尚不能成立：

- HRNet 一定比 PFLD 更准；
- RF-DETR Keypoint 一定优于 YOLO26x-pose；
- 论文 AP/NME 可以跨任务、输入、硬件和点位 schema 排名；
- heatmap 峰值或模型 visibility 分数已经是 DMS 可用性的 calibrated probability；
- 当前任何候选已经通过目标 NPU 或最终疲劳事件验收。

下一步由 [DMS eye keypoint model selection](../../research/experiments/dms-eye-keypoint-model-selection.md) 在统一数据、输入、schema、训练预算和硬件合同下区分这些候选。