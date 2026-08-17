# Data and training

本页不收集所有分支的训练配方，只解释自有数据如何经过输入、标签分配和损失影响 YOLO 结果。具体命令、配置和实验输出进入工程案例。

## 1. 训练因果链

```text
图像与框标注
→ resize / crop / augmentation
→ backbone + neck
→ Detect 的 P3/P4/P5 raw outputs
→ anchor points 与候选位置
→ 标签分配
→ classification / box / DFL loss
→ 梯度更新
```

固定 YOLO11 revision `b89d6f407` 使用 TaskAlignedAssigner，为候选位置生成目标分数和前景 mask；分类项使用 BCE，定位由 IoU 类 box loss 与 DFL 组成（Y019）。这只描述该实现，不能外推所有 YOLO 分支。

## 2. 训练前先回答四件事

1. **目标还有多少有效像素**：记录原图、裁剪后和网络输入中的目标宽高，并换算到 P3/P4/P5 尺度。
2. **标签是否完整且一致**：漏标会把正确候选当背景；框边界、遮挡和截断规则不一致会污染定位监督。
3. **预训练模型与任务差多远**：类别少不等于任务简单；IR、局部裁剪、极端视角和新尺寸分布都可能造成失配。
4. **训练输入能否在部署端复现**：颜色、range、resize、padding 和 normalization 不一致时，训练指标不能直接转成板端结果。

## 3. 标签分配为什么重要

多尺度输出只提供候选位置，不保证目标得到有效监督。标签分配决定：

- 哪个尺度、哪些位置成为正样本；
- 分类置信度和定位质量如何共同影响目标分数；
- 小目标、边界目标和重叠目标获得多少梯度；
- 标签噪声会影响哪些候选。

因此“小目标漏检”至少保留四种竞争解释：输入中有效像素不足、标签不完整、P3/P2 接口不合适、正样本分配不足。只有分层统计目标尺寸、正样本数和 raw score 才能区分。

## 4. 三类损失分别约束什么

| 项 | 直接约束 | 观察方式 | 常见误判 |
|---|---|---|---|
| Classification | 候选位置对各类别的 logits | 正负样本数量、类别分层、score 分布 | 总 cls loss 下降就表示召回改善 |
| Box / IoU | 解码框与目标框的重合关系 | IoU 分层、中心偏差、宽高误差 | 框偏一定来自坐标后处理 |
| DFL | anchor point 到框四边距离的离散分布 | 分布熵、边界 bin、decode 前后误差 | 只对比最终四个坐标即可定位量化问题 |

总 loss 是加权结果，可能掩盖某个尺度或类别没有正样本。必须同时看组件、尺度分层和最终任务指标。

## 5. 真正值得控制的变量

| 变量 | 它改变什么 | 需要固定或记录什么 |
|---|---|---|
| 输入尺寸与裁剪 | 目标像素、上下文、候选网格和算力 | 原图到输入的坐标链、目标尺寸分布 |
| 输出特征层 | 候选位置密度和融合成本 | P2/P3/P4/P5 接口、neck/head、延迟 |
| 冻结与解冻 | 预训练表征保留和新任务适配 | 冻结模块、epoch、optimizer state、梯度 |
| 学习率、batch、累积 | 优化噪声和有效步长 | scheduler、warm-up、有效 batch |
| mosaic、mixup、随机裁剪 | 尺度、上下文和目标共现分布 | 增强概率、关闭时机、增强后标签 |
| 标签分配 | 正样本数量和质量 | assigner 版本、参数、每尺度前景统计 |

## 6. 分支事实与当前经验

- YOLOX 使用 anchor-free、解耦 head 和 SimOTA，可作为动态分配机制的可读基线，不表示它在任意私有数据上更优（Y008）。
- YOLO11 主要由 Ultralytics 文档、配置和源码定义；复现必须冻结 package/revision，不能从营销概述补出未披露细节（Y019）。
- YOLO26 报告 Progressive Loss、STAL 和 P2/P6 配置；官方未为所有 P2/P6 规模提供对应预训练权重，适用性仍需自有训练验证（Y023）。
- YOLO-World、YOLOE 和 YOLOE-26 需要记录图文预训练、prompt、文本编码器或词汇缓存，不能套用闭集检测训练记录（Y018、Y021、Y023）。

[YOLO11n 局部目标案例记录](../../../../engineering/cases/yolo11n-local-target-hisi-int8.md)中声称训练—ONNX—INT8 链路已跑通，并描述了阈值敏感现象；但当前资产盘点尚未找到能对应同一权重、配置、日志和评测输出的原始证据。它目前不能支持训练策略、P2/P3 选择、量化根因或链路已复现等技术结论。

## 7. 每次训练最少保存什么

- 代码 revision、配置、模型和初始权重哈希；
- 数据清单、split、类别、标注规则与目标尺寸分层；
- 输入、增强、主要超参、冻结策略和 assigner；
- 每尺度正样本统计与 loss 组件；
- 最佳权重选择依据、任务指标和典型失败样本；
- 与导出、板端一致的预处理说明。

缺少这些信息时，训练结果只能作为观察，不能晋级为可复用结论。

## 8. 常用 Loss 最低掌握线

Loss 的最低掌握标准不是“知道名字”，而是至少能回答四件事：**预测量是什么、target 是什么、公式惩罚什么误差、梯度最终推动模型改变什么**。下面以 YOLO11 检测链为主，同时补上读其他视觉模型时最常见的基础形式。

### 8.1 Cross Entropy：单标签多分类的基础形式

若一个样本只属于 `C` 个类别中的一个，logits 为 `z_j`，softmax 概率：

\[
p_j=\frac{e^{z_j}}{\sum_{k=1}^{C}e^{z_k}}
\]

真实类别为 `y` 时：

\[
L_{CE}=-\log p_y
\]

要能解释：CE 让不同类别通过 softmax 归一化后相互竞争，适合“恰好一个类别”的常规分类。**固定 YOLO11 检测分类项不是用 softmax CE，而是 BCEWithLogits**（Y019），所以不能看到“分类 loss”就默认是 CE。

### 8.2 BCEWithLogits：独立二元目标

对单个 logit `z`、target `y∈[0,1]`，令 `p=σ(z)`：

\[
L_{BCE}=-\left[y\log p+(1-y)\log(1-p)\right]
\]

`BCEWithLogitsLoss` 在数值上直接从 logits 计算，不需要先手工 sigmoid。固定 YOLO11 的分类监督对各类别 logits 使用该形式（Y019）。

必须能区分：

- softmax CE：类别之间总概率被归一化为 1；
- BCE：每个类别 logit 独立建模，可接受 soft target；
- loss 下降只说明监督目标拟合改善，不等价于最终 precision/recall 同时改善。

### 8.3 Focal Loss：给困难样本更高相对权重

对二分类，定义

\[
p_t=\begin{cases}
p,& y=1\\1-p,& y=0\end{cases}
\]

Focal Loss 可写成：

\[
L_{focal}=-\alpha_t(1-p_t)^\gamma\log(p_t)
\]

当容易样本已经有较高 `p_t` 时，`(1-p_t)^γ` 会压低其贡献，把优化注意力更多留给困难样本。Ultralytics 固定源码中存在这一实现，但 YOLO11 默认 `v8DetectionLoss` 仍直接使用 BCEWithLogits；因此“代码里有 FocalLoss”不等于“当前模型训练默认用了 FocalLoss”（Y019）。

### 8.4 IoU：先理解框几何，再理解 IoU-family loss

预测框 `B_p` 与真实框 `B_g`：

\[
IoU=\frac{|B_p\cap B_g|}{|B_p\cup B_g|}
\]

最直接的 IoU loss：

\[
L_{IoU}=1-IoU
\]

它直接优化重叠关系，但当两框没有交集时，仅从普通 IoU 很难表达“应该向哪个方向靠近”。因此常见检测器进一步使用 GIoU、DIoU、CIoU 等几何项。

### 8.5 GIoU、DIoU、CIoU：分别补包围区域、中心距离和宽高比

令 `C` 为同时包围预测框和真实框的最小闭包矩形，则：

\[
GIoU=IoU-\frac{|C\setminus(B_p\cup B_g)|}{|C|}
\]

DIoU 再显式加入中心距离。令 `ρ` 为两框中心点欧氏距离，`c` 为最小闭包矩形对角线长度：

\[
DIoU=IoU-\frac{\rho^2}{c^2}
\]

CIoU 在此基础上再加入宽高比一致性：

\[
v=\frac{4}{\pi^2}\left(\arctan\frac{w_g}{h_g}-\arctan\frac{w_p}{h_p}\right)^2
\]

\[
\alpha=\frac{v}{1-IoU+v},\qquad
CIoU=IoU-\frac{\rho^2}{c^2}-\alpha v
\]

对应 loss 通常写成 `1 - metric`。固定 YOLO11 `BboxLoss` 调用 `bbox_iou(..., CIoU=True)`，再以 target score 加权，因此当前锚点的 box loss 不是简单 `1-IoU`（Y019）。

理解这些公式时不要把“项更多”直接等同于“任何数据都更准”；它们只是改变几何误差的优化形状，最终收益仍需数据与训练验证。

### 8.6 DFL：把连续距离监督成两个相邻离散 bin

对某一个 `l/t/r/b` 距离 target `y`，设：

\[
l=\lfloor y\rfloor,\qquad r=l+1
\]

相邻两个 bin 的线性权重：

\[
w_l=r-y,\qquad w_r=y-l
\]

预测对 `K` 个 bins 给出 logits，DFL 使用两个相邻类别的加权交叉熵：

\[
L_{DFL}=w_l\,CE(z,l)+w_r\,CE(z,r)
\]

这相当于不强迫连续 target 只能落到一个整数 bin，而是让监督质量在线性插值后分配到左右两个 bin。推理时再用 softmax 后分布期望恢复连续距离：

\[
\hat d=\sum_{i=0}^{K-1} i\,p_i
\]

因此 DFL 必须同时从“训练监督”和“推理解码表示”两侧理解。固定 YOLO11 `reg_max=16`；`DFLoss` 对四个方向分别产生离散距离监督，并与 CIoU box loss 同时优化（Y019）。

### 8.7 YOLO11 检测总损失：三条监督不要混成一个数字

固定实现的核心可抽象为：

\[
L=\lambda_{box}L_{CIoU}+\lambda_{cls}L_{BCE}+\lambda_{dfl}L_{DFL}
\]

其中 `λ` 来自具体训练配置/hyperparameters，而不是 YOLO 家族永久不变的数学常数。三个组件的作用不同：

| 组件 | 直接改变的预测 | 主要错误信号 | 单独下降不能证明 |
|---|---|---|---|
| BCE | 类别 logits | 候选对类别目标的匹配 | 框定位正确、最终召回必然提高 |
| CIoU | 解码后的 box geometry | 重叠、中心、宽高比 | 分类分数正确、DFL 分布正常 |
| DFL | `l/t/r/b` 离散 logits | 距离分布与连续 target 的匹配 | decode、stride、anchor point 实现正确 |

尤其在量化/部署对齐时，最终框偏差可能来自 raw distribution、DFL expectation、anchor point、stride 或后续 decode；只看 `box loss` 无法定位这些推理链问题。

### 8.8 标签分配与 Loss 是两个不同问题

固定 YOLO11 的 TaskAlignedAssigner 使用分类分数和 IoU 共同形成 alignment metric，可概括为：

\[
m=s^{\alpha}\,u^{\beta}
\]

其中 `s` 是对应类别分数、`u` 是 overlap/IoU，固定源码锚点使用 `α=0.5, β=6.0`（Y019）。assigner 决定“哪些候选进入监督以及 target score 是什么”，loss 决定“对这些候选如何产生梯度”。

因此：

```text
assigner 错/不合适
→ 正样本集合和 target 已经偏了
→ 即使 BCE / CIoU / DFL 实现完全正确，也可能训练出错误行为
```

这也是为什么修改 loss 前，要先核查正样本数量、目标尺度、标签质量和 assigner 输出。

## 9. Loss 掌握自检

至少应能在纸上或白板上完成以下解释：

1. 写出 softmax CE 与 sigmoid BCE 的基本公式，并说明 YOLO11 默认分类项为什么属于后者。
2. 写出 Focal Loss 的 `(1-p_t)^γ`，解释它到底在压谁、为什么不能看到类不平衡就机械替换 BCE。
3. 从交并面积写出 IoU，并说明 GIoU、DIoU、CIoU 分别额外加入了什么几何约束。
4. 手写 DFL 对相邻两个 bins 的线性插值权重，并从 logits 推导到连续距离期望。
5. 解释 `box/cls/dfl` 三个 loss 哪一个下降时，哪些最终检测问题仍然完全可能存在。
6. 区分 label assignment 与 loss：一个决定监督对象，一个决定对监督对象如何优化。
7. 当修改 loss 后 mAP 上升时，仍要检查哪些分层指标，才能避免总指标掩盖小目标、难例或特定类别退化。

如果只能记住“Focal 解决类别不平衡”“CIoU 比 IoU 好”“DFL 提升定位”，还没有达到本页定义的掌握线。