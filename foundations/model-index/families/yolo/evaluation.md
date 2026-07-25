# Evaluation

## Official result is not independent verification

论文、官方仓库或模型文档中的结果统一标记为 `official reported`。本条目尚未运行统一环境复测，因此不提供跨分支的“最好”排序。

## Required tuple

任何 AP、FPS、延迟、参数量或计算量必须绑定：

```text
model + weights + task + dataset/version/split + evaluator
+ input shape + precision + batch + hardware + runtime
+ warm-up/repeats + timing boundary + source revision
```

缺少关键条件的数字可以作为线索，但不能进入正式比较表。

## Detection quality

- COCO 常用 `AP@[.50:.95]`，同时可能报告 AP50、AP75 和按目标尺寸分组的 AP；不得把 AP50 与 AP@[.50:.95] 混排。
- VOC 不同年份和 evaluator 的 AP 定义可能不同；必须保留数据集年份和评价实现。
- 多任务版本的 detection、segmentation、pose、OBB 指标不能互相替代。
- 同名权重在不同代码版本、输入尺寸、TTA 或 NMS 设置下可能产生不同结果。

## Runtime

- 论文中的 GPU latency、官方导出 benchmark、端到端应用 FPS 是三种不同测量。
- 预处理、H2D/D2H、decode、NMS、跟踪和视频解码是否计时必须明确。
- batch=1 的实时延迟与批处理吞吐量不能互相替代。
- 硬件峰值算力不能推导真实延迟；算子支持、内存访问和图优化会改变结果。

## Official tables

指标不复制为易过期的聚合表，直接引用对应作者页面：

- 原始 YOLOv1–v3：论文和 Darknet YOLO 页面；
- YOLOv4、YOLOX、YOLOv6、YOLOv7、YOLOv9、YOLOv10：作者论文和仓库 README；
- Ultralytics YOLO11/YOLO26：各模型官方文档的性能表；
- 导出格式基准：Ultralytics Benchmark 文档，但结果只适用于其标注的环境。

入口集中在 [sources.md](sources.md)。将来形成统一复测后，应另建 `engineering/cases/` 记录环境和原始结果，再在此链接摘要。
