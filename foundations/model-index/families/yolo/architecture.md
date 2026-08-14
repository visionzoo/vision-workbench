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
