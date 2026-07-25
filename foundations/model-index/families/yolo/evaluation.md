# Evaluation

## Official result is not independent verification

论文、作者仓库或维护组织文档中的结果统一标记为 `first-party reported`。本条目尚未运行统一环境复测，因此不提供跨分支的“最好”排序。

## Required tuple

任何 AP、FPS、延迟、参数量或计算量必须绑定：

```text
model + weights + task + dataset/version/split + evaluator
+ input shape + precision + batch + hardware + runtime
+ warm-up/repeats + timing boundary + source revision
```

开放词汇模型还必须记录：

```text
prompt mode + vocabulary/class set + text encoder or cached embeddings
+ zero-shot/fine-tuned setting + pretraining-data disclosure
```

缺少关键条件的数字可以作为线索，但不能进入正式比较表。

## Detection quality

- COCO 常用 `AP@[.50:.95]`，同时可能报告 AP50、AP75 和按目标尺寸分组的 AP；不得把 AP50 与 AP@[.50:.95] 混排。
- VOC 不同年份和 evaluator 的 AP 定义可能不同；必须保留数据集年份和评价实现。
- YOLO-World/YOLOE 常涉及 LVIS、zero-shot、prompted 或开放词汇评价，不能与闭集 COCO AP 直接排名。
- 多任务版本的 detection、segmentation、pose、OBB 指标不能互相替代。
- 同名权重在不同代码版本、输入尺寸、TTA、词汇设置或 NMS 设置下可能产生不同结果。

## Runtime

- 论文中的 GPU latency、第一方导出 benchmark、端到端应用 FPS 是三种不同测量。
- 预处理、文本编码/词汇缓存、H2D/D2H、decode、NMS、跟踪和视频解码是否计时必须明确。
- batch=1 的实时延迟与批处理吞吐量不能互相替代。
- 硬件峰值算力不能推导真实延迟；算子支持、内存访问和图优化会改变结果。

## First-party tables

指标不复制为易过期的聚合排名，直接引用对应来源：

- 原始 YOLOv1–v3：论文和 Darknet YOLO 页面；
- 其他可归属正式分支：各自论文、作者/维护组织仓库和版本化模型文档；
- Ultralytics YOLO11/YOLO26：对应文档的性能表及其测试条件；
- YOLO-World/YOLOE：对应作者仓库中按数据集、prompt 模式和训练设置区分的表；
- 导出格式基准：对应 exporter/runtime 的文档，但结果只适用于其标注环境；
- 生态复现或芯片移植：只能标为该生态实现报告结果，不能改写为模型原作者结果。

入口集中在 [sources.md](sources.md)。将来形成统一复测后，应另建 `engineering/cases/` 记录环境和原始结果，再在此链接摘要。
