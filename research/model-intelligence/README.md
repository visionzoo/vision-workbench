---
status: working
type: research-question
rigor: standard
created: 2026-07-25
updated: 2026-07-25
confidence: medium
provenance: public-source-research
 evidence_status: partial
owner_review: pending
ip_review: not-applicable
tags: [visual-model-intelligence, vision-backbone, vlm, edge-ai, model-watch]
related: [protocol.md, registry.yaml, cases/turingvit.md]
---

# Visual model intelligence

本目录用于持续研究“新视觉底座如何改变视觉系统的能力、效率与部署方式”，而不是收藏模型新闻或建立模型百科。

首个切入口是小鹏 TuringViT：它把视觉编码器从 VLM/VLA 的通用附件，提升为面向高分辨率、多帧、物理 AI 与自研硬件联合设计的平台资产。

## 功能目标

每次出现值得研究的新视觉模型时，回答四个问题：

1. 它在完整系统中是什么角色：完整模型、视觉编码器、backbone、token compressor，还是任务 head；
2. 它相对既有 ViT、CNN、VFM、VLM/VLA 改变了什么机制；
3. 官方结果实际证明了什么，哪些结论仍没有端到端或真实硬件证据；
4. 哪些内容可迁移到检测、关键点、时序建模和嵌入式部署。

## 目录

- [protocol.md](protocol.md)：纳入标准、调研步骤和证据规则；
- [registry.yaml](registry.yaml)：候选模型及状态登记；
- [cases/turingvit.md](cases/turingvit.md)：首个完整案例。

## 状态流

```text
signal → screened → researching → reviewed → retained / rejected / superseded
```

模型进入 registry 不表示认可。只有形成明确机制判断、竞争解释、证据边界和可迁移动作后，才保留为长期案例。

## 标签约定

知识条目使用 YAML `tags`；本功能统一使用主标签 `visual-model-intelligence`，并按需增加：

- `vision-backbone`
- `high-resolution-vision`
- `video-encoder`
- `vlm`
- `vla`
- `edge-ai`
- `hardware-software-codesign`
- `distillation`

Git 版本标识只在一批功能形成可复用基线后创建，格式为 `visual-model-intelligence-vMAJOR.MINOR.PATCH`，不为每篇调研单独打 Tag。

## 当前边界

- 只使用公开论文、项目页、官方仓库、官方模型卡和可定位的第三方工程证据；
- 官方宣传不能替代论文、代码、硬件测试或端到端指标；
- 不把 VLM/VLA 扩展成独立通用专题，只研究其视觉编码和对嵌入式视觉的可迁移价值；
- 当前内容尚未经过本人验收，不能晋级为 validated 或 canonical。
