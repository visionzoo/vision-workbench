---
status: working
type: case
rigor: standard
provenance: owner-independent-experiment-and-first-party-platform-reference
evidence_status: partial
owner_review: pending
ip_review: accepted
confidence: medium
created: 2026-07-25
updated: 2026-07-25
---

# YOLO11 到 RV1126B：RKNN INT8 精度对齐

## 当前状态

这是一条独立的个人实验链路：YOLO11 → ONNX → RKNN INT8 → RV1126B，使用 RKNN Toolkit2。目标不是只完成转换，而是建立可重复的精度验证：同一输入下比较 ONNX、RKNN 模拟器和板端最终框、分数与类别，必要时再比较中间层。

这条链路仍在进行中。当前没有已确认的最终精度和延迟指标，因此本页不借用另一芯片案例、RKNN Model Zoo 或其他 SoC 的数字补齐结果。

## 已确认事实

| 项目 | 当前记录 |
|---|---|
| 模型 | YOLO11；具体规模和权重哈希待补 |
| 源格式 | ONNX |
| 板端格式 | RKNN INT8 |
| 芯片 | Rockchip RV1126B |
| 工具链 | RKNN Toolkit2；具体版本待补 |
| 目标 | 自动转换、同图逐级对齐、任务级精度比较、可复现 manifest |
| 最终精度 | 尚未形成 |
| 最终延迟 | 尚未形成 |

RKNN Model Zoo 当前提供 YOLO11n/s/m 的 FP16/INT8 示例，并把 RV1126B 列为支持平台（Y025）。这是厂商适配入口，不是本模型已经通过精度验收的证据。

## 要解决的问题

转换成功后仍可能出现：

1. ONNX 与 RKNN 的预处理不一致；
2. INT8 校准导致分类分数或定位分布压缩；
3. 输出顺序、DFL/decode、坐标格式或 NMS 实现不一致；
4. 模拟器与板端 runtime/driver 行为不同；
5. 单张图看似一致，但在小目标、暗光、遮挡等分层上掉点。

## 验证链路

```text
固定 Run ID、模型、数据清单和预处理
        ↓
ONNX Runtime 原始输出与检测结果
        ↓
RKNN 模拟器原始输出与检测结果
        ↓
RV1126B 板端原始输出与检测结果
        ↓
任务指标、分层差异和延迟
```

每一步保存：

- 模型、代码、Toolkit2、runtime 和 driver 版本；
- 输入文件哈希与送入模型前的数据哈希；
- 输出 tensor 名称、shape、dtype、量化参数和语义；
- 框匹配 IoU、类别一致率、分数差异；
- precision、recall、F1 或 AP 及其数据范围；
- 模型执行和完整链路延迟。

## 区分实验

| 现象 | 先做什么 | 目的 |
|---|---|---|
| 模拟器和 ONNX 已不同 | 核对预处理、量化参数和输出解释；比较非量化/INT8 | 区分接口问题与量化问题 |
| 模拟器一致、板端不同 | 固定 runtime/driver，回读实际输入输出 | 定位板端集成或版本差异 |
| 只有小目标掉点 | 按目标尺寸看分数和框差异，检查 calibration set | 避免全局均值掩盖局部失真 |
| 最终框不同但输出接近 | 对齐 decode、sigmoid、阈值和 NMS | 区分网络输出与后处理 |
| 最终输出仍无法定位 | 选择少量关键层 dump | 避免一开始就做全层对比 |

## 验收条件

最终阈值尚未设定。在个人评测集形成前，不预先承诺“相似度多少即通过”。至少要同时满足：

- 同图输出语义和后处理完全对齐；
- 任务级精度损失在明确阈值内；
- 小目标等关键分层没有不可接受退化；
- 连续运行、模型执行和完整链路性能可复现；
- Run ID 能回到模型、数据、工具链和原始结果。

## 当前边界

这不是已完成的 RKNN 精度验证系统，也不是厂商示例复述。真实模型、RV1126B 和后续指标均来自本人可独立支配的个人实验；公开剥离时重新做 IP 和 Git 历史审核。

相关基础页：[YOLO evaluation](../../foundations/model-index/families/yolo/evaluation.md)、[YOLO deployment](../../foundations/model-index/families/yolo/deployment.md)；通用诊断草稿：[模型量化与精度对齐](../diagnostics/model-quantization-accuracy-alignment.md)。
