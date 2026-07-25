# Model index

模型索引主要回答五个问题：

1. 这个模型在系统里充当什么角色；
2. 它解决什么任务；
3. 哪些版本属于谁，第一方定义在哪里；
4. 结构和训练发生了什么实质变化；
5. 导出、量化和部署时要核对什么。

## 模型角色

角色不是互斥分类，一个模型族可以同时有多个角色。

| Role | 含义 | 例子 |
|---|---|---|
| `task-model` | 输入数据后能直接给出分类、检测、分割等任务结果 | YOLO 检测器、MobileNet 分类模型 |
| `backbone` | 主要负责提取特征，需要接任务头才能输出结果 | MobileNet、ResNet |
| `component` | 被其他网络复用的结构、损失或后处理 | FPN、NMS、DFL |

只有“角色 + 任务 + 评测条件”一致时，两个模型才适合直接比较。YOLO 与 MobileNet 可以都出现在模型索引里，但不能因为同属视觉模型就横向排名。

统一比较口径见 [comparison-axes.md](comparison-axes.md)，登记信息见 [registry.yaml](registry.yaml)。当前已验收样板是 [YOLO](families/yolo/README.md)。
