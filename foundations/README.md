# Foundations

这里不做模型百科，只保留三类能反复用到的东西：

- `mechanisms/`：一个方法为什么起作用，什么时候会失效；
- `tasks/`：任务输入、输出、指标和常见误差；
- `model-index/`：某个模型族怎么选、怎么查官方资料、怎么落到工程上。

当前已用 [YOLO](model-index/families/yolo/README.md) 把这三层跑通，并完成样板验收；[目标检测架构演变](mechanisms/object-detection-architecture-evolution.md) 与 [DETR](model-index/families/detr/README.md) 作为第二组检测知识基线。关键点方向以 [2D landmark task](tasks/2d-landmark-localization.md) 统一 ROI/整图边界、坐标、visibility 和评价，以 [Keypoint output representations](mechanisms/keypoint-output-representations.md) 区分 direct coordinate、heatmap、dense pose 与 query/set prediction；具体对象分别回到 [PFLD](model-index/families/pfld/README.md)、[HRNet](model-index/families/hrnet/README.md)、[YOLO Pose](model-index/families/yolo/variants.md) 与 [RF-DETR Keypoint Preview](model-index/families/detr/README.md)。[MobileNet](model-index/families/mobilenet/README.md)、[DINO](model-index/families/dino-self-supervised/README.md)、[CLIP](model-index/families/clip/README.md) 与 [TuringViT](model-index/families/turingvit/README.md) 继续按各自对象边界维护。后续 family 仍按实际需要逐个建设，不批量铺目录。

## 怎么使用

碰到具体模型时，按下面顺序查：

1. 先确认它在系统里的角色，是整模型、backbone，还是单个组件；
2. 再看它解决的任务和核心机制；
3. 最后看该模型族的版本、官方资料、训练、评测和部署说明；
4. 真正的转换、量化、性能和故障记录放到 `engineering/`，这里只保留可复用结论和链接。

## 资料边界

官方论文、官方仓库和维护组织文档只说明“官方怎么定义和报告”，不等于本人已经复现。第三方实现和本人经验单独写；官方没披露的内容写 `not disclosed`，不靠推测补齐。

增删和维护规则见 [MAINTENANCE.md](MAINTENANCE.md)。
