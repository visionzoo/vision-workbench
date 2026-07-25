---
title:
status: working # working | validated | canonical
type: # mechanism | model-index | research-question | diagnostic | experiment | case | finding | playbook | product-hypothesis | market-case
rigor: standard # quick | standard | high-risk
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: low # low | medium | high
provenance: # source category plus path / URL / commit when available
evidence_status: unverified # unverified | partial | verified
owner_review: pending # pending | accepted
ip_review: pending # pending | accepted | not-applicable
tags: []
related: []
---

# Title

## Problem and current frame

真实问题、目标、成功标准和约束是什么？当前表征隐含了哪些前提？

## Provenance and evidence boundary

材料来自哪里？哪些是事实、观察、经验、推断或假设？给出路径、URL、提交、哈希或实验记录；对话重述本身不是证据。

## Competing explanations or options

STANDARD/HIGH-RISK：列出至少一个机制不同的替代解释/方案。分别预测什么？什么证据能推翻它？

## Discriminating action

哪个最小搜索、观察或实验能最大程度地区分当前候选？成本、副作用、可逆性和预期观察是什么？

## Current conclusion

只写现有证据允许支持的结论；证据不足时可以明确写“尚无结论”。

## Applicability, versions, and failure boundaries

结论在哪些数据、版本、环境与约束下成立？何时不能外推？什么新证据会触发降级或撤销？

## Decision and verification

记录关键承诺点、允许的动作和验收标准。HIGH-RISK 还必须写明人工确认、独立 Oracle、新鲜证据与回滚方式。

## Failed paths and open questions

保留被淘汰的假设、失败原因、残余不确定性和下一步。

## Reusable assets

链接独立代码仓库、公开数据、脚本、实验记录或相关条目。案例应说明旧经验为何需要适配，不能直接照搬。
