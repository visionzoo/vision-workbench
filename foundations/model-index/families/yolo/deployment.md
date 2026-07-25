# Deployment

## Deployment contract

模型文件名不是部署契约。每次导出必须冻结：

```yaml
source_repository:
source_revision:
model_and_weights_hash:
task:
input_layout_dtype_shape:
color_and_range:
resize_and_padding:
normalization:
exporter_and_version:
format_and_opset:
output_names_shapes_semantics:
decode_and_nms_location:
runtime_driver_target:
precision:
calibration_dataset:
acceptance_oracle:
```

## ONNX and runtime export

- 先确认输出是原始 head、已 decode 预测，还是包含 NMS 的端到端结果。
- 固定/动态 shape、batch、opset 和 simplify/fuse 会改变可支持算子与输出图。
- Ultralytics 的 export/benchmark 文档只保证其标明的模型、包版本和格式能力；其他作者分支需用各自导出脚本。
- 第三方转换脚本属于补充证据，不能被标记成原模型“官方嵌入式支持”。

## Quantization

- PTQ 需使用覆盖真实输入分布的 calibration set，并保存采样清单与预处理。
- 量化后至少比较输入、关键输出张量和任务级指标；单看转换器 cosine similarity 不足以验收检测结果。
- decode、sigmoid/softmax、DFL、NMS 或端到端选择算子的放置会影响 NPU 支持和精度。
- per-tensor/per-channel、对称/非对称、混合精度与排除节点必须绑定具体工具链版本。

## Embedded and NPU checks

- 芯片厂商支持的是算子、图模式和 runtime 版本，不是抽象的“支持 YOLO”。
- 核对 resize/letterbox、RGB/BGR、NV12 色域和 full/limited range、mean/std、stride 对齐及内存布局。
- 延迟至少分开模型执行与端到端链路；同时记录峰值内存、功耗/频率条件和热稳定性。
- 真实 RKNN、TensorRT、OpenVINO、CoreML、TFLite、NCNN 等记录进入 `engineering/deployment/` 或 case；此页只维护共同检查表。

## Licensing

部署前分别核查代码、权重、数据和依赖许可。不同 YOLO 分支许可不同；技术可导出不等于可在目标产品中合法分发。
