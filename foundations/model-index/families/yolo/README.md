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

YOLO 是以单阶段、实时目标检测为起点形成的模型家族名称，但它不是由单一组织连续维护的线性产品。原始 YOLOv1–v3 之后，编号分支、命名分支、开放词汇分支和生态实现由不同作者或组织维护，代码、许可和版本语义并不统一。

## Scope

本条目覆盖主要且能追溯到论文作者、发布组织或长期维护仓库的分支，用于理解结构、训练、评价和部署差异。不以“名称包含 YOLO”为唯一收录条件，也不把框架支持、第三方移植或汇总文章当作模型原始官方来源。

## Identity classes

- **原始作者谱系**：YOLOv1、YOLOv2/YOLO9000、YOLOv3；
- **可归属的正式分支**：由相应论文作者或维护组织正式发布，但不冒充原始作者的顺序续作；
- **生态改造/复现**：由第三方框架、芯片厂商或社区维护者移植、重实现或面向特定硬件改造，必须与模型原始实现分开评价。

本文中的“官方”始终是相对概念：只表示该资料由对应模型的作者或维护组织发布，不表示整个 YOLO 家族存在统一官方。

## Views

- [Architecture](architecture.md)：主要正式分支的核心机制；
- [Data and training](data-and-training.md)：官方披露与未披露项；
- [Evaluation](evaluation.md)：指标和比较口径；
- [Deployment](deployment.md)：导出、量化与边缘部署；
- [Variants](variants.md)：版本归属和选择导航；
- [Ecosystem implementations](ecosystem-implementations.md)：非原始实现但值得跟踪的复现、迁移与工程改造；
- [Limitations](limitations.md)：失败条件、命名冲突和未知项；
- [Sources](sources.md)：原始论文、正式仓库、文档和补充证据。

## Reading rule

各子页面共同构成一个知识条目并继承本页元数据。架构结论先回到对应分支的原始资料；生态实现只能证明该实现自身的行为，不能反向替代原模型定义。具体芯片的真实转换、性能与故障记录应进入 `engineering/`，本条目只保存跨项目可复用的模型级约束。

## Current boundary

- 已补齐主要编号分支、命名分支、开放词汇分支及来源入口；
- “主要”不等于穷举所有使用 YOLO 名称的论文，新增分支仍须通过收录门；
- 尚未逐个冻结所有仓库 revision、权重哈希和官方指标表；
- 生态实现已按来源身份隔离，但“值得跟踪”不等于已经独立验证其精度或维护质量；
- 尚未加入本人的统一硬件复测，因此不能给出跨版本速度冠军结论；
- YOLO 样板的文件粒度与维护成本仍待本人核验。
