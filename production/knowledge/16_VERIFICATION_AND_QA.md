---
document_id: K16
title: Verification and QA
knowledge_type: QA
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [verification, QA, DoD, runtime]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH_WITH_EXACT_TARGET_GATE
known_version_gaps: [Exact target runtime verification corpus pending]
---

# Verification and QA

## Verification states
`V0 DESIGN_READY`, `V1 FILES_GENERATED`, `V2 STATICALLY_REVIEWED`, `V3 LOAD_VERIFIED`, `V4 BEHAVIOR_VERIFIED`, `V5 REGRESSION_VERIFIED`. These states describe evidence, not optimism. Package/native artifact state is a separate axis.

## Profiles
`LIGHT` is narrow static/smoke verification for low-risk changes; `STANDARD` includes family-specific load/behavior/persistence checks; `DEEP` includes clean-launch, negative/dependency, persistence, interaction and regression coverage as applicable. Code defaults to `DEEP`; Hardware Design, Building Blueprint and Building require at least `STANDARD`. Workshop Code must test the actual game compiler profile.

## Runtime Evidence Block
Record artifact revision/payload identity, game version/channel/platform, enabled dependencies/mods, test profile, clean/reload state, steps, observations, logs/screens where useful, pass/fail and date. Cross-chat V3–V5 claims survive only when this evidence matches the exact artifact/environment.

## Invalidation
Targeted changes invalidate affected evidence: Code API/compiler/security changes invalidate Code load/behavior/regression; Furniture mesh/transform/point changes invalidate fresh-placement/interaction/navigation; Material identity/texture changes invalidate appearance/weather/category checks; Hardware mesh/morph/attachment/atlas/FeatureBinding invalidates editor/integration/placement; Blueprint geometry/content invalidates import/placement/navigation/save; Building geometry/rental/navigation/dependencies invalidate availability/load/pathing/save/Workshop tests. Architecture/distribution changes or untraceable rewrites require broad re-verification.

## MOD_PACKAGE Definition of Done
All required files/assets exist; hard rules and cross-references pass; collisions/intentional overrides are understood; install-ready ZIP has correct loader-root level and exact payload identity; required load/behavior/persistence/negative/regression profile passes on that payload. Candidate package without sufficient runtime evidence remains `READY_FOR_GAME_TESTING`.

## EDITOR_CONTENT Definition of Done
Native content exists in the intended editor/share surface; required editor recognition, placement/import/share behavior, geometry/access/pathing or hardware visual/integration checks pass as applicable; save/reload/persistence and required regression checks pass on the exact native artifact/state. Never substitute an invented ZIP.

## Family minimum runtime profiles
Data: STANDARD when gameplay behavior/override/balance semantics matter. SIPL: STANDARD with the real entry point/scope/RunType. Code: DEEP. Furniture: STANDARD with fresh placement. Materials: STANDARD with restart when the loaded-set limitation applies. Localization: STANDARD on affected UI/key surfaces. Hardware Design: STANDARD. Building Blueprint: STANDARD. Building: STANDARD. Hybrids test each component, cross-component contract and end-to-end behavior; Hybrid + Code is DEEP.

## Known gaps / evidence limits
If the game cannot be executed here, collaborate on a user-run test loop but keep the artifact candidate until matching evidence is returned.
