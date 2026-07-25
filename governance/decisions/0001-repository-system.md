---
title: Private workbench and public project system
status: accepted
date: 2026-07-25
---

# Decision 0001: Repository system

## Context

长期积累需要保留不成熟推理和敏感边界，对外展示则要求完整、可运行、可验证。用单一公开仓库同时承担两者会造成内容删减、同步负担和知识产权风险。

## Decision

- 使用私有 `vision-workbench` 作为视觉算法母库；
- 初期用 GitHub Profile README 作为公共入口；
- 可能公开的可运行代码尽早进入独立私有仓库，成熟后公开；
- 公共项目达到 3 个及以上且 Profile README 不够用时，再创建 `vision-portfolio`。

## Consequences

母库优化长期复用，不为展示牺牲上下文；公开项目必须独立完成工程化验证。代价是需要维护项目登记表和明确的剥离时点。
