---
name: materials
description: SIM specialist workflow for Software Inc Materials packs, serialization identity, texture channels, presets, atlas constraints, and runtime verification.
---

# Materials

Own Materials-specific analysis and proposed changes. Do not dispatch to peer specialists and do not mutate shared session state directly; return proposed changes to the central SIM orchestrator.

## Package and identity

Room/path/roof material packs live under `Materials/<Pack>/` with root `materials.tyd`. Referenced PNG textures are 256×256. The TyD table name is the serialization identity; use the canonical term `material_table_name`. Reusing a table name replaces the existing material, so distinguish intentional replacement from accidental collision.

## Presets and documented channels

A material can expose up to eight documented color presets. Preserve optional secondary-color controls according to the material schema.

`Base` carries documented player-color mapping behavior, `Bump` is the normal-map surface, and `Extra` encodes red=occlusion, green=smoothness/specularity, blue=metallic, alpha=rain/snow response for the documented range. Validate actual PNG channels rather than inferring them from screenshots.

The game combines supplied textures into shared global material atlases. The documented 256-material figure is an example for a 4096×4096 maximum texture size, not a universal hard cap.

Do not prescribe filenames such as `base.png` as mandatory; `Base`, `Bump`, and `Extra` are path fields and example filenames are not mandatory.

## Verification boundary

Static structure does not prove mapped colors, normal/specular/metallic/occlusion behavior, weather response, category behavior, or persistence. Newly introduced material sets may require restart rather than reload alone; unavailable runtime checks remain `NOT_EXECUTED`.
