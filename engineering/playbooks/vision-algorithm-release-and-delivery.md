---
title: Vision algorithm release and delivery
status: working
type: playbook
rigor: standard
created: 2026-07-25
updated: 2026-07-25
confidence: low
provenance: conversation-draft
evidence_status: unverified
owner_review: pending
ip_review: pending
tags: [release, manifest, model, sdk, traceability]
related: []
---

# Vision algorithm release and delivery

## Evidence boundary

本条目由历史对话重构，是待审查的流程草案。尚未用真实仓库结构、现行交付物、责任人、自动化脚本或一次完整发布运行验证；下列字段和门槛不能直接当作组织流程执行。

## Problem

候选问题表征：把训练模型、板端模型、算法库和最终 SDK/exapp 的版本关系变成可追溯、可复现、可审计的交付链，避免依靠文件名、聊天记录和人工记忆判断版本。

## Intended flow

```text
training run → exported model → device model → algorithm library → SDK package
      metadata and checksums carried forward at every boundary
```

该流程仍需与真实组织职责、产品分支和交付边界对齐。

## Candidate invariants

- 每阶段尽量只产生实体交付物、一个结构化 manifest 和必要验证报告；
- 最终 SDK 可包含面向测试和外部追溯的 release note；
- manifest 候选关联 source commit、Run ID、dataset/split manifest、model version、converter/toolchain version、target chip、library commit/version、SDK version、依赖、校验和、验证结果和批准人；
- SHA-256 可作为统一校验候选，但在现有消费者仍依赖 MD5 时不能擅自删除兼容字段。

## Competing explanations and risks

版本不可追溯未必只因缺少 manifest，也可能来自责任边界不清、实体存储与 Git 脱节、构建不可复现、手工交付绕过流程或消费端无法读取字段。单纯增加 YAML 可能形成“文档完整但交付仍不可验证”的空架子。

## Discriminating action

选取一次真实但可控的发布作为垂直切片，先盘点实际输入、输出、负责人、现有记录和消费端；再用最少字段贯穿一个模型到 SDK，并由下游根据 manifest 独立还原来源和校验实体。

## Human gates

训练数据/指标接受、转换精度接受、板端性能接受、SDK 内容与兼容性确认、知识产权和外发范围确认是候选人工门；具体责任人和签署方式待本人确认。

## Current conclusion

尚不能宣称这是可执行 playbook。它当前只保存候选不变量与验证方式；只有完成一次真实垂直切片并处理反例后，才可考虑晋级。
