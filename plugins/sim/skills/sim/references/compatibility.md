---
document_id: K13
title: Compatibility, Migration and Collisions
knowledge_type: WORKFLOW
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [compatibility, migration, collisions, overrides]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH
known_version_gaps: []
---

# Compatibility, Migration and Collisions

## Compatibility dimensions
Track game version, distribution profile, authoring family, artifact surface, referenced assets/APIs, and persistence-sensitive identities independently. Version compatibility is claim-specific: official provenance is not automatic currentness.

## Collision taxonomy
Check vanilla and installed-mod identifiers before generation where a corpus is available. Distinguish accidental collisions from documented intentional overrides/replacements. Prefix/namespacing is a best practice for new identifiers, not an engine syntax law.

## Domain-specific mutation
SoftwareType `Override True` is partial except that supplying `Features` replaces that list; `Override Delete` deletes the SoftwareType. CompanyTypes use `delete.txt`; NameGenerators merge or `[REPLACE]`; Personalities merge or `Replace True`; Materials replace by `material_table_name`. Do not generalize one domain's semantics to another.

## Load order and dependencies
No **documented public mod-level load-order or dependency-declaration mechanism** has been established in the canonical evidence set. Therefore do not generate invented engine fields/files such as `Dependencies`, `LoadAfter`, `Priority`, or a dependencies manifest. Studio build metadata may record dependencies for QA, but that metadata is not game syntax.

## Migration
Migrate at claim/artifact level. Preserve attribution/licensing, distribution constraints and user intent. Replace obsolete APIs/syntax only when evidence establishes the new contract. For Code, preserve the Workshop C#3 profile versus local DLL distinction; for PlayerPrefs on target >= Beta 1.8.34 migration is mandatory.

## Historical negative knowledge
Historical Scenario/mission references do not establish a current public authoring loader. Treat the surface as historical/unresolved and do not invent Scenario/Map files.

## Known gaps / evidence limits
Actual inter-mod resolution order, if relevant, requires exact-target/runtime evidence; absence of a documented declaration mechanism is not a claim of metaphysical nonexistence.
