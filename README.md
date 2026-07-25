# vision-workbench

个人视觉算法专业资产母库：以长期积累和解决真实问题为第一优先级，沉淀可复用的机制理解、工程判断、独立研究与技术产品化思考。

> Private by design. 本仓库不是公开作品集、模型百科、工作日志或公司项目备份。

## Repository system

- **vision-workbench**：私有母库，保存问题、证据、实验、判断与可复用知识。
- **GitHub Profile README**：初期公共入口，只展示专业定位、能力地图和成熟项目。
- **Independent repositories**：可运行且有公开可能的代码应尽早独立建为私有仓库，完成验证后再公开。
- **vision-portfolio**：仅当成熟公共项目达到 **3 个及以上**，且 Profile README 已不足以清晰组织成果时创建；只承担成果索引，不复制母库内容。

## Knowledge map

| Area | Purpose |
|---|---|
| [Foundations](foundations/README.md) | 按机制与任务理解视觉算法，模型族作为辅助索引 |
| [Engineering](engineering/README.md) | 结构化工程案例、诊断方法、部署与可重复流程 |
| [Research](research/README.md) | 从真实问题形成假设、实验和有边界的结论 |
| [Productization](productization/README.md) | 研究视觉技术如何形成产品、价值和交易 |
| [Workspace](workspace/README.md) | 暂存未成熟的问题与调查过程 |
| [Projects](projects/registry.yaml) | 跟踪独立项目的孵化、验证与公开状态 |

## Initial focus

1. [Model quantization and accuracy alignment](engineering/diagnostics/model-quantization-accuracy-alignment.md)
2. [Vision algorithm release and delivery](engineering/playbooks/vision-algorithm-release-and-delivery.md)
3. [DMS eye visibility and localization reliability](research/questions/dms-eye-visibility-and-localization-reliability.md)

## Working rule

```text
inbox → working → validated → canonical
                         └→ independent private repo → public
```

正式内容必须保留：真实问题、目标与约束、竞争解释、证据与反证、区分性实验、当前结论、适用边界、失败路径和未解决问题。详细规则见 [governance](governance/README.md)。

## Language

文件名、术语、代码和公共项目使用英文；核心分析正文优先使用中文；成熟公开成果再制作英文版本。
