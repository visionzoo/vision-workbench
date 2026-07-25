# Research

这里不保存“被调研过的内容”，只保存从真实视觉问题中形成的可证伪问题、实验和有边界的新判断。

- `questions/`：尚未解决的问题、竞争解释和验证路线；
- `experiments/`：有明确假设、变量、基线和判据的实验；
- `findings/`：由独立证据支持、但仍说明适用边界的阶段性结论。

## 分类边界

目录由知识对象及其逻辑关系决定，不由用户句子里的动作词决定：

- 调研新模型、框架、backbone 或视觉编码器 → 先进入 [Foundations model index](../foundations/model-index/README.md)；
- 训练、转换、量化、部署和故障复盘 → 进入 [Engineering](../engineering/README.md)；
- 只有出现可证伪问题，并需要实验区分竞争解释时 → 进入 Research。

因此，Research 不是论文或新模型的观察站，也不维护另一套模型 registry、筛选协议或状态流。

研究条目必须区分已有公开结论、工程观察和本人推断。当前入口：

- [DMS eye visibility and localization reliability](questions/dms-eye-visibility-and-localization-reliability.md)
