---
title: Organize reusable architecture knowledge by module role
status: accepted
date: 2026-07-25
---

# Decision 0004: Organize reusable architecture knowledge by module role

## Context

路线图曾把 MobileNet、ViT 设为一级待办，却把 ResNet、EfficientNet、ConvNeXt 降为“必要比较基线”。这种不对称不是由稳定的知识关系产生，而是由对话中先后出现的模型名产生；继续沿用会形成模型名单，而不是可复用的视觉架构知识。

眼部关键点任务又暴露了另一个缺口：HRNet 的高分辨率表征机制既影响 backbone 选择，也参与完整关键点方案；若只按任务或家族归档，很难区分究竟是 backbone、neck、head、输出表征还是训练条件带来的效果差异。

## Decision

- 把 \`backbone\`、\`neck\`、\`head\` 作为模型索引中的一级模块角色，并在路线图中分别建设。
- Backbone 待办统一覆盖 ResNet、MobileNet、EfficientNet、ConvNeXt、ViT、Swin、HRNet、TuringViT 等代表谱系；只有真实使用、材料规模和独立维护需求成立时才建立 family 页面。
- Neck 按跨层、跨尺度和跨模态特征融合组织；head 按任务输出表征组织，不按当前流行模型名称堆叠。
- YOLO、DETR、DINO detector 等完整 task model 仍按任务范式和可追溯谱系维护；DINO 自监督、CLIP 等训练或对齐体系也保持独立对象，不强行塞进三段式架构。
- HRNet 的高分辨率表征作为 backbone 机制维护；HRNet 与 PFLD 在眼部关键点上的实际差异进入关键点任务和工程案例。
- “当前实验中 HRNet 优于 PFLD”只记录为待补证据的本人观察。未控制数据、输入、输出表征、训练、规模和速度前，不升级为通用架构结论。

## Consequences

路线图从模型名平铺转为“模块角色 + 跨模块范式”两层结构。一个模型族可以承担多个角色，完整方案也可能跨越 backbone、neck、head；角色用于建立关系和控制比较口径，不制造互斥目录。

新增 family 或模块页面仍受 Foundations 维护规则约束：不预建空目录，不因资料多或模型热门就建立条目。DINO、CLIP、VLM/VLA、DETR、关键点、时序和分割保留，是因为它们描述训练范式、跨模态系统或任务问题，而不是遗漏在三段式架构中的模型名。

## Verification

- \`TODO.md\` 不再把 MobileNet、ViT 与其他 backbone 家族不对称地列为仓库级路线；
- Backbone、neck、head 分别有目标、边界和可验证出口；
- model index 与 registry 对三类模块使用一致角色名称；
- 关键点待办同时链接 HRNet 的 backbone 角色和完整任务比较；
- 没有为尚未形成内容的模块或模型族创建空目录。
