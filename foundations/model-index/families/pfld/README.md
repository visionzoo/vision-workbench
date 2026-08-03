---
status: working
type: model-index
rigor: standard
provenance: public-primary-paper-author-project-and-labeled-community-implementations
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-08-03
updated: 2026-08-03
---

# PFLD

PFLD（Practical Facial Landmark Detector）在本仓库中指 2019 年论文定义的轻量 **face landmark model family**：以检测后的人脸 ROI 为输入，使用 MobileNetV2 风格轻量 backbone、多尺度特征汇聚与直接坐标回归定位固定人脸关键点，并在训练期使用姿态辅助分支和困难样本加权。

它不是所有轻量人脸关键点网络的总称，也不是 MobileNet 架构族本身。公开 PyTorch、TensorFlow、ONNX、NCNN、MNN、TNN 移植来自不同社区维护者，必须与论文对象分开。

## 1. 对象身份

```text
face detector / known face ROI
→ crop and normalize
→ lightweight inverted-residual backbone
→ multi-scale feature aggregation
→ fully connected coordinate regression
→ fixed landmark vector
```

PFLD 是一个依赖外部 face ROI 的完整 landmark 子系统。它不能独立解决整图多人实例发现，因此与 YOLO26 Pose、RF-DETR Keypoint 的整图系统比较时，需要显式计入上游人脸检测与 crop。

Registry 建议身份：

- `entity_kind: model-family`；
- `usage_scopes: [complete-solution]`，这里的 complete 只针对“已知 face ROI → face landmarks”；
- `module_roles: []`，不把完整 ROI 模型误登记为通用 backbone/head；
- `tasks: [2d-landmark-localization]`。

## 2. 论文架构

### 2.1 Backbone

论文以 MobileNetV2 风格 inverted residual / linear bottleneck 为主要轻量块，通过 width multiplier 形成容量—延迟变化。其目标不是复刻 ImageNet MobileNet，而是为 112×112 左右的人脸 ROI 保留足够结构信息。

关键机制：

- depthwise convolution 降低计算；
- inverted residual 与 linear bottleneck 组织通道；
- 不同深度的特征进入 multi-scale fully-connected aggregation；
- 最终一次输出全部关键点坐标。

论文展示 PFLD 1X 与 0.25X 等容量关系。具体社区仓库的层数、点数、输入和 width 配置可能变化，不能只凭“PFLD”名称混用权重。

### 2.2 Multi-scale fully connected

人脸关键点不是相互独立的局部点。PFLD 将多个尺度的特征 flatten / pooling 后拼接，让最终坐标回归同时获得局部与全局人脸结构。

它的收益应理解为：

```text
local texture
+ medium-range facial parts
+ global face geometry
→ one joint coordinate vector
```

代价是最终 FC 与输入分辨率/特征 shape 绑定，随意修改输入、stage 或 flatten 语义可能破坏 checkpoint 兼容。

### 2.3 Auxiliary pose branch

训练期辅助网络从中间特征估计头部旋转信息，用于几何正则化和困难样本加权。论文明确该分支不参与测试，因此：

- 训练 checkpoint 可以包含辅助分支；
- 推理图应确认是否已移除；
- 不能把辅助姿态输出视为部署时免费可用的 head pose；
- 若社区实现保留/删除或改写 auxiliary loss，结果属于该实现。

## 3. Loss 与困难样本

论文的核心动机之一是长尾状态：大姿态、极端光照、遮挡和低质量样本较少，但更影响实际系统。其 loss 将坐标误差与姿态/样本状态权重结合，强调困难样本。

这个设计能支持的判断是：困难切片不应被总体平均值淹没。它不能证明：

- 任意社区 loss 已复现论文公式；
- 姿态加权一定适合 IR 眼部点；
- 只增加困难样本权重不会放大标注噪声；
- 模型已经学会 visibility 或 uncertainty。

真实训练必须记录 loss 公式、角度来源、权重范围和每个 slice 的有效样本量。

## 4. 输入输出合同

PFLD 常见实现输出 `2K` 归一化坐标：

```text
[x1, y1, x2, y2, ..., xK, yK]
```

采用前必须固定：

- landmark 数量与顺序：68、98、106 或自定义 eye12；
- 输入：112×112、56×56 或其它尺寸；
- RGB/BGR、range、mean/std；
- bbox expansion、square crop、padding；
- 坐标归一化范围与 inverse transform；
- 是否输出 auxiliary pose、visibility 或额外分支；
- checkpoint 与代码 revision。

社区常见 `PFLD-pytorch` 往往以 WFLW 98 点训练，并提供 ONNX/NCNN 示例；这不等于论文原始 300W/AFLW 配置，也不保证点位、预处理和指标一致。

## 5. 论文与实际系统证据

论文/作者项目报告：

- PFLD 0.25X 可约 2.1 MB；
- Qualcomm Snapdragon 845 上单脸超过 140 FPS；
- 实际 demo 采用 `MTCNN face detector → PFLD 0.25X`；
- 评测覆盖 300W 与 AFLW 等公开人脸基准。

这些数字是给定作者实现、设备和单脸条件下的第一方报告。不能直接外推到：

- RKNN、海思或其它 NPU；
- 端到端多人/视频 pipeline；
- IR 摄像头、眼镜反光和极小眼部 ROI；
- 社区 PyTorch 重实现；
- INT8 后定位与下游闭眼分类。

## 6. 工程案例

### 6.1 PyTorch → ONNX → NCNN

社区实现普遍采用标准 Conv、depthwise Conv、FC 与 reshape，可导出 ONNX 并转 NCNN。可迁移教训：

- 推理图简单，是 PFLD 的真实工程优势；
- 需要保存输出节点、点位顺序、input transform 和 coordinate range；
- 社区示例常把权重、模型对象和输入尺寸写死，不能直接形成可复现发布；
- `onnx2ncnn` 或 pnnx 成功不代表坐标数值、inverse transform 和任务 NME 对齐。

### 6.2 多人系统

论文 demo 对每个人脸分别运行 PFLD。人数增加时，PFLD 成本近似随 face count 线性增长；整图 YOLO/RF-DETR 则共享 backbone。单驾驶员固定场景通常更有利于 ROI 模型，多人舱内或大画面需要测完整调度成本。

### 6.3 DMS 眼部

若已有稳定 face detector，PFLD 可作为最低成本基线：

```text
face crop → eye-related landmarks → eye ROI → eye-state classifier
```

但传统 PFLD 只输出坐标。面对侧脸、反光、遮挡和模糊，需要另加：

- visibility/usable head；
- 几何一致性；
- crop clarity / reflection features；
- temporal stability；
- 或与 heatmap/uncertainty 模型做受控比较。

## 7. 适用场景

### 优先考虑

- 单人或少量人脸；
- 上游 ROI 稳定；
- 固定 landmark schema；
- 严格模型大小、延迟、功耗和算子约束；
- 下游主要消费坐标或简单几何；
- 需要先建立低成本 control。

### 谨慎或不适合

- 需要整图实例发现；
- 遮挡点必须输出 calibrated visibility/uncertainty；
- 需要多人共享大 backbone；
- 关键点 schema 按类别变化；
- 极细粒度点位要求亚像素精度且 direct regression 已显示系统性偏差；
- 需要从 response map 诊断多峰、模糊和局部歧义。

## 8. 与 HRNet heatmap 的有效比较

PFLD vs HRNet-W18 同时改变 backbone 与输出表征。最小比较必须对齐：

- 同一 face/eye ROI 与 transform；
- 同一点位、visibility 和 split；
- 同一输入像素或明确记录差异；
- 同一训练数据、augmentation 和 early stopping；
- PFLD 坐标 loss 与 HRNet heatmap loss分别调优，但预算受控；
- 同一 NME/FR、visibility、jitter、下游 eye-state 与硬件指标。

若目标是归因 heatmap vs coordinate，应增加一个轻量 backbone + heatmap head 或同 backbone 双 head 对照。

## 9. 导出、量化与排查

### 导出前

- 冻结代码、checkpoint hash、input size、point schema；
- 去除或明确辅助 branch；
- 确认输出不是训练 tuple 或中间 pose；
- 建立固定输入的 PyTorch/ONNX 坐标对齐。

### INT8

- FC/最后坐标层的量化尺度可能直接改变小数坐标；
- 只比较 tensor MSE 不足，应比较点误差和下游 ROI；
- 困难样本的小 margin 变化可能导致眼 ROI 越界；
- crop/inverse transform 使用 CPU float 时要纳入端到端链。

### 常见现象

| 现象 | 首查 |
|---|---|
| 所有点整体偏移 | crop、padding、归一化、inverse transform |
| 侧脸点被拉回平均脸 | 数据/姿态分布、global regression、标注定义 |
| 遮挡点仍稳定输出 | 模型没有 visibility；坐标先验在补全 |
| PC/板端小幅坐标漂移 | last FC、量化尺度、layout、输出顺序 |
| 视频抖动 | 上游 bbox jitter、单帧 regression、无时序约束 |

## 10. 竞争解释与验证门

PFLD 在 DMS 失败时，不能立即归因为模型太小。竞争解释包括：

- face crop 和关键点坐标链错误；
- landmark schema 与眼 ROI 需求不匹配；
- IR 域偏移；
- 标注噪声或 visibility 未定义；
- 下游分类器而非 landmark 是主瓶颈；
- 需要局部眼模型而非完整脸 98 点。

采用门：

1. 在目标 ROI 上达到预先固定的 point error/FR；
2. visibility/usable 通过独立 head 或组合信号达到门限；
3. 下游 eye-state/event 指标不低于当前方案；
4. 目标硬件延迟、内存、INT8 对齐通过；
5. 对 side-face/reflection/blur/occlusion 无不可接受 slice 退化。

## 11. 停止维护规则

默认不因下列变化更新：

- 又出现一个 PFLD PyTorch fork；
- 某社区权重在未固定协议下报告更高 NME；
- 新增 ONNX/NCNN 教程；
- 任意轻量人脸 landmark 模型自称 PFLD-like。

只有论文/作者 artifact 变化、被本仓真实采用的实现变化、目标硬件实验或重复检索需求才触发维护。若后续只有一个固定实现进入工程，具体转换和故障进入 `engineering/`，本页不保存日志和权重。

## 12. 来源

### 第一方

- [PFLD paper](https://arxiv.org/abs/1902.10859)
- [Author project and demo](https://sites.google.com/view/xjguo/fld)

### 第三方实现与分析

- [Papers With Code implementation index](https://paperswithcode.com/paper/pfld-a-practical-facial-landmark-detector)
- [polarisZhao/PFLD-pytorch](https://github.com/polarisZhao/PFLD-pytorch)
- [guoqiangqi/PFLD TensorFlow implementation](https://github.com/guoqiangqi/PFLD)
- [GiantPandaCV PFLD architecture analysis](https://cloud.tencent.com/developer/article/1647254)
- [ncnn/pnnx conversion guide](https://github.com/Tencent/ncnn/wiki/use-ncnn-with-pytorch-or-onnx)

第三方实现只定义自身结构、数据、权重和转换，不反过来定义论文对象。