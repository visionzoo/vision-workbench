# vision-workbench

个人视觉算法专业资产母库：以长期积累和解决真实问题为第一优先级，沉淀可复用的机制理解、工程判断、独立研究与技术产品化思考。

> Private by design. 本仓库不是公开作品集、模型百科、工作日志或公司项目备份。

## Repository system

- **vision-workbench**：私有母库，保存问题、证据、实验、判断与可复用知识。
- **GitHub Profile README**：初期公共入口，只展示专业定位、能力地图和成熟项目。
- **Independent repositories**：可运行且有公开可能的代码应尽早独立建为私有仓库，完成验证后再公开。
- **vision-portfolio**：仅当成熟公共项目达到 **3 个及以上**，且 Profile README 已不足以清晰组织成果时创建；只承担成果索引，不复制母库内容。

## Knowledge map

| Area | Purpose | Maintenance |
|---|---|---|
| [Foundations](foundations/README.md) | 按机制与任务理解视觉算法，模型族作为辅助索引 | [Rules](foundations/MAINTENANCE.md) |
| [Engineering](engineering/README.md) | 结构化工程案例、诊断方法、部署与可重复流程 | [Rules](engineering/MAINTENANCE.md) |
| [Research](research/README.md) | 从真实问题形成假设、实验和有边界的结论 | [Rules](research/MAINTENANCE.md) |
| [Productization](productization/README.md) | 研究视觉技术如何形成产品、价值和交易 | [Rules](productization/MAINTENANCE.md) |
| [Workspace](workspace/README.md) | 只暂存尚未分类的输入；可归类条目从创建起进入主题目录 | [Rules](workspace/MAINTENANCE.md) |
| [Projects](projects/registry.yaml) | 跟踪独立项目的孵化、验证与公开状态 | [Rules](projects/MAINTENANCE.md) |
| References | 管理跨条目复用的论文、仓库和数据集索引 | [Rules](references/MAINTENANCE.md) |
| Governance | 管理仓库边界、质量、生命周期和决策 | [Rules](governance/MAINTENANCE.md) |
| Templates | 提供最小、可删减的内容结构 | [Rules](templates/MAINTENANCE.md) |

全局修改和提交规则见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## Current focus

1. [YOLO](foundations/model-index/families/yolo/README.md)：目录样板已验收，正在用真实训练与板端案例完成第一版内容闭环。
2. [Model quantization and accuracy alignment](engineering/diagnostics/model-quantization-accuracy-alignment.md)：诊断框架草稿，尚未独立验证。
3. [Vision algorithm release and delivery](engineering/playbooks/vision-algorithm-release-and-delivery.md)：发布流程草稿，尚未独立验证。
4. [DMS eye visibility and localization reliability](research/questions/dms-eye-visibility-and-localization-reliability.md)：研究问题草稿，尚未独立验证。

## Working rule

```text
unclassified inbox → domain path / working → validated → canonical
                                             └→ independent private repo → public
```

文件位置表达主题，元数据表达知识状态；晋级不通过移动或复制文件完成。正式内容必须保留问题、证据边界、竞争解释、区分性行动、当前结论、适用边界和未解决问题。详细规则见 [governance](governance/README.md)，Agent 修改约束见 [AGENTS.md](AGENTS.md)。

## Language

文件名、术语、代码和公共项目使用英文；核心分析正文优先使用中文；成熟公开成果再制作英文版本。
