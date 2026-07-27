# Evaluation

模型评测分成两层：第一方资料说明某个实现公开报告了什么，个人复测回答它在目标数据、软件栈和硬件上是否可用。两者不能混写。

## 1. 少量第一方事实

下表只保留能支撑当前选型的代表项，不用于跨来源总排名。

| 模型 | 第一方报告条件 | 精度 | 规模与速度 | 能支持什么 | 不能支持什么 | Source |
|---|---|---|---|---|---|---|
| YOLO11n | COCO val、640、检测 | mAP50-95 39.5 | 2.6M 参数、6.5B FLOPs；CPU ONNX 56.1 ms，T4 TensorRT10 1.5 ms | Ultralytics nano 闭集检测的公开基线 | 自有数据、NPU 或其他 runtime 的精度与速度 | Y019 |
| YOLO26n | COCO val、640、检测 | 一对多 40.9；默认 e2e 40.1 | 融合后 2.4M 参数、5.4B FLOPs；CPU ONNX 38.9 ms，T4 TensorRT10 1.7 ms | 同一分支两种 head 的公开口径及默认 e2e 路线 | one-to-one 与 one-to-many 可不加说明地横向替换 | Y023 |
| YOLOX-s | COCO val、640、检测 | mAP50-95 40.5 | 9.0M 参数、26.8G FLOPs；V100 9.8 ms | anchor-free、解耦 head、动态匹配路线的代表基线 | 与 CPU、T4 或目标板速度直接比较 | Y008 |

CPU、T4 和 V100 的速度没有共同计时契约，不能横向排名。YOLO26 表中的参数量和 FLOPs 是融合并移除辅助一对多 head 后的模型。

RKNN Model Zoo 列出 YOLO11n/s/m 的 FP16/INT8 示例，并把 RV1126B 列为支持平台（Y025）。这只证明厂商示例覆盖该模型族、精度和 SoC 组合，不证明任意自训练权重已经对齐，也不能把其他芯片 FPS 当成 RV1126B 实测。

## 2. 个人评测的最小契约

先固定同一批输入、同一套预处理、同一输出解释和同一任务级 Oracle，再逐级比较：

```text
训练框架 → ONNX → 浮点板端模型 → INT8 板端模型
```

至少记录：

- 数据集 revision、样本量、类别、场景和目标尺寸分层；
- 框匹配策略、IoU、score、NMS 及 ignored region 规则；
- precision、recall、F1、AP 的计算实现与 operating point；
- 输入预处理、输出 tensor、decode 和坐标还原；
- 芯片、runtime、频率、batch、warm-up、重复次数和计时边界。

性能分为模型执行和端到端链路。后者包含输入转换、内存拷贝、decode、结果选择及必要的视频处理。

## 3. 平均指标之外必须看什么

| 切片 | 主要区分的解释 |
|---|---|
| 目标像素与 P3/P4/P5 尺度 | 小目标是否因输入或下采样失去信息 |
| 遮挡、模糊、边界、密集重叠 | 数据难例、标签规则与结果选择问题 |
| 类别、场景、光照、设备域 | 长尾、域偏移和预训练失配 |
| score / IoU 曲线 | 阈值问题还是候选本身消失 |
| FP / FN 样例簇 | 背景混淆、漏标、框偏或类别混淆 |
| 运行阶段 | 框架、ONNX、浮点板端和 INT8 首次出现差异的位置 |

多尺度特征不自动解决低有效像素，COCO/LVIS 指标也不能预测 IR、车载、工业或自定义类别表现。NMS-based 与 one-to-one 输出的 score 和结果选择语义不同，比较前先统一任务级输出。

## 4. 当前个人结果

- [海思 INT8 局部目标案例](../../../../engineering/cases/yolo11n-local-target-hisi-int8.md)：PC 端 F1 约 0.8；板端存在阈值敏感的少检现象。尚缺同一评测集上的 ONNX/OM 成对指标和完整延迟记录。
- [RV1126B RKNN INT8 案例](../../../../engineering/cases/yolo11-rv1126b-rknn-int8-alignment.md)：实验链路已确定，最终精度和性能指标尚未形成，不能借用厂商 benchmark 或另一个芯片案例补齐。

任何指标都要能回到工程案例。缺少模型、数据、输入、阈值、硬件或 runtime 的孤立数字不进入这里。
