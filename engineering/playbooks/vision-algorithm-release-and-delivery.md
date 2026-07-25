---
title: Vision algorithm release and delivery
status: working
type: playbook
created: 2026-07-25
updated: 2026-07-25
confidence: medium
tags: [release, manifest, model, sdk, traceability]
related: []
---

# Vision algorithm release and delivery

## Problem

把训练模型、板端模型、算法库和最终 SDK/exapp 的版本关系变成可追溯、可复现、可审计的交付链，避免依靠文件名、聊天记录和人工记忆判断版本。

## Intended flow

```text
training run → exported model → device model → algorithm library → SDK package
      metadata and checksums carried forward at every boundary
```

## Minimal artifacts

每阶段尽量只产生：实体交付物、一个结构化 manifest、必要的验证报告。最终 SDK 内含面向测试和外部追溯的 release note；完整变更和上游关系由 manifest 记录，校验统一使用 SHA-256，不重复维护 MD5。

## Required traceability

至少关联 source commit、Run ID、dataset/split manifest、model version、converter/toolchain version、target chip、library commit/version、SDK version、依赖、校验和、验证结果和批准人。

## Human gates

训练数据/指标接受、转换精度接受、板端性能接受、SDK 内容与兼容性确认、知识产权和外发范围确认必须由责任人明确签署。

## Current boundary

本条目先保存跨阶段不变量；具体目录、字段和自动化脚本应结合现有 `algo-release` 体系另行验证，不能假设一套 manifest 可无修改覆盖所有芯片与产品。
