# Content standard

## Required qualities

1. 术语使用可追溯到主流论文、官方文档或稳定业界共识；细分领域无统一标准时必须说明定义。
2. 区分 **fact / observation / experience / inference / hypothesis**，不得把个人经验、对话回忆或 Agent 重述写成事实。
3. 对话、旧笔记和检索结果只是候选材料；写入条目时必须标记来源与证据状态。
4. STANDARD 与 HIGH-RISK 内容至少保留一个机制不同的替代解释或反例，并定义能区分它们的证据。
5. 结论必须能指向原始证据，并写明适用条件、失效条件、版本和未知项。
6. 指标必须说明数据范围、样本量、评测口径、基线和变量，避免孤立数字。
7. canonical 内容应能帮助未来做决策或复现实验，而不只是阅读。

## Knowledge-entry metadata

以下字段适用于 foundations、engineering、research 与 productization 中的知识条目。治理 decision record 使用独立的 `accepted | superseded` 决策状态，`projects/registry.yaml` 也使用项目状态；二者不得与知识成熟度混用。

```yaml
status: working | validated | canonical
type: mechanism | task | model-index | research-question | diagnostic | experiment | case | finding | playbook | product-hypothesis | market-case
rigor: quick | standard | high-risk
provenance: <source category or evidence pointer>
evidence_status: unverified | partial | verified
owner_review: pending | accepted
ip_review: pending | accepted | not-applicable
confidence: low | medium | high
```

`confidence` 表示当前证据支持强度，不表示文档写得是否完整。`provenance: conversation-draft` 的条目在得到独立证据前必须保持 `evidence_status: unverified`，且 `confidence: low`。

## Proportional depth

| Rigor | Use when | Minimum content |
|---|---|---|
| quick | 问题清楚、低风险、可逆且有确定 Oracle | 目标、来源、边界、结论或动作、Oracle |
| standard | 存在竞争解释，或结论将被复用 | 问题表征、假设、证据/反证、区分性行动、边界 |
| high-risk | 涉及生产、公开、权限、删除、数据、IP 或关键架构承诺 | standard 全部内容，加人工承诺门、回滚、独立 Oracle 和审计证据 |

不因篇幅或措辞自动提高 rigor；由歧义、后果、不可逆性与证据缺口决定。

## Promotion gates

| Status | Gate |
|---|---|
| working | 问题、来源、证据缺口和下一步已写清；允许结论为空 |
| validated | 关键判断有新鲜、可寻址的证据；`owner_review: accepted`；`ip_review` 为 `accepted` 或 `not-applicable` |
| canonical | 重要替代解释已被区分，边界与版本明确，可复现或稳定复用，且验收证据不是生成内容的自述 |

任何 Agent 都不得仅凭聊天历史、文档内部自洽或自己的复述完成晋级。
