# Architecture

本页以 Ultralytics YOLO11 的固定实现 `b89d6f407` 为深入理解锚点，再用其他分支解释机制变化。固定 revision 很重要：配置段名、模块实现和导出路径会随 release 改变（Y019）。

YOLO26 的完整逐层结构不在本页重复维护；见 [YOLO26 architecture and modification map](yolo26-architecture.md)。本页只保留跨分支机制变化和 YOLO11 锚点。

## 1. 先看完整数据流

```text
image
→ preprocessing
→ stem / backbone: P1/2 → P2/4 → P3/8 → P4/16 → P5/32
→ SPPF + C2PSA
→ top-down fusion: P5 → P4 → P3
→ bottom-up fusion: P3 → P4 → P5
→ Detect(P3, P4, P5)
→ box distributions + class logits
→ DFL / decode / score handling
→ NMS or end-to-end selection
```

`preprocessing`、标签分配、损失、decode 和 NMS 不都属于网络层，但它们共同决定最终结果。排查时必须先确认差异位于哪一段。

## 2. YOLO11 P3–P5 参考图

下面的节点编号来自固定的官方 `yolo11.yaml`，用于说明拓扑，不保证其他 package revision 保持相同编号（Y019）。

| 阶段 | 参考节点 | 空间尺度 | 主要作用 | 先观察什么 |
|---|---:|---:|---|---|
| 输入 | 网络外 | `H×W` | 颜色、range、resize、padding、layout | 实际送入模型的 tensor 是否一致 |
| Stem / P1–P2 | 0–2 | `1/2`、`1/4` | 早期下采样和局部特征形成 | 小目标是否在早期已失去有效像素；padding 是否产生位移 |
| P3 backbone | 3–4 | `1/8` | 保留较高空间分辨率，服务小目标 | 纹理和边缘响应、目标区域与背景是否可分 |
| P4 backbone | 5–6 | `1/16` | 中等尺度表征 | 目标语义是否形成、定位是否仍稳定 |
| P5 backbone | 7–10 | `1/32` | 深层语义、SPPF 聚合和 C2PSA | 深层表征、注意力与目标 runtime 支持 |
| Top-down fusion | 11–16 | `1/16 → 1/8` | 上采样深层语义并与 P4/P3 拼接 | 上采样尺寸、concat 输入和 channel 顺序 |
| Bottom-up fusion | 17–22 | `1/8 → 1/32` | 把浅层定位信息重新聚合到 P4/P5 | 下采样后的空间对齐和融合输出 |
| Detect | 23 | P3/P4/P5 | 每个尺度分别产生回归分布和类别 logits | 三个输入顺序、shape、stride 和输出语义 |

对 640×640 输入，P3/P4/P5 的空间尺寸通常是 80×80、40×40、20×20；对 224×224 输入则是 28×28、14×14、7×7。它只说明候选位置密度，不保证小目标一定得到有效监督或正确预测。

## 3. 各模块到底做什么

### Conv 下采样

YOLO11 使用 stride-2 convolution 逐级降低空间分辨率并增加通道。它扩大有效感受野并降低后续计算，但也会把局部目标压缩到更少位置。小目标在 P3 之前已不可分时，增加更深层容量通常无法恢复原始像素信息。

排查重点：kernel、stride、padding、输入奇偶尺寸、导出后的 padding 语义，以及目标经过每次下采样后的有效像素。

### C3k2 与 CSP 类路径

固定实现中的 C3k2 继承 C2f 的分流—变换—拼接结构，并可在内部选择 C3k block。它的意义是组织特征复用和梯度路径，不是一个可以脱离宽度、深度、shortcut 和具体实现单独排名的名称。

排查重点：输入输出 channel、隐藏通道缩放、分支 concat 顺序、shortcut、模型 scale，以及转换器是否保持相同拓扑。

### SPPF

SPPF 在不继续降低空间尺寸的情况下串行使用相同 max-pooling 聚合不同范围的上下文，再拼接输出。它改变的是深层特征的上下文范围，不会恢复已丢失的高分辨率细节。

排查重点：pool kernel、padding、concat 顺序和目标后端对 pooling 的实现。

### C2PSA

固定 YOLO11 实现先把通道分成两部分，只对其中一部分堆叠 PSABlock，再拼接投影。PSABlock 包含 attention、前馈网络和残差路径。它为深层特征增加较长距离的空间交互，同时引入 attention reshape、矩阵运算和更高的部署敏感性。

排查重点：输入 shape、head 数、reshape/transpose、attention 数值范围、算子融合和 INT8 支持；不能把模块名称直接等同于目标硬件收益。

### Top-down 与 bottom-up feature fusion

官方 YAML 把融合层与最终 Detect 都放在 `head:` 配置段中，但按功能划分，Upsample、Concat、C3k2 和 stride-2 Conv 组成 neck，只有最终 Detect 承担 detection head。配置段名不能替代模块职责判断。

Top-down 路径把 P5 语义送回 P4/P3；bottom-up 路径再把融合后的浅层信息聚合到 P4/P5。融合要求空间尺寸、channel 和来源节点同时正确。只要上采样、padding、concat 顺序或节点选择不同，最终框可能变化，即使单个卷积实现本身正确。

### Detect、DFL 与 decode

固定实现对 P3/P4/P5 各设回归分支和分类分支。回归侧输出四个方向的离散分布，`reg_max=16`；分类侧输出每类 logits。训练时三层 raw tensor 直接交给损失；推理时各尺度被展平拼接，DFL 把分布积分为距离，再结合 anchor points 和 stride 解码为框，分类 logits 经 sigmoid 得到分数（Y019）。

YOLO11 默认不是仅靠一个 `objectness` 数值解释全部置信度。导出图是否包含 decode 或 NMS 取决于 exporter 与参数；必须查看真实输出，不能仅凭文件名判断。

## 4. 训练路径与推理路径不是同一张语义图

```text
训练：raw P3/P4/P5 → anchor points → 标签分配 → box / cls / DFL loss
推理：raw P3/P4/P5 → DFL → decode → score → NMS / result selection
```

训练 loss 正常不证明推理 decode 正确；最终框一致也可能掩盖 raw tensor 的系统偏移。标签分配和损失见 [Data and training](data-and-training.md)，输出与 runtime 契约见 [Deployment](deployment.md)。

## 5. 跨分支只保留机制变化

| 机制变化 | 代表分支 | 真正改变什么 | 不能直接推出什么 | Source |
|---|---|---|---|---|
| 单次整图预测 | YOLOv1 | 把检测组织为单次前向回归 | 现代分支仍使用相同网格与损失 | Y001 |
| anchor 与多尺度预测 | YOLOv2 / YOLOv3 | 候选尺度、解码和多层输出 | 任意数据都适合原 anchor | Y002–Y003 |
| CSP/ELAN 类路径与多尺度融合 | YOLOv4、YOLOv5、YOLOv7 等 | 特征与梯度路径、neck 组织 | 同名模块跨仓库完全相同 | Y004、Y007、Y011 |
| anchor-free、解耦 head、动态分配 | YOLOX、PP-YOLOE、YOLOv8 等 | 候选定义、分类/定位路径和正样本选择 | 不再需要坐标形式和标签分配 | Y008–Y009、Y012 |
| 结构重参数化 | YOLOv6、YOLOv7 | 训练图与推理图发生变换 | 转换器已正确完成融合 | Y010–Y011 |
| one-to-one / NMS-free | YOLOv10、YOLO26 | 训练匹配和结果选择 | 任意导出图都无需外部 NMS | Y017、Y023 |
| 开放词汇与提示 | YOLO-World、YOLOE | 类别表示和运行时依赖 | 权重、词表和提示可跨实现混用 | Y018、Y021 |

完整分支身份只在 [Variants and implementations](variants.md) 维护。

## 6. 看一个具体权重时

至少锁定：仓库 revision、配置、scale、权重哈希、输入预处理、P3/P4/P5 节点、stride、输出 tensor、坐标格式、训练专用模块是否已融合，以及 decode/NMS 位于模型内还是模型外。开放词汇模型还要确认文本编码器或词汇嵌入是否仍在运行时图中。

## 7. 基础模块最低掌握线

下面不是要求背源码，而是规定一个“读到模块名后至少能还原到什么程度”的能力基线。目标是看到 YAML、`nn.Module` 或导出图时，能够从 tensor 流、公式和作用三个层次解释，而不是只记模块名称。

### 7.1 `Conv2d(bias=False) → BatchNorm2d → SiLU`

固定 YOLO11 `Conv` 的默认路径就是 `Conv2d(bias=False) → BatchNorm2d → SiLU`（Y019）。至少应能写出三步：

卷积：

$$
z_{o,i,j}=\sum_{c}\sum_{u,v}W_{o,c,u,v}\,x_{c,i+u,j+v}
$$

BatchNorm 在训练时对一个 channel 使用 mini-batch 统计量：

$$
\hat z=\frac{z-\mu_B}{\sqrt{\sigma_B^2+\epsilon}},\qquad
\mathrm{BN}(z)=\gamma\hat z+\beta
$$

SiLU：

$$
\mathrm{SiLU}(x)=x\,\sigma(x)=\frac{x}{1+e^{-x}}
$$

结构作用必须能解释到：卷积负责局部线性特征提取/下采样/通道映射；BN 改变训练期激活的尺度与偏移并维护推理期 running statistics；SiLU 提供平滑非线性。`bias=False` 与后接 BN 有关：BN 本身已有可学习偏移，训练图没有必要再保留卷积 bias。

部署时还应知道 Conv+BN 可以折叠。若卷积原 bias 为 0，则对输出 channel：

$$
W' = \frac{\gamma}{\sqrt{\sigma^2+\epsilon}}W,\qquad
b' = \beta-\frac{\gamma\mu}{\sqrt{\sigma^2+\epsilon}}
$$

因此“训练图有 BN、推理图没有 BN”不一定是结构错误；先检查是否已经完成等价融合。

### 7.2 C2f：分流、逐级变换、全部拼接

固定实现可压缩为：

```text
x
→ 1×1 Conv → [a, b]                 # channel chunk
                 │
                 └→ m1 → y1 → m2 → y2 → ... → yn

[a, b, y1, y2, ..., yn]
→ concat(channel)
→ 1×1 Conv
→ out
```

若隐藏通道为 `c`、内部 block 数为 `n`，第一次 `1×1 Conv` 输出 `2c`，最终 concat 是 `(2+n)c` 个 channel，再由 `cv2` 投影到目标输出通道。它的核心不是“堆 n 个 Bottleneck”，而是保留初始分支和每一级中间结果共同参与最终融合。

必须能区分 C2f 与普通串行堆叠：串行网络主要传递最后一级输出；C2f 显式保留多条短路径，改变特征复用和梯度传播结构。

### 7.3 C3k2：C2f 外壳 + 可替换的内部变换单元

YOLO11 固定实现中 `C3k2` 继承 `C2f`，因此外层仍是上一节的 split/chain/concat。差异集中在 `m`：

```text
C3k2
├─ outer topology: C2f
└─ each m[i]
   ├─ c3k=False → Bottleneck
   └─ c3k=True  → C3k(..., n=2)
```

而 `C3k` 本身继承 C3：两条支路，一条经过若干 Bottleneck，另一条较短，最后 concat 后投影。这里最重要的能力是**不能只凭 `C3k2` 这个类名推断内部计算**；必须继续看 `c3k`、`n`、shortcut、kernel、宽深度缩放和模型 YAML 的实参。

### 7.4 SPPF：连续 `5×5` max-pool 近似多尺度池化

固定实现的主路径是：

```text
x0 = Conv1x1(x)
x1 = MaxPool5x5(x0)
x2 = MaxPool5x5(x1)
x3 = MaxPool5x5(x2)
out = Conv1x1(concat[x0, x1, x2, x3])
```

stride=1、same padding 下，连续三个 `5×5` max-pool 的有效感受范围对应约 `5×5`、`9×9`、`13×13`，因此源码把它描述为与并行 `SPP(k=(5,9,13))` 等价的快速实现（Y019）。

必须能说明：SPPF 聚合的是**同一空间分辨率上的更大范围上下文**；它不增加输出空间分辨率，也不能恢复下采样前已经丢失的小目标细节。

### 7.5 Attention：先把 `H×W` 看成 token，再做 Q/K/V 交互

固定 YOLO11 Attention 输入为 `B×C×H×W`，令 `N=H×W`，用 `1×1 Conv` 生成 Q/K/V，再按多头 reshape。对单个 head，可用标准形式理解：

```math
A=softmax\left(\frac{Q^T K}{\sqrt{d_k}}\right),\qquad
Y=V A^T
```

其中 `A` 的空间交互尺寸是 `N×N`。固定实现还在 value 上增加一个 depthwise `3×3 Conv` 的 positional encoding，再经过 `1×1` projection（Y019）：

```math
Y'=Proj(Y+PE(V))
```

必须能从这里推出部署含义：当 `H,W` 较大时，attention matrix 的成本随 `N^2=(HW)^2` 增长；因此 YOLO11 把 C2PSA 放在深层低分辨率特征上，不应仅凭“attention 有全局关系”就把它无条件前移到 P2/P3。

### 7.6 PSABlock：Attention 残差 + FFN 残差

固定实现可以写成：

```math
x_1=x+Attention(x)
```

```math
x_2=x_1+FFN(x_1)
```

FFN 是 `1×1 Conv: C→2C` 后接 `1×1 Conv: 2C→C`，第二层关闭激活。这里应能解释“Attention 负责 token/空间位置之间的信息交互，FFN 负责每个位置上的通道变换”，而 residual 让原特征可直接通过。

### 7.7 C2PSA：只让部分通道进入 PSA

固定实现先把输入投影成两份隐藏特征：

```text
x → 1×1 Conv → split(a, b)
                    │
                    ├─ a ─────────────────────────┐
                    └─ b → PSABlock × n → b'     │
                                                 concat
                                                   ↓
                                               1×1 Conv
                                                   ↓
                                                  out
```

可写成：

```math
(a,b)=split(Conv_{1×1}(x)),\qquad
b'=PSABlocks(b)
```

```math
y=Conv_{1×1}(Concat(a,b'))
```

所以 C2PSA 不是“整张 feature map 全部做 attention”，而是 CSP 风格地保留一条 bypass，只在部分通道上承担 attention 成本。

### 7.8 DFL：先区分“分布表示/解码”与“DFL loss”

固定 YOLO11 锚点中 `reg_max=16`；YOLO26 固定实现则需要单独看其 Detect 输出和训练实现，不能把 YOLO11 的 DFL 结论直接迁移过去。

对一个边界距离 `y`，离散 bin 为 `0,...,K-1`。模型输出 logits `z_i`，softmax 得到：

$$
p_i=\frac{e^{z_i}}{\sum_{j=0}^{K-1}e^{z_j}}
$$

推理时用期望得到连续距离：

$$
\hat y=\sum_{i=0}^{K-1} i\,p_i
$$

训练时目标 `y` 落在相邻两个 bin `l=floor(y)` 与 `r=l+1` 之间，线性权重为：

$$
w_l=r-y,\qquad w_r=y-l
$$

DFL loss 可理解为对两个邻近分类目标做加权交叉熵：

$$
L_{DFL}=w_l\,CE(z,l)+w_r\,CE(z,r)
$$

这里必须区分两件事：**DFL 表示/积分是推理 decode 机制；DFL loss 是训练监督机制。** 两者相关，但不是同一个算子。

### 7.9 最低自检

至少能够不看资料回答：

1. Conv 为什么通常 `bias=False` 再接 BN？Conv+BN 如何 fuse？
2. C2f 与普通串行 Bottleneck 堆叠的 tensor 路径有什么不同？
3. C3k2 中什么时候实际使用 C3k，什么时候使用 Bottleneck？
4. SPPF 连续三个 `5×5` pooling 为什么可以得到约 `5/9/13` 的有效范围？
5. Attention 为什么对 `H×W` 很敏感？为什么通常放在深层？
6. PSABlock 中 Attention、FFN、residual 各自负责什么？
7. C2PSA 为什么只让部分 channel 进入 PSA？
8. DFL 为什么能从离散 bins 得到连续距离；它与 DFL loss 分别发生在推理和训练的哪一段？
9. 修改其中任一模块后，参数量、FLOPs、feature-map shape、感受范围、梯度路径和目标 runtime 算子支持会分别怎么变化？

如果只能说“C2PSA 是注意力模块”“SPPF 扩大感受野”“DFL 提高定位精度”，还没有达到本页定义的掌握线。
