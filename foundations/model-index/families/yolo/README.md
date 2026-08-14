---
status: working
type: model-index
rigor: standard
provenance: official-papers-repositories-documentation-and-owner-use
evidence_status: partial
owner_review: accepted
ip_review: not-applicable
confidence: medium
created: 2026-07-25
updated: 2026-08-14
---

# YOLO

YOLO 是实时目标检测模型家族，但不是由单一组织连续维护的一条版本线。YOLOv3 之后，不同编号和命名分支来自不同作者或组织，代码、许可、结构和输出语义都可能不同。

## 总目标：从一个完整检测器建立专家知识链

这里积累 YOLO，不是为了记住版本号，而是为了能够沿真实因果链解释和排查一个视觉系统：

```text
任务与数据
→ 输入与标注
→ backbone 分层表征
→ neck 多尺度融合
→ detection head 原始输出
→ 训练时的标签分配与损失
  或推理时的 decode 与结果选择
→ 任务指标、延迟和部署边界
```

面对漏检、框偏、重复框或板端差异时，应先判断问题发生在哪一段，再选择证据；不能从最终现象直接归因“模型不够大”或“量化有问题”。

## 选分支时先问什么

下表是检索入口，不是跨来源排行榜。最终选择仍由目标数据、输入、实现版本和目标硬件复测决定。

| 需求 | 当前先看 | 关键原因 | 采用前必须确认 |
|---|---|---|---|
| 闭集、轻量、快速建立基线 | YOLO11n / YOLO11s | 训练、验证和导出入口完整；候选案例记录使用这一分支，但原始权重映射待确认 | package revision、许可、输入输出和目标 runtime |
| 小目标或局部目标 | 轻量分支 + 目标像素/标签/尺度分析 | 有效像素、标签完整性、P3/P2 接入和正样本覆盖通常先于扩大模型 | 目标尺寸分布、裁剪、stride、召回与延迟预算 |
| RKNN / RV1126B | 厂商已适配的 YOLO11 等实现 | 已有转换与运行入口，可减少接口猜测 | Model Zoo、Toolkit、runtime、SoC 和自有权重必须分别核验 |
| 减少外部 NMS | YOLO26 或其他明确的端到端分支 | one-to-one 输出可减少传统结果选择 | 实际导出的是哪条 head、runtime 是否支持、精度口径是否一致 |
| 运行时改变类别 | YOLO-World / YOLOE | 引入文本、视觉提示或开放词汇能力 | 原版与迁移版、文本编码器、词汇缓存、训练数据和许可 |

如果目标只是做一个闭集小模型，不因版本号更新直接换模型。先固定数据、输入、评测和部署 Oracle，再比较候选分支。

## 按问题进入

| 页面 | 负责的问题 |
|---|---|
| [Architecture](architecture.md) | YOLO11 参考数据流、各模块输入输出、机制变化和失效线索 |
| [YOLO26 architecture](yolo26-architecture.md) | 固定 YOLO26 实现的逐层结构、双 head、训练/推理路径、修改影响和学习 Oracle |
| [Data and training](data-and-training.md) | 数据、标签分配、损失、增强和迁移训练判断 |
| [Evaluation](evaluation.md) | 第一方代表事实、个人评测口径和任务级 Oracle |
| [Deployment](deployment.md) | 导出、量化、runtime、后处理和板端契约 |
| [Variants and implementations](variants.md) | 原作者分支、维护组织、第三方复现和芯片适配的身份关系 |
| [Sources](sources.md) | 稳定 Source ID、第一方资料和固定实现 revision |
| [目标检测机制](../../../mechanisms/object-detection-core.md) | 跨模型复用的检测因果链；不维护 YOLO 版本事实 |

新增分支先更新版本身份和来源。只有它确实改变结构、训练、评测或部署判断时，才修改对应页面。

## 工程候选记录

当前有两条由历史对话重构、但尚未找到完整原始证据映射的案例记录：

1. [YOLO11n 局部目标 → ONNX → 海思 INT8 OM](../../../../engineering/cases/yolo11n-local-target-hisi-int8.md)；
2. [YOLO11 → ONNX → RKNN INT8 → RV1126B](../../../../engineering/cases/yolo11-rv1126b-rknn-int8-alignment.md)。

第一条记录了训练、导出和板端阈值现象，第二条记录了拟建设的精度验证链路。当前资产盘点尚不能把这些陈述对应到同一组模型、配置、日志和评测输出，因此它们只能定义待恢复的问题，不能作为本人已验证结果。两条候选链路也不共用指标。

## 当前边界

- 本轮目录职责、固定 YOLO11 实现解释和第一方来源边界已于 2026-07-27 通过本人审查；
- 工程引用的证据降级边界已于 2026-07-27 通过本人审查；接受不改变底层 case 的未验证状态；
- 第一方结构和指标仍只代表对应版本与来源，不代表本人复测；
- 两个工程案例都缺少完整 manifest、成对任务指标和网络层证据；
- 没有进行统一硬件、统一 runtime 的家族横向复测；
- 以上降级不否定已接受的第一方技术内容；整个条目继续保持 working / partial / medium。
