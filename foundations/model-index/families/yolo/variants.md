# Variants and lineage

## Identity rule

YOLO 没有覆盖全部版本的单一“总官方”。本页分别记录原始作者谱系与其他可归属的正式分支；“正式”只说明能定位到该模型的论文作者或维护组织，不授予其对整个 YOLO 名称的排他权。

## Original-author lineage

| Name/branch | Primary authority | Relationship note |
|---|---|---|
| YOLOv1 | Redmon et al. paper | 原始统一实时检测框架 |
| YOLOv2 / YOLO9000 | Redmon & Farhadi paper, Darknet | 原始作者延续 |
| YOLOv3 | Redmon & Farhadi report, Darknet | 原始作者最后一个主要版本 |

## Officially attributable branches

| Name/branch | Primary authority | Relationship note |
|---|---|---|
| YOLOv4 | Bochkovskiy, Wang, Liao paper; AlexeyAB/darknet | Darknet 分支，不由原始作者维护 |
| Scaled-YOLOv4 | Wang, Bochkovskiy, Liao paper; WongKinYiu repository | YOLOv4 的缩放研究分支 |
| YOLOR | WongKinYiu paper/repository | 显式/隐式表示研究分支 |
| YOLOv5 | Ultralytics/yolov5 | Ultralytics 正式产品/开源分支，无同名论文作为唯一规范 |
| YOLOX | Megvii-BaseDetection/YOLOX | 独立 anchor-free 分支 |
| PP-YOLO / PP-YOLOv2 | PaddlePaddle papers; PaddleDetection | Paddle 官方分支 |
| PP-YOLOE / PP-YOLOE+ | PaddlePaddle papers; PaddleDetection | Paddle anchor-free 工业分支 |
| YOLOv6 | Meituan/YOLOv6 | 面向工业应用的独立分支 |
| YOLOv7 | WongKinYiu/yolov7 and paper | 独立研究分支 |
| YOLOv8 | Ultralytics docs/source | Ultralytics 分支 |
| DAMO-YOLO | Alibaba DAMO/TinyML paper and repository | 独立工业研究分支 |
| YOLO-NAS | Deci-AI/super-gradients | NAS 与量化导向分支 |
| Gold-YOLO | Huawei Noah paper/repository | 特征融合研究分支 |
| YOLOv9 | WongKinYiu/yolov9 and paper | PGI/GELAN 分支 |
| YOLOv10 | THU-MIG/yolov10 and paper | 端到端 NMS-free 分支 |
| YOLO-World | AILab-CVC/YOLO-World and paper | 开放词汇、视觉—语言分支 |
| YOLO11 | Ultralytics docs/source | Ultralytics 分支；正式名称不使用 `v` |
| YOLOv12 | sunsmarterjie/yolov12 and paper | attention-centric 独立研究分支；Ultralytics 标为 community model |
| YOLOE | THU-MIG/yoloe and paper | 多提示开放词汇检测/分割分支 |
| YOLOv13 | iMoonLab/yolov13 and paper | 超图增强独立研究分支 |
| YOLO26 / YOLOE-26 | Ultralytics docs/technical report/source | Ultralytics 端到端、多任务及开放词汇分支；正式名称不使用 `v` |

这张表说明“去哪里找该分支的第一方定义”，不暗示每一行都是上一行的直接继承，也不表示表中模型已被本人复现。

## Ecosystem relationship

MMYOLO、Ultralytics 的外部分支集成、RKNN Model Zoo 等属于实现或部署生态，不放入上面的模型原始 authority map。它们的价值、差异和适用边界见 [Ecosystem implementations](ecosystem-implementations.md)。

## Scale variants

`n/s/m/l/x` 等后缀通常表示同一实现内部的规模配置，但不同分支的深度、宽度、参数量和算子并不等价。比较时必须写完整模型名、任务后缀、权重来源和 source revision。

## Inclusion gate

新增一个可归属正式分支至少满足：

1. 作者或维护组织可识别；
2. 有原始论文、技术报告、正式仓库或模型卡；
3. 相对现有分支存在可说明的机制、训练、任务或部署差异；
4. 许可和维护状态可定位；
5. 不仅因为营销名称或第三方包支持而收录。

非原始实现必须进入生态实现清单，并额外说明上游模型、改造内容、权重来源、可复现证据和与原始指标不可直接互换的边界。
