---
title: Upper-face ROI information preservation
status: working
type: experiment
rigor: standard
created: 2026-08-11
updated: 2026-08-11
confidence: low
provenance: conversation-draft
evidence_status: unverified
owner_review: pending
ip_review: pending
tags: [dms, ir, eye, roi, yolo, scale, context, search-space, openness]
related: [../questions/small-scale-eye-information-preservation-and-openness-measurement.md, ../questions/dms-eye-visibility-and-localization-reliability.md, dms-eye-keypoint-model-selection.md]
---

# Upper-face ROI information preservation

## 1. Evidence boundary

本文定义 R1 的首轮实验系列，不报告结果。历史“人脸 ROI → 上半脸裁剪 → resize → YOLOv8 眼部检测”只提供实验入口；当前没有导入原始样本、模型、配置、日志或标注。

实验只能使用权属明确的公开或自建资产。若真实 DMS 数据不能进入本仓库，只保存脱敏 manifest schema、实验合同、聚合结果和外部证据指针；IP review 通过前不得晋级。

## 2. Decision question

上半脸 ROI 的收益究竟主要来自：

1. 眼睛在模型输入中占据更多像素；
2. 可见上下文改变；
3. 候选搜索空间缩小；
4. “眼睛位于上半脸”的位置先验；
5. 还是 ROI 漂移、裁断与重采样同时引入了新的损失？

实验最终还必须回答：这些变化只是提高了眼睛检出率，还是实际提高了眼睑结构与连续开合度的可量测性。

## 3. Hypotheses under test

本实验直接区分 R1 的 H2–H5，并为 H6–H8 提供输入边界：

| 假设 | 若成立，应观察到 |
|---|---|
| H2 尺度分配 | 固定上下文比例时，有效眼像素增加带来跨视频组稳定的正确候选、关键点或开合度改善 |
| H3 上下文/搜索空间 | 有效眼像素不变时，改变可见上下文或允许候选区域仍产生独立收益 |
| H4 条件位置先验 | 眼睛像素和局部纹理不变时，规范位置优于位置打乱，且差异超过模型自身平移误差 |
| H5 ROI 新损失 | 真实范围的人脸框扰动、上边界变化或侧脸裁剪存在明确失效边界 |
| H6–H8 后续机制 | 输入张量已等价或更好，但中间层、Head、阈值、部署或格式语义仍造成分歧 |

## 4. Frozen system contract

正式运行前冻结：

- 数据 manifest 与 group split；
- face/eye ground truth、eye-state 和可量测性标签版本；
- 人脸框来源、upper-face 计算方式、bbox expansion、padding 与 aspect ratio；
- resize 算法、像素中心、range、颜色/通道语义和归一化；
- YOLOv8-style eye detector 的代码、权重、输入、阈值前 raw output 和后处理版本；
- 眼睑结构/开合度 probe 的代码、权重和输出定义；
- 随机种子、运行环境和硬件；
- 同一套 evaluator。

若当前没有冻结的眼睑结构/开合度 probe，可以先完成变换正确性和眼睛检测阶段，但不得据此宣称“细粒度信息已经保留”。

## 5. Data contract

按 driver / vehicle / video session 分组，禁止同一视频相邻帧跨 split。test 在变换、阈值和判据冻结前不可查看。

最小切片：

- frontal / normal；
- eye-size bins；
- open / closed / intermediate / ambiguous；
- glasses / reflection；
- blur / motion；
- side-face；
- partial occlusion；
- face-box drift / truncation。

每条样本至少记录：

~~~yaml
sample_id:
group_id:
source_image_ref:
face_box:
left_eye_box:
right_eye_box:
eyelid_landmarks:
eye_state:
openness_oracle:
observability:
invalid_reason:
slice_tags:
annotation_review:
~~~

先抽样做双人标注一致性。若 openness 或 observability 的人工差异已经超过候选系统差异，先修 Oracle，不扩大模型实验。

## 6. Controlled interventions

### E0. Coordinate and transform integrity

目的：排除 crop/resize/逆变换本身的实现错误。

- 用人工几何图案和已知坐标验证 crop、padding、resize、flip 和 inverse transform；
- 同一源图只允许一次目标 resize，禁止先保存有损图再二次缩放；
- 保存模型实际输入 tensor 的 hash、shape、range 和可视化；
- 验证左右眼映射、像素中心、inclusive/exclusive bbox 和 stride 对齐。

E0 未通过，不运行后续实验。

### E1. Effective eye-pixel scale

目的：隔离 H2。

- 从同一高质量源区域出发；
- 固定眼睛周围上下文比例、插值方式和输入合同；
- 只改变眼睛在最终输入中的宽高；
- 同一样本生成成对条件；
- 记录原图眼睛像素、输入眼睛像素及 P2/P3/P4 理论覆盖单元。

避免把“先降采样再放大”的结果当作高分辨率输入。放大不能恢复已经丢失的源结构。

### E2. Visible context

目的：隔离局部纹理、上半脸和完整人脸上下文。

- 保持最终眼睛像素、中心位置和模型输入尺寸不变；
- 使用相同眼部 patch；
- 逐步显示 eye-only、upper-face、full-face 和 larger-context；
- 其余区域使用固定 neutral canvas 或来自同一图像的受控背景；
- 分开报告真实背景与 neutral canvas，避免遮罩边界成为新捷径。

### E3. Search-space contribution

目的：区分“像素变大”与“允许候选位置变少”。

第一阶段在完全相同的输入 tensor 和 raw Head 输出上，分别：

- 允许全图候选；
- 只允许冻结的 upper-face candidate region；
- 只读取 ground-truth 邻域的 raw candidate 作为诊断上界。

这只能测量推理读出阶段的搜索空间贡献。若要研究训练期搜索空间或标签分配，必须另建受控训练实验，不从后处理 mask 外推。

### E4. Conditional position prior

目的：测量“眼睛位于规范上半脸位置”的贡献。

- 保持眼部像素和局部上下文不变；
- 将 patch 放到多个预定义位置；
- 与纯平移等变误差基线比较；
- 左右眼互换、镜像和位置扰动遵守冻结语义；
- 不将越界 padding 或裁断样本混入位置先验结论。

若位置打乱只暴露 padding/stride 非等变，结论应归入网络实现，而不是语义先验。

### E5. ROI perturbation and failure boundary

目的：隔离 H5。

对同一人脸框施加可重复扰动：

- x/y 平移；
- width/height 缩放；
- upper-face vertical ratio；
- aspect-ratio correction；
- top/bottom boundary；
- side-face dependent asymmetric expansion。

扰动范围来自实际 face detector 误差分布或公开/自建模拟，不凭主观选择。记录第一次裁断眼角/眼睑、检测候选突降、关键点突变和 openness 越界的位置。

### E6. Detection versus fine-grained measurement

每个输入条件走两条固定路径：

~~~text
Path A: 输入 → 冻结 eye detector → raw candidate / eye ROI
Path B: 同一 eye ROI 或 oracle eye ROI → 冻结 eyelid probe → openness / confidence / UNKNOWN
~~~

同时比较 predicted ROI 与 oracle ROI：

- oracle ROI 成功、predicted ROI 失败：定位或 crop 链问题；
- 两者都失败：源信息、重采样或结构 probe 问题；
- 结构 probe 正确、最终状态错误：开合度标定或判决问题；
- PC 正确、目标端错误：部署或输入语义问题。

## 7. Experimental matrix

| Axis | Control | Intervention | Primary distinction |
|---|---|---|---|
| Scale | 相同样本、上下文比例、模型 | 最终 eye width/height | H1 vs H2 |
| Context | 相同 eye pixels/position/input | context extent / masking | H2 vs H3 |
| Search | 相同 input tensor/raw Head | allowed candidate region | H3 readout component |
| Position | 相同 patch/context/scale | normalized position | H4 vs shift non-equivariance |
| ROI error | 相同 source/model | bbox and upper-ratio perturbation | H5 |
| Measurement | 相同 crop | detector ROI vs oracle ROI | detection vs structure loss |
| Deployment | 相同 saved tensor | PC/ONNX/target runtime | H6/H7 vs H8 |

一次运行只改变矩阵中的一个主轴；交互项必须在主效应稳定后单独登记。

## 8. Measurements

### Input and geometry

- source eye width/height；
- final input eye width/height；
- eye area ratio；
- eye-corner and eyelid coverage；
- crop truncation ratio；
- P2/P3/P4 theoretical cell coverage；
- actual tensor hash/range。

### Detection and readout

- correct-location raw candidate recall at a diagnostic low threshold；
- frozen operating-threshold recall；
- score/rank of the best candidate overlapping ground truth；
- false positives per frame/ROI；
- localization error and ROI completeness；
- raw Head to decoded-output loss attribution。

降低阈值只用于判断正确候选是否存在，不作为生产修复或最终收益。

### Fine-grained structure and openness

- landmark error normalized by eye width；
- mean、median、P90/P95 and frozen failure rate；
- openness MAE and signed bias；
- rank/linear correlation with the independent Oracle；
- open/closed/intermediate separability；
- observability/UNKNOWN catch rate at a frozen valid-retention point；
- temporal jitter on static or slowly varying segments。

### Cost and robustness

- model-only and end-to-end latency；
- peak memory and input bandwidth；
- per-slice sample count and group-bootstrap interval；
- driver/video/camera domain stability；
- PC/ONNX/target-runtime numerical drift。

## 9. Pre-registered interpretation rules

具体数值门必须在 pilot 与人工一致性分析后、查看 frozen test 前写入版本化配置。当前只冻结方向性判据：

- 支持 H2：在 context-matched paired samples 上，尺度变化对结构/开合度存在稳定、有序且跨组复现的影响；
- 支持 H3：eye pixels 固定后，context 或 candidate region 仍提供独立收益，且不能由遮罩伪影解释；
- 支持 H4：规范位置收益显著超过同模型的平移/stride/padding 基线；
- 支持 H5：实际误差范围内存在可复现的 crop 失效边界，并与眼睑裁断或量测失败一致；
- 支持后续 H6/H7：输入和 ROI 已控制，但指定层/监督/Head 干预改变结构恢复；
- 支持 H8：保存的同一输入和 PC 中间量可用，而导出、量化、格式或后处理造成新增损失；
- 不支持任何机制：收益只出现在训练/阈值选择集、单一视频、单一切片，或区间与标注噪声无法区分。

AP、可视化或单个 Badcase 不得单独接受假设。

## 10. Execution gates

| Gate | Required artifact | Pass condition |
|---|---|---|
| P0 Contract | data/model/transform/evaluator manifest | 所有版本、语义和 group split 可复核 |
| P1 Geometry | synthetic transform tests | crop/resize/inverse-transform 在冻结容差内 |
| P2 Pilot | paired intervention outputs | 能区分变量且没有明显标签/实现错误 |
| P3 Frozen evaluation | unseen grouped test predictions | 方向、区间、slice 与失败样本完整 |
| P4 Measurement link | oracle/predicted ROI openness results | 检测收益是否转化为连续量测已回答 |
| P5 Deployment | saved-tensor cross-runtime outputs | PC/ONNX/target drift 定位到具体边界 |

通过 P1 只说明实现正确；至少通过 P4 才能形成关于“小尺度眼部精细感知”的阶段结论。

## 11. Required artifacts

每个 run 最少保留：

~~~text
experiment.yaml
data-manifest.yaml
model-manifest.yaml
predictions.parquet
metrics.json
report.md
~~~

其中 predictions 必须包含 sample/group ID、干预条件、输入几何、raw candidate、decoded ROI、结构、openness、observability 和 invalid reason。原图或模型若受限，只保存外部指针和审查状态，不复制进仓库。

## 12. Stop and rollback conditions

立即停止解释并回滚到前一 Gate：

- crop/resize/坐标测试失败；
- 同一 tensor 的 hash 或预处理不一致；
- group split 泄漏；
- openness/observability Oracle 一致性不足；
- 一个实验同时改变尺度、上下文和模型；
- ROI 扰动范围无法对应实际误差；
- raw candidate 与 decoded output 无法追踪；
- 使用受限资产但没有 IP 审查；
- 检测提升没有进入结构和开合度量测，却被写成 R1 完成。

## 13. Current status

协议已建立，尚未运行。下一步不是训练新模型，而是由本人冻结：

1. 合法数据来源和最小 slice；
2. YOLOv8-style baseline 的版本与输入合同；
3. upper-face ROI 的现有精确定义；
4. eyelid/openness Oracle 与 probe；
5. pilot 后的数值验收门。

这些对象未冻结前，实验保持 working / unverified / low。
