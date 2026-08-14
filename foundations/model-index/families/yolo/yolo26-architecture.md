---
status: working
type: model-index
rigor: standard
provenance: official-documentation-report-fixed-ultralytics-source-and-local-source-execution
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-08-14
updated: 2026-08-14
---

# YOLO26 architecture and modification map

本页服务三个目标：能够不看源码复述 YOLO26 检测模型的数据流；能够从一次结构修改追到训练、推理与导出接口；能够用机制回答面试追问。它不是模型宣传摘要，也不把尚未执行的修改写成经验。

## 1. 版本、对象与证据边界

本页只把 Ultralytics `8.4.2` 的提交 `486342c195c28c739a033f599bbbb720d749f3d0` 作为源码 Oracle（Y023），主要对象是默认闭集检测配置 `yolo26.yaml`。分析中的层号、参数含义和执行路径都绑定该提交；在线文档、后续 release、YOLOE-26、pose、segment、OBB、P2 与 P6 配置不能自动套用。

当前证据来自第一方文档、技术报告、固定源码阅读，以及一次 640×640 CPU 合成输入的 shape 与 eval 输出检查；该执行输出尚未形成持久化证据，且未运行 backward、fuse、export 或结构改造，因此保持 `working / partial / owner_review: pending`。下文“源码事实”表示固定 revision 中可定位的行为，不表示本人已经复现实验结果。

## 2. 一句话结构

```text
image
→ stride-2 Conv + C3k2 backbone
→ SPPF(shortcut) + C2PSA
→ top-down / bottom-up PAN-style fusion
→ P3/8, P4/16, P5/32
→ two decoupled Detect branches during training
   ├─ one-to-many: trains shared features and an auxiliary head
   └─ one-to-one: trains the inference head from detached features
→ direct l/t/r/b distance decode
→ sigmoid class scores
→ top-k selection without IoU-based NMS
```

YOLO26 的关键差异不只是“去掉 NMS”。默认配置同时选择 `end2end: true` 和 `reg_max: 1`：训练时建立 two-head supervision，推理时只消费 one-to-one head；回归头每个位置只输出四个距离，不再输出 YOLO11 默认的 4×16 个 DFL logits（Y023）。

## 3. 先读懂 YAML 如何变成网络

每一行配置遵循：

```text
[from, repeats, module, args]
```

- `from=-1` 表示上一层；列表表示取多个已保存输出；
- `repeats>1` 会先乘 depth scale 并至少保留一次；对 repeat module，缩放后的次数传入模块内部；
- 输出通道先受 width scale 和 `max_channels` 限制，再对齐到 8 的倍数；
- `Detect` 的 `reg_max`、`end2end` 和输入通道由 `parse_model()` 从顶层配置追加，不只来自该行 `[nc]`；
- `C3k2` 在 m/l/x scale 会被 parser 强制切到 `c3k=True`，所以同一个 YAML 的 n/s 与 m/l/x 不能只理解为等比例增宽加深。

默认 compound scales 为：

| Scale | depth | width | max channels | 结构解释边界 |
|---|---:|---:|---:|---|
| n | 0.50 | 0.25 | 1024 | 本页逐层 shape 锚点 |
| s | 0.50 | 0.50 | 1024 | repeats 与 n 相同，通道更宽 |
| m | 0.50 | 1.00 | 512 | parser 会改变 C3k2 内部选择 |
| l | 1.00 | 1.00 | 512 | repeats 增加，且使用 m/l/x 的 C3k2 路径 |
| x | 1.00 | 1.50 | 512 | 宽度继续增加但受 max channels 限制 |

因此比较 scale 时要同时比较有效 repeats、有效通道和 block 类型，不能只比较参数量。

## 4. YOLO26n 默认检测拓扑与 shape ledger

以下 shape 假设输入为 `B×3×640×640`，只记录模块输出。通道是 scale=n 经 parser 缩放后的有效值；空间尺寸要求输入与连接关系兼容，不代表任意奇数输入都能无条件 concat。

| Layer | From | Module | Output shape | Stride | 作用 |
|---:|---:|---|---|---:|---|
| 0 | -1 | Conv 3×3/s2 | `B×16×320×320` | 2 | stem 下采样 |
| 1 | -1 | Conv 3×3/s2 | `B×32×160×160` | 4 | 形成 P2 尺度 |
| 2 | -1 | C3k2 | `B×64×160×160` | 4 | 浅层局部特征 |
| 3 | -1 | Conv 3×3/s2 | `B×64×80×80` | 8 | 进入 P3 |
| 4 | -1 | C3k2 | `B×128×80×80` | 8 | P3 backbone feature |
| 5 | -1 | Conv 3×3/s2 | `B×128×40×40` | 16 | 进入 P4 |
| 6 | -1 | C3k2(c3k) | `B×128×40×40` | 16 | P4 backbone feature |
| 7 | -1 | Conv 3×3/s2 | `B×256×20×20` | 32 | 进入 P5 |
| 8 | -1 | C3k2(c3k) | `B×256×20×20` | 32 | 深层局部/语义特征 |
| 9 | -1 | SPPF(k=5,n=3,shortcut) | `B×256×20×20` | 32 | 多范围 pooling，上接残差 |
| 10 | -1 | C2PSA | `B×256×20×20` | 32 | 部分通道 attention |
| 11 | -1 | nearest upsample ×2 | `B×256×40×40` | 16 | top-down |
| 12 | 11,6 | Concat | `B×384×40×40` | 16 | 融合 P5 与 P4 |
| 13 | -1 | C3k2(c3k) | `B×128×40×40` | 16 | neck P4 |
| 14 | -1 | nearest upsample ×2 | `B×128×80×80` | 8 | top-down |
| 15 | 14,4 | Concat | `B×256×80×80` | 8 | 融合 neck P4 与 backbone P3 |
| 16 | -1 | C3k2(c3k) | `B×64×80×80` | 8 | Detect P3 input |
| 17 | -1 | Conv 3×3/s2 | `B×64×40×40` | 16 | bottom-up |
| 18 | 17,13 | Concat | `B×192×40×40` | 16 | 回融 top-down P4 |
| 19 | -1 | C3k2(c3k) | `B×128×40×40` | 16 | Detect P4 input |
| 20 | -1 | Conv 3×3/s2 | `B×128×20×20` | 32 | bottom-up |
| 21 | 20,10 | Concat | `B×384×20×20` | 32 | 回融 backbone deep feature |
| 22 | -1 | C3k2(c3k+attention) | `B×256×20×20` | 32 | Detect P5 input |
| 23 | 16,19,22 | Detect | 见下一节 | 8/16/32 | 双分支检测头 |

640 输入共有 `80² + 40² + 20² = 8400` 个候选位置。这个数字只表示候选密度；一个目标是否成为正样本仍由中心约束、task-aligned metric 和冲突处理决定。

## 5. Backbone 与 neck 模块不能只背名字

### Conv

默认 `Conv` 是 convolution、BatchNorm 和激活的组合。stride-2 Conv 同时改变空间尺寸、有效感受野和后续候选密度。替换 stem 或下采样层时，首先核对 padding、输出奇偶尺寸、通道和目标后端算子，而不是只比较 FLOPs。

### C3k2

`C3k2` 继承 C2f 的 split—transform—concat 路径。固定 revision 中，它的内部单元由 `c3k` 与 `attn` 控制：普通 Bottleneck、两层 C3k，或 Bottleneck 后接 PSABlock。最后一个 P5 neck block 的 YAML 显式传入 `attn=True`；m/l/x 还会被 parser 改写 `c3k`。因此“把 C3k2 换成某 block”至少改变隐藏通道、分支数、残差条件、attention 和权重键。

### SPPF with shortcut

YOLO26 默认 SPPF 先用 1×1 Conv 降通道，连续三次执行同一个 5×5/s1 max pool，把原特征及三次 pooling 结果 concat 后投影；配置的第四个参数使输入输出通道相同时再加原输入。它扩展深层上下文，不恢复 P3 之前已经丢失的细节。

### C2PSA

`C2PSA` 把通道分成两部分，只让其中一部分经过若干 PSABlock，再 concat 投影。PSABlock 内有 attention、FFN 与残差。它的主要修改风险是 head 数与通道整除、reshape/transpose、显存和部署算子支持，不能从模块名称直接推断板端收益。

### Bidirectional fusion

top-down 路径把深层语义送到 P4/P3，bottom-up 路径再把定位细节聚合回 P4/P5。每次 concat 都形成接口契约：来源层、空间大小、通道顺序和消费者必须一起检查。修改 backbone 输出层而不修改这些契约，通常会在建图或权重加载阶段失败；通过建图也不证明语义对齐。

## 6. Detect head：两套参数，不是一个输出做两次匹配

对每个 P3/P4/P5 输入，`Detect` 建立解耦的 box head `cv2` 和 classification head `cv3`。非 legacy 分类头使用两组 depthwise 3×3 + pointwise 1×1，再用 1×1 Conv 输出 `nc` 类 logits。box head 使用两组普通 3×3 Conv，再输出 `4 × reg_max` 个通道。

当 `end2end=True` 时，构造函数深拷贝 `cv2/cv3`，得到独立的 `one2one_cv2/one2one_cv3`。因此：

```text
shared P3/P4/P5
├─ one-to-many cv2/cv3 → auxiliary training predictions
└─ detach(P3/P4/P5) → one-to-one cv2/cv3 → inference-head training predictions
```

这里的 `detach` 很关键：one-to-one loss 更新 one-to-one head 参数，但不通过该分支把梯度传回 backbone/neck；shared features 主要由 one-to-many 路径提供梯度。它解释了为什么删除辅助头不只是减少参数，也会改变训练 shared features 的监督。

### 训练期 tensor 合同

默认 `nc=80`、`reg_max=1`、640 输入时，每个分支返回：

```text
boxes:  B × 4  × 8400
scores: B × 80 × 8400
feats:  [P3, P4, P5]
```

整个 Detect 训练输出是：

```text
{
  "one2many": {boxes, scores, feats},
  "one2one":  {boxes, scores, feats}
}
```

### 为什么默认没有 DFL 分布积分

`reg_max=1` 使 box head 每个候选只产生 `l,t,r,b` 四个值，`DFL` 模块退化为 `Identity`。loss 中 `use_dfl=False`，回归辅助项改为对按图像大小归一化后的四边距离做加权 L1；CIoU box loss 仍然存在。代码沿用 `loss[2]` 和超参数名 `dfl`，但此时该槽位的计算语义不是 distribution focal loss。面试或修改时应区分“变量仍叫 dfl”和“实际执行 DFL 分类分布”。

## 7. 标签分配与 Progressive Loss

固定 revision 的检测 criterion 为 `E2ELoss`：

- one-to-many 使用 TaskAlignedAssigner `topk=10`；
- one-to-one 先以 `topk=7` 选候选，冲突处理后再以 `topk2=1` 收缩到每个 GT 的单候选；
- task-aligned metric 为分类分数与定位重叠的联合函数，固定参数为 `alpha=0.5`、`beta=6.0`；
- 两个分支各自计算 classification、CIoU box 和回归辅助项。

Progressive Loss 在该实现中表现为两分支总 loss 权重随 epoch 更新：one-to-many 从 0.8 线性衰减到 0.1，one-to-one 从 0.2 增长到 0.9；trainer 每个 epoch 后调用一次 criterion `update()`。这不是学习率调度，也不是逐层冻结。恢复训练、改变 epoch 数或自定义 trainer 时，都要确认该状态和更新时机。

STAL 的名字不能替代源码检查。这里能直接确认的是：one-to-one assigner 使用两阶段 `topk=7 → topk2=1`，且候选中心约束会把小于最小 stride 的 GT 宽高临时扩展到下一 stride 的大小后再判断中心是否落入框内。其跨数据收益仍需实验，不能从实现存在直接推出。

## 8. 推理为什么 NMS-free

eval 模式只把 one-to-one prediction 送入 `_inference()`：

1. 以 P3/P4/P5 网格中心生成 anchor points；
2. 把四边距离解码成 `xyxy`，再乘对应 stride；
3. 对 class logits 做 sigmoid；
4. 先按每个候选的最大类分数取最多 `max_det` 个候选，再在候选×类别上取全局 top-k；
5. 返回 `B × K × 6`，字段为 `x1,y1,x2,y2,score,class_id`。

这里没有基于 IoU 的 suppression。NMS-free 的成立依赖 one-to-one 训练让高分重复预测受到约束，最终代码只是 top-k 选择；它不意味着结果完全没有后处理，也不保证任意自定义训练或移植 head 都不会产生重复框。

默认 `max_det=300`。输入很小时，Python 推理会把 k 限制到候选数；export 路径为了 TensorRT 常量 k 使用 exporter 预先约束后的 `max_det`。因此输出 shape、top-k 支持和动态输入能力都属于导出合同。

## 9. train、eval、fuse 与 export 是四张不同的语义图

| 状态 | 使用的 head | 返回内容 | 修改时的主要风险 |
|---|---|---|---|
| train | one-to-many + one-to-one | 两套 raw dict | detach、assigner、loss 权重和梯度路径 |
| eval, unfused | one-to-one 推理；同时保留 raw dict 供 Python 返回 | decoded top-k + raw predictions | 误把 raw 与最终结果混为同一输出 |
| fuse | 删除 one-to-many `cv2/cv3`，并做常规 Conv/BN 等融合 | 只保留推理所需参数 | 融合后不能继续原训练合同 |
| export | 先 deepcopy、eval、fuse，再设置 export/format | 通常为固定 top-k tensor | backend 能否表达 top-k、动态 shape 与 metadata |

固定 exporter 对后端有显式例外：例如 NCNN 会禁用 end-to-end branch，benchmark 代码也对 RKNN、Paddle、ExecuTorch 等组合设置限制（Y023）。所以“YOLO26 默认 NMS-free”不能直接改写成“所有导出格式都保持相同图”。实际部署判断仍进入 [Deployment](deployment.md)。

## 10. P2、默认与 P6 不是只差一个输出层

| 配置 | Detect inputs | 640 时位置数 | 结构变化 | 先验证什么 |
|---|---|---:|---|---|
| `yolo26-p2.yaml` | P2/P3/P4/P5 | 34,000 | top-down 多到 P2，并增加对应 bottom-up 回路 | 小目标召回、显存、延迟、正样本与误检 |
| `yolo26.yaml` | P3/P4/P5 | 8,400 | 默认三尺度 | 通用基线与目标尺寸分层 |
| `yolo26-p6.yaml` | P3/P4/P5/P6 | 8,500 | backbone 增加 P6，neck 改成四尺度 | 大目标、输入尺寸、深层算力与部署支持 |

候选位置数按方形 640 输入计算。P2 增加高分辨率候选不保证小目标改善；P6 增加深层尺度也不保证大目标收益。官方是否提供对应预训练权重、训练配方和目标硬件结果应另行确认。

## 11. 结构修改影响图

| 想改什么 | 必须同步检查 | 最小结构 Oracle | 任务/工程 Oracle |
|---|---|---|---|
| 增删 P2/P6 输出 | backbone save list、neck concat、Detect 输入数、stride、assigner、位置数 | 三/四尺度 shape 与 forward/backward | 尺寸分层 AP/recall、显存、延迟 |
| 替换 C3k2 | hidden channel、shortcut、parser 参数、state_dict key、export op | shape、参数加载报告、梯度非零 | 同预算消融与目标后端支持 |
| 修改通道或 scale | width/max_channels、concat 求和、attention head 数、Detect c2/c3 | 每层 channel ledger | 参数/FLOPs、显存、延迟、精度 |
| 删除 C2PSA/末端 attention | 残差与模块边界、权重兼容、部署图 | 替换前后目标节点 shape | 精度、延迟和首个数值分歧 |
| 改 `reg_max` | box 输出通道、DFL module、bbox loss、checkpoint、decode | raw box shape 与 decode 单测 | 定位误差、量化与导出一致性 |
| 改 one-to-one head | deep copy、detach、assigner、postprocess、fuse | train/eval 返回合同 | 重复框、召回、top-k 稳定性 |
| 删除 one-to-many head | shared feature 梯度、Progressive Loss、checkpoint、fuse | backbone 梯度和 loss 项 | 从头训练收敛与最终任务指标 |
| 修改分类头 | depthwise op、类别数、bias init、score 解释 | 每尺度 logits shape | 校准、长尾类别与后端算子 |
| 改 top-k/max_det | postprocess、export 常量、backend、输出 shape | K 边界与字段顺序 | crowded scene recall 与端到端延迟 |

结构能运行只是第一道门。接受修改至少需要独立任务指标；涉及导出或板端时，还要比较 source float、export float 与目标 runtime 的对应语义阶段。

## 12. 建议的源码阅读顺序

```text
cfg/models/26/yolo26.yaml
→ nn/tasks.py::parse_model
→ nn/modules/conv.py::Conv / DWConv
→ nn/modules/block.py::C3k2 / SPPF / C2PSA / PSABlock
→ nn/modules/head.py::Detect
→ utils/tal.py::TaskAlignedAssigner
→ utils/loss.py::v8DetectionLoss / E2ELoss
→ nn/tasks.py::DetectionModel.init_criterion / BaseModel.fuse
→ engine/trainer.py::criterion.update
→ engine/exporter.py
→ models/yolo/detect/predict.py
```

阅读每个函数时记录四件事：输入输出 shape、训练/推理分支、梯度是否截断、导出或融合是否改写模块。只读类定义而不追调用者，容易把可选路径误当默认路径。

## 13. 学习与修改的最小验证阶梯

1. **纸面重建**：不看 YAML 画出 P3/P4/P5 来源、两次 top-down 和两次 bottom-up；再与固定配置逐层比对。
2. **shape hook**：已用 640 方形合成输入核对 layer 0–22、stride、eval 与 raw branch shape；下一步补一个非方形合法输入并保存可寻址输出。
3. **输出合同**：分别在 train、eval、fuse、export 状态记录类型、shape、字段和 head 是否存在。
4. **梯度 Oracle**：对一个合成 batch 反向传播，确认 one-to-one 输入 detach 后 shared feature 梯度来源符合预期。
5. **最小改造**：一次只改变一个接口，例如添加 P2 或改变 `reg_max`；先跑 forward/backward 和权重加载报告。
6. **导出对齐**：固定输入，比较 decoded box、score 和 class，不用最终 AP 掩盖接口错误。
7. **任务验收**：用固定数据、阈值规则和目标尺寸切片比较修改前后；真实性能结果写入 `engineering/cases/`，本页只回写可复用结论。

## 14. 面试问题应从机制推导

### YOLO26 相对传统 NMS-based YOLO 的核心改变是什么？

不是简单删除一个函数。它训练独立 one-to-one inference head，并用稀疏匹配约束重复预测；推理时解码该分支后执行 score top-k，而不做 IoU suppression。辅助 one-to-many head 仍在训练 shared representation，融合时才被删除。

### one-to-one 分支为什么对输入 feature 做 detach？

固定实现让 one-to-one head 学习自己的参数，但不让它的稀疏监督直接改写 shared backbone/neck；shared feature 的主要训练信号来自 one-to-many 分支。代价是辅助头和 Progressive Loss 成为训练合同的一部分。

### `reg_max=1` 是否表示 DFL 只有一个 bin？

在接口上 `reg_max` 为 1，但代码不会执行单 bin DFL：DFL module 是 Identity，`BboxLoss` 进入无 DFL 分支，对归一化四边距离计算 L1。回答时应以控制流为准，而不是变量名。

### P2 为什么可能改善小目标，也可能变差？

P2 提供更密集、高分辨率候选，但同时增加计算、正负候选、显存和背景混淆。若输入中目标已经没有可分信息、标签不完整或 assigner 没给出有效正样本，增加 P2 不会自动修复问题。

### 为什么 NMS-free 不等于零后处理？

YOLO26 仍需 anchor-point decode、stride 还原、sigmoid、两级 top-k 和字段组装；只是没有 IoU-based NMS。不同 backend 对 top-k 的支持还可能改变导出路线。

### 修改一个 backbone block 后为什么不能只看模型能否 forward？

forward 只证明当前 shape 可连接。还需检查 state_dict、梯度路径、训练/推理双头、融合、导出算子、数值对齐和任务指标；任何一项都可能成为真正失效边界。

## 15. 当前未知项与降级条件

- 已独立运行 640 合成输入的 shape 与 eval 输出检查，但输出未持久化；梯度、fuse 和 export Oracle 尚未执行；
- 技术报告中的命名与收益声明尚未逐项映射到固定源码和可复现实验；
- 在线文档可能在不改变 URL 的情况下更新；固定 commit 才是实现事实锚点；
- P2/P6、其他任务 head、后续 release 和第三方移植必须建立自己的输出合同；
- 若固定链接、源码行为或独立运行结果与本文不符，应立即修正文档并降低相应结论的 evidence/confidence，不保留“只升不降”的叙事。

下一道晋级门：本人审查逐层图；运行至少一次 shape、train/eval、backward、fuse 和 ONNX 输出合同检查；把结果链接为独立证据后再考虑 `validated`。
