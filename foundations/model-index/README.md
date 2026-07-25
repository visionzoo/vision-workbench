# Model index

模型索引主要回答七个问题：

1. 当前条目是什么类型的知识对象；
2. 它在具体系统中承担哪些模块角色；
3. 它解决什么任务或支持什么系统；
4. 哪些版本属于谁，第一方定义在哪里；
5. 结构、训练或对齐方式发生了什么实质变化；
6. 它与完整模型、其他模块和工程案例如何组合；
7. 导出、量化和部署时要核对什么。

## 分类原则

模型索引按知识对象及其关系组织，不按当前对它执行的动作组织。“调研一个新模型”中的“调研”只决定证据搜集方式，不会把模型变成 Research 条目；新的机制回到 `mechanisms/`，真实部署结果回到 `engineering/`，可证伪问题、实验和 finding 才进入 `research/`。

本索引使用多个正交维度，不建立一棵假装互斥的统一分类树：

| 维度 | 回答的问题 | 例子 |
|---|---|---|
| 对象类型 | 当前登记的是完整模型族、可复用架构族，还是组件族 | YOLO 是完整模型族；TuringViT 是可复用架构族 |
| 模块角色 | 该对象在某个具体系统中承担什么职责 | backbone、visual encoder、neck、adapter、head、task decoder |
| 学习与对齐 | 表征如何获得或对齐 | 监督预训练、自监督 DINO、CLIP 对齐 |
| 任务 | 完整方案解决什么问题 | 检测、关键点、分割、跟踪 |
| 系统应用 | 视觉能力如何进入更大系统 | VLM 辅助标注、VLA 感知接口 |

这些维度允许交叉：同一对象可承担多个角色，也可服务多个任务；但事实只在一个权威条目维护，其他位置通过关系链接引用。`backbone / neck / head` 是重要的模块视角，不是适用于所有视觉网络的本体或强制目录结构。

## 对象类型

| Object type | 含义 | 例子 |
|---|---|---|
| `end-to-end-model-family` | 能以完整方案直接完成任务的可追溯模型谱系 | YOLO、完整 PFLD、检测器 DINO |
| `reusable-architecture-family` | 可作为一个或多个系统模块复用的架构谱系 | ResNet、HRNet、ViT、TuringViT |
| `reusable-component-family` | 边界明确、可嵌入其他架构的组件谱系 | FPN、BiFPN、特定 adapter |
| `learning-or-alignment-family` | 主要由训练或对齐目标定义的可追溯谱系 | 自监督 DINO、CLIP |

对象类型描述“它是什么”；不能用来代替模块角色、任务或应用场景。

## 模块角色

模块角色描述“它在这个系统里做什么”，允许多值，也允许因组合方式改变：

| Module role | 含义 | 例子 |
|---|---|---|
| `backbone` | 为任务网络提取分层特征 | ResNet、HRNet |
| `visual-encoder` | 将图像或视频编码为可供下游消费的表示 | ViT、TuringViT、CLIP image encoder |
| `neck` | 位于主要特征提取与任务输出之间的特征转换或融合模块 | FPN、PAN、BiFPN |
| `adapter` | 对齐分辨率、通道、模态或参数高效迁移接口 | projection adapter、跨模态 adapter |
| `head` | 将上游特征转换为局部任务输出 | YOLO detection head、heatmap keypoint head |
| `task-decoder` | 通过 query、token 或迭代解码产生任务结果 | DETR decoder、mask decoder |

`neck` 与 `head` 是常用工程术语，但不要求每个架构都有独立对应模块。loss、matcher、标签分配和后处理建立关系，不因位于输出链路就自动归为 head。

只有比较层级、对象类型或模块角色、任务和评测条件都匹配时，两个对象才适合直接比较。完整 HRNet-based 关键点方案与 PFLD 可以做系统级比较，但不能由此直接推导其 backbone 或输出表征谁普遍更优。

统一比较口径见 [comparison-axes.md](comparison-axes.md)，登记信息见 [registry.yaml](registry.yaml)。

当前条目：

- [YOLO](families/yolo/README.md)：实时目标检测模型族，目录样板已验收；
- [TuringViT](families/turingvit/README.md)：高分辨率图像/视频视觉编码器与 backbone，内容仍待本人验收。
