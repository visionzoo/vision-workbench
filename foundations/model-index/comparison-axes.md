# Backbone / visual encoder comparison contract

这份契约先判断对象是否具备比较资格，再记录指标。它不是模型排行榜，也不要求所有视觉架构都能拆成 `backbone / neck / head`。

## 1. 先区分角色

`backbone` 与 `visual encoder` 有交集，但不是同义词：

| 角色 | 在本文中的操作性定义 | 常见输出 | 比较时首先固定 |
|---|---|---|---|
| `backbone` | 在一个具体任务网络中承担主要特征提取，并把任务可消费的特征交给 neck、head 或 decoder | 单层或多层空间特征图、token hierarchy | 下游任务、消费接口、输出层级与训练协议 |
| `visual-encoder` | 把图像或视频编码为下游可消费的视觉表示；下游可以是视觉任务模块，也可以是检索、语言模型、世界模型或策略模块 | 全局 embedding、视觉 token、单尺度或多尺度特征 | 表示语义、粒度、下游消费者与适配方式 |

同一个实现可以在某个组合中同时承担两种角色。例如，一个 ViT 可以作为 VLM 的 visual encoder，也可以在稠密预测系统中被改造成 backbone；但角色必须由**具体组合与接口**证明，不能由模型名称或论文措辞推定。

“可提取中间特征”也不足以证明两个对象可直接互换。TorchVision 能从任意可追踪节点取出中间激活；真正决定比较资格的是选了哪些节点、输出语义与形状，以及下游如何消费这些特征。

## 2. 三种比较层级

### 2.1 完整方案

适用于端到端模型或可运行的系统组合。至少满足：

1. 任务、标签和输出定义相同；
2. 数据、输入、训练预算和评价协议足够接近；
3. 硬件、精度、runtime 和计时边界一致；
4. 明确结论属于完整方案，不能把差异直接归因给某个内部模块。

例如 HRNet-based heatmap 方案与 PFLD 可以在同一眼部关键点任务中比较；若 backbone、输出表征、训练设置和模型规模同时不同，结论只能是系统级差异。

### 2.2 模块

适用于具体组合中的 backbone、visual encoder、neck、接口组件、head 或 task decoder。至少满足：

1. 模块角色相同；
2. 输入、输出和下游消费契约相容；
3. 尽量固定其余模块、数据、训练与后处理；
4. 额外的特征选择、投影、上采样或融合必须计入系统；
5. 不要求所有架构都能强拆成相同模块。

比较 backbone 时，应固定 neck/head、任务输入和训练协议；比较 visual encoder 时，还必须固定输出表示如何被下游读取。若为接入候选而新增投影或融合，结果属于“模块＋适配”的系统比较，不能声称是裸 encoder 优劣。

### 2.3 学习与对齐范式

适用于监督预训练、自监督 DINO、CLIP 类视觉—语言对齐等方案。至少满足：

1. encoder 容量和初始化边界可比较；
2. 预训练数据可见性与训练预算透明；
3. 下游适配和评测协议一致；
4. 同时记录迁移收益与预训练、存储和部署代价。

不能把“使用某种预训练后更好”直接解释为 encoder 架构本身更优。

## 3. 比较资格

每次比较只能取以下一种结论：

| 资格 | 允许做什么 | 典型条件 | 禁止的结论 |
|---|---|---|---|
| `direct` | 在同一表中给出受控差异，并形成当前条件下的选型判断 | 层级、角色、输入输出、消费者、任务和评测协议匹配；主要非目标变量固定 | 宣称跨任务、跨硬件或普遍更优 |
| `controlled-adaptation` | 比较“候选模块＋明确适配”后的系统结果 | 需要投影、特征层选择、上采样、池化或 fusion；适配成本和训练变化完整计入 | 把系统差异全部归因于原模块 |
| `relation-only` | 记录角色、接口差异、证据缺口和未来区分性实验 | 层级不同、输出不可对接、预训练/数据不可分、代码权重缺失或评测条件不透明 | 排名、算差值或据此做采用承诺 |

资格不是对象的永久属性，而是一次具体比较的属性。同一对对象换了任务、consumer、权重或 runtime，必须重新判定。

## 4. 输入、输出与消费者契约

进入 `direct` 或 `controlled-adaptation` 前，至少填写：

| 项目 | 必填内容 |
|---|---|
| 比较对象 | family、具体实现、版本、权重、仓库 revision 和第一方来源 |
| 比较层级 | 完整方案 / 模块 / 学习与对齐范式 |
| 角色 | 在当前组合中的 `backbone`、`visual-encoder` 或其他角色 |
| 输入 | 模态、颜色空间、数值范围、shape/bucket、resize/crop、padding/mask、normalization、batch |
| 输出结构 | tensor 名称与数量、shape、layout、dtype、stride/patch、空间对应关系、可变长度规则 |
| 表示语义 | 全局 embedding、visual token、单尺度/多尺度特征，以及是否经过 pooling、projection 或 normalization |
| 消费者 | neck、head、task decoder、projector、LLM、检索头、world model 或其他明确模块 |
| 适配 | 节点选择、通道/分辨率投影、上采样、融合、token pooling；参数量、算力与延迟一并记录 |
| 训练 | 初始化、冻结策略、预训练来源、数据、分辨率、增强、优化器、周期和随机性控制 |
| 输出任务 | 标签与预测定义、loss、matcher/标签分配、解码和后处理 |

任何无法确认的项写 `not disclosed`、`not available` 或 `not measured`，不能用常见实现补齐官方未披露接口。

## 5. 指标与工程证据

| 维度 | 至少记录 |
|---|---|
| 精度 | 数据集版本、split、样本范围、指标定义、evaluator、均值/方差或重复次数 |
| 复杂度 | 参数量、FLOPs/MACs 口径、输入尺寸；动态输入要记录实际 token/像素数 |
| 速度 | 硬件、精度、batch、runtime/编译器版本、预热、同步方法、P50/P95/P99 和计时边界 |
| 内存 | 权重、峰值工作内存或运行时口径、batch、输入、runtime；可用时记录带宽或中间张量 |
| 导出 | 导出器与框架版本、格式、opset、静态/动态 shape、算子替换、图优化和输出核对 |
| 量化 | PTQ/QAT、校准数据、量化粒度/对称性、排除层、层级误差和最终任务变化 |
| 许可 | 代码、权重、预训练数据和衍生发布分别检查 |

速度与内存必须同时报告模块边界和完整链路边界。理论复杂度、GPU kernel 优势和固定功能 NPU 的真实延迟属于不同证据，不能互相替代。

## 6. 证据等级

| 等级 | 含义 | 可支持的结论 |
|---|---|---|
| 第一方披露 | 论文、官方仓库或维护组织文档 | 对方如何定义、实现和报告 |
| 第三方复现 | 可追溯环境、代码、权重和评测协议 | 在该复现条件下是否重现 |
| 本人受控实验 | 同数据、同协议、同硬件且保留原始结果 | 当前目标条件下的选型判断 |
| 生产/长期观察 | 权属清楚、口径稳定、能排除主要混杂变量 | 适用场景内的工程经验，不自动外推 |

跨论文 AP、FPS、FLOPs 或参数量即使列名相同，也只能作为线索；没有共同协议时一律为 `relation-only`。

## 7. 最小关系索引与压力测试

这张表只验证契约能否表达现有对象，不创建新的 family 页面，也不构成性能排名。

| 对象 | 权威身份 / 使用范围 | 在具体系统中的角色 | 当前比较资格 | 结论边界 |
|---|---|---|---|---|
| [YOLO](families/yolo/README.md) | `model-family` / `complete-solution` | 当前 family 条目代表完整检测方案；具体分支内部才可能识别 backbone | 对 YOLO family 与 TuringViT/CLIP：`relation-only` | 只有选定具体实现、抽出明确输出节点，并固定 detection neck/head、数据和训练协议后，才能做 backbone 替换实验 |
| [TuringViT](families/turingvit/README.md) | `architecture-family` / `reusable-module` | 官方定位为 visual encoder，并声称可接任务 head；可在具体稠密任务组合中承担 backbone | 当前为 `relation-only` | 代码、权重、真实输出接口和独立复现缺失；现在只能登记候选关系，不能与 YOLO 或其他 encoder 排名 |
| [OpenAI CLIP image encoder](https://github.com/openai/CLIP) | 外部反例；本仓库尚未建立 family 条目 | 官方 `encode_image()` 返回与文本表示对齐的 image features，典型 consumer 是相似度或下游 probe | 默认 `relation-only`；改造后可为 `controlled-adaptation` | “visual encoder”不自动等于稠密预测 backbone；若抽取中间 token/feature 并增加 neck，比较对象已包含适配系统 |

压力测试得到的关键结果：

1. 完整检测器、可复用视觉架构和对齐后的全局图像编码器不能因为都“提取视觉特征”而裸排名；
2. `backbone` 是组合内角色，不是 CNN 的同义词；`visual-encoder` 也不是 Transformer 的同义词；
3. 输出可接入不等于公平比较，适配层的训练、计算、内存、导出和量化成本都属于结果；
4. TuringViT 当前证据不足，契约应允许“只建立关系、不做实验”，而不是为了完成表格编造指标；
5. CLIP 在真实持续检索需求出现前只作为反例链接，不触发新目录或模型百科条目。

## 8. 采用与撤销

形成“采用候选 A”的承诺前，必须写清：

- 当前任务、数据、硬件、runtime 和预算；
- 比较资格与未固定变量；
- 选择理由及其证据等级；
- 对至少一个机制不同候选的反证结果；
- 若精度、P95、峰值内存、导出覆盖或量化误差越过什么阈值就撤销。

文档写完、单次跑通或第一方排行榜都不能充当最终 Oracle。

## Sources

- [MMDetection: Customize Models](https://mmdetection.readthedocs.io/en/latest/advanced_guides/customize_models.html)：检测框架中的 backbone、neck、head 等组件角色。
- [TorchVision: Feature extraction for model inspection](https://docs.pytorch.org/vision/main/feature_extraction.html)：从中间节点提取单层或多层特征，并交给下游网络。
- [OpenAI CLIP repository](https://github.com/openai/CLIP)：`encode_image()`、图文表示和零样本/linear-probe 使用方式。
- [TuringViT official project](https://turingvit.github.io/)：TuringViT 的第一方角色和架构披露；本人证据边界见其 family 条目。
