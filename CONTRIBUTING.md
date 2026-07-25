# Contributing

本仓库以“少量、完整、可审计的变更”维护，不以提交次数衡量进展。

## Before changing content

1. 阅读根目录 `AGENTS.md`、目标一级目录的 `MAINTENANCE.md`，以及相关治理文件。
2. 明确本次变更的单一主题、目标文件、证据来源和验收标准。
3. 优先补充现有条目；只有现有目录无法稳定承载内容时才新增文件或目录。
4. 不因资料丰富就批量创建空模型族、空章节或占位条目。

## Commit policy

- 一个提交应表达一个可独立理解和回退的完整意图；不要按文件、段落或工具调用拆提交。
- 同一主题的目录规则、导航更新和必要模板应合并为一个提交。
- 大规模内容扩展与治理规则变更原则上分开；若二者共同构成同一完整样板，可以合并并在正文列明。
- 修改尚未通过核查时不提交。只有需要保存可复现中间状态、多人协作交接或高风险隔离时才允许检查点提交。
- 提交前检查 `git diff --stat`、完整 diff、相对链接、元数据、来源边界和意外文件。

## Commit message

格式：

```text
<area>: <明确说明完成了什么>

- <主要修改 1>
- <主要修改 2>
- <验证或边界>
```

标题应让不了解上下文的人也能判断影响范围。禁止使用 `update docs`、`fix files`、`add content`、`misc changes` 等模糊信息。

示例：

```text
foundations: add maintenance rules and establish the YOLO family sample

- define create, update, split, and removal gates for every top-level area
- add the YOLO architecture, training, evaluation, deployment, variant, limitation, and source views
- keep non-official claims and unverified benchmark numbers out of the canonical record
```

## Review checklist

- 修改是否只服务于本次主题；
- 是否说明了新增、补充、拆分、合并和删除的理由；
- 官方披露、第三方证据和本人验证是否分开；
- 是否存在无法追溯的指标、训练数据或部署结论；
- 删除是否同步修复导航、反向链接和 registry；
- 提交标题和正文是否能准确概括全部 diff；
- 是否还有原则性冲突；如有，不得声明完成。
