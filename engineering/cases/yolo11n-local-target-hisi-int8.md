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

# YOLO11n 局部目标到海思 INT8：候选记录与证据恢复

## 当前证据结论

历史对话声称曾跑通 YOLO11n 局部目标训练、ONNX 导出和海思 INT8 OM 板端推理，并记录了“PC 端 F1 约 0.8”和“把 score threshold 降到 0.01 后恢复漏检”。当前没有找到能把这些描述连接到同一模型、数据、转换配置、设备运行和评测结果的原始证据，因此它们不是已确认的个人工程事实。

2026-07-28 的有界盘点得到两项可寻址观察：

- 本地 checkpoint `model/v11n_train50_best.pt` 的 SHA-256 为 `73524ba93aec1508ad950f7dd128cc1238b55edb75fcf3e3caadb36979507e02`。此前只通过归档清单与 `pickletools` 检查其嵌入元数据，没有反序列化或执行模型；元数据指向 480 输入、7 类 DMS 检测器，不是本页所述 224 输入、单类局部目标案例。
- `runs/detect/train*` 中三组可见训练记录使用 YOLOv8n，输入为 320 或 640；它们不能充当本页 YOLO11n 案例的训练记录。

在 `ultralytics`、`rknn`、`vision-workbench` 三个直接相关目录的 8 层范围内，没有找到身份匹配的 YOLO11 ONNX、海思 OM、转换配置、板端输出或评测 manifest。更大的全量搜索曾超时，所以这里记录的是盘点边界，不是“所有磁盘均不存在”的结论。

## 历史候选描述

| 项目 | 当前记录 |
|---|---|
| 任务 | 对话候选：单类眼部/局部目标检测 |
| 模型 | 对话候选：YOLO11n |
| 输入 | 对话候选：224×224 |
| 数据 | 来源、权属、数量和 split 均未恢复 |
| PC 模型 | 对话候选：ONNX；实体未定位 |
| 板端模型 | 对话候选：海思 INT8 OM；实体未定位 |
| 芯片 | 对话候选：海思 NPU；具体 SoC 未确认 |
| PC 指标 | 对话回忆：F1 约 0.8；缺少评测集、阈值、样本量和原始结果 |
| 板端现象 | 对话回忆：默认后处理少检，`score_thr=0.01` 后恢复；缺少成对输出 |
| 性能目标 | 对话候选：模型执行不超过 20 ms；没有实测证据 |

本页不能确认这些材料是否来自可独立支配的个人实验。证据与权属恢复前保持 `ip_review: pending`，不得把本页内容公开、晋级或作为作品集结果。

## 候选问题

如果历史现象能够在来源清楚的独立资产上复现，需要区分：

1. 量化把分类分数压低；
2. PC 与板端的颜色、range、resize 或 normalization 不一致；
3. 输出顺序、激活、DFL/decode、坐标还原或 NMS 解释不同；
4. 校准集没有覆盖真实局部目标分布；
5. 模型本身在低分目标上就不稳定，板端差异只是把它推过阈值。

不能从“降低阈值后恢复”直接选择其中任何一个解释。

## 待恢复的关键证据

| 历史候选观察 | 最小所需证据 | 恢复后仍不能自动支持什么 |
|---|---|---|
| PC 端 F1 约 0.8 | 模型哈希、数据 manifest、split、阈值、评测脚本和逐样本结果 | 不能证明板端一致，也不能外推其他数据 |
| 板端降低 score threshold 到 0.01 后恢复漏检 | 同一输入的 ONNX/OM 原始输出、预处理、decode/NMS 配置和设备版本 | 不能证明根因就是阈值，也不能直接成为产品阈值 |
| 海思 INT8 OM 已运行 | ONNX 与 OM 哈希、转换命令/config、校准清单、SoC、runtime、driver 和板端日志 | 不能证明精度或性能已经验收 |

当前没有证据排除输入、量化、输出解释、后处理或模型本身不稳定等竞争解释。

## 取得独立资产后的区分实验

1. 保存一张图在 PC 与板端的实际模型输入，逐像素核对；
2. 同图比较 PyTorch/ONNX/OM 的原始输出，先不做阈值和 NMS；
3. 对 FP16/非量化 OM 与 INT8 OM 做同样比较；
4. 在固定评测集上同时计算 precision、recall、F1、框匹配率和分数偏移；
5. 画出正常目标与漏检目标的 ONNX/OM 分数分布；
6. 固定工具链、SoC、频率和计时范围，补齐模型执行与完整链路延迟。

## 当前可复用的诊断假设

- 板端少检先比较同图原始输出，不先猜网络结构有问题；
- 极低阈值能恢复目标，是定位线索，不是验收结果；
- 小目标量化对齐必须看分数和框的分层结果，不能只看全局相似度；
- PC F1、板端精度和板端延迟是三项独立验收，不能互相替代。

这些判断目前只是由候选问题推导出的诊断路线，不是该案例已经验证的经验。

## 晋级与停止条件

只有同时取得身份一致的模型、数据 manifest、转换记录和板端证据，并完成本人 IP 审查，才考虑把本页改为 `evidence_status: partial`。如果恢复的资产指向不同任务、输入、模型族或平台，应新建真实案例或放弃本候选记录，不能强行拼接。

## 适用边界

本页只保存历史候选问题、有限资产盘点和未来验收合同。它不证明 YOLO11n、224×224、单类局部目标或海思 INT8 OM 链路已经运行。本案例保持 `working / unverified / pending / low`。

相关基础页：[YOLO training](../../foundations/model-index/families/yolo/data-and-training.md)、[YOLO evaluation](../../foundations/model-index/families/yolo/evaluation.md)、[YOLO deployment](../../foundations/model-index/families/yolo/deployment.md)；通用诊断草稿：[模型量化与精度对齐](../diagnostics/model-quantization-accuracy-alignment.md)。
