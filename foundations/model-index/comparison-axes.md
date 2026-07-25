# Model comparison

先确定比较层级，再看数字大小。完整方案、单个模块和学习范式不是同一种比较对象。

## 1. 完整方案比较

适用于端到端模型或可运行的系统组合。至少满足：

1. 任务和输出定义相同；
2. 数据、输入、训练预算和评价指标足够接近；
3. 硬件、精度、runtime 和计时边界一致；
4. 明确比较的是完整方案，不能把差异直接归因给某个内部模块。

例如 HRNet-based heatmap 方案与 PFLD 可以在同一眼部关键点任务中比较；若 backbone、输出表征、训练设置和模型规模同时不同，结论只能是系统级差异。

## 2. 模块比较

适用于 backbone、visual encoder、neck、adapter、head 或 task decoder。至少满足：

1. 模块角色和输入输出接口一致；
2. 尽量固定其余模块、训练设置和后处理；
3. 对不能控制的变量逐项说明；
4. 不要求所有架构都能强拆成 backbone / neck / head。

例如比较 backbone 时固定 fusion、head、输入和训练协议；比较关键点 head 时固定上游特征、标签定义与解码方式。

## 3. 学习与对齐范式比较

适用于监督预训练、自监督 DINO、CLIP 等训练或对齐方案。至少满足：

1. encoder 容量和初始化边界可比较；
2. 预训练数据、数据可见性与训练预算透明；
3. 下游适配协议一致；
4. 同时报告迁移收益与预训练、存储、部署代价。

不能把“使用某种预训练后更好”直接解释为 encoder 架构本身更优。

## 必须记录的信息

| 项目 | 至少记录 |
|---|---|
| 身份 | 模型/模块、版本、权重、仓库 revision、第一方来源 |
| 比较层级 | 完整方案 / 模块 / 学习与对齐范式 |
| 对象类型 | end-to-end model family / reusable architecture / component / learning-or-alignment family |
| 模块角色 | backbone / visual encoder / neck / adapter / head / task decoder；不适用时写 `not applicable` |
| 任务与输出 | 检测 / 分类 / 关键点 / 分割等，以及标签和输出定义 |
| 结构组合 | encoder/backbone、特征融合或 adapter、head/decoder、loss、后处理 |
| 训练 | 初始化、预训练来源、数据、分辨率、主要增强、优化器和训练周期 |
| 精度 | 数据集版本、split、指标定义、evaluator |
| 复杂度 | 参数量、FLOPs/MACs 口径、输入尺寸 |
| 速度 | 硬件、精度、batch、runtime、预热和计时边界 |
| 内存 | 峰值或运行时口径、batch、输入和 runtime |
| 导出 | 导出器版本、格式、opset、动态或固定 shape |
| 量化 | PTQ/QAT、校准数据、量化方式和精度变化 |
| 许可 | 代码、权重和数据分别检查 |
| 证据 | 第一方报告、第三方复现或本人实验 |

缺项写 `not disclosed` 或 `not measured`。不同论文里的 AP、FPS 和 FLOPs 不能因为列名相同就直接排序。
