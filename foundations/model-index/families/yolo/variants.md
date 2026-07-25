# Variants and lineage

## Authority map

| Name/branch | Primary authority | Relationship note |
|---|---|---|
| YOLOv1 | Redmon et al. paper | 原始统一实时检测框架 |
| YOLOv2 / YOLO9000 | Redmon & Farhadi paper, Darknet | 原始作者延续 |
| YOLOv3 | Redmon & Farhadi report, Darknet | 原始作者最后主要版本 |
| YOLOv4 | Bochkovskiy, Wang, Liao paper; AlexeyAB/darknet | Darknet 分支，不由原始作者维护 |
| YOLOv5 | Ultralytics/yolov5 | Ultralytics 产品/开源分支，无同名学术论文作为唯一规范 |
| YOLOX | Megvii-BaseDetection/YOLOX | 独立 anchor-free 分支 |
| YOLOv6 | Meituan/YOLOv6 | 面向工业应用的独立分支 |
| YOLOv7 | WongKinYiu/yolov7 and paper | 独立研究分支 |
| YOLOv8 | Ultralytics docs/source | Ultralytics 分支 |
| YOLOv9 | WongKinYiu/yolov9 and paper | PGI/GELAN 分支 |
| YOLOv10 | THU-MIG/yolov10 and paper | 端到端 NMS-free 分支 |
| YOLO11 | Ultralytics docs/source | Ultralytics 分支；命名不使用 v |
| YOLO26 | Ultralytics docs/technical report/source | Ultralytics 端到端部署导向分支 |

这张表说明“去哪里找权威定义”，不暗示每一行都是上一行的直接继承。

## Scale variants

`n/s/m/l/x` 等后缀通常表示同一实现内部的规模配置，但不同分支的深度、宽度、参数量和算子并不等价。比较时必须写完整模型名、任务后缀和 source revision。

## Inclusion gate

新增一个 YOLO 命名分支至少满足：

1. 作者或维护组织可识别；
2. 有原始论文、技术报告、官方仓库或正式模型卡；
3. 相对现有分支存在可说明的机制、训练或部署差异；
4. 许可和维护状态可定位；
5. 不仅因为营销名称或第三方包支持而收录。

社区模型可进入候选清单，但在来源归属未核验前不进入 authority map。
