---
status: working
type: case
rigor: standard
provenance: conversation-draft
evidence_status: unverified
owner_review: pending
ip_review: pending
confidence: low
created: 2026-07-25
updated: 2026-07-28
---

# YOLO11 到 RV1126B：RKNN INT8 候选记录与证据恢复

## 当前证据结论

历史对话把本页描述为一条独立个人实验链路：YOLO11 → ONNX → RKNN INT8 → RV1126B，并计划使用 RKNN Toolkit2 做逐级精度对齐。当前没有找到能确认该链路已经建立的模型、配置、转换产物、板端输出、版本清单或评测结果，因此本页只保留候选身份、证据门和平台投影。

2026-07-28 在 `ultralytics`、`rknn`、`vision-workbench` 三个直接相关目录的 8 层范围内进行了有界盘点。没有找到身份匹配的 YOLO11 ONNX、RV1126B RKNN、板端输出或评测 manifest；已发现的 `.rknn` 文件属于其他模型或其他平台示例。全量递归搜索曾超时，因此该结果只约束已检查范围。

## 候选身份

| 项目 | 当前记录 |
|---|---|
| 模型 | 对话候选：YOLO11；没有身份一致的权重哈希 |
| 源格式 | 对话候选：ONNX；实体未定位 |
| 板端格式 | 对话候选：RKNN INT8；实体未定位 |
| 芯片 | 对话候选：Rockchip RV1126B；设备与版本记录未定位 |
| 工具链 | 对话候选：RKNN Toolkit2；toolkit/runtime/driver 版本未定位 |
| 目标 | 候选计划：同图逐级对齐、任务级比较和可复现 manifest |
| 最终精度 | 无证据 |
| 最终延迟 | 无证据 |

厂商适配范围由 [YOLO deployment](../../foundations/model-index/families/yolo/deployment.md) 维护；它只能提供实施入口，不能替代本案例的自有模型与设备证据。

## 证据恢复门

重新激活转换或板端实验前，至少要取得：

- 可独立支配且权属清楚的源权重、模型配置和 SHA-256；
- ONNX 实体、导出命令、opset、输入输出签名和结构检查结果；
- RKNN 转换配置、校准数据 manifest、toolkit 版本和转换日志；
- RV1126B 设备标识、runtime、driver、SDK 来源与板端程序版本；
- 同一评测集、预处理和后处理合同，以及可独立复算的逐样本结果。

任何一项来自公司任务、设备、代码、数据、模型或客户上下文时，本页继续保持 `ip_review: pending`，不得复制资产或公开组合信息。

## 取得独立资产后的最小首轮

第一轮只回答“差异最早出现在哪个语义阶段”，不直接建设完整自动化系统：

```text
同一原始样本
  → ONNX / RKNN 模拟器 / RV1126B 的实际模型输入
  → 三端最终网络输出（decode 与 NMS 前）
  → 同一后处理下的框、分数与类别
```

每次运行必须保存 Run ID、模型与输入哈希、Toolkit2/runtime/driver 版本、输入输出签名、量化参数和原始结果。如果实际输入已经不同，先修正输入；如果最终网络输出一致但检测结果不同，先修正 decode/NMS。只有最终网络输出已经分歧时才进入网络层。

## 本案例的网络层投影

通用诊断顺序和记录字段只由 [Model quantization and accuracy alignment](../diagnostics/model-quantization-accuracy-alignment.md) 维护。本案例仅补充 YOLO/RKNN 的候选映射：

- 候选语义边界为 backbone 末端输出、P3/P4/P5 融合输出、Detect 输入和最终网络输出；
- 只有 ONNX 图与 RKNN 可观测 tensor 的上下游关系能够证明语义一致时，才允许比较；不能按节点序号或相似名称配对；
- 每个实际映射必须记录 ONNX tensor locator、RKNN tensor locator、shape/layout/dtype、scale/zero-point/axis 和观测 API；
- 如果 RKNN 转换融合或隐藏了候选边界，将其记为 `unknown`，选择最近的可证明等价点，不能伪造“逐层对齐”；
- 找到首个显著分歧后只检查相邻算子、融合和量化映射；最终仍回到固定评测集的任务指标。

## 任务与系统验收

阈值要在真实资产和基线形成后由本人预先接受，不能先写一个“相似度通过线”。未来至少同时检查：

- 三端输入、输出语义和同一后处理合同；
- 固定评测集上的 precision、recall、F1 或 AP，以及明确的基线和样本量；
- 小目标、暗光、遮挡等与真实任务相关的关键分层；
- 模型执行延迟、完整链路延迟和连续运行稳定性；
- Run ID 能返回模型、数据、转换配置、工具链和原始结果。

中间 tensor 相似度只负责定位，不替代任务与系统 Oracle。

## 晋级与停止条件

只有取得上述身份一致证据并完成人工 IP 审查，才考虑把本页改为 `evidence_status: partial`。如果实际资产对应其他 SoC、模型族或任务，应建立真实案例或放弃本候选记录，不得借用其他 RKNN 示例拼接链路。

## 当前边界

这不是已完成的 RKNN 精度验证系统，也不能确认真实模型、RV1126B 或结果来自可独立支配的个人实验。证据与权属恢复前保持 `working / unverified / pending / low`；不得公开、晋级或把厂商示例数字写成本人结果。

相关基础页：[YOLO evaluation](../../foundations/model-index/families/yolo/evaluation.md)、[YOLO deployment](../../foundations/model-index/families/yolo/deployment.md)。
