---
title: Colab to GitHub project intake
status: working
type: playbook
rigor: standard
created: 2026-08-03
updated: 2026-08-03
confidence: medium
provenance: conversation-draft; first-application at visionzoo/object-tracking-heatmap-baseline@a1f939ad7c96cb01afc3ce4a0270dc29ae09529d
evidence_status: partial
owner_review: pending
ip_review: pending
tags: [colab, github, notebook, project-intake, reproducibility]
related: [../../projects/registry.yaml, ../../governance/lifecycle.md, ../../governance/ip-policy.md]
---

# Colab to GitHub project intake

## Evidence boundary

本条目把“在 Colab 调试视觉代码并保存到 GitHub”的需求整理为候选流程。2026-08-03 已用 [object-tracking heatmap baseline](../cases/object-tracking-heatmap-baseline.md) 完成固定公开上游、创建私有仓库、推送初始提交、母库登记和本机核心 smoke；尚未从 Colab 界面保存、在全新 Colab 运行时完整执行或走完项目 PR，因此仍不能视为已经验证的平台操作说明。

## Problem and success criteria

Colab 运行时是临时执行环境，GitHub 是代码历史，`vision-workbench` 是知识与项目关系的母库。三者需要分工，避免 notebook 丢失，也避免把数据、权重、凭据、运行输出或一次性调试代码混入母库。

一次纳管成功至少满足：

- 代码进入边界清楚的私有 GitHub 仓库，并保留可理解的提交历史；
- notebook 不包含凭据、公司资产、客户信息、非公开数据或可反推项目的信息；
- 依赖、入口、输入来源和最小验收方式可追溯；
- 若建立独立仓库，`projects/registry.yaml` 同步登记仓库、来源主题、可见性、状态和 IP 审查状态；
- 从干净 Colab 运行时或其他干净环境重新执行最小路径后，才把“已保存”提升为“可复现”。

## Repository decision

不要建立无边界的 `colab-sandbox` 或 notebook 大杂烩仓库。按下面的顺序选择落点：

1. notebook 已属于 `projects/registry.yaml` 中的独立项目：保存到该项目仓库，建议路径为 `notebooks/<purpose>.ipynb`；
2. notebook 已形成可运行代码，能脱离公司资产验证，并具有复用或潜在公开价值：为这个具体视觉项目新建独立**私有**仓库，再在 registry 登记；
3. 只有问题、伪代码、观察或尚不能合法带出的片段：不提交代码仓库；把非敏感的问题与证据缺口写入 `vision-workbench` 对应主题条目，或在无法归类时暂存到 `workspace/`；
4. 仅是一次性、不可复现的调试：可暂留 Colab/Drive，但不因“需要备份”而把它包装成项目资产。

新仓库默认保持 private、`status: incubating`、`ip_review: pending`。公开是独立的 HIGH-RISK 动作，必须再次人工确认，而不是保存 notebook 的自然后续。

## Candidate operating flow

```text
define visual problem and IP boundary
  → choose existing project repo or create a scoped private repo
  → save notebook to a short-lived branch
  → inspect notebook diff and remove unsafe outputs
  → run the minimum path in a clean runtime
  → merge through review
  → update projects/registry.yaml and the source knowledge entry
```

### Before the first save

- 用一句话写清仓库只解决哪个视觉问题；仓库名描述问题或可验证产物，不描述工具环境；
- 优先复用已有项目仓库，不为每次 Colab session 建仓；
- 新仓库至少准备 `README.md`、`.gitignore`、依赖声明和 `notebooks/`；是否增加 `src/`、`tests/`、`data/` 取决于真实内容，不预建空目录；
- 数据集、模型权重、缓存和大体积输出默认不入 Git；记录合法来源、版本、哈希或获取方式；
- 凭据只放在 Colab Secrets 或 GitHub 的密钥设施中，禁止写进单元格、输出、URL、remote 或提交历史。

### Save from Colab

对于单个 notebook，候选默认路径是 Colab 的 **File → Save a copy in GitHub**，目标选择私有仓库、短生命周期分支和明确的 notebook 路径。提交前：

- 搜索 token、cookie、内网地址、真实人员信息、挂载盘路径和敏感样本；
- 清除不需要复核的 cell output，尤其是图片、日志、数据行和异常栈；
- 把安装命令固定到可解释的版本范围，记录 Python、CUDA/框架和关键包版本；
- 不把 `/content/` 中的临时文件当作已持久化资产；
- 提交信息说明本次可运行增量和仍未验证的边界。

只有 notebook 不足以承载多文件代码、测试或配置时，才在 Colab 中使用 Git 工作流。此时仍应推送到短生命周期分支并通过 PR 合并；不得把 GitHub token 明文放入 notebook 或输出。

### Review and merge

- 审查 `.ipynb` 的文本 diff，而不只看渲染后的页面；
- 用全新运行时执行最小入口，确认依赖可安装、输入可获得且关键断言通过；
- 把 reusable code 从 notebook 抽到 `src/` 的时机由真实复用或测试需求触发，不为目录整齐提前重构；
- 合并后删除已合并的短生命周期分支；有独立提交或未关闭验证问题的分支保留；
- 创建或改变独立仓库时，同一变更中更新 `projects/registry.yaml`；母库只保存问题、判断、实验摘要和仓库链接，不复制项目代码。

## Competing options and failure modes

- **直接把 notebook 放进 `vision-workbench`**：备份最省事，但破坏母库与可运行项目的边界，也扩大敏感历史和依赖噪声；默认拒绝。
- **所有实验共用一个 Colab 仓库**：仓库数量少，但项目边界、许可证、依赖和公开历史会互相污染；默认拒绝，除非它本身就是边界明确、可独立验证的统一工具。
- **每个 notebook 建一个仓库**：隔离彻底，但产生大量不可维护的小仓库；只有 notebook 已代表独立可验证产物时采用。
- **只保存到 Drive**：适合短期草稿，但缺少代码审查和清晰版本关系；不能替代 GitHub 中的项目资产。

主要失败模式包括 notebook 输出泄密、token 进入历史、依赖漂移、只在热运行时成功、数据或权重不可合法复现，以及 registry 链接滞后。任一项出现时都应停止合并或公开，而不是用说明文字绕过。

## Commitment and rollback

当前允许的动作是：对一个具体视觉项目选择或创建私有仓库、保存到分支、执行安全审查与最小复现、合并后在母库登记。当前不允许自动公开仓库，也不允许默认迁移来源不明的旧 notebook。

若误提交敏感信息，立即停止推送与合并、撤销相关凭据，并按完整 Git 历史泄露处理；普通代码错误可通过回退 PR 恢复，但删除工作树文件不能清除已泄露历史。

## Verification still required

首次应用已覆盖私有仓库创建、敏感输出排除、上游/IP 边界、固定依赖、本机 smoke 和 registry 登记。仍需保存以下新鲜证据，再决定是否提高本条目状态：

- Colab 保存到私有仓库分支的实际界面和权限行为；
- notebook diff 检查记录及 secrets/IP 扫描结果；
- 全新运行时的依赖安装与最小执行结果；
- PR 合并、分支删除和 registry 链接可达性；
- 平台行为变化或多文件项目出现时，本流程是否仍足够。
