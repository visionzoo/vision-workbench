---
status: working
type: case
rigor: standard
provenance: owner-independent-experiment
evidence_status: partial
owner_review: pending
ip_review: accepted
confidence: medium
created: 2026-07-25
updated: 2026-07-25
---

# YOLO11n 局部目标：从训练到海思 INT8

## 先说当前结论

YOLO11n 已经跑通局部目标训练、ONNX 导出和海思 INT8 OM 板端推理。PC 端 F1 约 0.8；板端少检可以通过把 score threshold 降到 0.01 恢复。

这只能说明目标候选仍存在、板端分数或输出链路发生了变化，不能把“阈值降下来”当成最终修复。完整结论还需要同一评测集上的 ONNX/OM 成对指标、FP16/INT8 对比和原始输出对齐。

## 实验事实

| 项目 | 当前记录 |
|---|---|
| 任务 | 单类眼部/局部目标检测 |
| 模型 | YOLO11n，轻量局部目标配置 |
| 输入 | 224×224 |
| 数据 | 本人可独立支配的局部目标实验数据；图像数量和 split 待从原始记录补齐 |
| PC 模型 | ONNX |
| 板端模型 | 海思 INT8 OM |
| 芯片 | 海思 NPU；具体 SoC 型号尚未写入当前证据 |
| PC 指标 | F1 约 0.8；评测集、阈值和样本量待补 |
| 板端现象 | 默认后处理下少检一只眼；`score_thr=0.01` 后恢复 |
| 性能目标 | 板端模型执行不超过 20 ms；当前实测值待补 |

这些数据来自本人可独立支配的个人实验。当前仓库是 private；以后拆出公开项目时，仍要重新检查数据、指标、设备信息和完整 Git 历史。

## 问题

PC 端 ONNX 能检出目标，INT8 OM 板端在同类输入上出现少检。要区分：

1. 量化把分类分数压低；
2. PC 与板端的颜色、range、resize 或 normalization 不一致；
3. 输出顺序、激活、DFL/decode、坐标还原或 NMS 解释不同；
4. 校准集没有覆盖真实局部目标分布；
5. 模型本身在低分目标上就不稳定，板端差异只是把它推过阈值。

## 已做实验和能支持的判断

| 实验 | 结果 | 能支持什么 | 不能支持什么 |
|---|---|---|---|
| PC 端训练与 ONNX 评测 | F1 约 0.8，视频观察可用 | 该模型在当前 PC 评测条件下有可用性 | 不能证明板端一致，也不能外推其他数据 |
| 板端降低 score threshold 到 0.01 | 原先漏掉的眼睛恢复 | 候选结果可能仍在，优先检查分数分布和后处理 | 不能证明根因就是阈值，也不能作为最终产品阈值 |

目前还没有证据排除预处理、输出解释和 calibration set 问题。

## 下一轮区分实验

1. 保存一张图在 PC 与板端的实际模型输入，逐像素核对；
2. 同图比较 PyTorch/ONNX/OM 的原始输出，先不做阈值和 NMS；
3. 对 FP16/非量化 OM 与 INT8 OM 做同样比较；
4. 在固定评测集上同时计算 precision、recall、F1、框匹配率和分数偏移；
5. 画出正常目标与漏检目标的 ONNX/OM 分数分布；
6. 固定工具链、SoC、频率和计时范围，补齐模型执行与完整链路延迟。

## 可以复用的判断

- 板端少检先比较同图原始输出，不先猜网络结构有问题；
- 极低阈值能恢复目标，是定位线索，不是验收结果；
- 小目标量化对齐必须看分数和框的分层结果，不能只看全局相似度；
- PC F1、板端精度和板端延迟是三项独立验收，不能互相替代。

## 适用边界

当前结论只适用于这条 YOLO11n、224×224、单类局部目标、海思 INT8 OM 链路。具体 SoC、转换器/runtime 版本、数据 split、板端任务指标和实测延迟补齐前，本案例保持 `working / partial`。

相关基础页：[YOLO training](../../foundations/model-index/families/yolo/data-and-training.md)、[YOLO evaluation](../../foundations/model-index/families/yolo/evaluation.md)、[YOLO deployment](../../foundations/model-index/families/yolo/deployment.md)。
