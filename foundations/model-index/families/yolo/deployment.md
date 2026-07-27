# Deployment

YOLO 能导出，不等于形成了可用的板端模型。部署对象是一条带版本的数值与语义链，不是一个文件名。

## 1. 导出前锁定完整契约

- 源仓库、revision、配置、scale、模型与权重哈希；
- 输入 layout、dtype、shape、颜色、range、resize、padding 和 normalization；
- exporter、版本、opset、固定或动态 shape；
- 每个输出的 shape、顺序、stride 和语义；
- DFL、decode、sigmoid、NMS 或 one-to-one 选择位于模型内还是模型外；
- 目标 SoC、转换工具、runtime、driver 和精度；
- 校准图片清单、预处理和任务级验收 Oracle。

固定 YOLO11 实现的训练输出是 P3/P4/P5 raw tensors，常规推理路径还会执行 DFL、框解码和分类 sigmoid（Y019）。exporter 可以改变图的边界，因此不能仅从模型名称推断输出。

## 2. 按语义阶段对齐

```text
source preprocessing
→ source raw P3/P4/P5
→ source decode / result selection
→ ONNX 对应阶段
→ 浮点板端对应阶段
→ INT8 板端对应阶段
```

同一张图先检查接口与中间语义，同一评测集再判断差异是否影响任务：

1. 保存实际输入 tensor，排除颜色、range、resize、padding、layout 和 dtype 差异；
2. 建立输出节点表，确认比较的是相同语义、shape、尺度和顺序；
3. 从输入向后找到首个显著分歧边界，再检查相邻模块；
4. 最终以 decode 后框、分数、类别和任务指标决定是否接受。

张量相似度用于定位，不是最终 Oracle。不同 shape、不同 decode 阶段或不同尺度的张量即使数值接近也没有直接可比性。

## 3. 板端少检的竞争解释

| 现象 | 仍需保留的解释 | 区分动作 |
|---|---|---|
| 降低 score threshold 后目标恢复 | 分类分数压缩、预处理偏差、sigmoid/输出解释差异、校准失配 | 比较 raw logits、score 分布和浮点/INT8 |
| 框整体平移或缩放 | resize/padding 逆变换、坐标格式、stride/decode 错误 | 固定输入，逐步核对输入坐标到输出坐标 |
| 只在小目标上退化 | 输入像素、P3 特征、DFL 分布、量化动态范围 | 按目标尺寸分层并比较 P3 与回归输出 |
| 重复框或类别异常 | 输出拼接顺序、sigmoid、NMS/one-to-one 语义 | 核对三个尺度与后处理契约 |
| 某层后突然分歧 | 算子实现、融合、padding、量化参数或张量布局 | 在首个分歧边界两侧做局部下钻 |

这张表是诊断入口，不是根因判定。网络层证据如何命名、捕获和比较，将在独立诊断工作包中建立；本页不提前写入未执行结果。

## 4. 两条个人链路

- [YOLO11n 局部目标 → ONNX → 海思 INT8 OM](../../../../engineering/cases/yolo11n-local-target-hisi-int8.md)：已有板端少检与阈值观察。当前只能说明候选在较低阈值下仍出现，不能排除量化、预处理和输出解释。
- [YOLO11 → ONNX → RKNN INT8 → RV1126B](../../../../engineering/cases/yolo11-rv1126b-rknn-int8-alignment.md)：厂商示例覆盖该模型族与 SoC（Y025），个人实验仍需完成同输入、逐级输出和任务指标对齐。

两条链路的模型图、转换器、runtime、芯片和结果不同，不共用阈值、指标或中间节点结论。通用入口见[模型量化与精度对齐](../../../../engineering/diagnostics/model-quantization-accuracy-alignment.md)；真实结果只进入对应工程案例。
