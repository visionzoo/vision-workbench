# Engineering

工程内容必须从可迁移的问题出发，保留诊断链路和验证方法，不记录“改了某参数就好了”的孤立经验。

- `cases/`：具体案例的观察—假设—实验—结论；
- `diagnostics/`：精度、性能、数据和部署差异的系统诊断；
- `deployment/`：ONNX、NPU、量化、C/C++ 集成等通用部署知识；
- `playbooks/`：可重复执行、有输入输出和人工确认点的流程。

当前入口：

- [YOLO11n 局部目标到海思 INT8：候选记录](cases/yolo11n-local-target-hisi-int8.md)
- [YOLO11 到 RV1126B RKNN INT8 对齐：候选记录](cases/yolo11-rv1126b-rknn-int8-alignment.md)
- [Model quantization and accuracy alignment](diagnostics/model-quantization-accuracy-alignment.md)
- [Vision algorithm release and delivery](playbooks/vision-algorithm-release-and-delivery.md)
