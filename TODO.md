# TODO

这里同时保留长期积累方向和已经激活的仓库级工作，但不充当视觉知识分类树。候选方向只说明为什么值得积累、何时启动和边界；遇到真实问题或明确检索需求后，才拆成可验收工作包。

## 使用规则

- `Active work` 最多同时保留 1–2 项；只有这里的项目才是当前执行承诺。
- `Accumulation candidates` 是开放的积累候选，不是排期、完成度清单或批量建目录许可。
- `Repository maintenance` 与知识建设分开，避免迁移、整理任务与视觉对象并列分类。
- 一条分支原则上只完成一个激活工作包；未激活候选不预拆子项。
- 同一事实只有一个权威条目；目录表达归属，元数据和链接表达模块、范式、任务、系统及证据关系。
- Foundations 内容修改按照 `foundations/MAINTENANCE.md` 执行维护影响检查；TODO 只记录工作包及其影响结论，不承载详细维护规则。只有发现新的维护责任，或影响权威来源、比较资格、验收门、撤销条件、元数据或交叉引用时，才在同一变更中同步更新对应维护模块；无影响也要在 PR 中记录判断。
- family 页面只有通过 Foundations 新增门槛后才创建；真实重复需求出现前不新增模板或空目录。
- 真实案例必须区分公开资料、第三方结果、本人独立验证和公司/IP 受限观察；不能以“文档已写”代替验证。

## Active work

### Phase 3A：YOLO11 PyTorch → ONNX 数值证据基线

- **Problem**：建立第一条不依赖公司资产、可从固定公开来源复现的 YOLO 工程证据链，先回答静态 FP32 ONNX Runtime CPU 是否在 NMS 前保持固定 PyTorch 实现的输出。
- **Belief**：私有独立仓库 [visionzoo/yolo11-onnx-evidence-baseline](https://github.com/visionzoo/yolo11-onnx-evidence-baseline) 的候选 run `smoke-001` 已记录固定源码、权重、输入、配置、ONNX 和环境身份；接口为 `[1, 84, 8400]`，当前数值门 `allclose(rtol=1e-4, atol=1e-5)` 通过。该结果尚未独立重复或经本人接受。
- **Commitment**：本工作包只激活身份、接口、静态 FP32 导出和数值一致性；不激活训练、COCO 任务精度、图简化、动态 shape、FP16/INT8、RKNN、海思或设备实验。独立仓库保持 `private / incubating / ip_review: pending`。
- **Verification**：在关闭 Phase 3A 前，冻结完整解析依赖锁，从干净环境重新构建并重复 smoke，核对候选报告与原始哈希，再提交本人 `Accept / Revise / Reject / Escalate`。任务级 `|ΔmAP50-95| ≤ 0.001` 留作后续独立工作包。

### MobileNet 架构族信息基线

- **Problem**：现有 backbone 选型页已经覆盖轻量网络分面，但 MobileNet 仍缺少独立 family 身份、v1–v4 机制边界、官方实现责任和目标硬件反证；继续只用“MobileNet 类”会把 depthwise、搜索、激活、注意力和其它轻量谱系混为一谈。
- **Belief**：MobileNet v1–v4 形成可追溯的 Google 架构谱系，值得用一个单页权威条目维护；ShuffleNet、GhostNet、EfficientNet、MobileOne、RepViT 等只建立关系，不能并入一个轻量模型百科。
- **Commitment**：本工作包只新增一个 MobileNet family README、registry 和必要导航；复用现有 comparison/backbone-selection 契约，不新增通用机制页、variants/deployment/sources 子页，不激活权重下载、训练、跨论文排名、导出、量化或目标设备实验。
- **Verification**：本人审查 family 边界、v1–v4 机制图、论文—固定官方代码—概览文档的来源责任、接口与硬件检查，以及停止拆页和停止追踪的维护规则；接受前保持 `working / partial / pending / medium`。

目标检测架构演变与 DETR 信息基线已通过 PR #17 / #18 合并；剩余的本人范围审查由 family 页面和 registry 状态维护，不再占用 `Active work` 执行位。

Phase 2 YOLO 工程证据完整性审查已于 2026-07-28 通过本人审查并关闭：本轮没有恢复出模型—配置—导出—运行—评测的完整链路，两篇历史案例继续保持 `working / unverified / pending / low`。本次接受只覆盖证据身份纠正、盘点边界、IP 门和未来验证合同，不验证历史指标、转换结果或板端行为；真实训练、转换和设备实验按独立工作包重新激活。

YOLO family 信息审校已于 2026-07-27 通过本人审查；其条目继续保持 `working / partial / medium`，不因工程审查自动晋级。

## Accumulation candidates

候选项只在真实任务、持续检索需求、可披露案例或明确决策出现时激活；启动时再确定交付物、依赖和验收标准。

| 候选方向 | 启动信号 | 当前边界 |
|---|---|---|
| **2. Visual feature extraction** | 需要在具体任务和硬件约束下选择或替换 backbone / visual encoder | MobileNet family 信息基线已激活；其它 family 仍按真实需求启动。具体选型、训练、适配和硬件验证另行激活 |
| **Classification** | 出现图像、ROI 或帧状态分类的复用需求 | 区分闭集与开放词汇、单帧状态与时序事件；眼睛开闭等真实经验可进入 |
| **Neck / feature fusion** | 多尺度或多层融合成为可区分变量 | 只维护中间特征转换与融合；不建立统一 Adapter 父项 |
| **Task output representation** | 任务误差需要反推 head、decoder、loss、matcher 或解码选择 | 输出链路相邻不等于同一对象；任务特有事实回到具体任务 |
| **Self-supervised visual representation** | 需要判断监督预训练与 DINO 等自监督谱系的真实差异 | Meta DINO 与检测器 DINO 分开 |
| **Vision-language alignment** | CLIP 类对齐或开放词汇能力进入真实视觉决策 | 区分模型谱系、训练方法与下游任务，不扩成通用 VLM 百科 |
| **Video representation** | 单帧表征不足，且需要学习时空特征 | 不把跟踪关联、报警状态机或“使用视频”混成一个任务 |
| **Detection / DETR** | 固定任务、训练预算和目标硬件后，需要与 YOLO 做受控比较 | 架构演变与 DETR 信息基线已合并并待审查；检测器 DINO 归 DETR，自监督 DINO 分开；未激活训练或硬件结论 |
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
