# Model index

模型索引主要回答六个问题：

1. 这个模型或模块在系统里充当什么角色；
2. 它解决什么任务；
3. 哪些版本属于谁，第一方定义在哪里；
4. 结构和训练发生了什么实质变化；
5. backbone、neck、head 与完整任务模型如何组合；
6. 导出、量化和部署时要核对什么。

## 分类原则

模型索引按对象在视觉系统中的稳定角色和逻辑关系组织，不按当前对它执行的动作组织。“调研一个新模型”中的“调研”决定证据搜集方式，不会把模型变成 Research 条目；模型仍应放入对应 family，新的机制回到 `mechanisms/`，真实部署结果回到 `engineering/`。

架构知识优先按 `backbone / neck / head` 三类可复用模块角色建立关系，再连接完整 task model、训练范式与工程案例。模型家族仍用于维护可追溯谱系，但不会因为本轮提到了某个名字，就把它提升为与模块并列的仓库级分类。

只有当材料形成了可证伪的独立问题、实验和 finding，才进入 `research/`。不能为了持续关注新模型，再复制一套候选 registry、状态流或版本标签。

## 模型与模块角色

角色不是互斥分类，一个模型族可以同时有多个角色；同一名称在不同用法下也可能承担不同角色。

| Role | 含义 | 例子 |
|---|---|---|
| `task-model` | 输入数据后能直接给出分类、检测、关键点或分割等任务结果 | YOLO 检测器、完整 PFLD |
| `backbone` | 提取分层特征或视觉 token，供下游模块使用 | ResNet、MobileNet、ConvNeXt、ViT、HRNet、TuringViT |
| `neck` | 转换或融合 backbone 的跨层、跨尺度特征 | FPN、PAN、BiFPN |
| `head` | 将共享特征转换为分类、框、关键点、mask 等任务输出 | YOLO detection head、heatmap keypoint head |
| `component` | 不适合归入前三类、但可被网络复用的结构、损失或后处理 | NMS、DFL、matcher |

只有“角色 + 任务 + 评测条件”一致时，两个对象才适合直接比较。完整 HRNet 关键点网络与 PFLD 可以在同一关键点任务中做系统级比较，但不能由此直接推导其 backbone 或输出表征谁普遍更优；需要控制数据、输入、训练、模型规模和计时边界。

统一比较口径见 [comparison-axes.md](comparison-axes.md)，登记信息见 [registry.yaml](registry.yaml)。

当前条目：

- [YOLO](families/yolo/README.md)：实时目标检测模型族，目录样板已验收；
- [TuringViT](families/turingvit/README.md)：高分辨率图像/视频视觉编码器与 backbone，内容仍待本人验收。
