#!/usr/bin/env python3
"""Reproducible structural smoke tests for an Ultralytics YOLO26 source checkout."""

from __future__ import annotations

import argparse
import copy
import gc
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True, help="Ultralytics source checkout root")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--onnx-output", type=Path)
    return parser.parse_args()


def grad_abs(module) -> float:
    return float(sum(p.grad.abs().sum() for p in module.parameters() if p.grad is not None))


def shape_of(value):
    if hasattr(value, "shape"):
        return list(value.shape)
    return type(value).__name__


def build_model(DetectionModel, cfg, nc=80):
    return DetectionModel(cfg, ch=3, nc=nc, verbose=False)


def model_contract(DetectionModel, cfg: Path, imgsz: int, collect_layers=False) -> dict:
    import torch

    model = build_model(DetectionModel, cfg).eval()
    shapes = {}
    hooks = []
    if collect_layers:
        for i, layer in enumerate(model.model[:-1]):
            hooks.append(
                layer.register_forward_hook(
                    lambda _module, _inputs, output, index=i: (shapes.__setitem__(index, shape_of(output)), None)[1]
                )
            )
    with torch.inference_mode():
        final, raw = model(torch.zeros(1, 3, imgsz, imgsz))
    for hook in hooks:
        hook.remove()
    result = {
        "strides": model.stride.tolist(),
        "final": shape_of(final),
        "one2many_boxes": shape_of(raw["one2many"]["boxes"]),
        "one2many_scores": shape_of(raw["one2many"]["scores"]),
        "one2one_boxes": shape_of(raw["one2one"]["boxes"]),
        "one2one_scores": shape_of(raw["one2one"]["scores"]),
    }
    if collect_layers:
        result["layers"] = shapes
        result["c3k2_units"] = {
            str(i): [type(x).__name__ for x in layer.m]
            for i, layer in enumerate(model.model)
            if type(layer).__name__ == "C3k2"
        }
        result["layer22_inner"] = [type(x).__name__ for x in model.model[22].m[0]]
    del model
    gc.collect()
    return result


def gradient_contract(DetectionModel, cfg: Path) -> dict:
    import torch

    torch.manual_seed(0)
    model = build_model(DetectionModel, cfg).train()
    head = model.model[-1]

    preds = model(torch.randn(1, 3, 128, 128))
    one2one_probe = preds["one2one"]["boxes"].mean() + preds["one2one"]["scores"].mean()
    one2one_probe.backward()
    one2one = {
        "backbone_layer0": grad_abs(model.model[0]),
        "one2many_head": grad_abs(head.cv2) + grad_abs(head.cv3),
        "one2one_head": grad_abs(head.one2one_cv2) + grad_abs(head.one2one_cv3),
    }

    model.zero_grad(set_to_none=True)
    preds = model(torch.randn(1, 3, 128, 128))
    one2many_probe = preds["one2many"]["boxes"].mean() + preds["one2many"]["scores"].mean()
    one2many_probe.backward()
    one2many = {
        "backbone_layer0": grad_abs(model.model[0]),
        "one2many_head": grad_abs(head.cv2) + grad_abs(head.cv3),
        "one2one_head": grad_abs(head.one2one_cv2) + grad_abs(head.one2one_cv3),
    }

    assert one2one["backbone_layer0"] == 0 and one2one["one2one_head"] > 0
    assert one2many["backbone_layer0"] > 0 and one2many["one2many_head"] > 0
    return {"one2one_probe": one2one, "one2many_probe": one2many}


def regression_contract(DetectionModel, yaml_api, cfg: Path) -> dict:
    import torch

    config = yaml_api.load(cfg)
    direct = build_model(DetectionModel, copy.deepcopy(config)).train()
    dfl_config = copy.deepcopy(config)
    dfl_config["reg_max"] = 16
    dfl = build_model(DetectionModel, dfl_config).train()
    with torch.no_grad():
        direct_output = direct(torch.zeros(1, 3, 128, 128))["one2one"]["boxes"]
        dfl_output = dfl(torch.zeros(1, 3, 128, 128))["one2one"]["boxes"]
    return {
        "reg_max_1": {"raw_boxes": shape_of(direct_output), "decoder": type(direct.model[-1].dfl).__name__},
        "reg_max_16": {"raw_boxes": shape_of(dfl_output), "decoder": type(dfl.model[-1].dfl).__name__},
    }


def fuse_contract(DetectionModel, cfg: Path) -> dict:
    import torch

    torch.manual_seed(0)
    model = build_model(DetectionModel, cfg).eval()
    sample = torch.randn(1, 3, 320, 320)
    with torch.inference_mode():
        before = model(sample)[0]
    parameters_before = sum(p.numel() for p in model.parameters())
    model.fuse(verbose=False)
    parameters_after = sum(p.numel() for p in model.parameters())
    with torch.inference_mode():
        after = model(sample)[0]
    return {
        "parameters_before": parameters_before,
        "parameters_after": parameters_after,
        "one2many_removed": model.model[-1].cv2 is None and model.model[-1].cv3 is None,
        "one2one_retained": model.model[-1].one2one_cv2 is not None,
        "max_abs_output_difference": float((before - after).abs().max()),
    }


def onnx_contract(DetectionModel, cfg: Path, output: Path) -> dict:
    import onnx
    import torch

    model = build_model(DetectionModel, cfg).eval().fuse(verbose=False)
    head = model.model[-1]
    head.export = True
    head.format = "onnx"
    sample = torch.zeros(1, 3, 320, 320)
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        model,
        sample,
        output,
        opset_version=13,
        input_names=["images"],
        output_names=["output0"],
        do_constant_folding=True,
    )
    graph = onnx.load(output)
    onnx.checker.check_model(graph)
    operators = sorted({node.op_type for node in graph.graph.node})
    return {
        "path": str(output),
        "output_dims": [dim.dim_value for dim in graph.graph.output[0].type.tensor_type.shape.dim],
        "has_topk": "TopK" in operators,
        "has_nms": "NonMaxSuppression" in operators,
    }


def main() -> None:
    args = parse_args()
    source_root = args.source_root.resolve()
    sys.path.insert(0, str(source_root))

    import torch
    from ultralytics.nn.tasks import DetectionModel
    from ultralytics.utils import YAML

    torch.set_num_threads(1)
    cfg_dir = source_root / "ultralytics/cfg/models/26"
    results = {
        "source_commit_expected": "b103ba8d0944bfd8de69bfded9778ac5daadd956",
        "torch": torch.__version__,
        "default": model_contract(DetectionModel, cfg_dir / "yolo26.yaml", args.imgsz, collect_layers=True),
        "p2": model_contract(DetectionModel, cfg_dir / "yolo26-p2.yaml", args.imgsz),
        "p6": model_contract(DetectionModel, cfg_dir / "yolo26-p6.yaml", args.imgsz),
        "gradient": gradient_contract(DetectionModel, cfg_dir / "yolo26.yaml"),
        "regression": regression_contract(DetectionModel, YAML, cfg_dir / "yolo26.yaml"),
        "fuse": fuse_contract(DetectionModel, cfg_dir / "yolo26.yaml"),
    }
    if args.onnx_output:
        results["onnx"] = onnx_contract(DetectionModel, cfg_dir / "yolo26.yaml", args.onnx_output.resolve())

    assert results["default"]["strides"] == [8.0, 16.0, 32.0]
    assert results["default"]["final"] == [1, 300, 6]
    assert results["default"]["one2many_boxes"] == [1, 4, 8400]
    assert results["default"]["layer22_inner"] == ["Bottleneck", "PSABlock"]
    assert results["p2"]["strides"] == [4.0, 8.0, 16.0, 32.0]
    assert results["p2"]["one2many_boxes"] == [1, 4, 34000]
    assert results["p6"]["strides"] == [8.0, 16.0, 32.0, 64.0]
    assert results["p6"]["one2many_boxes"] == [1, 4, 8500]
    assert results["regression"]["reg_max_1"]["decoder"] == "Identity"
    assert results["regression"]["reg_max_16"]["decoder"] == "DFL"
    assert results["fuse"]["one2many_removed"] and results["fuse"]["one2one_retained"]
    if args.onnx_output:
        assert results["onnx"]["has_topk"] and not results["onnx"]["has_nms"]
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
