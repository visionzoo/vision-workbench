---
status: working
type: mechanism
rigor: standard
provenance: primary-papers-and-owner-directed-research
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-07-30
updated: 2026-07-30
---

# 目标检测架构演变：从候选框流水线到可提示集合预测

本页不维护“模型发布时间排行榜”，也不把目标检测写成 `R-CNN → YOLO → DETR` 的单线替代史。架构演变真正改变的是检测系统内部的职责边界、候选表示、训练匹配和语义接口；不同路线长期并存，并会重新组合。

触发本轮调研的微信公众号文章只作为问题线索，不作为事实来源：当前无法稳定提取其全文和图示。下述判断全部回到论文或第一方仓库；文章中的具体表述若需逐句核查，仍需另行保存可寻址正文。

## 1. 用六个轴描述检测器

一个检测架构至少同时回答六个问题：

| 轴 | 核心问题 | 常见形态 |
|---|---|---|
| 候选空间 | 模型在哪里寻找目标？ | 外部 region proposal、RPN proposal、dense anchor、point、object query、text/visual prompt |
| 特征组织 | 不同位置和尺度如何共享视觉计算？ | 每候选独立 CNN、共享 feature map、FPN/PAN、multi-scale attention、vision-language fusion |
| 监督分配 | 哪个预测负责哪个标注？ | 固定 IoU 阈值、中心区域、动态匹配、task-aligned、Hungarian one-to-one、one-to-many + one-to-one |
| 输出表示 | 类别和框以什么形式产生？ | anchor offset、中心点与尺寸、四边距离、离散分布、迭代 query refinement、token sequence |
| 结果选择 | 重复候选如何变成最终集合？ | score threshold、NMS/Soft-NMS、级联筛选、learned one-to-one set prediction |
| 语义接口 | 类别集合何时确定？ | 固定 closed set、运行时文本词表、referring expression、视觉提示、prompt-free large vocabulary |

因此，`two-stage / one-stage`、`anchor-based / anchor-free`、`CNN / Transformer`、`closed-set / open-vocabulary` 是不同分析轴，不能混成一条等级链。

## 2. 主干演变不是单线替代

| 阶段 | 代表工作 | 关键重构 | 仍然保留的约束 |
|---|---|---|---|
| 候选区域 + 分类器 | R-CNN | 用 CNN 表征外部 region proposals，把检测建立在强分类特征上 | 候选生成在网络外；每个候选重复计算；训练链路分裂 |
| 共享特征的区域检测 | Fast R-CNN、Faster R-CNN | 整图只计算一次特征；RoI 汇聚复用特征；RPN 把 proposal 学习并入网络 | 仍是“先产生稀疏候选，再逐候选分类/回归”的两阶段职责 |
| 稠密单阶段预测 | YOLOv1、SSD | 直接在整图特征上预测大量位置，不再显式执行 proposal + RoI 分类 | 候选定义、正负样本和重复结果处理仍依赖人工设计 |
| 多尺度与类别不平衡重构 | FPN、RetinaNet | 让不同分辨率都具有强语义；Focal Loss 使稠密检测不被易负样本淹没 | 仍通常依赖 dense anchors 与 NMS；FPN 是通用组件，不等于某一种 detector |
| Anchor-free 稠密预测 | FCOS、CenterNet | 用像素点、中心点或边界距离替代预设框，减少 anchor 形状超参数 | 仍需定义正样本区域、尺度归属、回归形式和 NMS；“无框锚”不等于“无先验” |
| 学习式分配与质量对齐 | ATSS、GFL、OTA、TOOD | 把性能瓶颈从 anchor 形状转向正样本选择、分类—定位质量一致性和分布式回归 | 大多仍是稠密 one-to-many 监督和后处理选择 |
| 集合预测 | DETR | 用固定 object queries、全局集合损失和 Hungarian matching 直接预测唯一结果集合 | 原始 DETR 收敛慢、对小目标和多尺度不友好，且计算并不天然适合实时部署 |
| 可训练的高效查询 | Deformable DETR、DINO | 稀疏多尺度采样、query 初始化、去噪训练和迭代 refinement 改善收敛与定位 | query、reference point、采样算子和 decoder 仍形成新的结构先验与部署约束 |
| 实时端到端收敛 | RT-DETR、RT-DETRv2、D-FINE、YOLOv10 | DETR 路线压缩 encoder/decoder；YOLO 路线引入 one-to-one 分支，使实时检测与 NMS-free 开始汇合 | “端到端”必须核对实际导出图、算子和结果选择，不能由模型名称推断 |
| 开放词汇与可提示检测 | Grounding DINO、YOLO-World、YOLOE | 类别从训练时固定 logits 变为运行时文本、视觉提示或大词表对齐 | prompt、词表、文本编码器、校准和训练语料成为新的系统状态 |
| 统一生成式视觉接口 | Florence-2 等 | 检测、grounding、caption、segmentation 可共享 prompt-to-sequence 接口 | 它改变的是任务接口与统一建模目标，不代表已取代低延迟专用 detector |

这张表描述“什么职责被重构”，不做跨论文性能排名。不同论文的数据、backbone、训练预算、输入尺寸、硬件和延迟口径不同，不能把作者报告的数字直接串成连续进步曲线。

## 3. 候选空间：从枚举窗口到对象查询

### 3.1 Region proposal

R-CNN 把外部算法生成的区域当作候选对象；Fast R-CNN 解决候选间重复卷积，Faster R-CNN 再用共享特征上的 RPN 学习候选。关键变化不是“CNN 更深”，而是候选生成从系统外部进入可训练图，并与检测共享特征。

### 3.2 Dense anchor 与 dense point

YOLO、SSD、RetinaNet 在规则网格和多尺度特征上稠密地产生候选。Anchor-free 方法通常把候选单元从预设矩形改成点，但仍然枚举大量空间位置。ATSS 的分析进一步说明：anchor-based 与 center-based anchor-free 的重要差异经常来自正负样本定义，而不只是候选几何形状。

因此：

```text
anchor-free ≠ candidate-free
anchor-free ≠ assignment-free
anchor-free ≠ NMS-free
```

### 3.3 Object query

DETR 把候选从图像网格上的局部模板改成固定数量的预测槽位。每个 query 通过 decoder 与图像特征交互，并由全局一对一匹配约束为唯一结果。Query 不是天然可解释的“对象类别原型”；它首先是集合预测中的槽位与检索状态。

Deformable DETR、DINO 和 RT-DETR 又把 reference points、query selection、denoising 和稀疏采样加入查询过程。这说明演变并非不断删除先验，而是把固定 anchor 先验替换成可学习、可优化但仍需明确的查询先验。

### 3.4 Prompt-conditioned candidate

Grounding DINO 将文本参与 feature enhancement、query selection 和 cross-modal decoding；YOLO-World 在实时稠密检测器中引入 region-text 对齐；YOLOE 进一步统一文本、视觉和 prompt-free 机制。此时空间候选和语义候选开始耦合：模型不只问“哪里像目标”，还问“哪里与当前提示匹配”。

## 4. 特征组织：从重复计算到多尺度交互

演变的第一条效率主线是减少重复视觉计算：

```text
每个 proposal 独立卷积
→ 全图共享 feature map + RoI
→ 多尺度共享 feature pyramid
→ 全局/稀疏 multi-scale attention
→ 视觉与语言特征联合交互
```

FPN 的价值不只是增加一个 neck，而是用 top-down 与 lateral connections 让高分辨率层获得更强语义。它随后被 two-stage、dense one-stage 和 DETR 变体共同采用，说明“特征金字塔”与“检测范式”是正交关系。

Transformer 也没有自动消除多尺度问题。原始 DETR 使用单尺度高层特征时，小目标和收敛受限；Deformable DETR 通过围绕 reference point 的稀疏多尺度采样修复这一缺口。RT-DETR 的 hybrid encoder 则继续拆分 intra-scale interaction 与 cross-scale fusion，以控制实时计算。

## 5. 监督分配：架构演变中最容易被忽略的主线

### 5.1 固定规则

早期 anchor detector 通常以 IoU 阈值、最佳 anchor 或中心约束指定正负样本。它们同时决定正样本数量、尺度归属和回归起点，因此是训练架构的一部分，而不是无关的实现细节。

### 5.2 动态与质量对齐

- ATSS 根据候选与标注的统计关系自适应确定正样本；
- OTA 把全局分配表述为 optimal transport；
- TOOD 用 task-aligned assignment 缓解分类和定位最优位置不一致；
- GFL 将定位质量并入分类表示，并把框位置建模为分布。

这些工作说明：从 anchor-based 迁移到 anchor-free 后，主要矛盾并不会消失，而会转移到“谁负责该目标”和“分类分数是否反映定位质量”。

### 5.3 One-to-one 与混合监督

DETR 的 Hungarian matching 强制一个标注只匹配一个最终预测，从训练目标上抑制重复结果。DINO 用 denoising 和更好的 query 初始化改善这一训练。实时路线又常引入混合监督：训练时保留 one-to-many 提供更密集梯度，同时让 one-to-one 分支承担最终无 NMS 输出；YOLOv10 的 consistent dual assignments 是这一汇合方向的代表。

因此，`NMS-free` 的根因不是简单删除 NMS 算子，而是训练匹配、head 分支和推理输出共同保证结果唯一性。

## 6. 框表示：从确定坐标到分布与迭代 refinement

常见框表示包括：

```text
anchor offset
→ center + width/height
→ point-to-boundary distances
→ discrete probability distribution over distances
→ query-conditioned iterative box refinement
→ sequence tokens
```

GFL/DFL 类分布式回归不是“换一个 loss 名称”，而是把单一坐标目标改成离散概率分布，再通过积分或期望恢复距离。D-FINE 将类似的细粒度分布 refinement 引入实时 DETR，并通过 decoder 层逐步细化定位。

比较两个模型时必须区分：训练表示、raw tensor、decode 后坐标和最终结果。仅比较最终框可能掩盖中间语义差异；仅比较 raw tensor 又可能比较了本来就不等价的表示。

## 7. 结果选择：NMS 与集合预测的系统边界

传统 dense detector 通常输出远多于真实目标的候选，再由阈值和 NMS 选择结果。NMS 简单、成熟且容易替换，但它把最终行为分散到模型外部：类别处理、IoU 阈值、class-aware/class-agnostic 策略、top-k 和 runtime 实现都会改变结果。

集合预测把唯一性更多写入训练目标和模型输出，但不自动保证所有部署链路都真正无后处理。至少要核对：

1. 推理走 one-to-one 还是 one-to-many 分支；
2. 导出图是否包含 decode、top-k 或其他选择；
3. runtime 输出是否仍需要阈值、排序和坐标还原；
4. 文档中的 NMS-free 指模型算法、官方实现，还是当前实际 artifact。

## 8. “端到端”至少有四种含义

| 层级 | 含义 | 代表变化 |
|---|---|---|
| E1 | 单个神经网络从图像产生 raw detection predictions | YOLOv1 相对分类器流水线的统一 |
| E2 | proposal、特征、分类和回归可联合训练 | Faster R-CNN 将 RPN 并入共享网络 |
| E3 | 最终结果集合不依赖 NMS | DETR、RT-DETR、YOLOv10 的 one-to-one 路线 |
| E4 | 任务和类别也由 prompt 统一指定 | Grounding DINO、YOLOE、Florence-2 类接口 |

讨论“端到端检测”时必须先声明层级。One-stage 可能仍依赖 NMS；two-stage 也可以联合训练；Transformer detector 也可能在具体实现中附加后处理。

## 9. 语义接口：从固定类别到开放提示

Closed-set detector 把类别数和分类权重冻结在训练产物中。开放词汇检测将区域特征与文本特征对齐，使类别集合可以在运行时变化；grounding 还允许属性或关系表达，而不只类别名。

这带来新的系统状态：

- prompt 模板、同义词、负词表和类别冲突；
- 文本编码器版本与 embedding cache；
- region-text score 的校准和阈值；
- 预训练 grounding 数据的覆盖与偏差；
- prompt-free 大词表是否真的覆盖目标域；
- 文本/视觉 prompt 是否保留在部署图中。

开放词汇不是“无需数据即可识别一切”。它把闭集标签成本部分转移为预训练语料覆盖、提示设计、校准和目标域验证成本。

## 10. 三条仍然并行的工程路线

### 10.1 规则算子友好的 dense CNN detector

适合固定类别、低延迟、边缘 NPU 和成熟部署工具链。默认优势来自规则卷积、明确多尺度输出和大量工程实现；风险集中在输入尺度、标签分配、decode/NMS、量化和算子融合。

### 10.2 Query-based end-to-end detector

适合希望统一结果选择、减少 NMS 依赖，或需要更强全局关系建模的场景。是否适合目标设备取决于 attention、sampling、decoder、top-k 和动态 shape 的真实支持，不能只看 FLOPs。

### 10.3 Open-vocabulary / promptable detector

适合类别经常变化、长尾发现、自动标注和人机交互。固定类别高可靠实时任务仍需比较专用 closed-set 模型；开放词汇模型可以作为离线教师、候选发现器或异常上送模型，而非默认替代板端 detector。

这些是选型起点，不是结论。最终选择必须回到目标数据、错误成本、硬件、运行时和评测 Oracle。

## 11. 从架构迁移进入工程核查

两个 detector 或两个版本之间，先按语义阶段对齐，不按层名硬匹配：

| 检查项 | 需要冻结的事实 |
|---|---|
| 输入 | resize/crop/letterbox、颜色、range、normalization、layout |
| 特征 | 实际输出尺度、stride、节点来源、融合方式 |
| 候选 | anchor/point/query/prompt 的数量、坐标和尺度语义 |
| 分配 | one-to-many/one-to-one、正样本规则、质量目标 |
| Head | 分类、objectness、quality、box representation 的真实张量 |
| Decode | DFL/offset/reference point、stride、坐标格式 |
| 选择 | NMS、top-k、one-to-one branch、class-aware 规则 |
| 语义 | 固定类别、文本词表、prompt、embedding 版本 |
| Runtime | 导出图、融合、插件算子、量化、动态 shape、后处理位置 |

架构发生变化时，“同名输出”不保证同义，“不同 tensor”也不一定不可比。应先定义任务级等价点，再寻找首个显著分歧边界。

## 12. 应拒绝的简化叙事

| 简化说法 | 问题 |
|---|---|
| two-stage 已被 one-stage 淘汰 | 两者优化目标、候选稀疏度、实例特征和部署条件不同，仍长期并存 |
| anchor-free 没有人工先验 | 候选点、中心区域、尺度范围、分配和回归形式仍是先验 |
| DETR 就是把 backbone 换成 Transformer | DETR 的关键是 set prediction、object queries 和 bipartite matching；backbone 可以仍是 CNN |
| NMS-free 只需删除 NMS | 唯一性必须由训练匹配、head 与推理分支共同支持 |
| one-stage 就是端到端 | 它可能仍依赖手工 assignment、decode 和 NMS |
| 开放词汇能识别任意目标 | 能力受预训练覆盖、prompt、校准、域偏移和阈值影响 |
| 新架构一定更适合边缘部署 | 算子、内存访问、量化与 runtime 支持可能比参数量更决定延迟 |

## 13. 当前结论与证据边界

### 当前结论

1. 目标检测架构的长期方向是把候选生成、监督分配、结果选择和类别接口逐步纳入可学习系统，但每次“减少手工组件”都会引入新的可学习状态和部署契约。
2. 现代检测器正出现两种汇合：dense YOLO 路线吸收 one-to-one/NMS-free，DETR 路线吸收多尺度、分布回归和实时化；它们不是简单的 CNN 与 Transformer 二选一。
3. 开放词汇与可提示检测改变的是语义接口和训练数据规模，不应与 backbone、one/two-stage 或 NMS-free 混为同一代际。
4. 对工程最有价值的不是记住模型顺序，而是能识别一次架构修改改变了六个轴中的哪几个，并同步更新训练、导出、评测和部署契约。

### 竞争解释与反证

- 若固定数据、训练预算和 runtime 后，所谓“新范式”收益主要来自更强 backbone、更多数据或更长训练，则不能把收益归因于候选/匹配架构本身。
- 若 NMS-free 模型在目标导出和 runtime 中仍需外部重复结果处理，则“端到端”只在原始实现成立。
- 若开放词汇模型在目标类别和场景上需要大量 prompt 调优或微调，其工程优势应按总数据与校准成本重新计算。

### 未解决问题

- 目标设备上 dense CNN、RT-DETR、D-FINE 和 one-to-one YOLO 的真实端到端延迟、内存和量化稳定性；
- 小目标任务中收益究竟来自更高分辨率特征、分配、回归表示还是预训练数据；
- 开放词汇 detector 作为离线教师、大小模型协同节点和端侧模型时的不同验收标准；
- 不同范式之间可复用的语义节点和自动化精度对齐合同。

## Sources

访问日期：2026-07-30。来源只支持对应论文明确披露的架构和实验，不代表本人已复现，也不用于跨论文直接排名。

| ID | 主题 | 第一方资料 |
|---|---|---|
| D001 | R-CNN | [paper](https://arxiv.org/abs/1311.2524) |
| D002 | Fast R-CNN | [paper](https://arxiv.org/abs/1504.08083) |
| D003 | Faster R-CNN / RPN | [paper](https://arxiv.org/abs/1506.01497) |
| D004 | YOLOv1 | [paper](https://arxiv.org/abs/1506.02640) |
| D005 | SSD | [paper](https://arxiv.org/abs/1512.02325) |
| D006 | FPN | [paper](https://arxiv.org/abs/1612.03144) |
| D007 | RetinaNet / Focal Loss | [paper](https://arxiv.org/abs/1708.02002) |
| D008 | FCOS | [paper](https://arxiv.org/abs/1904.01355) |
| D009 | CenterNet / Objects as Points | [paper](https://arxiv.org/abs/1904.07850) |
| D010 | ATSS | [paper](https://arxiv.org/abs/1912.02424) |
| D011 | GFL / distributional box representation | [paper](https://arxiv.org/abs/2006.04388) |
| D012 | OTA | [paper](https://arxiv.org/abs/2103.14259) |
| D013 | TOOD / task alignment | [paper](https://arxiv.org/abs/2108.07755) |
| D014 | DETR | [paper](https://arxiv.org/abs/2005.12872), [repository](https://github.com/facebookresearch/detr) |
| D015 | Deformable DETR | [paper](https://arxiv.org/abs/2010.04159), [repository](https://github.com/fundamentalvision/Deformable-DETR) |
| D016 | DINO | [paper](https://arxiv.org/abs/2203.03605), [repository](https://github.com/IDEA-Research/DINO) |
| D017 | RT-DETR | [paper](https://arxiv.org/abs/2304.08069), [repository](https://github.com/lyuwenyu/RT-DETR) |
| D018 | RT-DETRv2 | [paper](https://arxiv.org/abs/2407.17140) |
| D019 | D-FINE | [paper](https://arxiv.org/abs/2410.13842), [repository](https://github.com/Peterande/D-FINE) |
| D020 | YOLOv10 | [paper](https://arxiv.org/abs/2405.14458), [repository](https://github.com/THU-MIG/yolov10) |
| D021 | Grounding DINO | [paper](https://arxiv.org/abs/2303.05499), [repository](https://github.com/IDEA-Research/GroundingDINO) |
| D022 | YOLO-World | [paper](https://arxiv.org/abs/2401.17270), [repository](https://github.com/AILab-CVC/YOLO-World) |
| D023 | YOLOE | [paper](https://arxiv.org/abs/2503.07465), [repository](https://github.com/THU-MIG/yoloe) |
| D024 | Florence-2 | [paper](https://arxiv.org/abs/2311.06242) |

具体 YOLO 分支身份、版本和实现关系仍由 [YOLO family](../model-index/families/yolo/README.md) 唯一维护；本页只保存跨检测器的架构演变机制。核心数据流与诊断入口见 [目标检测的核心因果链](object-detection-core.md)，任务契约与 Oracle 见 [目标检测](../tasks/object-detection.md)。
