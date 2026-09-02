---
name: furniture
description: SIM specialist workflow for Software Inc Furniture packs, hierarchy dependencies, bounds/debug behavior, mesh replacements, and fresh-placement verification.
---

# Furniture

Own Furniture-specific analysis and proposed changes. Do not dispatch to peer specialists and do not mutate shared session state directly; return proposed changes to the central SIM orchestrator.

## Package and identity

Furniture packages use `Furniture/<Pack>/`. Treat root `Name` as the unique furniture identity; `LocalizedName` is UI text. Referenced thumbnails are 128×128 and referenced assets must be package-complete.

## Transform dependency scope

`Models`, `Transforms`, `SnapPoints`, `InteractionPoints`, and component tables form the Furniture transform/component graph. A `TransformParent` must reference an object that has already been created in the relevant hierarchy, so definition order matters for this dependency surface. This is not a universal TyD field-order rule.

## Runtime and development helpers

`FURNITURE_DEBUG True` is useful for visual boundary/point checks. `RELOAD_FURNITURE` does not update already placed furniture; changed definitions require fresh placement for verification. `EXPORT_FURNITURE_BOUNDS` may rewrite formatting/remove comments, so treat it as a destructive development helper and preserve source before use.

Mesh replacements belong at `Furniture/<Pack>/replacements.tyd`; do not confuse them with room-material `Materials/<Pack>/materials.tyd`.

## Verification boundary

Static checks do not prove placement, navigation, interaction, snap points, save/reload, or replacement behavior. Verify changed furniture with fresh placement and keep unavailable runtime checks as `NOT_EXECUTED`.
