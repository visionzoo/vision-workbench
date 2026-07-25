# Engineering maintenance

## Create

只有当内容包含可迁移的问题结构、输入输出和验证方法时，才建立 case、diagnostic、deployment 或 playbook 条目。具体项目的一次性操作留在项目仓库。

## Add or update

补充观察、竞争解释、区分实验、环境版本、结果与回滚条件；新证据与旧结论冲突时保留冲突并重新评估状态。真实芯片、SDK 和性能记录放在这里，Foundations 只保留模型级摘要和链接。

## Split or merge

同一根因链保持在一个诊断条目；当平台、工具链或 Oracle 不同到无法共同复现时拆分。重复 playbook 合并为参数化流程。

## Remove

删除不可复现且没有诊断价值的操作记录，或迁移到独立项目仓库；同步修复入口与引用。失败实验若能排除假设则不得删除。

## Verify

确认环境、输入、变量、日志、Oracle、结果和适用边界可追溯；不得把“运行成功”当作精度或产品验收。
