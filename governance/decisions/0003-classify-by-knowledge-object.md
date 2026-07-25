---
title: Classify by knowledge object, not action words
status: accepted
date: 2026-07-25
---

# Decision 0003: Classify by knowledge object, not action words

## Context

在调研 TuringViT 时，Agent 因用户使用了“调研”一词，把视觉编码器及其候选模型观察流程放入 `research/model-intelligence/`，并额外建立 protocol、registry、状态流和版本 Tag 约定。

这套结构回答的仍是模型角色、机制、训练、评测和部署问题，与现有 `foundations/model-index/` 重复。错误不在内容是否经过调研，而在于把处理动作误当成了知识对象。

## Decision

- 顶层和主题目录按内容长期描述的对象、系统角色及逻辑关系划分，不按“调研”“评测”“部署”“复盘”等动作词划分。
- 新模型、框架、backbone 和视觉编码器进入 `foundations/model-index/families/`；新机制进入 `mechanisms/`；真实工程结果进入 `engineering/`。
- `research/` 只承载可证伪问题、实验和 finding，不充当论文、新模型或行业动态的观察站。
- 删除 `research/model-intelligence/` 的独立 protocol、候选 registry、状态流和版本标签；TuringViT 迁入统一模型 registry。
- 未经本人确认、仅被筛选出的候选模型不迁移为长期资产。

## Consequences

模型与框架只有一个登记和维护位置，不再因不同获取方式复制体系。Research 的边界更窄，但仍保留真实问题产生的假设与实验。以后新增目录前必须先回答：去掉动作词后，对象是否仍无法归入现有结构；新目录表达了什么新的稳定关系；是否会复制现有索引、状态或证据规则。

## Verification

- 仓库中不再存在 `research/model-intelligence/` 或其反向链接；
- TuringViT 只在统一 model index 中登记一次；
- DMS 等可证伪研究问题继续保留在 Research；
- 根 README、Foundations、Research 与 registry 的入口一致。
