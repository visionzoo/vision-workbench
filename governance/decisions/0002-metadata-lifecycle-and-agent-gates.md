---
title: Metadata lifecycle and Agent evidence gates
status: accepted
date: 2026-07-25
---

# Decision 0002: Metadata lifecycle and Agent evidence gates

## Context

初始结构同时使用 `workspace/working/` 与文档状态元数据，造成两套生命周期；历史对话生成的启动条目也缺少来源、证据、本人审查与 IP 状态，容易把检索材料过早提交为长期知识。

## Decision

- `workspace/` 仅保留未分类 inbox；可归类内容从创建起进入所属主题目录。
- 生命周期只由元数据表达，文件不因晋级而复制或移动。
- 正式条目记录 `rigor`、`provenance`、`evidence_status`、`owner_review` 与 `ip_review`。
- 对话草稿在独立证据和本人审查前保持低置信度、未验证和 working。
- 根级 `AGENTS.md` 将问题、信念、承诺和验收原则转为操作门槛；流程深度按风险分级。
- 启动条目的类型按实际认识状态命名，不把诊断框架称为已完成案例，也不把研究问题称为已运行实验。

## Consequences

链接在生命周期中保持稳定，Agent 无法仅靠叙述把草稿晋级为知识。代价是每个正式条目需要少量元数据，并在证据或 IP 状态变化时维护。为避免形式主义，QUICK 内容只保留最小字段和 Oracle，STANDARD/HIGH-RISK 才展开完整诊断与承诺记录。
