# Variants and implementations

YOLO 没有覆盖全部版本的单一“总官方”。这里的正式分支只表示能找到对应作者、维护组织及第一方资料，不表示它是原始作者的顺序续作。

本页唯一负责分支身份、维护方和实现关系。结构、训练、指标和部署判断分别进入对应页面。

## 1. 原始作者版本

| 分支 | 第一方来源 | 关系 |
|---|---|---|
| YOLOv1 | Y001 | 原始模型 |
| YOLOv2 / YOLO9000 | Y002 | 原作者延续 |
| YOLOv3 | Y003 | 原作者最后一个主要版本 |

## 2. 其他可追溯分支

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

这张表说明去哪里查第一方定义，不表示已经由本人逐个复现。

### YOLO26 Pose task extension

`yolo26n/s/m/l/x-pose.pt` 属于 Ultralytics YOLO26 的正式 pose scales，其中 `yolo26x-pose` 是最大 scale，不是独立 family。固定源码 Y028 中：

- `Pose26` 在 box/class head 之外增加每尺度 keypoint head；
- 支持 one-to-many 与 one-to-one 分支；
- keypoint schema 为 `(K, 2)` 或 `(K, 3)`，第三维表示关键点存在/可见 logit；
- 训练期额外预测每点 `sigma_x/sigma_y` 并使用 RealNVP/RLE loss；
- 标准 `fuse()` 会移除 sigma/flow 分支，因此推理输出不能自动解释为完整概率分布。

官方 COCO 17 点权重只证明该 schema/数据上的第一方结果。自定义 DMS eye landmarks 必须重新训练并固定 `kpt_shape`、box class、数据、revision、export branch 和目标 hardware。完整任务合同见 [2D landmark localization](../../../tasks/2d-landmark-localization.md)，输出机制见 [Keypoint output representations](../../../mechanisms/keypoint-output-representations.md)。

## 3. 复现、迁移和芯片适配

这些实现有工程价值，但只能定义自身改造，不能反过来定义上游模型。

| 实现 | 身份 | 实际价值 | 使用边界 | Source |
|---|---|---|---|---|
| OpenMMLab MMYOLO | 第三方统一复现/工具箱 | 在 MMDetection 体系统一训练和部署多个 YOLO 分支 | 默认超参、指标和导出图不是原模型事实 | Y024 |
| Ultralytics 对外部分支的集成 | 第三方框架集成或权重迁移 | 为 YOLO-World、YOLOv9/10/12、YOLOE 等提供统一入口 | 层、权重和支持程度随 package 变化；身份仍归原作者 | 对应上游 Source + Y019 |
| Rockchip RKNN Model Zoo YOLO ports | 芯片厂商适配 | 提供模型转换及 C/Python 示例 | SoC、Toolkit/runtime、量化和后处理必须绑定版本 | Y025 |
| YOLOv5-Lite | 社区轻量化改造 | 面向 Raspberry Pi、NCNN、MNN、TNN、ONNX Runtime 等 | 速度与量化结论只适用于给定模型、输入和设备 | Y026 |

采用第三方实现前沿以下链路核对：

```text
上游 revision 与权重
→ 预处理与输出语义
→ 结构或算子差异
→ 原框架结果
→ 导出结果
→ 目标硬件精度与延迟
```

## 4. 新对象怎么加

只有满足以下条件才在本页增加一行；不另建百科式 family 页面：

1. 作者或维护组织可确认；
2. 有论文、技术报告、正式仓库、模型卡或可运行适配；
3. 相对现有对象确有结构、训练、任务、接口或部署变化；
4. 许可、维护状态与上游关系可查；
5. 不是因为名称里带 YOLO 就收录。

迁移权重不能只因文件名相近就视为等价。所有 Source ID 在 [Sources](sources.md) 维护。
