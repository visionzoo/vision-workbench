# AGENTS.md

本文件是 Agent 修改 `vision-workbench` 的最小操作契约。它约束状态提交与外部动作，不要求简单任务执行重型流程。

## Before editing

1. 阅读 `governance/scope.md`、`governance/ip-policy.md`、`governance/content-standard.md` 和 `governance/lifecycle.md`。
2. 明确本次目标、授权范围、目标文件和验收方式；不要顺带扩展目录或主题。
3. 把对话、旧笔记、检索结果和 Agent 生成内容视为候选材料，而非已验证事实。
4. 若内容可能来自公司任务、设备、代码、数据、模型或客户上下文，保持 `ip_review: pending`，不得公开或晋级。

## Four states to preserve

- **Problem**：目标、观察、约束、未知量、候选机制和错误成本。
- **Belief**：仍存活的假设、支持/反对证据、默认假设和置信边界。
- **Commitment**：为什么现在允许行动、允许做什么、残余不确定性和撤销触发器。
- **Verification**：验收标准、独立 Oracle、新鲜证据及接受/拒绝/回滚结果。

不要求每篇 QUICK 条目完整展开四类状态；但不得把其中一种偷换为另一种，例如把用户判断写成证据，或把计划写成已完成结果。

## Risk modes

- **QUICK**：低风险、可逆、问题清楚且 Oracle 明确。
- **STANDARD**：存在多个解释，或结论将被复用；必须保留替代表征、反证条件和区分性行动。
- **HIGH-RISK**：公开、生产、权限、删除、数据、IP 或关键架构承诺；必须停在本人确认门，并记录回滚与独立验收。

## State and evidence gates

- 可归类条目直接放入对应主题目录，以元数据表达 `working | validated | canonical`；不要建立 `workspace/working/` 或复制文件晋级。
- `provenance: conversation-draft` 必须保持 `evidence_status: unverified`、`confidence: low`、`owner_review: pending`，直到出现独立证据和本人审查。
- 晋级到 `validated` 需要新鲜、可寻址的证据；晋级到 `canonical` 还需明确版本、边界、反例与复用条件。
- Agent 的自然语言总结、同一文档内部自洽或生成者自评不能充当最终 Oracle。
- 证据失效或出现重要反例时必须降低状态或置信度，不维护“只升不降”的叙事。

## Editing and completion

- 先做最小、相关修改；结构或治理规则发生实质变化时新增 decision record。
- 不新增无内容目录、模型百科式条目或不可执行的大框架。
- 修改后至少检查：元数据、相对链接、规则冲突、来源/证据边界、IP 状态、过度结论和公开触发条件。
- 只有检查结果与实际文件共同支持时才能声明完成；报告剩余的非原则性限制，不伪造“绝对无问题”。
