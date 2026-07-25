# Model index

模型索引主要回答八个问题：

1. 当前条目是什么类型的知识对象；
2. 它可以作为完整方案、可复用模块还是预训练来源；
3. 它在具体系统中承担哪些模块角色；
4. 它通过什么学习或对齐方式获得能力；
5. 它解决什么视觉任务、进入什么系统上下文；
6. 哪些版本属于谁，第一方定义在哪里；
7. 它与其他模型、组件、任务、案例和证据是什么关系；
8. 导出、量化和部署时要核对什么。

## 分类原则

模型索引按知识对象及其关系组织，不按当前对它执行的动作组织。“调研一个新模型”中的“调研”只决定证据搜集方式，不会把模型变成 Research 条目；新的机制回到 `mechanisms/`，真实部署结果回到 `engineering/`，可证伪问题、实验和 finding 才进入 `research/`。

本索引不建立一棵假装互斥且穷尽的统一分类树，也不把分面复制为目录：

| 分面 | 回答的问题 | 例子 |
|---|---|---|
| `entity_kind` | 权威条目本身是什么 | model family、architecture family、component family、method family |
| `usage_scopes` | 它以多大范围被使用 | complete solution、reusable module、pretraining source |
| `module_roles` | 它在具体组合中承担什么职责 | backbone、visual encoder、neck、head、task decoder |
| `learning_paradigms` | 表征或任务行为如何获得、适配或对齐 | supervised、self-supervised、vision-language alignment |
| `tasks` | 完整系统解决什么视觉问题 | classification、detection、2D keypoint localization、segmentation、tracking |
| `system_contexts` | 视觉能力如何进入更大工作流或闭环 | VLM-assisted labeling、VLA perception interface |
| `relations` | 它与哪些谱系、组件、任务、案例和替代方案相关 | derived-from、uses、pretrained-by、evaluated-in、alternative-to |

字段允许为空和多值；新对象只填写有证据的关系。事实只在一个权威条目维护，其他位置通过 typed relation 或普通链接引用。

## Entity kind 与 usage scope

`entity_kind` 描述对象身份，`usage_scopes` 描述它如何被使用，两者不能互相代替：

| Entity kind | 含义 | 例子 |
|---|---|---|
| `model-family` | 以可追溯版本谱系维护的一组完整或近完整模型 | YOLO、检测器 DINO |
| `architecture-family` | 主要由可复用结构机制和接口定义的架构谱系 | ResNet、HRNet、ViT、TuringViT |
| `component-family` | 边界明确、可嵌入其他架构的组件谱系 | FPN、BiFPN |
| `method-family` | 主要由训练、对齐、适配或推理方法定义的谱系 | 自监督 DINO、PEFT 方法 |

例如，一个 architecture family 可以同时具有 `reusable-module` 和 `pretraining-source` 使用范围；一个 model family 是否能拆出可复用模块，需要由具体实现和关系证明，不能仅靠名称推定。

## Module roles

模块角色描述“它在这个系统里做什么”，允许多值，也允许因组合方式改变：

| Module role | 含义 | 例子 |
|---|---|---|
| `backbone` | 为任务网络提取分层特征 | ResNet、HRNet |
| `visual-encoder` | 将图像或视频编码为可供下游消费的表示 | ViT、TuringViT、CLIP image encoder |
| `neck` | 位于主要特征提取与任务输出之间的特征转换或融合模块 | FPN、PAN、BiFPN |
| `head` | 将上游特征转换为局部任务输出 | YOLO detection head、heatmap keypoint head |
| `task-decoder` | 通过 query、token 或迭代解码产生任务结果 | DETR decoder、mask decoder |

`backbone` 与 `visual-encoder`、`head` 与 `task-decoder` 是相邻但不等同的角色。loss、matcher、标签分配和后处理只建立关系，不因位于输出链路就自动归为 head。

本索引不定义统一的 `adapter` 角色：分辨率/通道投影属于具体接口组件，跨模态 projector 属于多模态架构关系，PEFT adapter 属于学习方法。共享词名不能替代对象身份。

## 比较边界

只有比较层级、对象身份或使用范围、模块角色、任务和评测条件都匹配时，两个对象才适合直接比较。完整 HRNet-based 关键点方案与 PFLD 可以做系统级比较，但不能由此直接推导其 backbone 或输出表征谁普遍更优。

Classification 是与 detection、keypoint localization 等并列的任务；visual encoding 是模块角色或能力，不是同层任务。开放词汇分类/检测仍归任务能力，只有标注、筛选、难例分析和评测辅助等更大流程归 VLM system context。

统一比较口径见 [comparison-axes.md](comparison-axes.md)，登记信息见 [registry.yaml](registry.yaml)；分面组织决策见 [Decision 0005](../../governance/decisions/0005-use-faceted-model-relations.md)。

当前条目：

- [YOLO](families/yolo/README.md)：实时目标检测模型族，目录样板已验收；
- [TuringViT](families/turingvit/README.md)：高分辨率图像/视频视觉编码器与 backbone，内容仍待本人验收。
