# Sources

访问日期：2026-07-25。以下优先列论文作者、发布组织仓库和正式文档；来源权威性只覆盖对应分支。

## Original YOLO and Darknet

- YOLOv1 paper: https://arxiv.org/abs/1506.02640
- YOLO9000 / YOLOv2 paper: https://arxiv.org/abs/1612.08242
- YOLOv3 report: https://arxiv.org/abs/1804.02767
- Joseph Redmon Darknet and YOLO pages: https://pjreddie.com/darknet/ and https://pjreddie.com/darknet/yolo/

## Darknet and WongKinYiu research branches

- YOLOv4 paper: https://arxiv.org/abs/2004.10934
- YOLOv4 implementation / maintained Darknet fork: https://github.com/AlexeyAB/darknet
- Scaled-YOLOv4 paper: https://arxiv.org/abs/2011.08036
- Scaled-YOLOv4 repository: https://github.com/WongKinYiu/ScaledYOLOv4
- YOLOR paper: https://arxiv.org/abs/2105.04206
- YOLOR repository: https://github.com/WongKinYiu/yolor
- YOLOv7 paper: https://arxiv.org/abs/2207.02696
- YOLOv7 author repository: https://github.com/WongKinYiu/yolov7
- YOLOv9 paper: https://arxiv.org/abs/2402.13616
- YOLOv9 author repository: https://github.com/WongKinYiu/yolov9

## Ultralytics branches

- YOLOv5 repository: https://github.com/ultralytics/yolov5
- Ultralytics main repository: https://github.com/ultralytics/ultralytics
- YOLOv8 documentation: https://docs.ultralytics.com/models/yolov8/
- YOLO11 documentation: https://docs.ultralytics.com/models/yolo11/
- YOLO26 documentation: https://docs.ultralytics.com/models/yolo26/
- YOLO26 technical report: https://arxiv.org/abs/2606.03748
- YOLOE documentation, including YOLOE-26: https://docs.ultralytics.com/models/yoloe/
- Export documentation: https://docs.ultralytics.com/modes/export/
- Benchmark documentation: https://docs.ultralytics.com/modes/benchmark/

## Industrial and research branches

- YOLOX paper: https://arxiv.org/abs/2107.08430
- YOLOX official repository: https://github.com/Megvii-BaseDetection/YOLOX
- PP-YOLO paper: https://arxiv.org/abs/2007.12099
- PP-YOLOv2 paper: https://arxiv.org/abs/2104.10419
- PP-YOLOE paper: https://arxiv.org/abs/2203.16250
- PaddleDetection repository/configs: https://github.com/PaddlePaddle/PaddleDetection
- YOLOv6 paper: https://arxiv.org/abs/2209.02976
- YOLOv6 official repository: https://github.com/meituan/YOLOv6
- DAMO-YOLO paper: https://arxiv.org/abs/2211.15444
- DAMO-YOLO repository: https://github.com/tinyvision/DAMO-YOLO
- YOLO-NAS home in SuperGradients: https://github.com/Deci-AI/super-gradients/blob/master/YOLONAS.md
- Gold-YOLO paper: https://arxiv.org/abs/2309.11331
- Gold-YOLO author repository: https://github.com/huawei-noah/Efficient-Computing/tree/master/Detection/Gold-YOLO
- YOLOv10 paper: https://arxiv.org/abs/2405.14458
- YOLOv10 author repository: https://github.com/THU-MIG/yolov10
- YOLOv12 paper: https://arxiv.org/abs/2502.12524
- YOLOv12 author repository: https://github.com/sunsmarterjie/yolov12
- YOLOv13 paper: https://arxiv.org/abs/2506.17733
- YOLOv13 author repository: https://github.com/iMoonLab/yolov13

## Open-vocabulary branches

- YOLO-World paper: https://arxiv.org/abs/2401.17270
- YOLO-World author repository: https://github.com/AILab-CVC/YOLO-World
- YOLOE paper: https://arxiv.org/abs/2503.07465
- YOLOE author repository: https://github.com/THU-MIG/yoloe

## Ecosystem implementations and ports

- MMYOLO repository: https://github.com/open-mmlab/mmyolo
- MMYOLO documentation: https://mmyolo.readthedocs.io/
- Ultralytics YOLO-World documentation: https://docs.ultralytics.com/models/yolo-world/
- Ultralytics source note that YOLO-World weights were migrated from AILab-CVC: https://github.com/ultralytics/ultralytics/blob/main/docs/en/models/yolo-world.md
- Rockchip RKNN Model Zoo: https://github.com/airockchip/rknn_model_zoo
- YOLOv5-Lite community project: https://github.com/ppogg/YOLOv5-Lite

## Source-use rules

- 论文用于论文中明确陈述的结构、训练与报告指标；
- 作者/维护组织仓库用于实现、配置、权重、release 和许可；
- “模型原作者正式实现”“第三方框架正式集成”“芯片厂商正式移植”是三种不同身份，禁止合并成一个“官方”；
- 当前在线文档会变化，复现必须另外记录 package/tag/commit；
- issue、讨论、第三方移植只能作为补充工程证据；
- 引用第一方来源不等于已完成独立复现。
