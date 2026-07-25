# Ecosystem implementations and adaptations

本页收录非模型原作者实现但具有明确工程价值的复现、迁移和定向改造。它们不进入模型原始 authority map；“值得跟踪”只表示来源清楚、改造目的明确且存在可检查产物，不代表已经由本人验证全部指标。

## High-value ecosystem implementations

| Project | Identity | What it adds | Boundary |
|---|---|---|---|
| OpenMMLab MMYOLO | 第三方统一复现/工具箱 | 在 MMDetection 体系中实现和对齐 YOLOv5、YOLOv6、YOLOv7、YOLOv8、YOLOX、PP-YOLOE 等，提供配置、权重转换、训练与部署入口 | 不能把 MMYOLO 指标、默认超参或导出图写成各模型原始官方行为 |
| Ultralytics YOLO-World integration | 第三方框架迁移 | 将 AILab-CVC YOLO-World 权重迁移到 Ultralytics 接口，降低推理与部署使用门槛 | 官方文档明确权重来自原始仓库迁移；层数、参数和表现可能不同，必须标注为 Ultralytics 实现 |
| Ultralytics integrations of external YOLO branches | 第三方框架集成 | 为 YOLOv9、YOLOv10、YOLOv12、YOLOE 等提供统一 API、训练/推理或导出能力 | 支持程度随版本变化；模型身份仍归原作者，需同时记录 Ultralytics package revision |
| Rockchip RKNN Model Zoo YOLO ports | 芯片厂商部署适配 | 提供 YOLOv5/6/7/8/10、YOLO11、YOLOX、PP-YOLOE、YOLO-World 等 RKNN 转换及 Python/C API 示例 | 是部署参考，不是模型结构官方定义；支持 SoC、toolkit/runtime、量化配置和后处理必须绑定版本 |
| YOLOv5-Lite | 社区轻量化结构改造 | 以更轻 backbone/head、移除 Focus slicing 等方式面向 Raspberry Pi、NCNN、MNN、TNN、ONNX Runtime 等部署 | 社区项目；其速度与量化结论只适用于给定模型、输入、设备和后端，不能替代 YOLOv5 官方基线 |

## Admission criteria

后续新增非官方改造至少满足以下四项：

1. 明确写出上游模型和基准 revision；
2. 改造目标不是简单改名，且结构、任务、部署或复现价值可说明；
3. 有可运行代码、公开权重/转换脚本或可复核实验；
4. 能明确许可、维护状态、硬件/框架条件和已知偏差。

仅有结构图、博客摘录、单次演示、无法对应源码的 mAP/FPS，或以“官方”自称但无法对应论文作者/发布组织的仓库，不进入本清单。

## Verification before adoption

采用生态实现前至少比较：

```text
upstream revision and weights
→ preprocessing and output semantics
→ parameter/operator differences
→ native-framework parity
→ exported-model parity
→ target-hardware accuracy and latency
```

任何迁移权重都不能仅因文件名相近就视为与上游权重等价。
