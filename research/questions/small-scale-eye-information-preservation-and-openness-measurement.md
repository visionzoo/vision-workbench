---
title: Small-scale eye information preservation and openness measurement
status: working
type: research-question
rigor: standard
created: 2026-08-11
updated: 2026-08-18
confidence: low
provenance: conversation-draft
evidence_status: unverified
owner_review: pending
ip_review: pending
tags: [dms, ir, eye, small-target, roi, information-preservation, eyelid, openness, observability, uncertainty, selective-measurement, deployment]
related: [../experiments/upper-face-roi-information-preservation.md, dms-eye-visibility-and-localization-reliability.md, ../experiments/dms-eye-keypoint-model-selection.md, ../../foundations/tasks/2d-landmark-localization.md, ../../foundations/mechanisms/keypoint-output-representations.md, ../../engineering/diagnostics/ir-camera-input-chain-and-chroma-anomaly.md]
---

# Small-scale eye information preservation and openness measurement

## 1. Evidence boundary

本条目把历史 DMS 工程对话重构为研究问题。当前仓库没有导入原始 IR 图像、人工开合度标注、冻结模型、训练日志、板端输出或可复现实验，因此本文只建立问题、竞争假设、区分性实验和验收门，不报告任何已验证收益。

2026-08-12 对外部训练与目标端工作区做了只读制品核查。核查确认存在训练、评价和部署实现，也发现训练与目标端 ROI 语义、模型谱系和评价器有效性仍未绑定。原始制品没有进入本仓库；在形成可披露的不可变证据指针、通过 owner/IP review 并完成新鲜复现以前，这些内容只改变当前承诺和 Gate 状态，不构成 finding。

历史经验可能来自工作任务、设备或非公开数据。这里只保留抽象后的视觉问题，继续保持 owner/IP review pending；任何原始数据、模型、指标和实现进入仓库前都必须重新确认权属与可披露边界。

## 2. Research identity

研究编号：R1。

> 在给定原始成像质量、输入分辨率和计算预算下，眼睑开合相关信息如何经过人脸先验、上半脸 ROI、裁剪与重采样、网络下采样、多尺度融合、任务监督和 Head 读出而被保留、削弱或丢失？首次导致眼睛开合度无法可靠量测的因果边界在哪里？

研究对象不是“能否检测到眼睛”，而是小尺度眼部是否仍具有足够的细粒度可观测性，能够支持眼角、上下眼睑和连续开合度量测。

| 结果层 | 必须形成的结果 |
|---|---|
| 工程结果 | 在真实 IR 和低算力约束下，形成可观测性判断、眼部定位、眼睑结构、连续开合度、可信度与 UNKNOWN 降级接口 |
| 研究结果 | 区分原始信息不足、采样损失、表征削弱、信息未利用和最终读出失败，并定位首个可证实的因果边界 |

只有效果提升而没有机制区分，不能关闭 R1；只有机制分析而不能在真实 DMS 与目标部署链成立，也不能关闭 R1。

## 3. Task boundary

### In scope

- IR 眼部是否可量测；
- 人脸与上半脸先验怎样重新分配有效像素、上下文和搜索空间；
- crop、resize、网络 stride、特征融合、监督和 Head 对眼睑信息的影响；
- 眼角/眼睑结构和归一化连续开合度；
- 模糊、反光、遮挡、侧脸、ROI 裁断和小尺寸下的 UNKNOWN；
- PC、ONNX 与目标端 INT8 的结构和开合度一致性；
- 结论能否迁移到其他小尺度细粒度视觉任务。

### Out of scope

- 完整疲劳报警状态机；
- 所有 DMS 行为识别；
- 以 YOLO26 教程或模型排行榜代替机制研究；
- 从单一眼部数据直接宣称所有小目标的普遍规律；
- 单纯追求更高 AP、更低延迟或更大模型；
- 在当前条目中冻结生产阈值。

时序眨眼、持续闭眼和 PERCLOS 只作为眼部信号的下游 Oracle，不反过来掩盖单帧不可观测或错误量测。

## 4. Candidate output contract

对左右眼分别输出：

~~~text
observability: VALID | UNKNOWN
eye_roi: 完整保留眼角和上下眼睑的区域
eyelid_structure: 眼角、上下眼睑或等价结构表达
openness: 归一化连续开合度
confidence: 本次量测可信度
invalid_reason: blur | reflection | occlusion | truncation | pose | too-small | input-anomaly | other
~~~

该接口是研究合同，不是已经冻结的生产 API。核心约束是：

> 检测到眼睛不等于可以量测开合度；无法可靠量测时必须输出 UNKNOWN，不能强行输出开眼或闭眼。

## 5. Causal chain

~~~mermaid
flowchart TD
    A["IR 成像与输入语义"] --> B["人脸先验与可观测性"]
    B --> C["上半脸 ROI、裁剪与重采样"]
    C --> D["Backbone 下采样与分层表征"]
    D --> E["Neck、监督与任务 Head"]
    E --> F["眼睑结构与连续开合度"]
    F --> G["PC／ONNX／INT8 与时序验证"]
~~~

每一层都必须保留可寻址输入、输出和坐标合同。最终报警变化不能直接反推上游哪一层丢失了信息。

## 6. Operational distinctions

| 状态 | 可操作定义 | 当前允许的结论 |
|---|---|---|
| 原始信息不足 | 在合法高质量标注和受限上界方法下，源图中的眼睑结构或开合状态仍不能稳定区分 | 成像/目标像素本身构成上限 |
| 采样损失 | 不同任务标签的源区域经过确定性 crop/resize/downsample 后变成相同或在冻结 Oracle 下不可区分的张量 | 指定变换造成任务相关信息损失 |
| 表征削弱 | 输入仍可区分，但指定层在提前定义的探针族下显著降低结构或开合度可恢复性 | 只能相对该层、该探针和该预算成立 |
| 信息未利用 | 中间表征仍可恢复任务量，但当前监督、分配、融合或 Head 没有利用 | 不能归因为“信息已经消失” |
| 读出失败 | 正确位置存在候选或表征，但阈值、解码、量化、后处理或接口语义阻止最终输出 | 属于读出/系统问题，不是成像或 Backbone 根因 |

“热力图看不见”“线性探针失败”“最终漏检”都不足以单独证明绝对不可恢复。强不可逆结论至少需要确定性变换冲突或预先定义的独立上界证据。

## 7. Conversation-derived observations

以下只作为待验证线索：

- 曾使用“整图 → 人脸 ROI → 上半脸裁剪 → resize → YOLOv8 眼部检测”的链路；
- 上半脸方案可能同时改变眼睛有效像素、背景上下文、候选搜索空间和位置先验；
- 某些板端漏眼在降低候选阈值后重新出现，提示至少部分失败可能发生在读出而非信息存在性；
- 侧脸、反光、模糊、遮挡和 ROI 偏移可能使关键点或闭眼分类失效；
- NV12/NV21、亮度或色度语义变化可能显著改变局部眼部判断；
- 关键点、闭眼分类、可见性门控和时序判决目前提供了不同但尚未统一的眼状态证据。

### 7.1 2026-08-12 artifact intake

以下是对可定位但尚未获准进入本仓库的外部制品所作的受限观察：

- 训练侧把任务表述为 upper-face crop 上的单类眼睛检测；目标端实现使用由人脸框中心扩展得到的方形区域。两者不是同一个已冻结的 ROI 合同，因此当前首个待核边界位于模型之前的 crop、padding 与 resize 链；
- 目标端已有眼睛检测、左右分配和下游 eye ROI 接口，但部署模型缺少能够从训练 run 经导出、转换追到目标制品的完整不可变谱系；“代码与模型已进入分支”只能证明实现存在，不能证明训练—部署等价或任务通过；
- 关键点工作区已有 PFLD/HRNet、对齐训练和统一比较实现，但现有对比结果早于最新对齐运行，且聚合指标出现会支配均值的异常值。评价器原因未定位、运行未按冻结合同重做以前，任何模型优劣判断均拒绝接收；
- 检测训练记录存在配置身份与文字说明不一致的候选 run。该冲突必须在 P0 解决，不能由文件名、最新时间或发布说明猜测实际模型身份。

这些观察共同支持一个较窄的行动变化：先验证制品身份和端到端语义，再解释模型效果。它们不支持“ROI 有效”“HRNet 优于 PFLD”或“目标端已经验证”等结论，也不提高本文的证据强度。

这些观察没有绑定公开资产、模型版本、样本量或复现实验，不能作为 finding 引用。

## 8. Competing hypotheses and predictions

| ID | 假设 | 区分性预测 |
|---|---|---|
| H1 | 原始 IR 中已经没有足够眼睑信息 | 在使用高质量源 ROI、扩大输入和更强但受限的结构 Oracle 后，开合度误差仍接近标注噪声上限或无法区分 |
| H2 | 主要瓶颈是尺度分配 | 固定上下文比例与模型后，最终输入中的眼睛像素增加会稳定改善正确位置候选、结构误差和开合度，且具有可重复的尺寸拐点 |
| H3 | 主要收益来自上下文或搜索空间缩小 | 保持眼睛最终像素不变时，改变可见上下文或候选区域仍显著改变假阳性、正确位置分数或可量测率 |
| H4 | “眼睛位于上半脸”的条件先验是关键 | 在眼睛像素和局部纹理不变时，打乱其规范位置会产生超出平移等变误差的下降 |
| H5 | ROI 同时引入新的信息损失 | 模拟真实人脸框平移、缩放、侧脸和上边界裁剪后，检测或开合度在可重复扰动边界处突降 |
| H6 | 网络下采样或分层表征首先破坏细粒度结构 | 输入仍可由浅层/受限 Oracle 量测，但在某个 stride 后结构探针和开合度探针同步失效；受控 P2、抗混叠或更少下采样能改变该边界 |
| H7 | 主要问题是监督或任务 Head 未利用现存信息 | 固定输入与 Backbone 后，改变标签分配、任务表示或 Head 可改善输出，而中间探针能力基本不变 |
| H8 | 主要问题是部署读出和输入语义 | PC 中间量存在，但 ONNX/INT8、格式解释、阈值、解码或后处理使正确候选、结构或开合度丢失 |

H3、H6 和 H7 分别承载此前的 Neck、下采样与监督竞争解释；在需要不同实验和评价标准前，不另立为并行主问题。

## 9. Evidence gates

| Gate | 必须回答的问题 | 最低标准 |
|---|---|---|
| G0 语义合同 | 比较的是否是同一任务和输入 | 冻结数据、split、ROI、resize、坐标、输入格式、标签、模型版本、预算和评价器 |
| G1 现象复现 | 研究的是否是稳定现象 | 在新鲜运行和按视频分组的数据上复现，保留输入、原始输出和 Badcase |
| G2 解释可区分 | 是否存在自证循环 | 至少两个机制不同的假设提前写出不同预测；结果淘汰或明显收窄至少一个解释 |
| G3 因果归因 | 变化是否来自目标变量 | 单变量干预；控制有效眼像素、上下文、搜索空间、容量、预算和后处理 |
| G4 双层验证 | 是否只是玩具或单一模型偶然 | 受控实验与真实 DMS 至少两层独立支持，并报告跨身份/视频/相机切片和不确定性 |
| G5 创新储备 | 是否暴露结构性矛盾 | 指出现有机制的隐含前提、失效边界、替代方向和可被后续实验推翻的预测 |

一次 AP 提升最多通过 G1；至少通过 G3 才能形成有边界的 research finding，通过 G4 后才有资格回写 Foundations。

## 10. Current commitment

当前只承诺：

1. 先为现有训练、PC 推理和目标端链建立可披露的制品身份、ROI、padding、resize、通道、range、坐标与后处理合同，并用合成输入完成几何验证；
2. 合同通过后运行 [Upper-face ROI information-preservation experiment](../experiments/upper-face-roi-information-preservation.md)，分离尺度、上下文、搜索空间、位置先验和 ROI 误差；
3. 将 [Eye visibility and localization reliability](dms-eye-visibility-and-localization-reliability.md) 作为 observability 子问题；
4. 将 [DMS eye keypoint model selection](../experiments/dms-eye-keypoint-model-selection.md) 作为眼睑结构恢复与部署候选比较；评价器未通过有效性测试前拒绝模型排名；
5. 以历史 YOLOv8 上半脸链路作为第一个现象入口，以 YOLO26 作为现代整机观察锚点，YOLO11和经典结构只按区分需要进入；
6. 在形成合法、可披露、可复现的代码资产前，不建立独立 lab，不修改 projects registry。

本次建立研究不授权下载未审查数据、训练模型、接触公司资产、冻结阈值或宣称工程收益。

## 11. Phase-one completion standard

R1 第一阶段只有同时满足以下条件才可关闭或重构：

- 建立“原始信息不足—采样损失—表征削弱—信息未利用—读出失败”的可执行诊断路径；
- 分离 YOLOv8 上半脸方案中尺度、上下文、搜索空间、位置先验和 ROI 误差的贡献；
- 在 ROI 与非 ROI 链路中定位至少一个首个语义分歧边界；
- 淘汰或严格限制至少一个原本合理的竞争解释；
- 用独立标注把定位能力连接到眼睑结构、连续开合度和 UNKNOWN；
- 同时得到受控实验与真实 DMS 场景支持；
- PC、ONNX 与目标端误差有明确边界；
- 结论实际改变下一步的 ROI、采样、网络层级、监督或 Head 设计。

提出新结构不是第一阶段硬性要求。若证据推翻当前表述，应重构问题而不是保住原假设。

## 12. Acceptance and rollback

每项结果必须提供 artifact、claim、预注册 acceptance criterion、独立 Oracle、fresh evidence、next-step readiness 和 rollback trigger。

出现以下任一情况时降级或回滚：

- 数据泄漏、坐标链错误或模型/预处理版本不一致；
- 改变多个关键变量却仍宣称单一机制；
- 只有训练内或阈值选择集结果；
- 关键收益不能跨视频组或困难切片复现；
- 开放度 Oracle 的人工一致性不足；
- 结果只改善检测 AP，不能改善或解释细粒度量测；
- 发现内容依赖不可披露资产。

当前结论仅是：R1 已满足 Research 准入条件，尚无任何机制假设被验证。

## 13. Candidate paper direction: observability-aware continuous eye openness estimation

本节把 R1 收敛为一个候选论文问题，不改变 R1 当前 `working / unverified` 的证据状态，也不承诺必须设计新 backbone、新 detector 或端到端联合网络。论文只有在下面的可证伪命题得到独立证据支持后才成立。

### 13.1 Working title

候选英文标题：

> **When Is a Tiny Eye Measurable? Observability-Aware Continuous Eye Openness Estimation under Infrared Degradations**

更保守的工程化标题：

> **Observability-Aware Continuous Eye Openness Estimation for Small-Scale Infrared Driver Monitoring**

核心研究对象不是“闭眼二分类准确率”，也不是“眼睛检测 AP”，而是：

> 对小尺度 IR 眼部，能否在恢复眼睑结构和连续开合度的同时，判断当前输入是否仍足以支持可靠量测，并在不可量测时主动输出 UNKNOWN？

### 13.2 Why this is a research problem rather than a project report

论文需要区分三个经常被混为一谈的能力：

~~~text
Eye existence / detection
        ↓
Eyelid localization / structure recovery
        ↓
Continuous openness measurability
~~~

可能存在以下稳定失配：

~~~text
Eye detection        = success
Eye localization     = success
Eyelid structure     = unstable
Continuous openness  = unreliable
~~~

因此，“检测到眼睛”不能作为“可量测”的替代标签；同样，landmark 有坐标输出也不能证明该点可见、可标注或足以支持眼状态判断。

本论文候选的核心区分为：

~~~text
findable
    ≠
visible
    ≠
usable_for_openness
~~~

其中 `usable_for_openness` 是任务相关可观测性，而不是通用可见性。

### 13.3 Candidate scientific claims

论文最终最多尝试支持以下有边界的命题，不能预先写成结论：

| ID | 候选命题 | 必须被什么证据支持 |
|---|---|---|
| P1 | 小尺度眼部的“可检测尺度”和“可连续量测尺度”不是同一个边界 | 按有效眼宽/高分层后，检测、结构误差和 openness 误差出现稳定且可复现的不同失效拐点 |
| P2 | `visible` 不能充分预测 `usable_for_openness` | 在 visibility 相近样本中，存在与尺度、反光、模糊、姿态或裁断相关的系统性 measurability 差异 |
| P3 | 显式 observability / uncertainty 可以减少灾难性错误量测 | 在冻结 coverage 下，selective measurement 的风险显著低于仅按 detector/keypoint score 拒识的基线 |
| P4 | 结构化连续量测比强制 open/closed 二分类提供更稳定的下游证据 | 连续 openness 在中间状态、困难切片或跨域条件下改善 calibration、阈值稳定性或时序判决，而不是只提高训练域分类分数 |
| P5 | 真实部署链会改变细粒度可量测边界 | 保存同一输入或建立语义等价输入后，PC、ONNX、INT8/目标端的差异能被定位到明确边界，并影响结构/openness 而非只影响总体 AP |

若 P1–P5 中只有“换模型后平均指标更高”成立，则论文方向应降级为普通工程优化，不使用 observability 作为主张。

### 13.4 Candidate method abstraction

第一阶段不绑定具体 backbone。最小系统抽象为：

~~~mermaid
flowchart TD
    A["IR face / upper-face input"] --> B["Fine-grained visual representation"]
    B --> C["Eyelid structure head"]
    B --> D["Observability / usability head"]
    B --> E["Optional direct openness head"]
    C --> F["Geometry-derived openness"]
    D --> G{"Reliable enough to measure?"}
    E --> H["Continuous openness candidate"]
    F --> H
    G -->|YES| I["VALID + openness + confidence"]
    G -->|NO| J["UNKNOWN + invalid reason"]
    H --> I
~~~

候选实现可以是：

- direct coordinate regression；
- HRNet-style heatmap；
- eyelid contour / segmentation；
- geometry + direct openness multi-head；
- detector / pose 一体化路线。

这些是竞争实现，不是论文贡献本身。只有受控实验表明某种结构机制是可量测边界的主要限制时，才把网络结构升级为方法贡献。

### 13.5 Output representation

建议最小研究输出为：

~~~text
structure:
  eyelid landmarks | heatmaps | contour | equivalent geometry

observability:
  VALID | UNKNOWN

openness:
  continuous normalized value

confidence_or_uncertainty:
  calibrated score or distribution

invalid_reason:
  too-small | blur | reflection | occlusion | pose | truncation | input-anomaly | other
~~~

连续开合度的 Oracle 不能只由同一组预测关键点公式反推，否则会形成自证循环。至少保留两类候选定义并在 pilot 阶段验证人工一致性：

1. 独立人工或高质量结构标注导出的连续 geometry Oracle；
2. 与最终 DMS 需求一致、但不依赖候选模型自身输出的独立 openness 标注或排序 Oracle。

若二者一致性不足，先修 Oracle，不训练复杂网络。

### 13.6 Selective measurement formulation

论文不要求模型对所有帧强制给出可信 openness。令：

- `o` 为真实连续开合度；
- `o_hat` 为预测；
- `q` 为可量测置信度；
- `tau` 为冻结的接受阈值。

推理规则为：

~~~text
q >= tau  →  VALID, report o_hat
q <  tau  →  UNKNOWN
~~~

核心评价不只报告全样本 MAE，而要报告 risk–coverage：

~~~text
coverage ↑  → 保留更多样本
risk     ↑  → 通常承担更多困难/不可量测样本
~~~

至少比较：

- detector confidence；
- keypoint/heatmap confidence；
- visibility score；
- explicit `usable_for_openness`；
- uncertainty-aware selective measurement。

只有在相同 coverage 下风险下降，才能说明 observability 信号具有独立决策价值。

### 13.7 Controlled degradation axes

论文实验优先使用与真实 DMS 一致、但可单变量控制的退化轴：

| Axis | 主要回答的问题 |
|---|---|
| effective eye width / height | 检测可行尺度与连续量测可行尺度是否分离 |
| blur / motion | 高频眼睑结构丢失是否早于 eye existence 丢失 |
| reflection / glasses | 局部高亮是否导致 visible 与 usable 解耦 |
| occlusion | 部分结构缺失时模型是否强行补全坐标或状态 |
| yaw / pitch / side face | 透视压缩和自遮挡如何改变结构与 measurability |
| ROI shift / truncation | 上游 face/eye 定位误差何时跨过量测失效边界 |
| input-chain anomaly | NV12/NV21、range、亮度/色度或目标端输入语义是否制造额外失效 |

退化实验的目标不是生成一张 robustness 排名表，而是寻找：

> 从“仍可检测”到“仍可定位”再到“仍可连续量测”的任务相关失效边界。

### 13.8 Experimental protocols

#### Protocol A: Oracle ROI

目的：隔离 fine-grained representation 与 observability。

~~~text
source image
→ oracle / frozen high-quality eye ROI
→ structure + observability + openness
~~~

这个协议回答“已知眼睛在哪里以后还能不能量测”，不让 detector 失败掩盖细粒度问题。

#### Protocol B: Predicted ROI

目的：评价真实 pipeline。

~~~text
source image
→ face / eye detector
→ predicted ROI
→ structure + observability + openness
~~~

与 Protocol A 对照后至少区分：

- Oracle 成功、Predicted 失败 → detection / crop bottleneck；
- 两者都失败 → source information / representation / fine-grained head bottleneck；
- structure 正确、openness 错误 → measurement definition / calibration bottleneck；
- PC 正确、target 错误 → deployment / input semantic bottleneck。

#### Protocol C: Deployment equivalence

使用保存的同一输入 tensor 或可证明语义等价的输入，逐层比较：

~~~text
PC FP32
→ ONNX
→ converted model
→ target runtime / INT8
~~~

论文不能把输入格式、ROI、resize 或 decode 不一致造成的收益/退化归因给模型。

### 13.9 Baseline ladder

第一篇论文不需要一次比较所有新模型，优先形成能回答科学问题的最小梯度：

| Baseline | 输出 | 目的 |
|---|---|---|
| B0 binary eye-state classifier | open / closed | 现有离散任务参考 |
| B1 structure only | landmarks / heatmap + geometry openness | 判断结构恢复能否替代直接分类 |
| B2 structure + visibility | geometry + visible | 判断通用 visibility 是否足够 |
| B3 structure + task-specific usability | geometry + usable_for_openness | 判断任务相关 observability 的增量价值 |
| B4 structure + usability + calibrated uncertainty/selective output | VALID/UNKNOWN + openness | 检验最终论文主张 |

PFLD-style regression 与 HRNet-style heatmap 优先承担 B1/B2 的机制对照。YOLO26 Pose、RF-DETR Keypoint 或其他整图一体化方案只有在上游实例发现被证明是主要瓶颈时才进入完整系统比较。

### 13.10 Metrics

#### Detection / ROI

- correct-location raw candidate recall；
- operating-point recall / precision；
- false positives per frame / ROI；
- ROI completeness / truncation；
- eye-size-binned failure rate。

#### Structure

- normalized landmark / contour error；
- median、P90、P95；
- catastrophic failure rate；
- temporal jitter；
- visible / occluded / side-face / reflection slices。

#### Continuous openness

- MAE / median absolute error；
- signed bias；
- rank / linear correlation with independent Oracle；
- open / intermediate / closed separability；
- per-size and per-degradation failure boundary。

#### Observability / selective measurement

- AUROC / AUPRC for `usable_for_openness`；
- calibration / ECE；
- risk–coverage curve；
- catastrophic-error catch rate at frozen valid-retention points；
- UNKNOWN rate by degradation slice；
- domain-holdout threshold stability。

#### Downstream DMS oracle

- false-open / false-closed；
- blink event errors；
- sustained-closure / fatigue false alarms and misses；
- event delay；
- invalid/UNKNOWN 对最终状态机的影响。

时序指标只用于验证单帧量测是否真的有业务价值，不允许用 smoothing 掩盖单帧不可量测性。

### 13.11 Paper-worthy gates

该方向至少满足以下条件，才值得从 R1 中抽成论文实施计划：

1. **Oracle gate**：continuous openness 与 `usable_for_openness` 有可接受的人工一致性和稳定标注合同；
2. **Boundary gate**：至少一个困难轴上复现“检测仍可用但细粒度量测已失效”的独立边界；
3. **Observability gate**：task-specific observability 在相同 coverage 下显著优于 detector score、keypoint score 或通用 visibility 基线；
4. **Measurement gate**：连续结构量测在困难切片或跨域条件下提供二分类没有提供的稳定信息；
5. **Causality gate**：收益不能由更大输入、更大模型、更多数据、不同 ROI 或不同后处理解释；
6. **Deployment gate**：至少在一个真实目标运行时验证关键结论没有被量化和输入语义破坏；
7. **Downstream gate**：改进至少能解释或改善一个真实 DMS 下游错误类型，而不只是离线平均指标。

若第 2 或第 3 项失败，应放弃“observability-aware”作为论文主轴；若第 4 项失败，应重新评估 continuous openness 是否值得替代直接状态分类。

### 13.12 Negative results that still change the project

以下负结果也有研究和工程价值，但不应包装成正向论文结论：

- 检测与 continuous measurement 的失效尺度基本一致 → “任务边界分离”假设被削弱；
- visibility 已经等价于 usable → 不需要额外 task-specific observability head；
- risk–coverage 没有优于简单 confidence threshold → uncertainty 设计没有独立价值；
- 更精确 landmarks 不改善 openness / event → fine-grained geometry 不是当前主瓶颈；
- Oracle ROI 显著优于 predicted ROI → 论文应转向定位/ROI 或 small-target detection；
- PC 与目标端出现新增结构误差 → 优先转向部署语义/量化边界，而不是继续加模型复杂度。

### 13.13 Position of YOLO, STAL and small-target assignment

YOLO11/YOLO26、DFL、TaskAlignedAssigner、STAL 或 P2/P3 等机制在本论文中是候选上游解释，不是默认主贡献。

只有满足以下链路时才升级为核心实验：

~~~text
small eye miss
→ diagnostic low-threshold raw candidate absent
→ input / ROI observability 已通过
→ feature representation 或 positive allocation 成为主要嫌疑
→ controlled assignment / feature-level intervention
~~~

如果 raw candidate 已经存在而最终被阈值、decode、量化或 ROI 逻辑丢掉，则不应通过修改 label assignment 解决读出问题。

### 13.14 Candidate paper narrative

若证据支持，论文叙事应保持以下顺序：

~~~text
Tiny IR eye
    ↓
Eye can still be detected
    ↓
But fine-grained measurability may already fail
    ↓
Detection / visibility confidence is insufficient to identify that boundary
    ↓
Task-specific observability + structured continuous openness
    ↓
Selective VALID / UNKNOWN measurement
    ↓
Lower risk under scale / blur / reflection / occlusion / pose / ROI errors
    ↓
Confirmed on the deployment chain and downstream DMS oracle
~~~

论文不应写成：

~~~text
new backbone
+ attention module
+ new loss
→ higher score
~~~

除非 R1 的受控实验先证明某个具体结构机制就是首要因果瓶颈。

### 13.15 Execution order

在不打乱当前项目主线的前提下，论文工作按以下顺序附着在现有任务上：

1. 完成 P0/G0：统一训练、PC、目标端的 ROI、resize、输入和 evaluator 合同；
2. 从现有数据建立一个小而严格的 `eye-observability-v1` 标注子集，先验证 openness / usable 的人工一致性；
3. 用 Oracle ROI 测量有效眼像素与 blur/reflection/pose 等因素下的结构和 openness 边界；
4. 复用 PFLD / HRNet 选型实验建立 B1/B2；
5. 只有存在明确 observability gap 时实现 B3/B4；
6. 再接回 predicted ROI，判断 detector、assignment、crop 是否成为瓶颈；
7. 最后做 ONNX/INT8/目标端与时序 DMS 验证；
8. 达到 paper-worthy gates 后再拆出独立实验计划、结果表和论文写作资产。

因此，当前论文方向只是 R1 的一个收敛目标，不改变现阶段最优先的工程动作：先证明输入、ROI、评价器和部署语义是一致的，再解释模型效果。
