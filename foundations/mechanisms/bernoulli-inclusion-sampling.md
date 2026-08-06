---
status: working
type: mechanism
rigor: standard
provenance: public-primary-papers-and-official-implementations
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-08-04
updated: 2026-08-04
tags: [sampling, dataset, bernoulli, poisson-subsampling, class-imbalance, reproducibility]
---

# Bernoulli inclusion sampling for training data

## 1. Problem

“通过伯努利采样生成训练样本”容易混淆两件事：

1. **生成新样本**：合成新的图像、标注或特征；
2. **从候选池抽取训练子集**：决定已有样本是否进入本次数据集或训练迭代。

伯努利采样只直接解决第二件事。对候选样本 \(i\) 生成独立包含变量：

\[
Z_i \sim \operatorname{Bernoulli}(p_i),\qquad
S=\{i\mid Z_i=1\}.
\]

其中 \(p_i\) 是样本的包含概率，\(S\) 是最终子集。它不创造新的视觉信息，也不自动保证类别、人员、车辆、场景或时间分布合理。

本文只讨论这种**独立包含机制**在视觉训练数据选择中的作用、边界和验证方式，不把所有随机抽样方法统称为伯努利采样。

## 2. Terminology and identity

当所有样本共享同一个概率 \(p\) 时：

\[
|S|\sim \operatorname{Binomial}(N,p),\qquad
\mathbb{E}|S|=Np,\qquad
\operatorname{Var}(|S|)=Np(1-p).
\]

当每个样本使用不同的 \(p_i\) 时，样本总数服从 Poisson-binomial distribution，期望为：

\[
\mathbb{E}|S|=\sum_i p_i.
\]

不同领域的命名并不完全一致：

- CatBoost 官方文档把“每个样本按 `subsample` 概率独立选入”称为 **Bernoulli bootstrap**；
- 差分隐私文献和 Opacus 把同类独立包含机制称为 **Poisson subsampling**；
- CatBoost 同时还定义了另一种 **Poisson bootstrap**，其对象权重来自 Poisson 分布，不能仅凭“Poisson”一词判断是否与独立 0/1 包含相同。

因此，记录方案时至少写清：

```text
sampling unit
+ inclusion probability
+ whether decisions are independent
+ with/without replacement
+ fixed or random sample size
+ resampling frequency
```

不要只写“Bernoulli sampling”或“Poisson sampling”。

## 3. Where it is actually used

### 3.1 Stochastic boosting

随机子采样可在每棵树或每层选择分裂时减少参与计算的训练样本，并引入正则化。CatBoost 的 Bernoulli 模式明确让每个样本独立地以 `subsample` 概率参与当前分裂选择。

这说明该机制是实际训练算法的一部分，但不能反推出它对任意视觉神经网络或离线数据集都更优。

### 3.2 Differentially private SGD

Opacus 的 `DPDataLoader` 使用 Poisson sampling：每个数据项按 `sample_rate` 独立决定是否进入下一批次，因此 batch size 是随机的，并可能出现空 batch。这里的采样方式与隐私会计假设绑定，不能用普通 shuffle + fixed batch 替代后仍沿用相同隐私结论。

### 3.3 Learned set subsampling

视觉研究中也有方法用条件独立 Bernoulli 变量先筛选候选元素，再用后续依赖模型处理元素间关系。此类工作说明 Bernoulli 决策可以作为可学习子采样的第一阶段，但已经不再是固定概率的简单数据抽取。

## 4. What it is not

| 方法 | 样本数 | 是否允许重复 | 主要控制对象 | 与伯努利独立包含的差异 |
|---|---:|---:|---|---|
| Fixed-size simple random sampling | 固定为 \(k\) | 否 | 总量 | 样本包含事件相互依赖 |
| Bootstrap sampling | 通常固定抽取次数 | 是 | 重采样分布 | 同一样本可以出现多次 |
| Stratified sampling | 各层固定或受控 | 视实现而定 | 类别/场景比例 | 显式保证分层覆盖 |
| Group/cluster sampling | 以组为单位 | 通常否 | 人员、视频、车辆、场景 | 组内样本共同进入或退出 |
| Importance sampling | 固定或随机 | 视实现而定 | 信息量或梯度贡献 | 非均匀概率通常需要权重校正 |
| Hard-example mining | 由模型错误驱动 | 视实现而定 | 困难样本 | 选择并非独立且会随模型变化 |

如果目标是“恰好抽取 10 万张图”，固定大小无放回抽样通常比伯努利采样直接；如果目标是保持各类和各场景比例，分层采样通常更稳。

## 5. When the mechanism is reasonable

伯努利独立包含适合以下条件：

- 候选池很大，允许最终样本量围绕期望值波动；
- 每个样本可以独立决策，便于流式、分布式或增量处理；
- 只需要控制边际包含概率，不要求精确配额；
- 数据已先按人员、车辆、视频或采集批次完成隔离，不会因单帧抽样制造数据泄漏；
- 采样结果有 manifest、随机种子和分布审计，可以复现与撤销。

它的工程优势主要是决策局部化：每个样本只需知道自己的 \(p_i\) 和随机数，不必先对全体排序或维持全局固定计数。

## 6. Failure modes in vision datasets

### 6.1 Rare slices can disappear

某个稀有切片只有 \(m\) 个样本、统一包含概率为 \(p\) 时，该切片一个样本都未选中的概率为：

\[
P(K=0)=(1-p)^m.
\]

例如 \(m=5,p=0.2\) 时，完全丢失该切片的概率约为 32.8%。因此，长尾类别、强侧脸、反光、遮挡、极小目标等关键切片不能只依赖统一概率。

### 6.2 Frame-level independence does not imply information independence

连续视频帧即使分别抛硬币，视觉内容仍高度相关。结果可能保留大量近重复帧，却遗漏另一个视频、人员或摄像头条件。

对于视频任务，抽样单位通常应优先考虑：

```text
event / clip / track / person / vehicle / scene
```

而不是默认单帧。

### 6.3 It does not preserve business distributions

统一 \(p\) 只能在期望意义上保持总体比例；单次结果仍可能在小切片上偏移。不同项目、人员、设备和时间段的样本量差异很大时，大组会继续主导结果。

### 6.4 Non-uniform probabilities change the training objective

若困难样本使用更高 \(p_i\)，训练子集已经不再代表原始经验分布。目标是优化原始分布期望时，可能需要按包含概率进行权重校正；目标本来就是提高关键切片权重时，则应明确这是任务分布重定义，而不是“无偏采样”。

### 6.5 Randomness can hide unstable conclusions

只运行一个 seed，可能把偶然抽样波动误判为模型改进。样本预算越小、长尾越严重，这个问题越明显。

## 7. Recommended vision-data contract

### 7.1 Freeze the sampling unit first

先定义一条独立决策对应什么：

- 独立图片；
- 同一事件的 clip；
- 同一目标的 track；
- 同一人员或车辆；
- 同一采集场景或批次。

用于 train/validation/test 隔离的 group，不应在组内再按帧随机拆到不同 split。

### 7.2 Use stratified Bernoulli only when needed

可以按切片设置 \(p_g\)：

\[
Z_i\sim \operatorname{Bernoulli}(p_{g(i)}).
\]

但 \(p_g\) 不能只由类别标签决定，还要考虑人员、设备、场景、时间、难度和标注可靠性。关键稀有层更适合使用：

```text
minimum quota
+ Bernoulli sampling for the remaining pool
```

而不是继续提高全局 \(p\)。

### 7.3 Make selection order-independent

直接按列表顺序调用随机数生成器，会让文件排序、分片或并行方式改变结果。更稳的做法是由固定 seed 与稳定 `sample_id` 生成确定性随机值：

```python
from hashlib import blake2b


def stable_uniform(sample_id: str, seed: int) -> float:
    payload = f"{seed}:{sample_id}".encode("utf-8")
    value = int.from_bytes(blake2b(payload, digest_size=8).digest(), "big")
    return value / 2**64


def selected(sample_id: str, probability: float, seed: int) -> bool:
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be in [0, 1]")
    return stable_uniform(sample_id, seed) < probability
```

这不是密码学安全承诺，只用于让同一数据版本、ID、seed 和概率得到稳定结果。

### 7.4 Persist a manifest

至少保存：

```text
sample_id
source_version
group_id
stratum
inclusion_probability
seed or sampler_version
selected
split
reason / policy_version
```

仅保存最终文件列表不足以解释为什么某个样本进入或退出，也无法在策略变化后做差异审计。

## 8. Verification

在视觉训练数据上采用前，不用“有人使用”作为充分证据，应做等预算对照：

```text
A. fixed-size uniform sampling without replacement
B. uniform Bernoulli inclusion
C. stratified fixed-size sampling
D. stratified Bernoulli inclusion
```

至少固定：

- 相同候选池和 group split；
- 相同期望样本预算；
- 相同训练配置与评测集；
- 多个 sampling seed 和 training seed；
- 类别、场景、人员、设备、难度分桶指标。

报告内容至少包括：

- 实际样本总数及其波动；
- 每个关键切片的样本数和零覆盖情况；
- 重复/近重复比例；
- 总体指标与最差切片指标；
- 多 seed 均值、方差和最坏结果；
- 采样耗时、存储和可复现性。

### Acceptance condition

只有当独立包含带来的实现简化、训练加速、正则化或隐私假设收益，超过样本量波动、长尾丢失和分布失控成本时，才值得采用。

### Rejection or rollback triggers

- 任一关键切片低于最低样本数；
- 人员、视频、车辆或场景发生 split 泄漏；
- 结果对 seed 高度敏感；
- 仅总体指标提升，但关键切片显著退化；
- 无法从 manifest 重现选样结果；
- 实际需求是固定配额或严格比例，却仍使用统一伯努利采样。

## 9. Current belief and boundary

**当前判断**：伯努利独立包含是一种真实、简单且被实际训练系统采用的采样原语；它适合随机大小子集、局部独立决策和特定训练/隐私机制，但不是视觉训练集构造的通用最优方案。

**竞争解释**：如果它在某个项目中有效，收益可能来自减少训练量、增加随机正则化、改变困难样本权重或修正原数据冗余，而不一定来自“伯努利分布本身更适合训练”。受控对照应区分这些解释。

**未验证项**：本页尚未在本仓库的具体视觉数据集上运行多 seed 对照；因此保持 `working / partial / pending`，不把理论性质或外部实现使用情况升级为本人的视觉训练结论。

## Sources

1. CatBoost, [Bootstrap options](https://catboost.ai/docs/en/concepts/algorithm-main-stages_bootstrap-options): Bernoulli mode independently samples each example with probability controlled by `subsample`; the same page distinguishes it from CatBoost's Poisson bootstrap.
2. Opacus, [DP Data Loader](https://opacus.ai/api/data_loader.html): Poisson sampling independently selects each dataset element for the next batch and therefore produces variable-size and possibly empty batches.
3. Yuqing Zhu and Yu-Xiang Wang, [Poisson Subsampled Rényi Differential Privacy](https://proceedings.mlr.press/v97/zhu19c.html), ICML 2019: defines Poisson subsampling as selecting each data point independently with a coin toss.
4. Jerome H. Friedman, [Stochastic Gradient Boosting](https://doi.org/10.1016/S0167-9473(01)00065-2), 2002: establishes random per-iteration training-data subsampling in gradient boosting; the original formulation uses fixed-size sampling without replacement, which is related but not identical to Bernoulli independent inclusion.
5. Bruno Andreis et al., [Set Based Stochastic Subsampling](https://arxiv.org/abs/2006.14222), 2020: uses conditionally independent Bernoulli variables as a first-stage learned subsampling mechanism across visual tasks.
