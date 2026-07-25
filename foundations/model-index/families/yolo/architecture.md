# Architecture

YOLO 各分支变化很多，但真正需要抓住的是四个位置：多尺度特征、标签分配、检测头、结果选择。通用解释见 [目标检测的四个核心机制](../../../mechanisms/object-detection-core.md)。

## 主要变化

| 变化 | 代表分支 | 解决什么 | 边界 | Source |
|---|---|---|---|---|
| 从整图一次预测检测结果 | YOLOv1 | 把检测做成单次前向的回归问题 | 网格限制明显，定位误差较多 | Y001 |
| anchor、多尺度训练和多尺度预测 | YOLOv2、YOLOv3 | 提高不同尺寸目标的覆盖 | 依赖 anchor、解码和 NMS | Y002–Y003 |
| 更强的 backbone 与特征融合 | YOLOv4、YOLOv5、YOLOv7、YOLOv8 等 | 改善特征提取和多尺度融合 | 同名模块在不同仓库里不一定相同 | Y004、Y007、Y011–Y012 |
| anchor-free 与解耦头 | YOLOX、PP-YOLOE、YOLOv8 等 | 简化先验框，分开分类与定位 | 仍要核对正样本分配和输出解释 | Y008–Y009、Y012 |
| 重参数化 | YOLOv6、YOLOv7 等 | 训练时增加表达，部署时合并结构 | 必须区分训练图和推理图 | Y010–Y011 |
| 端到端、NMS-free | YOLOv10、YOLO26 | 减少后处理和端到端延迟 | 是否真正免 NMS 取决于实现和导出图 | Y017、Y023 |
| 视觉语言与开放词汇 | YOLO-World、YOLOE | 用文本或视觉提示扩展类别 | prompt、词汇缓存和权重不能跨实现混用 | Y018、Y021 |

完整分支归属只在 [Variants](variants.md) 维护。Source ID 在 [Sources](sources.md) 查询。

## 看一个具体权重时

```text
input → preprocessing → backbone → feature fusion → head
      → decode → score/class handling → NMS or end-to-end selection
```

至少确认：仓库 revision、权重来源、输入预处理、输出张量、stride、anchor/anchor-free、坐标格式、训练专用模块是否已融合，以及 NMS 在模型内还是模型外。开放词汇模型还要确认文本编码器或词汇嵌入是否仍在运行时图中。
