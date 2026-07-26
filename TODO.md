# TODO

这里同时保留长期积累方向和已经激活的仓库级工作，但不充当视觉知识分类树。候选方向只说明为什么值得积累、何时启动和边界；遇到真实问题或明确检索需求后，才拆成可验收工作包。

## 使用规则

- `Active work` 最多同时保留 1–2 项；只有这里的项目才是当前执行承诺。
- `Accumulation candidates` 是开放的积累候选，不是排期、完成度清单或批量建目录许可。
- `Repository maintenance` 与知识建设分开，避免迁移、整理任务与视觉对象并列分类。
- 一条分支原则上只完成一个激活工作包；未激活候选不预拆子项。
- 同一事实只有一个权威条目；目录表达归属，元数据和链接表达模块、范式、任务、系统及证据关系。
- 每次修改都检查是否产生新的维护责任；若影响权威来源、比较资格、验收门、撤销条件、元数据或交叉引用，必须在同一变更中同步更新，不能只增加内容。
- family 页面只有通过 Foundations 新增门槛后才创建；真实重复需求出现前不新增模板或空目录。
- 真实案例必须区分公开资料、第三方结果、本人独立验证和公司/IP 受限观察；不能以“文档已写”代替验证。

## Active work

### 2B. 面向任务与部署约束的 Backbone 选型

- **来源方向**：Visual feature extraction；前置 2A 比较契约已合并。
- **交付物**：把比较契约落实为可执行的选型经验：先判断瓶颈是否来自 backbone，再按任务表征、结构分面、输出接口、预训练、目标 runtime、量化和维护成本筛选候选；建立分阶段实验、采用/撤销门和变更驱动的维护反馈闭环。
- **边界**：不建立跨论文排行榜，不把“全面性”解释为批量创建候选 family 页面，不把用户任务中的标签、ROI、head、坐标链或转换问题偷换成架构问题；YOLO 版本实现与通用 Backbone 选型只保留一个事实源。
- **验收出口**：能直接指导 ROI 分类、局部关键点和轻量检测三类实验；用多分面覆盖常用候选而不制造互斥分类树；架构收益与预训练收益分开；训练前先做接口/算子可行性；最终采用由同协议任务结果与目标硬件 INT8 结果共同决定；每次变更都能反向更新维护规则。
- **状态**：实质条目已在独立分支实现，等待本人验收。

## Accumulation candidates

候选项只在真实任务、持续检索需求、可披露案例或明确决策出现时激活；启动时再确定交付物、依赖和验收标准。

| 候选方向 | 启动信号 | 当前边界 |
|---|---|---|
| **2. Visual feature extraction** | 需要在具体任务和硬件约束下选择或替换 backbone / visual encoder | 当前只激活 2B；具体模型家族按需建设 |
| **Classification** | 出现图像、ROI 或帧状态分类的复用需求 | 区分闭集与开放词汇、单帧状态与时序事件；眼睛开闭等真实经验可进入 |
| **Neck / feature fusion** | 多尺度或多层融合成为可区分变量 | 只维护中间特征转换与融合；不建立统一 Adapter 父项 |
| **Task output representation** | 任务误差需要反推 head、decoder、loss、matcher 或解码选择 | 输出链路相邻不等于同一对象；任务特有事实回到具体任务 |
| **Self-supervised visual representation** | 需要判断监督预训练与 DINO 等自监督谱系的真实差异 | Meta DINO 与检测器 DINO 分开 |
| **Vision-language alignment** | CLIP 类对齐或开放词汇能力进入真实视觉决策 | 区分模型谱系、训练方法与下游任务，不扩成通用 VLM 百科 |
| **Video representation** | 单帧表征不足，且需要学习时空特征 | 不把跟踪关联、报警状态机或“使用视频”混成一个任务 |
| **Detection / DETR** | 现有 YOLO 经验需要与集合预测或开放词汇检测比较 | 检测器 DINO 归 DETR 关系；通用 backbone 机制不重复 |
| **2D landmark / keypoint localization** | 眼部等局部关键点方案需要可复现实验与选型 | 当前不承诺人体、动物或 3D pose 全域建设 |
| **Multi-object tracking** | 逐帧检测无法满足身份连续性或轨迹需求 | 与视频表征、事件判定分别维护 |
| **Temporal recognition and event decision** | 单帧状态不足以定义事件、触发或恢复 | 学习式时序识别/定位归任务知识；平滑、状态机、报警触发与恢复归 Engineering |
| **Segmentation** | 掩码相对检测框产生明确新增价值 | 语义、实例、可提示分割先区分任务，再建立关系 |
| **VLM-assisted visual workflows** | 标注、筛选、难例分析或评测辅助有真实基线可比较 | 开放词汇分类/检测归任务能力；VLM 不能自证效果 |
| **VLA visual interface brief** | 需要说明视觉模块在具身闭环中的接口和约束 | 只保留视觉相关边界；机器人学、控制和通用 VLA 转独立载体 |

接口投影、跨模态 projector 和 PEFT adapter 因名称相似但问题不同，不建立共同父项：前者是具体接口组件，中者是多模态架构关系，后者是参数高效微调方法。只有真实对象出现时，才在相应权威条目中登记。

扩散生成、3D 视觉以及其他方向暂不进入正式候选表；真实问题触发后再判断是否符合本仓库边界。

## Repository maintenance

### 1. 盘点 ProjectCollection 中仍有价值的内容

- **来源**：[visionzoo/projectcollection](https://github.com/visionzoo/projectcollection)。
- **目标仓库**：[visionzoo/vision-workbench](https://github.com/visionzoo/vision-workbench)。
- **下一步**：需要启动时，先只做内容盘点与去向清单；每项标明权威对象、证据/IP 状态及迁移、保留或放弃建议。
- **边界**：不整体复制旧仓，不因盘点预建目录；单对象迁移、迁移顺序以及旧仓保留、归档或删除均另行确认。
- **状态**：Deferred。
