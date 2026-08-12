---
title: Small-scale eye information preservation and openness measurement
status: working
type: research-question
rigor: standard
created: 2026-08-11
updated: 2026-08-11
confidence: low
provenance: conversation-draft
evidence_status: unverified
owner_review: pending
ip_review: pending
tags: [dms, ir, eye, small-target, roi, information-preservation, eyelid, openness, deployment]
related: [../experiments/upper-face-roi-information-preservation.md, dms-eye-visibility-and-localization-reliability.md, ../experiments/dms-eye-keypoint-model-selection.md, ../../foundations/tasks/2d-landmark-localization.md, ../../foundations/mechanisms/keypoint-output-representations.md, ../../engineering/diagnostics/ir-camera-input-chain-and-chroma-anomaly.md]
---

# Small-scale eye information preservation and openness measurement

## 1. Evidence boundary

本条目把历史 DMS 工程对话重构为研究问题。当前仓库没有导入原始 IR 图像、人工开合度标注、冻结模型、训练日志、板端输出或可复现实验，因此本文只建立问题、竞争假设、区分性实验和验收门，不报告任何已验证收益。

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

1. 运行 [Upper-face ROI information-preservation experiment](../experiments/upper-face-roi-information-preservation.md)，分离尺度、上下文、搜索空间、位置先验和 ROI 误差；
2. 将 [Eye visibility and localization reliability](dms-eye-visibility-and-localization-reliability.md) 作为 observability 子问题；
3. 将 [DMS eye keypoint model selection](../experiments/dms-eye-keypoint-model-selection.md) 作为眼睑结构恢复与部署候选比较，不用模型排名替代 R1；
4. 以历史 YOLOv8 上半脸链路作为第一个现象入口，以 YOLO26 作为现代整机观察锚点，YOLO11和经典结构只按区分需要进入；
5. 在形成合法、可披露、可复现的代码资产前，不建立独立 lab，不修改 projects registry。

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
