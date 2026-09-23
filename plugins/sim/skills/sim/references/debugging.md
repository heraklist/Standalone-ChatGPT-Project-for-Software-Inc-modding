---
document_id: K12
title: Debugging, Console and Runtime
knowledge_type: WORKFLOW
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [debugging, console, reload, runtime]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH
known_version_gaps: []
---

# Debugging, Console and Runtime

## Exact command identifiers
Preserve documented command spelling. Core development commands include `RELOAD_MOD`, `RELOAD_FURNITURE`, `RELOAD_MATERIALS`, `RELOAD_LOCALIZATION`, `RECOMPILE_DLL_MOD`, `RELOAD_DLL_MOD`, `UNLOAD_DLL_MOD`, `LIST_SCOPE_MEMBERS`, `TEST_DEV_MOD`, `CHECK_SPEC_REP`, and `CHECK_ADDON_MARKET`. Do not invent aliases such as `RELOAD_FURNITURE_MOD`.

## Reload caveats
`RELOAD_MOD` reloads Data definitions for development but does **not** update the currently running game state; a clean/new runtime path is required for final load/behavior proof. `RELOAD_FURNITURE` does not update furniture instances already placed, so changed Furniture requires fresh placement. Material reload is limited by the material sets loaded at startup; newly introduced sets may require restart. `RELOAD_LOCALIZATION` reloads data but already rendered UI may not update immediately.

## Code development helpers
`RECOMPILE_DLL_MOD`, `RELOAD_DLL_MOD`, `UNLOAD_DLL_MOD`, `EXECUTE`, and inspector/debug helpers are development tools. Reload/recompile success is not final clean-launch/regression proof and may leave state that differs from a fresh process. Use `-DisableModErrors` only as a diagnostic when investigating Code errors.

## Data and SIPL diagnostics
Use `TEST_DEV_MOD`, `CHECK_SPEC_REP`, and `CHECK_ADDON_MARKET` for their documented Data diagnostics; use `LIST_SCOPE_MEMBERS` for SIPL/member inspection. Record the exact command, target artifact revision, game version, environment and observed result.

## Runtime evidence
Runtime proof is scoped to exact artifact identity and environment. Capture command/output/log context without promoting a development reload into V3–V5 verification when the required clean-run profile was not executed.

## Known gaps / evidence limits
Commands or arguments not present in the canonical evidence set remain `RESEARCH_REQUIRED`; do not infer them from naming patterns.
