---
name: editor-native
description: SIM specialist workflow for Software Inc editor-native Hardware Design, Building Blueprint, and Building content without inventing unverified filesystem schemas.
---

# Editor Native

Own editor-native analysis and proposed changes. Do not dispatch to peer specialists and do not mutate shared session state directly; return proposed changes to the central SIM orchestrator.

## Ownership and artifact surface

Hardware Design is a capability domain owned by `DATA` integration, not a separate generic loader-family claim. Building Blueprint and Building are native editor/Workshop content surfaces with no verified generic public standalone filesystem schema in the canonical evidence set.

Do not invent `/Mods/Buildings`, `/Mods/Blueprints`, `Building.tyd`, `BuildingBlueprint.tyd`, or equivalent package representations to make native content look like a normal Data mod.

## Hardware Design

Use the documented Hardware Design editor concepts: meshes/base meshes, morph targets, attachment points, texture atlas/sub-atlas concepts, and the documented design volume. Shipped/editor-generated internal fields may be observed evidence but are not automatically public authoring schema.

Data-side integration through documented SoftwareType `Design` / `FeatureBinding` references remains owned by the Data domain.

## Native verification

For Hardware Design, verify native-open/editor load, mesh/morph integrity, attachments, atlas mapping, preview/randomized generation where applicable, SoftwareType integration, developed-product use, placement where supported, and save/reload.

For Building Blueprint and Building, use the native in-game/editor/share surface and verify discovery/import, placement/use, geometry/access/navigation, dependency integrity, save/reload, and Workshop/share cycle where applicable.

Native content progresses through native artifact evidence, not fabricated ZIP/TyD substitutes. If the environment cannot produce or open the required native artifact, report `TOOLING_BLOCKED`. A repository-only check does not establish native-open verification; unavailable checks remain `NOT_EXECUTED`.
