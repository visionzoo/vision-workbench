---
status: working
type: case
rigor: standard
provenance: fixed-public-source-local-execution-and-public-issue-review
evidence_status: partial
owner_review: pending
ip_review: not-applicable
confidence: medium
created: 2026-08-14
updated: 2026-08-14
---

# YOLO26 architecture smoke tests

## Problem and acceptance criteria

仅阅读 YAML 不足以证明实际计算图。本案例针对 Ultralytics YOLO26 建立一个最小、可重复的结构 Oracle，回答以下问题：

- 默认、P2、P6 配置的 stride 和输出张量是否符合结构推导；
- 各个 `C3k2` 实际实例化了 `Bottleneck`、`C3k` 还是 `Bottleneck + PSABlock`；
- one-to-one 分支的 `detach` 是否阻断回到 backbone 的梯度；
- `reg_max=1` 与 `reg_max=16` 是否改变回归通道和 DFL decoder；
- `fuse()` 是否移除 one-to-many head，并保持 one-to-one 输出；
- 默认 E2E ONNX 是否包含 TopK、是否不包含 NMS。

验收以运行时 shape、模块类型、梯度、融合前后输出和 ONNX graph operator 为独立 Oracle。它验证结构合同，不验证检测精度、训练收益或目标部署后端的数值一致性。

## Fixed environment

| Item | Value |
|---|---|
| Ultralytics release | `v8.4.120` |
| Source commit | `b103ba8d0944bfd8de69bfded9778ac5daadd956` |
| Python | 3.10.19 |
| PyTorch | 2.5.1+cu121 |
| Platform | Linux 7.0.0-28-generic x86_64 |
| Input | synthetic zeros/random tensors; no private data or weights |
| Test script | [`yolo26_architecture_smoke_test.py`](yolo26_architecture_smoke_test.py) |
| Recorded output | [`yolo26_architecture_smoke_test_results.json`](yolo26_architecture_smoke_test_results.json) |

Run from the repository root:

```bash
YOLO_CONFIG_DIR=/tmp/yolo26-smoke-config \
python engineering/cases/yolo26_architecture_smoke_test.py \
  --source-root /path/to/ultralytics-v8.4.120 \
  --imgsz 640 \
  --onnx-output /tmp/yolo26-smoke/yolo26n-e2e.onnx
```

The script imports the supplied checkout directly. Do not let a separately installed `ultralytics` package shadow that path.

## Observations

### Scale contracts

| Config | Strides | Dense locations at 640 | E2E output |
|---|---:|---:|---:|
| default | 8, 16, 32 | 8,400 | 1×300×6 |
| P2 | 4, 8, 16, 32 | 34,000 | 1×300×6 |
| P6 | 8, 16, 32, 64 | 8,500 | 1×300×6 |

The default dense branch produced boxes `1×4×8400` and scores `1×80×8400`. The P2/P6 YAML files change feature scales and candidate count, while the E2E postprocess contract remains `B×300×6` for this configuration.

### `C3k2` runtime composition

| YAML layers | Runtime unit |
|---|---|
| 2, 4 | `Bottleneck` |
| 6, 8, 13, 16, 19 | `C3k` |
| 22 | `Sequential(Bottleneck, PSABlock)` |

This is the discriminating check behind the architecture diagrams: the class name `C3k2` alone does not identify the inner computation. Its arguments do.

### Gradient isolation

| Probe loss | Backbone layer 0 gradient sum | one-to-many head | one-to-one head |
|---|---:|---:|---:|
| one-to-one output only | 0.0000 | 0.0000 | 37.9897 |
| one-to-many output only | 7.9043 | 39.7383 | 0.0000 |

The observation supports a narrow implementation claim: the one-to-one path consumes detached features in this revision. It does not prove that the branch has no effect on optimization as a whole; shared initialization, joint loss scheduling and optimizer state remain separate questions.

### Regression and fusion contracts

At a 128×128 probe input, `reg_max=1` produced `1×4×336` raw box channels with an `Identity` decoder; the counterfactual `reg_max=16` produced `1×64×336` with `DFL`.

`fuse()` reduced parameters from 2,572,280 to 2,408,932, removed `cv2/cv3` (one-to-many), retained the one-to-one head, and produced a maximum absolute output difference of 0.0 on the fixed probe. This is one sample, not a complete numerical-equivalence campaign.

### ONNX contract

The temporary 320×320 E2E export had output `1×300×6`, contained `TopK`, and contained no `NonMaxSuppression` node. The ONNX file was a disposable test artifact and is not stored in this repository.

## Version-drift incident

The first run imported `yaml_load`, an API used by the earlier pinned source, and failed against `v8.4.120`; the current source uses `YAML.load`. Updating the test to the current public API made it pass. This is useful evidence in itself: even when `yolo26.yaml` is unchanged, helper APIs, head logic and exporters can move, so a package version plus runtime probe is part of the architecture description.

## Public practice signals

Public Ultralytics issues were reviewed as field reports, not ground truth (Y029):

- E2E and raw outputs are frequently confused (`B×300×6` versus `B×84×8400`), especially when editable and installed packages are mixed.
- An older class-filter/`max_det` interaction shows why tests must include filtering after top-k instead of checking only unfiltered output.
- TensorRT partial-batch failures point to checking dynamic export settings before blaming a model block.
- INT8 reports show that confidence calibration and stale calibration caches can fail even when ranking remains usable; threshold reuse is not a valid accuracy Oracle.
- Current RKNN export deliberately disables E2E where backend TopK support is unsuitable, so “YOLO26 is NMS-free” is not a universal deployment-graph claim.

These reports generate test hypotheses. They do not establish prevalence or causality without a controlled local reproduction.

## Decision and remaining work

The observed contracts are sufficient to use the associated architecture page as a `working` implementation guide. They are insufficient for `validated` because no second environment, training run, official checkpoint accuracy comparison, dynamic-batch export matrix or target-runtime numerical comparison has been completed.

Promotion requires rerunning the script from a clean checkout, reviewing the stored output, and adding at least one independent target-runtime comparison. Roll back any structural modification if its declared shape/gradient/export contract fails, even if model construction itself succeeds.
