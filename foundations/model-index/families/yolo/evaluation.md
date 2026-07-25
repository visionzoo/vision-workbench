# Evaluation

模型评测分成两件事：第一方资料告诉我“这个分支大致处在什么位置”，个人复测回答“它在我的数据和硬件上是否可用”。两者不能混写。

## 少量第一方事实

下表只保留能支撑当前选型的代表项，不用于跨来源总排名。

| 模型 | 第一方报告条件 | 精度 | 规模与速度 | 能说明什么 | Source |
|---|---|---|---|---|---|
| YOLO11n | COCO val、640、检测 | mAP50-95 39.5 | 2.6M 参数、6.5B FLOPs；CPU ONNX 56.1 ms，T4 TensorRT10 1.5 ms | Ultralytics nano 闭集检测基线；速度仅适用于文档标注环境 | Y019 |
| YOLO26n | COCO val、640、检测 | 一对多 mAP50-95 40.9；默认 e2e 40.1 | 融合后 2.4M 参数、5.4B FLOPs；CPU ONNX 38.9 ms，T4 TensorRT10 1.7 ms | 默认一对一 head 更便于免 NMS 部署，但精度和输出语义与一对多 head 不同 | Y023 |
| YOLOX-s | COCO val、640、检测 | mAP50-95 40.5 | 9.0M 参数、26.8G FLOPs；V100 9.8 ms | 可作为 anchor-free、解耦头和动态匹配路线的参考 | Y008 |

这些数字是第一方报告，不是本人复测。CPU、T4 和 V100 的速度不能横向比较；YOLO26 表中的参数量和 FLOPs 是融合并移除辅助一对多 head 后的模型。

## 厂商适配事实

RKNN Model Zoo 当前列出 YOLO11n/s/m 的 FP16/INT8 示例，并把 RV1126B 列为支持平台（Y025）。这只证明厂商示例覆盖了该模型族、精度和 SoC 组合，不证明任意自训练 YOLO11 都能直接对齐，也不能把 Model Zoo 其他芯片的 FPS 当作 RV1126B 实测。

## 本人复测怎么做

先固定同一批输入、同一套预处理和同一任务级 Oracle，再逐级比较：

```text
训练框架 → ONNX → 浮点板端模型 → INT8 板端模型
```

至少保留：

- 数据集版本、样本量、类别和目标尺寸分层；
- precision、recall、F1 或 AP 的定义和阈值；
- 框匹配 IoU、类别一致率和分数偏移；
- 预处理、后处理和 NMS/一对一输出设置；
- 芯片、runtime、频率、batch、warm-up、重复次数和计时边界。

性能至少分成模型执行和完整链路。完整链路包括输入转换、内存拷贝、decode、NMS 以及必要的视频处理。

## 当前个人结果

- [海思 INT8 局部目标案例](../../../../engineering/cases/yolo11n-local-target-hisi-int8.md)：PC 端 F1 约 0.8；板端存在阈值敏感的少检现象。尚缺同一评测集上的 ONNX/OM 成对指标和完整延迟记录。
- [RV1126B RKNN INT8 案例](../../../../engineering/cases/yolo11-rv1126b-rknn-int8-alignment.md)：实验链路已确定，最终精度和性能指标尚未形成，不能借用厂商 benchmark 或另一个芯片案例补齐。

任何指标都要能回到工程案例；缺少模型、数据、输入、阈值、硬件或 runtime 的孤立数字不进入这里。Source ID 见 [Sources](sources.md)。
