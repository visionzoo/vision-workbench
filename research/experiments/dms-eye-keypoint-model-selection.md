---
title: DMS eye keypoint model selection
status: working
type: research-experiment
rigor: standard
created: 2026-08-03
updated: 2026-08-11
confidence: medium
provenance: public-research-plus-user-problem-definition
evidence_status: protocol-only
owner_review: pending
ip_review: pending
tags: [dms, ir, eye, keypoint, pfld, hrnet, yolo26, rf-detr, visibility, deployment]
related: [../questions/small-scale-eye-information-preservation-and-openness-measurement.md, ../questions/dms-eye-visibility-and-localization-reliability.md, upper-face-roi-information-preservation.md, ../../foundations/tasks/2d-landmark-localization.md, ../../foundations/mechanisms/keypoint-output-representations.md]
---

# DMS eye keypoint model selection

## 1. Evidence boundary

本文定义实验，不报告尚未运行的结果。用户历史信息表明目标场景包含 IR DMS、小尺寸眼部、侧脸、眼镜反光、模糊和遮挡，并且关键点用于后续闭眼/疲劳判断；但当前仓库未附原始图像、完整标签、固定模型、训练日志、runtime 或目标设备结果。任何结论必须由合法、可披露且通过 IP 审查的数据产生。

## 1.1 Relationship to R1

本实验是 [R1](../questions/small-scale-eye-information-preservation-and-openness-measurement.md) 的眼睑结构恢复与部署候选比较。它可以回答“在冻结 ROI 后怎样恢复结构”，但不能单独回答 ROI 为什么有效、信息首次在哪里受损，或检测收益是否已经转化为连续开合度；这些由 [upper-face ROI experiment](upper-face-roi-information-preservation.md) 与 R1 共同维护。

## 2. 决策问题

在固定 DMS 数据、点位、ROI、训练预算与目标部署合同下，以下哪类系统能以可接受成本提供最可靠的眼部定位与可用性判断？

1. PFLD-style direct coordinate regression；
2. HRNet-W18 heatmap；
3. YOLO26x-pose custom keypoints；
4. RF-DETR Keypoint Preview custom keypoints。

这不是四个同层模型的排行榜。需要回答两个不同问题：

```text
Q1: 已知 face/eye ROI 后，哪种 landmark representation 最可靠？
Q2: 将实例发现与 keypoint 合并，是否比现有 detector→ROI pipeline 更有价值？
```

## 3. 主要假设与反证

### H1：Heatmap 对困难眼部更稳定

预测：固定 ROI 后，HRNet heatmap 在侧脸、遮挡、反光和模糊切片的 P90 error、failure rate 与 jitter 优于 direct regression；heatmap entropy/peak margin 与真实误差或 unusable 标签相关。

反证：总体和困难切片无稳定收益，或收益只来自更高输入/更大容量；轻量 heatmap control 达不到同样收益；目标 NPU 成本不可接受。

### H2：Direct regression 是足够好的部署基线

预测：PFLD-style 模型在正常和大部分困难切片达到下游 eye-state 门限，并显著降低延迟、内存和 INT8 风险。

反证：遮挡点被平均脸补全、crop jitter 敏感、visibility/usable 无法可靠判断，导致下游误报/漏报明显高于 heatmap。

### H3：一体化 pose 模型能减少上游 ROI 误差

预测：YOLO26x-pose 或 RF-DETR Keypoint 从整图直接定位实例与关键点，减少 face detector/crop 失效，并在大姿态/部分遮挡下改善端到端成功率。

反证：单驾驶员场景中上游 face ROI 已稳定；整图输入稀释小眼部像素；模型主要学习人体/COCO prior；端到端成本更高且下游无收益。

### H4：显式 visibility/uncertainty 改善 usable 判断

预测：RF-DETR 的 findable/visible/covariance，或 HRNet 的 heatmap统计 + visibility head，比 YOLO/PFLD 单一坐标/visible score 更能区分 `usable_for_eye_state`。

反证：这些信号只与标注 visibility 相关，不与下游闭眼可判性相关；校准跨车型/相机失效；规则组合已达到相同效果。

### H5：关键点不是主要瓶颈

预测：更换 landmark system 后定位指标改善，但 eye-state/event 指标不变，说明主要误差来自图像质量、分类器、时序或标签定义。

反证：关键点/usable 指标改善稳定转化为下游误报/漏报降低。

## 4. 数据合同

### 4.1 Split

- 以 driver identity / vehicle / video session 为 group；
- 同一视频相邻帧不得跨 train/val/test；
- test 在方案和阈值冻结前不可查看；
- 若存在客户/设备域，至少保留一个 domain-holdout；
- 所有模型使用同一 manifest。

### 4.2 最小规模

第一阶段不追求大而全，先建立可复核小验证集：

- normal/frontal：确认基础坐标链；
- side-face：按 yaw/pitch 分层；
- glasses/reflection：左右眼、强弱反光；
- blur/motion：按清晰度或人工等级；
- occlusion：手、镜框、头发、遮阳板等；
- low-light/over-exposure；
- eye small-size bins；
- open/closed/ambiguous eye-state。

每个 slice 需要足够样本估计 failure rate；若样本太少，应报告区间和样本数，不做百分位排名。

### 4.3 标注

建议 schema：

```text
eye12-v1:
  left eye: 6 contour points
  right eye: 6 contour points
```

若业务需要眼角、上下眼睑或瞳孔，应另建版本，不在训练中悄悄改变点位。每点至少：

- `(x, y)`；
- `findable`；
- `visible`；
- `usable_for_eye_state` 可按眼或 ROI 标注；
- ambiguous 原因。

至少双人复核一部分样本，计算坐标一致性与 label agreement。没有可靠 Oracle 时先修标注，不训练更复杂模型。

## 5. 输入与 ROI 两套协议

### Protocol A：固定 ROI

目的：比较 landmark representation。

- 使用同一人工框或冻结的人脸检测器输出；
- 相同 bbox expansion/aspect ratio；
- 对所有模型保存实际输入 crop；
- 输入可按各模型原生尺寸运行，但另设相同像素 control；
- 所有输出还原到原图后评价。

### Protocol B：端到端整图

目的：比较完整系统。

- PFLD/HRNet 包含冻结 face detector + crop；
- YOLO26/RF-DETR 直接整图实例+keypoint；
- face miss、wrong instance、duplicate 和 keypoint error 全计入；
- 同时报告 model-only 与 end-to-end latency。

Protocol A 与 B 结果不得混为一个排行榜。

## 6. 候选实现冻结

### PFLD baseline

- 明确采用哪个 PyTorch实现或本人重实现；
- 记录 paper-equivalent 与实际差异；
- 112×112 或固定输入；
- direct `2K` coordinates；
- auxiliary pose 只训练；
- 可选独立 visibility/usable head，必须同时保留无 head baseline。

### HRNet heatmap baseline

- HRNet-W18；
- 固定 input/heatmap size，例如 128→32 或 256→64；
- Gaussian sigma、loss、decoder（argmax / DARK / soft-argmax）冻结；
- 先跑 standard heatmap，再加入 visibility head；
- 记录 peak、second-peak margin、entropy、spatial variance。

### YOLO26x-pose candidate

- 固定 `ultralytics` revision `81d076f8c38a49126cc1d5be369c8c107ec69789` 或训练时实际 tag；
- `yolo26x-pose` 只是初始化/scale 身份，必须改 custom `kpt_shape` 和数据；
- 记录 one-to-many/one-to-one、Pose26/RLE、input、box class、export branch；
- 不把 COCO 17-keypoint pretrained AP 当作 eye12 证据；
- 若 x 规模在 Gate 0/1 已超预算，降到 n/s/m 做机制筛查，x 仅作上限。

### RF-DETR Keypoint Preview candidate

- 固定 revision `f50258b07d51efc23771a9418dc13f20de71866b`；
- 记录 Preview checkpoint、DINOv2 backbone、resolution、query/decoder配置；
- custom keypoint schema；
- 分别导出 findable、visible、covariance；
- 优先作为服务器/研究上限；只有 Gate 0 算子与内存通过才进入板端承诺。

## 7. 变量控制

| 变量 | 控制方式 |
|---|---|
| 数据与 split | 同一 manifest、同一过滤规则 |
| 点位 | eye12-v1，顺序和 mirror map 固定 |
| ROI | Protocol A 完全一致；Protocol B 单独评价 |
| 输入 | 原生尺寸 + 至少一个相同有效眼像素 control |
| augmentation | 公共基础集；模型特有增强另记 |
| 预训练 | 明确来源；结果不归因给架构单变量 |
| 训练预算 | 同一 early-stop 规则；另报 GPU hours/peak memory |
| decoder | 每模型固定；heatmap decoder 做独立消融 |
| visibility | 同一标签；输出语义单独映射 |
| evaluator | 一套版本化脚本 |
| hardware | PC 精度、GPU latency、目标 NPU 分开 |

## 8. 指标

### 8.1 Landmark

- per-point error / eye width；
- mean、median、P90、P95；
- failure rate at frozen thresholds；
- left/right eye and point-group error；
- WFLW-compatible NME 仅作公共参考，DMS 主指标按 eye width；
- confidence interval / bootstrap by video group。

### 8.2 Visibility / usable

- findable、visible、usable AP/AUROC/F1；
- bad ROI catch rate at 95% normal retention；
- calibration/ECE；
- uncertainty coverage：例如 90% ellipse 是否覆盖约 90% GT；
- threshold 在新 vehicle/camera domain 的稳定性。

### 8.3 Video

- static-segment jitter / eye width；
- point drop/flip/swap rate；
- invalid jump rate；
- frame-to-frame detector box contribution；
- smoothing 前后 error、事件延迟和 recovery。

### 8.4 Downstream

- eye ROI extraction success；
- open/closed frame F1、false-open/false-closed；
- fatigue event false alarms / misses / delay；
- uncertain/reject coverage 与保留样本精度；
- drink/yawn/occlusion 等非目标混淆若受眼 ROI 影响也需记录。

### 8.5 Engineering

- params、model file、FLOPs 只作描述；
- batch=1 model-only latency；
- preprocess + inference + decode + inverse transform；
- peak RAM/VRAM/NPU memory；
- export graph operators/fallback；
- FP32/FP16/INT8 coordinate and task drift；
- training cost and iteration time。

## 9. 分阶段漏斗

### Gate 0：接口与硬件可行性

不训练或只用随机/官方权重，检查：

- custom point count 是否支持；
- static ONNX/export；
- target runtime operator coverage；
- output shape/semantics；
- estimated memory/latency；
- license/IP。

淘汰条件：无法表达 schema、关键算子 fallback、内存/延迟数量级超预算、Preview/许可不符合当前交付。

### Gate 1：小数据过拟合与坐标链

每候选在同一几十/几百样本上过拟合：

- 确认 loss下降、坐标还原、flip/mirror、visibility；
- 保存输入/GT/output overlay；
- 合成几何测试通过；
- 若不能过拟合，不进入正式训练。

### Gate 2：统一小验证集

优先完成两类机制：

1. PFLD direct regression；
2. HRNet heatmap。

这是最低成本且能回答核心 output-representation 问题的比较。YOLO26/RF-DETR 先完成 Gate 0，不因模型新就同时消耗训练预算。

### Gate 3：完整候选

只有以下任一条件成立才训练 YOLO26/RF-DETR：

- Protocol B 显示现有 face ROI 是主要失败源；
- 显式 visibility/uncertainty 是关键决策变量，PFLD/HRNet 无法满足；
- 多实例/多类别可变 schema 是真实需求；
- 服务器端 accuracy upper bound 有明确价值。

### Gate 4：目标硬件

对通过任务门的 1–2 个方案做 ONNX/INT8/NPU：

- 同一校准集；
- final output + task metrics；
- 第一语义分歧定位；
- 采用/撤销门。

## 10. 预注册采用门

具体数值由用户结合现有 baseline 填写后冻结：

```text
landmark:
  P95 eye-normalized error <= __
  failure rate <= __
visibility/usability:
  bad-ROI catch @ 95% normal retention >= __
downstream:
  eye-state F1 >= baseline + __
  event false alarm <= __
engineering:
  target-device end-to-end latency <= __ ms
  model memory <= __
  INT8 metric drop <= __
```

没有预注册门，容易在看到结果后移动标准，形成“每个模型都在某方面最好”的无效结论。

## 11. 结果表结构

### Full-system table

| Candidate | ROI/instance mode | Landmark | Usable | Downstream | Latency | Memory | Export/INT8 | Decision |
|---|---|---:|---:|---:|---:|---:|---|---|
| PFLD | detector→ROI | | | | | | | |
| HRNet heatmap | detector→ROI | | | | | | | |
| YOLO26 Pose | full image | | | | | | | |
| RF-DETR KP | full image/query | | | | | | | |

### Slice table

| Slice | n videos | PFLD FR | HRNet FR | YOLO26 FR | RF-DETR FR | Main failure mode |
|---|---:|---:|---:|---:|---:|---|
| frontal | | | | | | |
| side-face | | | | | | |
| reflection | | | | | | |
| blur | | | | | | |
| occlusion | | | | | | |
| small-eye | | | | | | |

结果必须附置信区间和原始 manifest/run ID。

## 12. 预期决策，不是预设结论

基于结构与当前场景的先验顺序是：

1. PFLD：部署下限/control；
2. HRNet-W18 heatmap：精度与空间不确定性 baseline；
3. YOLO26 Pose：仅在整图一体化有实际价值时进入；
4. RF-DETR Keypoint Preview：遮挡/uncertainty upper bound，先服务器后硬件。

这是资源分配顺序，不是准确率排名。实验可以推翻它。

## 13. 交付物

- versioned dataset manifest 与 label schema；
- evaluator + coordinate-chain unit tests；
- 每候选固定 config/checkpoint/source revision；
- Gate 0 operator/runtime report；
- 至少 PFLD 与 HRNet 的统一小验证集结果；
- slice、visibility、jitter、downstream、latency/size 表；
- 失败案例图集；
- `Adopt / Reject / Keep as research upper bound / Escalate` 结论；
- 结论的适用域和撤销条件。

## 14. 停止条件

停止继续扩候选，当：

- 两个机制不同的 baseline 已达到业务门；
- 新候选没有改变决策变量或预测；
- 数据/标注一致性成为主要瓶颈；
- 目标硬件已淘汰复杂路线；
- 下游指标证明关键点不是主要误差源。

失败结果仍需记录，不因不好看而删除。
