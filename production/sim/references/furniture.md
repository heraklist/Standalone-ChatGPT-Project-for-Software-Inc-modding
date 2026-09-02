---
document_id: K08
title: Furniture
knowledge_type: FAMILY
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [Furniture, models, snap points, interaction points]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH_WITH_EXACT_TARGET_GATE
known_version_gaps: []
---

# Furniture

## Package structure and identity
Furniture packages live under `Furniture/<Pack>/`. Each furniture definition is TyD-based and references required local assets. `Thumbnail` is a **128×128** image. The root `Name` is the unique furniture identity; `LocalizedName` is UI text and is not the identifier.

## Models, transforms and components
`Models`, `Transforms`, `SnapPoints`, `InteractionPoints` and component tables form a transform/component graph. `TransformParent` must reference an object that has already been created in the relevant Furniture hierarchy, so definition order matters **for this dependency surface**. This is not a universal TyD field-order rule. Root tables may expose documented Unity component surfaces only where the Furniture guide explicitly does so.

## Bounds, points and runtime debug
`AutoBounds` can generate placement/navigation bounds. Keep documented height constraints, including `Height2 <= 2`; carpet-like definitions use the documented negative height values where applicable. `FURNITURE_DEBUG True` has documented visual semantics: navigation boundary transitions green→pink, build boundary cyan→red, interaction points blue, snap points yellow. These are useful runtime fixtures.

`RELOAD_FURNITURE` is a development helper; already placed furniture does not update. Verification of changed furniture requires **fresh placement**. `EXPORT_FURNITURE_BOUNDS` can rewrite formatting/remove comments, so treat it as a destructive-development helper and preserve source before use.

## Mesh replacements
Mesh replacement definitions live at `Furniture/<Pack>/replacements.tyd`, the root of the specific Furniture package. Do not confuse this with room material `Materials/<Pack>/materials.tyd` or Furniture-local shader/material definitions.

## Runtime verification
Validate identity, thumbnail, meshes/materials, transform hierarchy, bounds, snap/interaction points, fresh placement, interaction/navigation, save/reload and any replacement behavior affected by the change.

## Known gaps / evidence limits
Unity component details are only authoritative where the Software Inc Furniture documentation explicitly exposes/delegates them.
