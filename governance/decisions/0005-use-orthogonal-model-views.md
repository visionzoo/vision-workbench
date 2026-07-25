---
title: Use orthogonal views for model knowledge
status: proposed
date: 2026-07-25
supersedes_if_accepted: 0004
---

# Decision 0005: Use orthogonal views for model knowledge

## Context

Decision 0004 corrected a real asymmetry: MobileNet and ViT had been promoted because their names appeared in the conversation, while ResNet、EfficientNet、ConvNeXt and HRNet were treated as secondary baselines. It introduced `backbone / neck / head` as first-class module roles and prevented the roadmap from becoming a flat model list.

A second review found that this correction was too strong in three places:

1. `backbone / neck / head` is a useful component view, but not every CNN、Transformer、DETR、encoder-decoder or end-to-end model can be unambiguously decomposed this way;
2. the roadmap grouped Meta self-supervised DINO and detector DINO because they share a name, even though one is a representation-learning lineage and the other is a DETR detection lineage;
3. the registry used one `roles` field to mix whole-model scope with module roles, while the roadmap mixed learning paradigms, tasks and system applications at the same level.

This is the same class of failure that earlier caused “调研” to become a Research directory: one salient surface feature was promoted into the main classification axis before checking the underlying object and relations.

## Proposed decision

Use four orthogonal views instead of a single supposedly exhaustive taxonomy:

1. **Architecture modules**：backbone / visual encoder、neck / feature fusion / adapter、head / task decoder；
2. **Learning and alignment paradigms**：supervised or self-supervised representation learning、visual-language alignment；
3. **Tasks and complete solutions**：detection、keypoint/pose、segmentation、tracking and temporal solutions；
4. **System applications**：VLM and VLA uses that place visual capabilities inside a larger workflow or closed loop.

These views are indexes and relationship dimensions, not four mandatory directory trees. An object may appear in several views, but facts have one canonical owner and other views link to it.

Specific consequences:

- Meta DINO is maintained under self-supervised representation learning.
- Detector DINO is maintained under Detection → DETR as its own family; separate construction does not mean a duplicate top-level category.
- `backbone / neck / head` remain important module roles, expanded where needed with `visual-encoder`、`adapter` and `task-decoder`, but they do not define every network's ontology.
- The registry separates `object_type` from `module_roles`. Tasks、learning paradigms and system applications remain independent relations rather than values squeezed into either field.
- HRNet's high-resolution architecture is maintained through the architecture/module view; HRNet-based heatmap versus PFLD is maintained as a keypoint task and system-level experiment.
- No empty directories are created merely to mirror the four views.

## Evidence boundary

This proposal is based on the structure exposed by the current roadmap and registry, plus the user's real HRNet/PFLD and detection work. It has not yet been stress-tested against a large collection of model families. Acceptance should depend on whether it can represent the next real entries without duplicate ownership or forced classification.

## Migration if accepted

- Replace the three-section roadmap with the four views above.
- Move detector DINO into the Detection/DETR task context while keeping it an independently built family.
- Upgrade `registry.yaml` from a single `roles` axis to `object_type` plus `module_roles`.
- Keep Decision 0004 as historical context; mark it superseded only after this decision is explicitly accepted.
- Do not create module, task or application directories until real content makes a separate reading path necessary.

## Verification

- Every pending item has a clear primary view and explicit cross-links where needed.
- Meta DINO and detector DINO no longer sit together because of their shared name.
- Detection family、keypoint task、video task and segmentation are not mixed with VLM/VLA system applications.
- Registry entries distinguish what the object is from what role it plays.
- A complete-model comparison cannot be mistaken for evidence about a single backbone or head.
- No empty directories or duplicate registries are introduced.
