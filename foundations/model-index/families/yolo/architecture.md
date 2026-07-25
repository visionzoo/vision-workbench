# Architecture

## Stable family-level pattern

YOLO 的稳定抽象是：一次前向计算产生密集或集合式检测预测，再通过解码和可选后处理形成目标框。不同分支对 backbone、特征融合、预测头、标签分配和 NMS 的选择差异很大，因此“YOLO 是单阶段检测器”不能替代版本级结构说明。

## Major mechanism changes

| Branch | Officially described change | Boundary |
|---|---|---|
| YOLOv1 | 将检测表述为从整图直接回归网格位置的框和类别概率 | 原始设计存在每格预测限制和定位误差问题 |
| YOLOv2 / YOLO9000 | anchor boxes、dimension clusters、多尺度训练、passthrough features，以及联合检测/分类训练 | 具体训练组合需回到论文和 Darknet 配置 |
| YOLOv3 | Darknet-53 残差 backbone、三个尺度预测、独立 logistic 分类 | 仍依赖 anchor 和后续 NMS |
| YOLOv4 | CSPDarknet53、SPP、PAN，以及系统化的 bag-of-freebies / bag-of-specials | 论文与 AlexeyAB/darknet 是该分支权威来源 |
| YOLOX | anchor-free、decoupled head、SimOTA | 是独立分支，不等同于 v5 的顺序后继 |
| YOLOv6 | 面向工业部署的硬件友好 backbone/neck、重参数化与高效 decoupled head | 不同 release 架构会变化，必须绑定版本 |
| YOLOv7 | E-ELAN、可扩展设计和 trainable bag-of-freebies | 训练时辅助结构与部署图需区分 |
| YOLOv9 | PGI 与 GELAN | 辅助训练路径不应被误认为全部保留在推理图 |
| YOLOv10 | consistent dual assignments 与整体效率设计，目标是端到端、NMS-free 检测 | 导出物是否真正端到端取决于具体实现和导出配置 |
| Ultralytics lineage | YOLOv5、YOLOv8、YOLO11、YOLO26 由 Ultralytics 文档、源码和各自技术资料定义 | 不用第三方逆向文章补全官方未披露细节 |

## How to inspect a concrete model

选择具体权重时必须重新记录：

```text
input → preprocessing → backbone → feature aggregation → task head
      → decode → confidence/class handling → NMS or end-to-end selection
```

同时确认训练专用模块是否已融合或移除、输出张量语义、stride、anchor/anchor-free、类别激活和坐标格式。模型名称相同但 exporter、仓库 revision 或 task head 不同，部署图可能不同。

## Mechanism links

计划关联但暂不创建空条目：multi-scale representation、label assignment、decoupled heads、structural re-parameterization、end-to-end set prediction。
