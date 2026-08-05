---
status: working
type: mechanism
rigor: standard
provenance: public-primary-papers
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-08-05
updated: 2026-08-05
tags: [degradation, augmentation, robustness, image-restoration, dms, ir]
related: [../tasks/task-oriented-image-enhancement.md, ../../research/experiments/dms-degradation-and-enhancement-validation.md]
---

# Visual degradation modeling

数据退化建模回答的不是“怎样把图片变好看”，而是：**真实成像、传输和处理链路会怎样破坏任务所需信息，以及训练和评测如何近似这些变化。**

## 1. 对象边界

给定原始或相对高质量图像 `x`，退化过程生成低质量观测 `y`：

```text
y = D(x; z)
```

其中 `D` 是退化链，`z` 是模糊核、缩放、噪声、曝光、压缩等参数或学习到的退化表示。

退化建模可以用于：

1. **训练增强**：让感知模型接触合理的低质量样本；
2. **压力测试**：测量模型从轻度到严重退化的性能曲线；
3. **恢复模型配对数据构造**：生成 `HQ → LQ` 训练对；
4. **域差异诊断**：验证某类退化是否解释真实 badcase。

它不等于：

- 生成新的语义样本；
- 修复 NV12/NV21、full/limited range、CSC 或 stride 等输入链路错误；
- 证明某个增强模型会提高下游任务；
- 用任意模糊和噪声代替真实数据采集。

## 2. 三类退化建模

### 2.1 受控参数退化

常见原语包括：

- isotropic / anisotropic blur；
- motion blur / defocus blur；
- downsample + upsample；
- Gaussian / Poisson / sensor-like noise；
- JPEG 或视频压缩；
- 亮度、对比度、gamma、局部过曝和欠曝；
- ISP 风格的降噪涂抹、锐化和 ringing。

优点是变量可解释、可消融、适合建立性能曲线；缺点是参数和组合若脱离真实链路，会生成“形式复杂但分布错误”的样本。

BSRGAN 将 blur、downsampling、noise 等原语随机重排以扩大真实退化覆盖；Real-ESRGAN 进一步使用高阶退化过程，并显式考虑 JPEG、ringing 和 overshoot。二者首先服务于 blind super-resolution 的训练对合成，不能自动视为检测、关键点或 DMS 的合适默认增强。

### 2.2 链路驱动退化

从具体设备链路出发建模：

```text
scene motion
→ exposure / gain
→ sensor noise
→ ISP denoise / sharpen
→ resize / color conversion
→ encoder
→ decoder / algorithm input
```

这种方式的价值在于每个参数都能对应到真实观测或日志。它通常比无约束的复杂退化更适合工业感知，但需要保存原始输入、编码参数、ISP 状态或至少可重复的场景切片。

### 2.3 学习式退化

ReDegNet 使用真实低质量人脸及其恢复得到的伪高质量对应，学习退化感知、尽量与内容解耦的表示，再把退化迁移到其他高质量图像上。

这说明退化可以由数据学习，而不必全部手工枚举；但它没有证明：

- 恢复后的伪高质量图像是真实 ground truth；
- 从可见光人脸学习到的退化可直接迁移到 IR DMS；
- 学习式退化一定比受控参数退化更接近目标设备；
- 生成样本保持了眼睛开闭、可见性等安全相关语义。

## 3. DMS 中的主要用途

### 3.1 鲁棒性训练

对已有合法样本施加与真实 badcase 对应的退化，训练：

- 人脸和眼部检测；
- 关键点定位；
- 眼睛开闭分类；
- 图像质量或 `usable / unknown` 判断。

优先建模的候选通常包括：小尺寸眼部、运动模糊、失焦、压缩、低对比度、IR 反光、局部过曝和降噪涂抹。具体顺序必须由真实失败分布决定。

### 3.2 专项压力测试

固定一批语义明确的样本，逐级增加单一退化强度，可以回答：

- 眼部尺寸降到什么范围后首先失效；
- 关键点误差从哪个模糊等级开始陡增；
- open/closed 置信度何时失去校准；
- usability gate 是否早于错误分类拒绝输入。

这种曲线比只看一个混合 badcase 指标更能定位瓶颈。

### 3.3 训练恢复模型

退化模型也可生成 `HQ/LQ` 对训练图像增强或恢复网络；此用途与“直接训练 DMS 感知模型的 augmentation”必须分开评价。恢复图更清晰，不表示下游眼状态更可靠。

## 4. 关键失败模式

### 4.1 标签失效

当模糊、反光或降采样已经让眼睛状态不可判定时，继续继承原始 `open/closed` 标签会制造错误监督。退化后应重新判定：

```text
semantic label preserved?
landmark still findable?
eye state still usable?
otherwise → ambiguous / unknown / reject
```

### 4.2 组合失真

多个真实退化各自合理，不代表任意顺序和强度组合仍合理。过度叠加可能产生设备上不会出现的图像，并让模型学习合成伪影。

### 4.3 掩盖工程错误

颜色偏紫、亮度范围错误、UV/VU 颠倒或板端预处理差异属于确定性链路错误。把这些错误加入训练只能让模型适应 bug，而不是修复输入合同。

### 4.4 视频相关性被忽略

逐帧独立退化无法模拟曝光变化、运动轨迹、压缩 GOP 和 IR 反光的时间连续性。事件级 DMS 需要同时检查退化的时间模型和报警状态机。

### 4.5 长尾覆盖幻觉

合成了很多图像，不等于覆盖了真实困难场景。应按 driver / vehicle / session 分组，并在真实 domain-holdout 上验收。

## 5. 最小设计合同

每次退化实验至少固定：

```yaml
degradation_id: <name-and-version>
source_manifest: <immutable-sample-list>
sampling_unit: image | roi | video-segment
degradation_order: <ordered-or-randomized>
parameter_ranges: <versioned-config>
random_seed: <seed>
label_policy: preserve | relabel | unknown | reject
output_manifest: <generated-sample-list>
```

同时保存：

- 原始样本 ID；
- 每个样本实际抽到的退化参数；
- 代码 commit 和依赖版本；
- 生成前后可视化；
- 真实 badcase 与合成样本的分桶比较。

## 6. 竞争解释

若退化训练后真实 badcase 指标改善，至少仍需区分：

1. 退化分布更接近真实链路；
2. 只是增加了数据量或正则化强度；
3. 阈值或类别分布被改变；
4. 模型牺牲了正常样本性能以换取困难样本性能；
5. 测试集和退化参数存在同源泄漏。

区分它们需要等样本预算、等训练预算、真实 holdout、多 seed 和正常集回归。

## 7. DMS 实际验证入口

本机制当前不承诺进入生产。统一验证合同见：

- [DMS degradation and enhancement validation](../../research/experiments/dms-degradation-and-enhancement-validation.md)

第一阶段只比较：

```text
no degradation
vs controlled single/composed degradation
```

只有受控退化无法解释真实 badcase，且具备合法数据和可复核 Oracle 时，才激活 Real-ESRGAN-style 高阶退化或 ReDegNet-style 学习退化。

## 8. 当前判断与撤销条件

当前判断：退化建模是视觉鲁棒性训练和测试中的可复用机制；在 DMS 中更可信的起点是**真实链路驱动、参数受控、标签可重新判定**的退化，而不是默认使用最复杂的生成器。

该判断会被以下证据修订：

- 受控退化在真实 holdout 上持续无效；
- 学习式退化经多 seed 和独立测试稳定优于受控方案；
- 合成退化无法保持 DMS 语义或导致正常集显著退化；
- 新设备链路表明主要问题不是像素退化，而是 ROI、标签、模型或时序决策。

## 9. Primary sources

- Zhang et al., *Designing a Practical Degradation Model for Deep Blind Image Super-Resolution (BSRGAN)*: https://arxiv.org/abs/2103.14006
- Wang et al., *Real-ESRGAN: Training Real-World Blind Super-Resolution with Pure Synthetic Data*: https://arxiv.org/abs/2107.10833
- Official Real-ESRGAN implementation: https://github.com/xinntao/Real-ESRGAN
- Li et al., *From Face to Natural Image: Learning Real Degradation for Blind Image Super-Resolution (ReDegNet)*: https://www.ecva.net/papers/eccv_2022/papers_ECCV/html/2925_ECCV_2022_paper.php
