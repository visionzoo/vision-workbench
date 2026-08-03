---
title: Object-tracking heatmap baseline
status: working
type: case
rigor: standard
created: 2026-08-03
updated: 2026-08-03
confidence: medium
provenance: independent-private-repo at 6870134b06f144004dd945e4e356bf9a404029c9; upstream-public-source at 81d076f8c38a49126cc1d5be369c8c107ec69789
evidence_status: partial
owner_review: pending
ip_review: pending
tags: [object-tracking, heatmap, yolo26, colab, reproducibility]
related: [../playbooks/colab-to-github-project-intake.md, ../../projects/registry.yaml, ../../foundations/model-index/families/yolo/README.md]
---

# Object-tracking heatmap baseline

## Problem and current frame

目标是把 Ultralytics 的 Heatmap Colab 示例变成第一个受 `vision-workbench` 管理的独立私有项目，并回答一个受限问题：固定公开上游、依赖、模型和视频输入后，目标跟踪热力图的最小视频链路能否产生可解码的非空输出。

本项目不把“生成了一段视频”解释为跟踪准确、热力图有效或适合真实摄像头。Heatmap 在这个边界内是跟踪轨迹的空间累积可视化，不是分类激活图或可解释性方法。

## Provenance and IP boundary

独立仓库为 [visionzoo/object-tracking-heatmap-baseline](https://github.com/visionzoo/object-tracking-heatmap-baseline)，当前是 private / incubating。初始提交固定为 `6870134b06f144004dd945e4e356bf9a404029c9`。

notebook 派生自 Ultralytics 公开仓库 revision `81d076f8c38a49126cc1d5be369c8c107ec69789` 的 [`examples/heatmaps.ipynb`](https://github.com/ultralytics/ultralytics/blob/81d076f8c38a49126cc1d5be369c8c107ec69789/examples/heatmaps.ipynb)。上游仓库在该 revision 使用 AGPL-3.0；项目保留同许可证、固定源链接、Git blob、下载哈希和修改说明，不声称拥有上游实现、模型、权重、样例视频、商标或文档。

当前未纳入公司代码、数据、模型、设备或客户材料，但许可证适用性和本人最终权属判断尚未审查，因此保持 `ip_review: pending`，不得公开。

## Current beliefs and alternatives

当前证据支持：固定的 Ultralytics 8.4.115 核心链路能在一次本机 CUDA 环境中处理官方公开视频，并写出可解码视频。

仍存活的替代解释包括：

- 结果只证明 OpenCV writer 和模型调用没有中断，不能证明跟踪 ID 稳定或累积强度符合预期；
- 本机环境已有 PyTorch/OpenCV 等系统依赖，成功可能无法迁移到干净 Colab；
- 官方短视频可能只覆盖容易路径，不能代表遮挡、镜头运动、低帧率或自定义类别场景；
- 该输出是基于检测与跟踪位置的累计图，而非真实世界停留时间或密度的无偏估计。

## Implemented commitment

已允许并完成的范围：

- 创建边界明确的独立私有仓库，不把可运行 notebook 复制进母库；
- 固定上游 revision、`ultralytics==8.4.115`、`lap==0.5.13` 和 `shapely==2.1.2`；
- 使用 Ultralytics 官方公开 `solutions_ci_demo.mp4` 和运行时下载的 `yolo26n.pt`；
- 清空 notebook outputs，忽略视频、权重、缓存和数据目录；
- 保留 AGPL-3.0、归属与修改记录；
- 将项目链接、状态、许可证和 IP 门登记到 `projects/registry.yaml`。

当前未允许自动公开，也没有把 smoke 结果晋级为准确性或产品结论。若发现许可证、权属、凭据或敏感输出问题，停止公开/合并并按完整 Git 历史处理；普通实现错误通过后续 PR 回退。

## Verification evidence

项目仓库的 `VALIDATION.md` 记录了 2026-08-03 本机核心 smoke：

- 固定包版本导入成功；首次运行暴露 `lap` 与 `shapely` 隐式依赖，随后已显式固定；
- 官方输入处理 62 帧，输出文件为 320330 bytes；
- `ffprobe` 独立解码为 MPEG-4、640 × 360、30 fps、62 帧、2.066667 秒；
- 输入、模型和输出均记录 SHA-256；第二次核心复跑输出哈希一致，且未再次触发依赖自动安装；
- 本地隔离环境缺少 `IPython`，所以展示调用被排除；完整 notebook 尚未在干净 Colab 中执行。

这些证据允许 `evidence_status: partial`，但不足以把条目或项目提升为 validated / validating。

## Next discriminating actions

1. 从仓库 Colab 链接启动全新运行时，完整顺序执行 notebook，记录 Python、GPU、关键依赖、输入/模型/输出哈希和输出视频可播放性；
2. 用带已知轨迹的短合成视频检查热力累积位置是否与 Oracle 匹配，而不只检查文件存在；
3. 分别制造短暂漏检、遮挡和摄像机运动，判断热区变化来自真实停留、跟踪漂移还是画面坐标变化；
4. 本人审查 AGPL-3.0 与预期复用方式；如果未来涉及商业或网络服务，先完成单独许可判断。

## Current conclusion

第一个 Colab 项目已形成私有、可追溯、可回滚的最小基线，并通过一次本机核心链路验证。Colab 端到端、跟踪质量、热力图有效性、真实数据适用性和公开许可仍未验证；项目维持 incubating，知识条目维持 working / partial / pending。
