# Ecosystem implementations and adaptations

这里记录非原作者实现但确实有工程价值的复现、迁移和芯片适配。它们可以帮助训练和部署，但不能反过来定义原模型。

## 当前值得保留的实现

| 项目 | 它是什么 | 实际价值 | 使用边界 |
|---|---|---|---|
| OpenMMLab MMYOLO | 第三方统一复现/工具箱 | 在 MMDetection 体系中实现 YOLOv5、YOLOv6、YOLOv7、YOLOv8、YOLOX、PP-YOLOE 等，便于统一配置、训练和部署 | 不能把 MMYOLO 的指标、默认超参或导出图写成原模型行为 |
| Ultralytics YOLO-World integration | 第三方框架迁移 | 把 AILab-CVC YOLO-World 权重迁移到 Ultralytics 接口 | 文档明确权重来自迁移；层数、参数和表现可能不同，必须标注实现身份 |
| Ultralytics integrations of external YOLO branches | 第三方框架集成 | 为 YOLOv9、YOLOv10、YOLOv12、YOLOE 等提供统一训练、推理或导出入口 | 支持程度随 package 版本变化；模型身份仍归原作者 |
| Rockchip RKNN Model Zoo YOLO ports | 芯片厂商部署适配 | 提供 YOLOv5/6/7/8/10、YOLO11、YOLOX、PP-YOLOE、YOLO-World 等转换及 C/Python 示例 | 支持 SoC、Toolkit/runtime、量化配置和后处理必须绑定版本；不是原模型定义 |
| YOLOv5-Lite | 社区轻量化改造 | 以更轻结构和部署友好修改面向 Raspberry Pi、NCNN、MNN、TNN、ONNX Runtime 等 | 社区项目；速度与量化结论只适用于给定模型、输入、设备和后端 |

## 什么时候值得加入

新增条目至少要说清：

1. 上游模型和基准 revision；
2. 改造解决的实际问题；
3. 可运行代码、权重、转换脚本或可复核实验；
4. 许可、维护状态、硬件条件和已知偏差。

只有结构图、博客摘录、单次演示或无法对应源码的 mAP/FPS，不加入。

## 采用前怎么核对

```text
上游 revision 和权重
→ 预处理与输出语义
→ 结构或算子差异
→ 原框架结果
→ 导出模型结果
→ 目标硬件精度与延迟
```

迁移权重不能只因文件名相近就视为与上游权重等价。Source ID 见 [Sources](sources.md)。
