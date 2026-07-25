# Model index

模型索引主要回答五个问题：

1. 这个模型在系统里充当什么角色；
2. 它解决什么任务；
3. 哪些版本属于谁，第一方定义在哪里；
4. 结构和训练发生了什么实质变化；
5. 导出、量化和部署时要核对什么。

## 分类原则

模型索引按对象在视觉系统中的稳定角色和逻辑关系组织，不按当前对它执行的动作组织。“调研一个新模型”中的“调研”决定证据搜集方式，不会把模型变成 Research 条目；模型仍应放入对应 family，新的机制回到 `mechanisms/`，真实部署结果回到 `engineering/`。

只有当材料形成了可证伪的独立问题、实验和 finding，才进入 `research/`。不能为了持续关注新模型，再复制一套候选 registry、状态流或版本标签。

## 模型角色

角色不是互斥分类，一个模型族可以同时有多个角色。

| Role | 含义 | 例子 |
|---|---|---|
| `task-model` | 输入数据后能直接给出分类、检测、分割等任务结果 | YOLO 检测器、MobileNet 分类模型 |
| `backbone` | 负责提取特征或视觉 token，需要接任务头、LLM 或 policy 才能输出最终结果 | MobileNet、ResNet、TuringViT |
| `component` | 被其他网络复用的结构、损失或后处理 | FPN、NMS、DFL |

只有“角色 + 任务 + 评测条件”一致时，两个模型才适合直接比较。YOLO 与 MobileNet 可以都出现在模型索引里，但不能因为同属视觉模型就横向排名。

统一比较口径见 [comparison-axes.md](comparison-axes.md)，登记信息见 [registry.yaml](registry.yaml)。

当前条目：

- [YOLO](families/yolo/README.md)：实时目标检测模型族，目录样板已验收；
- [TuringViT](families/turingvit/README.md)：高分辨率图像/视频视觉编码器与 backbone，内容仍待本人验收。
