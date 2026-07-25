# Deployment

YOLO 能导出，不等于已经形成可用的板端模型。部署时要锁定完整契约，而不是文件名。

## 导出前先锁定

- 源仓库、revision、模型与权重哈希；
- 输入 layout、dtype、shape、颜色、range、resize、padding 和 normalization；
- exporter、版本、opset、固定或动态 shape；
- 每个输出的 shape 和语义；
- decode、DFL、NMS 或一对一选择在模型内还是模型外；
- 目标 SoC、转换工具、runtime、driver 和精度；
- 校准图片清单、预处理和任务级验收 Oracle。

## 按四级结果排查

```text
原框架 → ONNX → 浮点板端模型 → INT8 板端模型
```

每一级先跑同一张图，再跑同一评测集：

1. 同一张图用于核对输入、输出张量、框、分数和类别；
2. 同一评测集用于判断差异是否会改变任务指标；
3. 只有任务级差异存在且最终输出不足以定位时，再 dump 中间层；
4. 转换器的相似度只能作为线索，不能代替检测结果验收。

## 两条个人链路

- [YOLO11n 局部目标 → ONNX → 海思 INT8 OM](../../../../engineering/cases/yolo11n-local-target-hisi-int8.md)：已有板端少检与阈值实验。降低 score threshold 后目标恢复，说明候选结果仍在，但根因仍可能是量化分数压缩、预处理或输出解释。
- [YOLO11 → ONNX → RKNN INT8 → RV1126B](../../../../engineering/cases/yolo11-rv1126b-rknn-int8-alignment.md)：厂商 Model Zoo 已覆盖该模型族和 SoC（Y025），个人实验仍要完成相同输入、逐级输出和任务级指标对齐。

两条链路的模型图、转换器、runtime、芯片和结果不同，不能共用阈值或指标。

## 板端少检先查什么

1. 保存送入 NPU 前的实际输入，核对 RGB/BGR、NV12 色域与 full/limited range、resize 和 padding；
2. 对同一张图比较 ONNX 与板端的原始输出，确认输出顺序、DFL/decode、sigmoid 和坐标还原；
3. 比较 FP16/非量化与 INT8，区分算子/输出解释问题和量化问题；
4. 画分数分布并检查 calibration set，而不是先固定一个极低阈值；
5. 最后用任务级指标决定阈值和是否接受。

相关通用诊断：[模型量化与精度对齐](../../../../engineering/diagnostics/model-quantization-accuracy-alignment.md)。它目前仍是方法草稿；真实结果以两份工程案例为准。Source ID 见 [Sources](sources.md)。
