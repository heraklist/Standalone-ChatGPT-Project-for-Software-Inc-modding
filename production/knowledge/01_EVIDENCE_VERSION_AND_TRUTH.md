---
document_id: K01
title: Evidence, Version and Truth
knowledge_type: TRUTH
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [evidence, provenance, versioning]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: EXACT_TARGET
known_version_gaps: []
---

# Evidence, Version and Truth

## Evidence tuple
Classify claims by `source_class × source_role × currency × scope × confidence × verification`. Source class and role are orthogonal: an official developer wiki page and an official patch note have different evidentiary jobs.

## Source roles
Canonical roles include `DEVELOPER_WIKI`, `OFFICIAL_PATCH_NOTE`, `ENGINE_FORK_SOURCE`, `LINKED_ENGINE_API`, `UPSTREAM_SPEC`, `EXACT_VANILLA_CORPUS`, `OLDER_VANILLA_CORPUS`, `ASSEMBLY_SURFACE`, `OFFICIAL_WORKSHOP_METADATA`, `PRIMARY_MOD_SOURCE`, `COMMUNITY`, and `RUNTIME_EVIDENCE`.

## Currency and scope
Currency values include `EXACT_TARGET`, `TARGET_BRANCH`, `OLDER_VERSION`, `FUTURE_DEV`, `UNKNOWN_VERSION`, `NOT_VERSION_SENSITIVE`. Scope includes `ENGINE_GENERAL`, `MOD_FAMILY`, `API_OR_SCHEMA`, `VANILLA_CONTENT`, `ARTIFACT`, `ENVIRONMENT`. Official provenance does not imply exact-target currency. An unchanged wiki date does not upgrade Beta 1.7.15 vanilla evidence to Beta 1.8.42.

For the canonical Beta 1.8.42 target, the exact-target generation gate is resolved. The governed capture is `GENERATION_GRADE_EXACT_TARGET` with `currency: EXACT_TARGET`. This does not erase claim-specific evidence limits: runtime behavior, editor-native storage/publishing details, or other surfaces still require their own scoped evidence when the relevant knowledge document says so.

## Conflict handling
Use `CONSISTENT`, `SOURCE_CONFLICT`, `VERSION_CONFLICT`, `SCOPE_CONFLICT`, or `UNRESOLVED`. Never hide a conflict by selecting the more convenient source. Runtime evidence is strongest only for the exact tested artifact/environment surface.

## Negative knowledge
Absence from vanilla does not prove parser rejection. Presence/layout in vanilla does not establish a public mod loader path. No verified current public Scenario/Map authoring loader or Building/Blueprint filesystem schema has been established; classify as `RESEARCH_REQUIRED`/`NO_DOCUMENTED_SURFACE` rather than inventing one. Generic upstream TyD and Unity docs are not Software Inc parser/API law unless specifically corroborated or delegated.

## Known gaps / evidence limits
Do not describe the canonical Beta 1.8.42 target itself as pending. Apply only claim-specific gaps documented for the relevant family, API, runtime, or editor surface.
