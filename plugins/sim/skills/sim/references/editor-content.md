---
document_id: K11
title: Editor Content: Hardware, Blueprints and Buildings
knowledge_type: EDITOR_CONTENT
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [Hardware Design, Building, Blueprint]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH
known_version_gaps: [Building and Blueprint public filesystem schema unverified]
---

# Editor Content: Hardware, Blueprints and Buildings

## P0 Building/Blueprint preflight

Before any web search, repository search, personal-context lookup, source browsing, path reasoning, or artifact generation, a Building/Blueprint request for exact folders, an install path, package tree, installer, or ZIP must be classified against the loader/install evidence ceiling.

When loader/install semantics are not already verified for the target version:

- do not search for or repeat filesystem paths, filenames, extension-to-directory mappings, loader locations, or storage directory names;
- do not show a negative example tree, rejected tree, hypothetical package skeleton, path mapping, or "what not to do" layout;
- do not convert storage/export observations into claims that files "load as", "go in", "belong in", or install at a particular location;
- return `TOOLING_BLOCKED — native Building/Blueprint authoring/export evidence required.`;
- state that the current canonical evidence does not establish standalone loader/install semantics and require a real native export/artifact or supported native authoring/export surface before filesystem discussion continues.

The preflight ends the package-path branch immediately. A disclaimer or later refusal cannot authorize path enumeration.

## Ownership and artifact surface
Hardware Design is a **capability domain owned by `DATA` integration**, not a separate loader-family claim. Building Blueprints and Buildings are supported editor/Workshop content types, but their public standalone filesystem schema has not been verified. They therefore use `EDITOR_CONTENT`, not an invented Mods-root package.

## Hardware Design authoring
The official Hardware Design editor exposes meshes/base meshes, morph targets, attachment points, texture-atlas/sub-atlas concepts and an overall 2×2×2 design volume. Shipped/editor-generated TyD internal fields may be `UNDOCUMENTED_BUT_OBSERVED`; do not elevate them to documented public field schema solely because an older vanilla corpus contains them. Data `SoftwareType` integration through documented `Design` / `FeatureBinding` references belongs in `04_DATA_MODDING.md`.

## Hardware Design verification
Minimum profile: **STANDARD**. Verify editor load, mesh/morph integrity, attachments, texture/atlas mapping, randomized/editor preview, SoftwareType integration, developed-product use, office placement where the target version supports it (Beta 1.8.34+), and save/reload. Mesh/morph/attachment/atlas or FeatureBinding changes invalidate the corresponding visual/integration/placement evidence.

## Building Blueprint
Use the native in-game/editor/share surface. Minimum verification: discovery/import, placement on the intended plot, geometry/furniture/dependency integrity, access/navigation sanity, save/reload, and share/Workshop import cycle where applicable. Never invent `Data/BuildingBlueprint.tyd`, `/Mods/Blueprints/`, or another public package representation merely to satisfy delivery.

## Building
Treat Building as a distinct editor/Workshop content type. Minimum verification: content discovery/enablement, intended building/rental behavior, geometry/access/pathing, dependencies, new-game/load path where applicable, save/restart and clean subscription/import cycle. Workshop ecosystem evidence does not reveal a public parser/file schema.


## Building/Blueprint package hard stop
When the target-version evidence does not establish a supported public loader/install schema, a request for exact folders, an install tree, package layout, installer, or ZIP must stop before any concrete filesystem structure is proposed. Do not enumerate or present a concrete install tree such as `Software Inc\Buildings\...`, `Software Inc\Blueprints\...`, `Buildings/*.build`, or `Blueprints/*.xml`, even if those names were observed in storage, cloud data, Workshop metadata, or exported artifacts. Such names may be described only as storage/export observations with an explicit statement that they do not establish installation or delivery semantics. Do not convert them into a tree diagram, path mapping, package skeleton, or install recipe. If the supported native authoring/export path is unavailable, report `TOOLING_BLOCKED`. A later refusal to fabricate the final ZIP does not cure an earlier unverified concrete install-tree claim.

## Native artifact delivery
Editor-native content ends as `CANDIDATE_NATIVE_ARTIFACT` then `FINAL_VERIFIED_NATIVE_ARTIFACT` when the required evidence exists. If the environment cannot produce/export the native artifact, report `TOOLING_BLOCKED`; do not manufacture a ZIP or TyD format.

## Known gaps / evidence limits
Exact-target editor storage/publishing internals are intentionally not inferred from historical files or Workshop metadata.
