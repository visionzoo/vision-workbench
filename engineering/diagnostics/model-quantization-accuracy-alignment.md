---
title: Model quantization and accuracy alignment
status: working
type: diagnostic
rigor: standard
created: 2026-07-25
updated: 2026-07-28
confidence: low
provenance: conversation-draft
evidence_status: unverified
owner_review: pending
ip_review: pending
tags: [onnx, rknn, int8, accuracy, deployment]
related: [foundations/model-index/families/yolo/deployment.md]
---

# Model quantization and accuracy alignment

## Evidence boundary

本条目由历史对话和当前工程推断重构，用于保存待验证的问题结构；没有导入身份一致的源模型、转换配置、运行日志、板端 dump 或评测结果。下文是候选诊断合同，不是已经通过某一工具链验证的方法，也不激活转换或设备实验。

## Problem

候选问题表征：建立从源模型到量化设备模型的可复现精度验证方法，区分模型转换、量化、预处理、运行时和后处理分别造成的偏差。RV1126B、RKNN Toolkit2 或海思 OM 都只是案例投影；通用诊断不能替代对精确 toolkit、runtime、driver、SDK 和图变换的核验。

## Goal, constraints, and evaluation

以下是待确认目标，不是已接受的实验结果：

- 同一原始输入和同一语义预/后处理下比较源端、转换端与设备端输出；
- 同时考虑输入字节、中间网络边界、最终网络输出和任务级结果；
- Run ID、模型版本、转换配置、量化数据集和实体文件可追溯；
- 量化模式、输入尺寸、颜色、range、layout、mean/std、容差和 API 能力必须逐运行确认；
- 数值相似度负责定位，任务指标和系统行为负责最终验收。

## Competing explanations

若最终精度下降，候选原因至少包括：输入不一致、图优化或算子替换、校准集分布、量化参数、颜色与范围、layout/resize、runtime/driver 兼容性、输出反量化、decode 或 NMS。不能从最终 mAP、漏检或低分现象直接承诺“量化导致”，也不能从某层相似度较低直接承诺该层是根因。

## 语义边界—首个分歧—局部下钻

1. **冻结运行身份**：记录源模型、转换模型、运行代码、数据清单、工具链与设备版本；任一关键身份未知时先停止归因。
2. **冻结输入契约**：从同一原始样本生成各端实际模型输入，核对 resize/letterbox、颜色、range、layout、dtype、padding 和输入字节哈希。
3. **对齐最终网络输出**：比较进入 decode/NMS 前具有相同语义的输出，先核对名称映射、shape、layout、dtype、量化参数和反量化规则，再比较数值。
4. **定位首个显著分歧边界**：只有最终网络输出已经分歧时，才选择少量具有相同图语义的中间边界，由输出向输入二分或分段排查。
5. **局部下钻**：找到首个分歧边界后，只检查该边界两侧的相邻算子、融合、量化和 layout 变化；不从最终症状直接跳到某个上游模块。
6. **回到任务 Oracle**：修正后重新计算固定数据上的任务指标、关键分层和设备稳定性；中间 tensor、余弦相似度或 Agent 解释都不能单独完成接受。

“同一层”必须由图语义和输入输出关系证明，不能按节点序号或相似名称猜测。若转换器融合、拆分或删除了边界，应记录最近的语义等价点和映射限制；无法建立映射时，该层比较为 `unknown`，不是失败证据。

## 网络层比较记录

每个被选择的边界至少记录：

| 字段 | 作用 |
|---|---|
| source/runtime tensor locator | 证明比较对象可以重新定位 |
| upstream/downstream semantic role | 证明两端边界具有可比语义 |
| shape/layout/dtype | 先排除接口解释差异 |
| scale/zero-point/axis | 明确量化与反量化合同 |
| min/max/mean/std 与异常通道 | 识别饱和、偏移或局部失真 |
| cosine、MAE、max error 等定位指标 | 描述差异，不充当最终 Oracle |
| sample ID 与输入哈希 | 防止跨样本或跨预处理比较 |

不默认全层 dump。只有现有边界仍无法区分竞争解释、工具链确实支持观测且存储/IP 风险可接受时，才增加相邻层。

## Required environment record

```yaml
run_id:
source_model_sha256:
converted_model_sha256:
target_soc:
toolkit_version:
runtime_version:
driver_version:
sdk_provenance:
preprocess_contract:
output_contract:
graph_mapping_revision:
layer_probe_capability:
dataset_manifest:
postprocess_contract:
```

## 区分性结果解释

| 现象 | 优先动作 | 当前能区分什么 |
|---|---|---|
| 实际模型输入已不同 | 修正输入生成并重新运行 | 输入链路与网络执行 |
| 模拟器和源端最终网络输出不同 | 核对量化参数、图变换和输出解释 | 转换/量化侧与后处理侧 |
| 模拟器一致、板端不同 | 固定 runtime/driver，回读实际输入输出 | 设备集成与离线转换 |
| 最终网络输出接近但最终框不同 | 对齐 decode、阈值和 NMS | 网络输出与后处理 |
| 只有关键分层掉点 | 按尺寸、场景或类别检查分数和框差异 | 全局平均与局部退化 |
| 关键边界出现首个分歧 | 检查该边界相邻算子与量化映射 | 定位范围，不直接证明根因 |

## 案例投影

- [YOLO11n 局部目标到海思 INT8](../cases/yolo11n-local-target-hisi-int8.md)只保存该候选案例的身份、历史观察和恢复条件。
- [YOLO11 到 RV1126B RKNN INT8](../cases/yolo11-rv1126b-rknn-int8-alignment.md)只保存 RKNN/RV1126B 的候选环境、证据门和可能的 YOLO 边界映射。
- 模型级部署事实由 [YOLO deployment](../../foundations/model-index/families/yolo/deployment.md) 维护。

## Current conclusion

当前没有平台级技术结论。当前形成的候选诊断顺序是：先锁定身份和输入契约，再比较最终网络输出；确认分歧后寻找首个语义分歧边界并局部下钻，最终回到任务级和系统级 Oracle。该顺序仍需在来源清楚的独立实验中验证，因此本页保持 `working / unverified / pending / low`。
