# Variants and lineage

YOLO 没有覆盖全部版本的单一“总官方”。这里的“正式分支”只表示能找到对应作者、维护组织及其第一方资料，不表示它是原始作者的顺序续作。

本页是版本归属的唯一维护位置。其他页面只在确实需要解释机制时引用分支，不再复制完整名单。

## 原始作者版本

| 分支 | 第一方来源 | 关系 |
|---|---|---|
| YOLOv1 | Y001 | 原始模型 |
| YOLOv2 / YOLO9000 | Y002 | 原作者延续 |
| YOLOv3 | Y003 | 原作者最后一个主要版本 |

## 其他正式分支

| 分支 | 第一方来源 | 关系 |
|---|---|---|
| YOLOv4 | Y004 | Darknet 分支，不由原始作者维护 |
| Scaled-YOLOv4 | Y005 | YOLOv4 的缩放研究 |
| YOLOR | Y006 | 显式/隐式表示研究 |
| YOLOv5 | Y007 | Ultralytics 工程分支，无同名论文作为唯一规范 |
| YOLOX | Y008 | Megvii anchor-free 分支 |
| PP-YOLO 系列 | Y009 | PaddleDetection 分支 |
| YOLOv6 | Y010 | 美团工业部署分支 |
| YOLOv7 | Y011 | WongKinYiu 研究分支 |
| YOLOv8 | Y012 | Ultralytics 分支 |
| DAMO-YOLO | Y013 | 阿里 DAMO/TinyML 分支 |
| YOLO-NAS | Y014 | Deci NAS 与量化导向分支 |
| Gold-YOLO | Y015 | 华为诺亚特征融合分支 |
| YOLOv9 | Y016 | PGI/GELAN 分支 |
| YOLOv10 | Y017 | THU-MIG 端到端分支 |
| YOLO-World | Y018 | AILab-CVC 开放词汇分支 |
| YOLO11 | Y019 | Ultralytics 分支，正式名称不带 `v` |
| YOLOv12 | Y020 | attention-centric 独立研究分支 |
| YOLOE | Y021 | THU-MIG 多提示开放词汇分支 |
| YOLOv13 | Y022 | iMoonLab 超图增强分支 |
| YOLO26 / YOLOE-26 | Y023 | Ultralytics 端到端及开放词汇分支，正式名称不带 `v` |

Source ID 的论文、仓库和文档见 [Sources](sources.md)。上表说明去哪里查第一方定义，不表示已经由本人逐个复现。

## 第三方实现

MMYOLO、Ultralytics 对外部分支的集成、RKNN Model Zoo 和 YOLOv5-Lite 不进入上表。它们是复现、迁移或硬件改造，见 [Ecosystem implementations](ecosystem-implementations.md)。

## 新分支怎么加

至少满足：

1. 作者或维护组织能确认；
2. 有论文、技术报告、正式仓库或模型卡；
3. 相对现有分支确实有结构、训练、任务或部署变化；
4. 许可和维护状态能查到；
5. 不是因为名称里带 YOLO 就收录。
