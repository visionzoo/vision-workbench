# Architecture

## Stable family-level pattern

YOLO 的稳定抽象是：一次前向计算产生密集或端到端检测预测，再通过解码和可选后处理形成目标框。不同分支对 backbone、特征融合、预测头、标签分配、开放词汇对齐和 NMS 的选择差异很大，因此“YOLO 是单阶段检测器”不能替代版本级结构说明。

## Original-author lineage

| Branch | Officially described change | Boundary |
|---|---|---|
| YOLOv1 | 将检测表述为从整图直接回归网格位置的框和类别概率 | 原始设计存在每格预测限制和定位误差问题 |
| YOLOv2 / YOLO9000 | anchor boxes、dimension clusters、多尺度训练、passthrough features，以及联合检测/分类训练 | 具体训练组合需回到论文和 Darknet 配置 |
| YOLOv3 | Darknet-53 残差 backbone、三个尺度预测、独立 logistic 分类 | 原始作者最后一个主要 YOLO 版本；仍依赖 anchor 和 NMS |

## Officially attributable numbered branches

这里的“正式分支”只表示能追溯到对应作者或维护组织，不表示它们是 YOLOv3 的统一官方续作。

| Branch | Author/maintainer-described change | Boundary |
|---|---|---|
| YOLOv4 | CSPDarknet53、SPP、PAN，以及系统化的 bag-of-freebies / bag-of-specials | 论文与 AlexeyAB/darknet 是该分支来源 |
| YOLOv5 | Ultralytics 的 PyTorch 工程分支，持续迭代模型配置、训练、导出与多尺寸权重 | 无同名论文作为冻结规范；必须绑定 tag/commit，不能用当前源码概括全部历史版本 |
| YOLOv6 | 面向工业部署的 EfficientRep/CSPStackRep、重参数化、高效 decoupled head，以及后续 BiC/AAT 等演进 | release 间结构变化明显，必须绑定版本 |
| YOLOv7 | E-ELAN、可扩展设计、模型重参数化和 trainable bag-of-freebies | 训练时辅助结构与部署图需区分 |
| YOLOv8 | Ultralytics 的 anchor-free split head、C2f 特征提取和多任务统一工程接口 | 主要规范来自版本化源码/配置与文档；不要由非官方结构图补全 |
| YOLOv9 | PGI 与 GELAN | 辅助训练路径不应被误认为全部保留在推理图 |
| YOLOv10 | consistent dual assignments 与整体效率设计，目标是端到端、NMS-free 检测 | 导出物是否真正端到端取决于实现和导出配置 |
| YOLO11 | Ultralytics 改进 backbone/neck、训练流程和跨检测/分割/姿态/OBB/分类任务效率 | 官方页面未完整公开逐层机制解释；精确结构应读取对应版本 YAML 和源码 |
| YOLOv12 | attention-centric 设计，以 area attention 和 R-ELAN 等机制控制注意力代价 | 是独立研究分支；Ultralytics 将其标为 community model，不属于 Ultralytics 自有编号谱系 |
| YOLOv13 | HyperACE 等超图增强的自适应视觉表征 | 是 iMoonLab/论文作者分支；部署支持包含社区贡献，需逐项核验 |
| YOLO26 | Ultralytics 的端到端 NMS-free 默认路径、DFL-free regression、Progressive Loss + STAL、MuSGD 和多任务头 | 属于 Ultralytics 正式分支；训练辅助组件、融合导出图和常规推理图必须区分 |

## Officially attributable named branches

| Branch | Author/maintainer-described change | Boundary |
|---|---|---|
| Scaled-YOLOv4 | 将 CSP 网络设计与模型缩放原则结合，覆盖小型到大型检测器 | 与 YOLOv4 相关但有独立论文和实现 |
| YOLOR | 统一显式与隐式知识表示，用一个网络服务多任务 | 是独立研究分支，不是编号版本 |
| YOLOX | anchor-free、decoupled head、SimOTA | 是旷视分支，不等同于 YOLOv5 的顺序后继 |
| PP-YOLO / PP-YOLOv2 | 基于 PaddleDetection 的工程增强与训练技巧组合 | 以 Paddle 官方实现和对应论文为准 |
| PP-YOLOE / PP-YOLOE+ | anchor-free、高效 task-aligned head/学习与工业部署优化 | PP-YOLOE+ 等变化必须绑定 PaddleDetection release/config |
| DAMO-YOLO | NAS backbone、RepGFPN、ZeroHead/轻量 head、AlignedOTA 与蒸馏 | 阿里 DAMO/TinyML 团队分支，不属于编号谱系 |
| YOLO-NAS | AutoNAC 搜索得到的架构、量化友好模块与选择性量化路线 | 权重许可和商用边界必须单独核验 |
| Gold-YOLO | gather-and-distribute 机制增强多尺度特征融合 | 华为诺亚分支；不能只凭名称推断与编号版本的继承关系 |
| YOLO-World | 在 YOLO 检测器中引入视觉—语言对齐、开放词汇预训练和 prompt-then-detect/词汇重参数化 | 原始实现基于 MMYOLO；Ultralytics 版本属于迁移实现，二者不能混用指标 |
| YOLOE | 统一文本、视觉和 prompt-free 开放词汇检测/分割，引入 RepRTA 等可重参数化对齐机制 | THU-MIG 原始分支与 Ultralytics 集成需绑定各自版本 |
| YOLOE-26 | 将 YOLOE 的开放词汇能力建立在 YOLO26 的端到端、多任务基础上 | 属于 Ultralytics YOLO26 技术报告范围，不等同于早期 YOLOE 权重 |

## How to inspect a concrete model

选择具体权重时必须重新记录：

```text
input → preprocessing → backbone → feature aggregation → task/prompt head
      → decode → confidence/class handling → NMS or end-to-end selection
```

同时确认训练专用模块是否已融合或移除、输出张量语义、stride、anchor/anchor-free、类别激活、坐标格式，以及文本编码器或词汇嵌入是否仍在运行时图中。模型名称相同但 exporter、仓库 revision、权重来源或 task head 不同，部署图可能不同。

## Mechanism links

计划关联但暂不创建空条目：multi-scale representation、label assignment、decoupled heads、structural re-parameterization、end-to-end set prediction、vision-language alignment、open-vocabulary detection。
