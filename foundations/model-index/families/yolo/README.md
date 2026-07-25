---
status: working
type: model-index
rigor: standard
provenance: official-papers-repositories-documentation-and-owner-use
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-07-25
updated: 2026-07-25
---

# YOLO

YOLO 是实时目标检测模型家族，但不是一条由单一组织连续维护的版本线。YOLOv3 之后，不同编号和命名分支来自不同作者或组织，代码、许可和版本含义也不同。

## 先解决怎么选

下面是当前判断，不是跨来源排行榜。最终选择仍以目标数据和目标芯片复测为准。

| 任务 | 当前先看 | 为什么 | 使用前要确认 | 本人经验 |
|---|---|---|---|---|
| 闭集、轻量、希望训练导出省事 | YOLO11n / YOLO11s | Ultralytics 的训练、验证和导出入口完整；nano/small 便于先建立速度—精度基线 | package 版本、许可、目标 runtime 的算子和后处理 | YOLO11n 已用于局部目标训练、ONNX 导出和 INT8 部署 |
| 小目标或局部目标 | 先用轻量分支做目标像素和标签实验，再决定是否加高分辨率特征层 | 小目标首先受有效像素、标注和正样本影响；换大模型不一定解决 | 目标尺寸分布、裁剪方式、P2/P3 输出、输入尺寸和延迟预算 | 已有 YOLO11n、224×224、单类局部目标案例 |
| RKNN / RV1126B | 优先从 RKNN Model Zoo 已适配的 YOLO11、YOLOX 等分支中选 | 厂商已有 FP16/INT8 转换和 C/Python 示例，可减少接口猜测 | Model Zoo、Toolkit2、runtime、SoC 必须绑定版本；厂商支持不等于自有模型已对齐 | YOLO11 → RKNN INT8 对齐案例进行中 |
| 需要去掉外部 NMS | YOLO26 或其他明确的端到端分支 | 默认一对一 head 可直接输出最终结果，减少传统后处理 | 导出的是一对一还是一对多 head，目标 NPU 是否支持整张图 | 尚无本人部署结论 |
| 类别在运行时变化 | YOLO-World / YOLOE | 支持文本、视觉提示或开放词汇路线 | 原始实现与框架迁移版、文本编码器、词汇缓存、训练数据和许可 | 尚无本人验证 |

如果目标只是做一个闭集小模型，不要因为版本号更新就直接换模型；先固定数据、输入、评测和板端 Oracle，再比较候选分支。

## 在 Foundations 里的位置

- 角色：`task-model`
- 主要任务：[目标检测](../../../tasks/object-detection.md)
- 核心机制：[多尺度、标签分配、检测头、结果选择](../../../mechanisms/object-detection-core.md)
- 真实工程案例：[海思 INT8 局部目标](../../../../engineering/cases/yolo11n-local-target-hisi-int8.md)、[RV1126B RKNN INT8 对齐](../../../../engineering/cases/yolo11-rv1126b-rknn-int8-alignment.md)

## 本人经验

已确认有两条可独立支配的个人实验链路：

1. YOLO11n 局部目标训练 → ONNX → 海思 INT8 OM；
2. YOLO11 → ONNX → RKNN INT8 → RV1126B。

两条链路分开记录。第一条已有训练和板端现象，第二条仍在建设精度验证流程；不得共用指标或把计划写成结果。

## 各页面分工

| 页面 | 只负责什么 |
|---|---|
| [Variants](variants.md) | 版本归属、维护方和主来源；这是谱系的唯一维护位置 |
| [Architecture](architecture.md) | 结构和机制发生了什么变化 |
| [Data and training](data-and-training.md) | 迁移训练时真正影响结果的判断 |
| [Evaluation](evaluation.md) | 少量第一方事实和本人的评测口径 |
| [Deployment](deployment.md) | 导出、量化和板端检查 |
| [Ecosystem implementations](ecosystem-implementations.md) | 高质量第三方复现、移植和改造 |
| [Limitations](limitations.md) | 已知限制和未完成项 |
| [Sources](sources.md) | Source ID 与原始链接 |

新增分支时，先改 `variants.md` 和 `sources.md`；只有结构、训练、评测或部署确实有新内容时，才改对应页面。

## 当前到哪一步

- 目录分工和维护方式已经由本人验收；
- 主要分支、第三方生态改造和 Source ID 已建立；
- 两条本人实验已经独立建案，但实验记录和内容尚未完成人工验收；
- 没有逐个冻结所有仓库 revision、权重哈希和完整指标条件；
- 没有做统一硬件、统一 runtime 的全家族复测。

因此当前仍是 `working / partial`。这里的 `owner_review: pending` 指技术内容尚待本人验收，不否定此前已经完成的目录样板验收。
