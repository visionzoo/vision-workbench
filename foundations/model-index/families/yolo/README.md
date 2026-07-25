---
status: working
type: model-index
rigor: standard
provenance: official-papers-repositories-and-documentation
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-07-25
updated: 2026-07-25
---

# YOLO family

YOLO 是以单阶段、实时目标检测为起点形成的模型家族名称，但它不是由单一组织连续维护的线性产品。原始 YOLOv1–v3、Darknet/YOLOv4、Ultralytics、YOLOX、YOLOv6、YOLOv7/9、YOLOv10 等具有不同作者、代码库、许可和版本语义。

## Scope

本条目覆盖主要且能追溯到原作者论文或维护仓库的分支，用于理解结构、训练、评价和部署差异。不以“名称包含 YOLO”为唯一收录条件，也不把第三方汇总表当作官方事实。

## Views

- [Architecture](architecture.md)：核心机制如何演进；
- [Data and training](data-and-training.md)：官方披露与未披露项；
- [Evaluation](evaluation.md)：指标和比较口径；
- [Deployment](deployment.md)：导出、量化与边缘部署；
- [Variants](variants.md)：版本归属和选择导航；
- [Limitations](limitations.md)：失败条件、命名冲突和未知项；
- [Sources](sources.md)：原始论文、官方仓库和文档。

## Reading rule

各子页面共同构成一个知识条目并继承本页元数据。页面中的“官方”只指对应版本的作者或维护组织，不代表整个 YOLO 家族存在统一官方。具体芯片的真实转换、性能与故障记录应进入 `engineering/`，本条目只保存跨项目可复用的模型级约束。

## Current boundary

- 已建立主要分支和证据入口；
- 尚未逐个冻结所有仓库 revision、权重哈希和官方指标表；
- 尚未加入本人的统一硬件复测，因此不能给出跨版本速度冠军结论；
- YOLO 样板的文件粒度与维护成本仍待本人核验。
