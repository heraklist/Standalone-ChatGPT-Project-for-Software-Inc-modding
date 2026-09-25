---
document_id: K02
title: Mod Ecosystem and Router
knowledge_type: ROUTER
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [routing, families, feasibility]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH
known_version_gaps: []
---

# Mod Ecosystem and Router

## Intent routing
Primary intents: `DISCOVER`, `BUILD`, `MODIFY`, `UNDERSTAND`. Modifiers include `BRAINSTORM`, `REPAIR`, `DEBUG`, `EXPAND`, `MIGRATE`, `AUDIT`, `TRANSLATE`, `VERIFY`, `PACKAGE`, `PUBLISH`. Ask only questions that change routing or the artifact contract.

## Capability routing
Prefer declarative Data. Escalate to `DATA_SIPL` only when a documented SIPL entry point/scope can satisfy the behavior. Escalate to Code only for deeper runtime/API/UI behavior. Hardware Design is a capability domain owned by Data integration, not a standalone loader-family claim.

## Family routing
Canonical owner families: `DATA`, `DATA_SIPL`, `CODE`, `FURNITURE`, `MATERIALS`, `LOCALIZATION`, `BUILDING_BLUEPRINT`, `BUILDING`, `NONE`. Hybrid is an architecture property, not a family value.

## Feasibility states
`SUPPORTED`, `SUPPORTED_WITH_CONSTRAINTS`, `RESEARCH_REQUIRED`, `RUNTIME_PROOF_REQUIRED`, `NO_DOCUMENTED_SURFACE`, `CONSTRAINT_CONFLICT`. `BUILDING` and `BUILDING_BLUEPRINT` are editor/Workshop content with public filesystem schema unverified.

## Environment and distribution
Resolve environment lazily. Distribution targets: `LOCAL`, `WORKSHOP`, `BOTH`, `UNDECIDED`. Workshop Code uses the game-compiled source profile; local precompiled DLL is a distinct path. Artifact surfaces are `MOD_PACKAGE` or `EDITOR_CONTENT`.

## Known gaps / evidence limits
Do not infer undocumented loader paths from Workshop taxonomy or historical vanilla layout.
