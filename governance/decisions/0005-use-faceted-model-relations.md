---
title: Use faceted relations for model knowledge
status: accepted
date: 2026-07-25
supersedes: 0004
---

# Decision 0005: Use faceted relations for model knowledge

## Context

Decision 0004 corrected a real asymmetry: a few named models had been promoted while other relevant families were treated as secondary baselines. It introduced `backbone / neck / head` as first-class module roles and prevented the roadmap from becoming a flat model list.

Further review found that module roles still could not serve as a general model taxonomy:

1. not every CNN, Transformer, DETR, encoder-decoder or end-to-end model can be unambiguously decomposed into `backbone / neck / head`;
2. names do not determine identity: Meta self-supervised DINO and detector DINO belong to different lineages;
3. object identity, usage scope, module role, learning paradigm, task and system context answer different questions;
4. a fixed four-view roadmap mixed knowledge classification with execution planning and turned possible future coverage into premature work commitments;
5. `adapter` grouped interface projection, multimodal connectors and parameter-efficient fine-tuning only because they share a word.

This is the same class of failure that earlier caused “调研” to become a Research directory: one salient surface feature was promoted into the main classification axis before checking the underlying object and relations.

## Decision

Use faceted relations instead of a single supposedly exhaustive taxonomy or a fixed set of mandatory directory trees.

The model index may describe an object through these independent fields:

1. **Entity kind**：what the canonical object is, such as a model family, architecture family, component family or method family;
2. **Usage scopes**：whether it is used as a complete solution, reusable module or pretraining source;
3. **Module roles**：what responsibility it takes in a concrete system, such as backbone, visual encoder, neck, head or task decoder;
4. **Learning paradigms**：how representations or task behavior are learned or aligned;
5. **Tasks**：what visual problem the complete system solves, including classification, detection, keypoint localization, segmentation and tracking;
6. **System contexts**：how the visual capability is used in a larger workflow or closed loop;
7. **Relations**：typed links to parent lineages, components, pretraining sources, tasks, cases and competing alternatives.

These fields are relationship dimensions, not a promise that every entry must populate every field. Facts have one canonical owner; other views link to that owner. Directories continue to follow long-term knowledge purpose, while metadata expresses cross-cutting relationships and `TODO.md` controls work activation.

Specific consequences:

- Meta DINO is represented through self-supervised learning relations; detector DINO is maintained in the Detection / DETR lineage.
- `backbone / visual-encoder` and `head / task-decoder` remain distinct but adjacent module roles; they are not synonyms or universal decomposition rules.
- There is no generic `adapter` module role or roadmap parent. Interface projections are components, multimodal projectors are multimodal architecture relations, and PEFT adapters are learning methods.
- Classification is a task relation independent of backbone or head, and includes real image/ROI/state classification work.
- Visual encoding is a module role or capability, not a task at the same level as classification or detection.
- Open-vocabulary classification and detection are task capabilities; VLM-assisted annotation, filtering, hard-case analysis and evaluation are system workflows.
- Temporal recognition/localization is separated from engineering decision logic such as smoothing, state machines, alarm triggering and recovery.
- No empty directories or family pages are created merely to mirror the facets.

## Evidence boundary

This decision is based on repeated pressure tests against the current roadmap, registry, YOLO and TuringViT entries, the user's real classification, detection and eye-keypoint work, and counterexamples from representation learning, DETR, video and multimodal systems. Acceptance records the repository-organization decision; it does not claim that the vocabulary is complete.

New real entries may add or refine values when existing facets cannot represent them without forced classification. They must not create a new directory tree or parent category merely to make the taxonomy look complete.

## Migration

- Keep Decision 0004 as historical context and mark it superseded by this decision.
- Replace `object_type` with `entity_kind` and separate identity from `usage_scopes`.
- Remove generic `adapter` from `module_roles`.
- Rename `primary_tasks` to `tasks`; remove `visual-encoding` from TuringViT tasks.
- Add empty relation fields only where they are part of the registry contract, not as speculative content.
- Reframe `TODO.md` as active work, accumulation candidates and repository maintenance; only activated work is decomposed.
- Split the root README into knowledge areas and repository support.

## Verification

- A model family, architecture family, component family and method family can be distinguished from how each is used.
- Meta DINO and detector DINO cannot become adjacent merely because of a shared name.
- Interface projection, multimodal projector and PEFT adapter do not share a false canonical parent.
- Classification can be represented without pretending that a backbone or head is itself the task.
- TuringViT can be a visual encoder without declaring `visual-encoding` as a task.
- Temporal model knowledge and product alarm logic have different canonical homes.
- The TODO can preserve open accumulation directions without converting all candidates into work commitments.
- No empty directory, duplicate fact owner or second knowledge map is introduced.
