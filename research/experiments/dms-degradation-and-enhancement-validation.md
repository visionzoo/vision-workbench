---
status: working
type: experiment
rigor: standard
provenance: public-research-plus-user-problem-definition
evidence_status: unverified
owner_review: pending
ip_review: pending
confidence: low
created: 2026-08-05
updated: 2026-08-05
tags: [dms, degradation, enhancement, ir, robustness, validation, deployment]
related: [../../foundations/mechanisms/visual-degradation-modeling.md, ../../foundations/tasks/task-oriented-image-enhancement.md]
---

# DMS degradation and enhancement validation

## 1. Evidence boundary

本文只定义验证协议，不报告尚未运行的结果。当前没有在仓库中固定合法数据 manifest、退化参数统计、HQ/LQ 配对、增强模型、训练日志、目标设备或人工语义安全复核结果。

用户问题指向 IR DMS 中的模糊、低照度、压缩、反光、小尺寸眼部及关键点/眼状态任务；这些只用于确定实验对象，不构成方法有效性的证据。任何数据、模型和设备结果在进入仓库前必须重新检查权属和可披露边界。

## 2. 决策问题

本实验要区分三个问题：

```text
Q1: 受控退化训练是否提高真实 DMS 坏画质鲁棒性？
Q2: 复杂或学习式退化是否比简单受控退化提供额外信息？
Q3: 推理前增强是否在鲁棒训练之外继续提高任务效果，且不引入语义风险和不可接受成本？
```

不能用一组增强图更清晰、PSNR 更高或单个 badcase 修复，直接回答上述问题。

## 3. 主要假设与反证

### H1：链路驱动的受控退化有效

预测：在训练预算和样本预算一致时，基于真实 badcase 参数范围的模糊、缩放、噪声、压缩、曝光和局部反光退化，会改善真实退化 holdout 上的检测、关键点、眼状态或 usability 指标，同时正常集退化受控。

反证：收益只出现在合成测试集；真实 holdout 无改善；正常集明显退化；或提升来自额外样本量、阈值变化和数据泄漏。

### H2：高阶或学习式退化只在分布更接近真实链路时有价值

预测：Real-ESRGAN-style 高阶组合或 ReDegNet-style 学习退化，在简单受控方案无法覆盖的真实 slice 上进一步改善任务指标。

反证：复杂方案仅提高视觉多样性，不改善真实任务；产生标签失效和不现实组合；对 seed 敏感；或学习到伪 HQ / 数据源偏差。

### H3：增强模型不是默认必要模块

预测：鲁棒训练已经吸收大部分收益，独立增强前处理的额外增益有限，或被时延、量化和状态翻转抵消。

反证：在多个真实 holdout 和目标设备上，增强前处理稳定提高下游指标，且正常集、语义安全和时延均通过冻结门限。

### H4：任务导向 loss 比纯视觉质量 loss 更符合 DMS 目标

预测：加入下游 detection/keypoint/classification/usability loss 后，任务指标优于只使用 L1/Perceptual/Edge 的增强模型，并降低增强诱发的语义翻转。

反证：任务 loss 只过拟合冻结下游模型；跨模型或跨设备失效；视觉保真下降；或无需增强即可取得同等收益。

### H5：输入链路或标签可能才是主要瓶颈

预测：修正 YUV 顺序、range、CSC、resize/crop、标签和 usability 规则后，退化/增强的边际收益显著下降。

反证：在输入合同和 Oracle 冻结后，真实退化仍是主要误差来源。

## 4. Gate 0：先冻结输入和 Oracle

任何退化或增强实验前必须通过：

- 确认算法输入是 NV12/NV21、YUV/YVU、420/422 及实际 stride；
- 固定 full/limited range、BT.601/BT.709 和 CSC；
- 保存同一帧原始 YUV、PC 解码图和模型实际输入 tensor；
- 固定 crop、resize、padding、通道、归一化和坐标逆变换；
- 建立 `open / closed / ambiguous / unusable` 及关键点可标注性规则；
- 同一 driver / vehicle / session 不跨 split；
- 阈值在 test 之前冻结。

Gate 0 未通过时，停止后续实验；数据增强不能用于掩盖链路错误。

## 5. 数据合同

### 5.1 三套数据

1. **Clean/control set**：基础画质和语义明确，用于检查正常性能回归；
2. **Real degradation holdout**：真实模糊、噪声、压缩、反光、过曝、低对比度、小眼部等，不参与退化参数调优；
3. **Synthetic degradation set**：从训练样本按版本化配置生成，只用于训练或开发集压力测试。

若没有真实 HQ/LQ 配对，不伪造 PSNR/SSIM 的 ground truth；增强模型可先使用公开/自建合法配对或自监督方案，但最终仍由真实任务 holdout 验收。

### 5.2 采样单位

- 静态任务：image / face ROI / eye ROI；
- 时序任务：video segment；
- 同一源帧的多个退化版本只能出现在同一 split；
- 结果置信区间按 driver 或 video group bootstrap，不按帧假设独立。

### 5.3 Slice

至少记录：

- eye effective pixel size；
- motion blur / defocus；
- noise / low contrast；
- compression；
- local over-exposure / IR reflection；
- glasses / occlusion；
- frontal / side-face；
- open / closed / ambiguous / unusable。

## 6. 实验矩阵

### Phase A：退化训练

| ID | 训练输入 | 目的 |
|---|---|---|
| D0 | 原始训练数据 | 基线 |
| D1 | 等样本预算的单项受控退化 | 识别有效退化原语 |
| D2 | 链路驱动的受控组合退化 | 验证真实组合是否有增益 |
| D3 | Real-ESRGAN-style 高阶退化 | 仅在 D2 覆盖不足时激活 |
| D4 | ReDegNet-style 学习退化 | 仅在有合法数据、伪 HQ 误差可审查时激活 |

D1–D4 必须保持：

- 相同基础训练样本 ID；
- 相同训练 step / early-stop；
- 相同模型、初始化和 evaluator；
- 至少多个 seed；
- 原图与退化图混合比例冻结；
- 每个生成样本记录实际参数。

### Phase B：增强模型

| ID | 系统 | 目的 |
|---|---|---|
| E0 | 最佳 D0–D2 感知模型，原图推理 | 鲁棒训练控制组 |
| E1 | 增强图仅作为训练 augmentation，推理仍用原图 | 测试 deployment-free 收益 |
| E2 | `L1/Charbonnier` 增强前处理 + 冻结感知模型 | 像素保真基线 |
| E3 | `pixel + perceptual + edge` + 冻结感知模型 | 检查视觉 loss 的边际作用 |
| E4 | `pixel/edge + downstream task + safety` 联合或分阶段训练 | 任务导向候选 |
| E5 | 条件触发增强，否则原图 | 仅在 quality gate 稳定后激活 |

不要求一开始实现全部候选。最低信息增益顺序是：

```text
D0 → D1/D2 → E1 → E2 → E4
```

D3、D4、E3、E5 只有当前结果留下可区分问题时再激活。

## 7. 任务指标

### 7.1 检测与定位

- face / eye detection precision、recall、F1；
- small-eye bins recall；
- landmark NME、median、P90、P95；
- failure rate；
- ROI extraction success。

### 7.2 眼状态与 usability

- open/closed frame F1；
- false-open / false-closed；
- ambiguous / unusable catch rate；
- usable gate 在固定 normal retention 下的坏样本召回；
- confidence calibration；
- 若进入事件链，报告事件级误报、漏报、延迟和恢复。

### 7.3 分桶与不确定性

所有主指标分别报告：

- clean；
- each real degradation slice；
- overall real holdout；
- domain-holdout；
- mean + group bootstrap interval；
- 多 seed 均值与方差。

总体平均不能掩盖某个安全关键 slice 的退化。

## 8. 增强语义安全指标

增强模型除任务指标外必须统计：

```text
state_flip:
  raw and enhanced predictions disagree,
  and human Oracle supports raw or marks enhanced as wrong

unknown_to_confident:
  raw input is unusable/ambiguous,
  enhanced output receives high-confidence open/closed

structure_hallucination:
  enhanced eye contour/keypoints appear stable,
  but source pixels do not support the structure
```

具体报告：

- enhancement-induced open↔closed flip rate；
- unusable→confident rate；
- left/right eye contradiction；
- landmark displacement normalized by eye width；
- temporal flicker and state oscillation；
- 人工复核的 hallucination / oversharpen / reflection amplification。

人工 Oracle 不必覆盖全部数据，但抽样方案、人数、分歧处理和样本数必须记录。

## 9. 图像质量与退化拟合指标

图像指标是辅助证据：

- 有真实配对：PSNR、SSIM、LPIPS、edge preservation；
- 无真实配对：亮度、噪声、模糊、压缩和频谱分布；
- 合成退化与真实 slice 的参数/特征分布比较；
- 人工检查不现实组合和标签失效。

不能用“视觉上更清晰”替代任务与语义安全验收。

## 10. 工程指标

- degradation generation throughput and storage；
- enhancement-only latency；
- end-to-end P50/P95 latency；
- CPU/GPU/NPU utilization；
- model size and peak memory；
- FP32/FP16/INT8 task alignment；
- conditional enhancement trigger rate；
- fallback and bypass behavior。

推理增强必须保留原图直通和可回滚开关。

## 11. 接受门与停止条件

具体数值由本人在查看 test 前冻结：

```yaml
clean_regression_max: T_clean
real_holdout_gain_min: T_real
critical_slice_regression_max: T_slice
state_flip_max: T_flip
unknown_to_confident_max: T_unknown
latency_budget: T_latency
memory_budget: T_memory
```

### 接受 D1/D2

- 真实 holdout 达到 `T_real`；
- clean 与关键 slice 不超过退化门；
- 多 seed 稳定；
- 无 split / parameter leakage。

### 激活 D3/D4

仅当 D1/D2 的残余错误与复杂退化相关，并且新方案能产生不同预测；不得因为方法新颖自动激活。

### 接受推理增强

- 相比最佳鲁棒训练控制组仍有稳定任务增益；
- state flip、unknown→confident 和 hallucination 通过门限；
- 量化和目标设备上收益保留；
- 时延、内存、fallback 和诊断能力满足预算。

### 停止增强路线

任一条件成立即停止或退回离线 augmentation：

- 只改善 PSNR/观感，不改善真实任务；
- 改善困难集但破坏 clean 或关键安全 slice；
- 产生不可接受的语义翻转；
- 量化后收益消失；
- 性能成本超过收益；
- 链路修复后增强不再有边际价值。

## 12. 必须保存的制品

```text
manifests/
  train.jsonl
  val.jsonl
  real_holdout.jsonl
configs/
  degradation-*.yaml
  enhancement-*.yaml
runs/<run_id>/
  environment.json
  model-manifest.json
  metrics.json
  slice-metrics.json
  semantic-safety.json
  latency.json
  examples/
```

每个 run 至少绑定：Git commit、数据 manifest hash、模型权重 hash、随机种子、预处理版本、退化配置和 evaluator 版本。

## 13. 当前状态

- 协议已定义，实验未运行；
- 未选择具体增强网络；
- 未承诺 Real-ESRGAN 或 ReDegNet 进入训练；
- 未冻结任何数值门限；
- 未取得可写入仓库的 DMS 数据与设备证据；
- 本文只有在真实制品和本人审查支持后才能晋级。
