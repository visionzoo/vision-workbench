# Deployment

YOLO 能导出，不等于已经形成可用的板端模型。部署时要锁定的是完整契约，不是文件名。

## 必须保存

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

## 导出

- 先确认输出是原始 head、已 decode 结果，还是已经包含最终选择；
- 固定/动态 shape、batch、opset、simplify 和 fuse 都可能改变图；
- 不同 YOLO 分支优先使用各自仓库的导出方式；
- 第三方转换脚本只能证明该脚本支持的版本，不能倒推成模型原作者承诺。

## 量化

- 校准集要覆盖真实输入分布，并保存图片清单和预处理；
- 至少比较原框架、导出模型和板端模型的任务级结果；
- 必要时再比较关键输出张量，不能只看转换器给出的相似度；
- DFL、decode、激活、NMS 或端到端选择放在哪里，会直接影响 NPU 支持和精度。

## 板端

- 芯片支持的是具体算子、图和 runtime 版本，不是抽象的“支持 YOLO”；
- 重点核对 resize/letterbox、RGB/BGR、NV12 色域与 full/limited range、mean/std、内存布局；
- 延迟分成模型执行和完整链路，同时记录内存、频率和连续运行条件；
- 代码、权重、数据和依赖许可分别检查。

## 本人经验与工程回链

已确认有 YOLO 训练、导出和部署的实际经验；具体模型、芯片、数据和指标只有在能提供独立材料时才进入工程记录。

现有相关条目：[模型量化与精度对齐](../../../../engineering/diagnostics/model-quantization-accuracy-alignment.md)。该条目目前仍是未验证的问题草稿，链接只表示问题相关，不表示 RKNN 流程已经完成或结论已经成立。
