# Model-family comparison axes

跨模型比较必须至少绑定以下维度，缺失项写 `not disclosed` 或 `not measured`：

| Dimension | Required context |
|---|---|
| Identity | model, variant, task head, weights, source revision |
| Architecture | backbone, neck/encoder, head, assignment, post-processing |
| Training | initialization, disclosed data, schedule, augmentation, resolution |
| Quality | dataset version, split, metric definition, evaluator |
| Complexity | parameters, FLOPs/MACs definition, input shape |
| Latency | hardware, precision, batch, runtime, warm-up, timing boundary |
| Memory | peak/runtime definition, batch, input, runtime |
| Export | exporter version, format, opset, dynamic/static shape |
| Quantization | PTQ/QAT, calibration data, granularity, accuracy delta |
| License | code, weights and data terms checked separately |
| Evidence | official report, third-party reproduction, or first-party experiment |

不同论文表格中的 AP、FPS 或 FLOPs 不因列名相同就可直接排序。只有评价协议和计时边界足够接近时才形成比较结论。
