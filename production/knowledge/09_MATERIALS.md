---
document_id: K09
title: Materials
knowledge_type: FAMILY
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [Materials, textures, atlas]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH_WITH_EXACT_TARGET_GATE
known_version_gaps: []
---

# Materials

## Package structure and identity
Room/path/roof material packs live under `Materials/<Pack>/` with root `materials.tyd`. Referenced PNG textures are **256×256**. The TyD table name is the serialization identity; use the canonical term `material_table_name`. Defining the same table name replaces the existing material, so distinguish intentional replacement from accidental collision.

## Categories, floor types and presets
Documented categories are `Floor`, `Interior`, `Exterior`, `Roof`, and `Path`. Documented `FloorType` values are `Wood`, `Ceramic`, `Carpet`, and `Concrete`. A material can expose up to eight documented color presets; preserve optional secondary-color controls according to the material schema.

## Texture channels
`Base` maps player coloration through documented channels (red/green mapping, while blue-positive pixels preserve literal color behavior). `Bump` is the normal-map surface. `Extra` channels encode red=occlusion, green=smoothness/specularity, blue=metallic, and alpha=rain/snow response in the documented version range. Validate actual PNG channel presence rather than inferring alpha from a screenshot.

## Global atlas system
The game combines default and supplied material textures into **three shared global material texture atlases**. Aggregate capacity is GPU/runtime-maximum-texture-size dependent and also depends on installed content. The documented `256 materials` figure is an example for a 4096×4096 maximum texture size, not a universal hard cap.

## Reload and verification
Material reload has a startup-loaded-set limitation; newly introduced material sets may require restart. Runtime QA checks appearance, mapped colors, normal/specular/metallic/occlusion behavior, weather response where applicable, category/floor audio behavior and persistence.

## Known gaps / evidence limits
Do not prescribe filenames like `base.png` as mandatory: `Base`, `Bump` and `Extra` are path fields, and example filenames are examples.
