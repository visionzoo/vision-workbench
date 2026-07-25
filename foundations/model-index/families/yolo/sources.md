# Sources

访问日期：2026-07-25。Source ID 用于让其他页面的具体判断能回到原始资料。第一方只对对应分支负责，不存在覆盖全部 YOLO 的统一官方。

| ID | 分支/用途 | 第一方资料 |
|---|---|---|
| Y001 | YOLOv1 | [paper](https://arxiv.org/abs/1506.02640) |
| Y002 | YOLOv2 / YOLO9000 | [paper](https://arxiv.org/abs/1612.08242) |
| Y003 | YOLOv3 | [report](https://arxiv.org/abs/1804.02767), [Darknet YOLO](https://pjreddie.com/darknet/yolo/) |
| Y004 | YOLOv4 | [paper](https://arxiv.org/abs/2004.10934), [repository](https://github.com/AlexeyAB/darknet) |
| Y005 | Scaled-YOLOv4 | [paper](https://arxiv.org/abs/2011.08036), [repository](https://github.com/WongKinYiu/ScaledYOLOv4) |
| Y006 | YOLOR | [paper](https://arxiv.org/abs/2105.04206), [repository](https://github.com/WongKinYiu/yolor) |
| Y007 | YOLOv5 | [repository](https://github.com/ultralytics/yolov5) |
| Y008 | YOLOX | [paper](https://arxiv.org/abs/2107.08430), [repository](https://github.com/Megvii-BaseDetection/YOLOX) |
| Y009 | PP-YOLO 系列 | [PaddleDetection](https://github.com/PaddlePaddle/PaddleDetection), [PP-YOLO](https://arxiv.org/abs/2007.12099), [PP-YOLOv2](https://arxiv.org/abs/2104.10419), [PP-YOLOE](https://arxiv.org/abs/2203.16250) |
| Y010 | YOLOv6 | [paper](https://arxiv.org/abs/2209.02976), [repository](https://github.com/meituan/YOLOv6) |
| Y011 | YOLOv7 | [paper](https://arxiv.org/abs/2207.02696), [repository](https://github.com/WongKinYiu/yolov7) |
| Y012 | YOLOv8 | [documentation](https://docs.ultralytics.com/models/yolov8/), [repository](https://github.com/ultralytics/ultralytics) |
| Y013 | DAMO-YOLO | [paper](https://arxiv.org/abs/2211.15444), [repository](https://github.com/tinyvision/DAMO-YOLO) |
| Y014 | YOLO-NAS | [SuperGradients model page](https://github.com/Deci-AI/super-gradients/blob/master/YOLONAS.md) |
| Y015 | Gold-YOLO | [paper](https://arxiv.org/abs/2309.11331), [repository](https://github.com/huawei-noah/Efficient-Computing/tree/master/Detection/Gold-YOLO) |
| Y016 | YOLOv9 | [paper](https://arxiv.org/abs/2402.13616), [repository](https://github.com/WongKinYiu/yolov9) |
| Y017 | YOLOv10 | [paper](https://arxiv.org/abs/2405.14458), [repository](https://github.com/THU-MIG/yolov10) |
| Y018 | YOLO-World | [paper](https://arxiv.org/abs/2401.17270), [repository](https://github.com/AILab-CVC/YOLO-World) |
| Y019 | YOLO11 | [documentation](https://docs.ultralytics.com/models/yolo11/), [repository](https://github.com/ultralytics/ultralytics) |
| Y020 | YOLOv12 | [paper](https://arxiv.org/abs/2502.12524), [repository](https://github.com/sunsmarterjie/yolov12) |
| Y021 | YOLOE | [paper](https://arxiv.org/abs/2503.07465), [repository](https://github.com/THU-MIG/yoloe) |
| Y022 | YOLOv13 | [paper](https://arxiv.org/abs/2506.17733), [repository](https://github.com/iMoonLab/yolov13) |
| Y023 | YOLO26 / YOLOE-26 | [YOLO26 documentation](https://docs.ultralytics.com/models/yolo26/), [technical report](https://arxiv.org/abs/2606.03748), [YOLOE documentation](https://docs.ultralytics.com/models/yoloe/) |
| Y024 | MMYOLO | [repository](https://github.com/open-mmlab/mmyolo), [documentation](https://mmyolo.readthedocs.io/) |
| Y025 | RKNN Model Zoo | [repository](https://github.com/airockchip/rknn_model_zoo) |
| Y026 | YOLOv5-Lite | [repository](https://github.com/ppogg/YOLOv5-Lite) |
| Y027 | Ultralytics export | [export documentation](https://docs.ultralytics.com/modes/export/), [benchmark documentation](https://docs.ultralytics.com/modes/benchmark/) |

## 使用规则

- Source ID 建立后不重新编号；来源失效时保留 ID，并标明替代链接或失效原因；
- 论文用于论文明确写出的结构、训练和指标；
- 仓库用于实现、配置、权重、release 和许可；
- 在线文档会变化，复现时另外记录 package、tag 或 commit；
- 第三方移植只能证明移植本身，不能替代模型原作者定义；
- 引用第一方资料不等于本人已经复现。
