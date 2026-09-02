---
document_id: K06
title: Code Modding Core and Distribution
knowledge_type: FAMILY
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [Code, CSharp, Workshop, DLLMods]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH_WITH_EXACT_TARGET_GATE
known_version_gaps: [Exact target assemblies pending]
---

# Code Modding Core and Distribution

## Package and compiler profiles
Code mods live under `DLLMods/<ModName>/`. Software Inc supports precompiled DLLs and game-compiled `.cs`, but they are distinct distribution profiles. The documented game compiler targets .NET 4-era assemblies and **C# 3**; Workshop Code uses the game-compiled source profile. A local precompiled DLL may be built externally, but runtime/API compatibility still has to match the game.

For game-compiled source do not emit syntax introduced after C# 3, including `async`/`await`, string interpolation, `nameof`, `dynamic`, null-conditional operators, or expression-bodied members. C# 3 **does** support `var`, lambdas/query expressions and LINQ; do not invent a prohibition on those.

## Official example conflict and enum caveat
The official Code page includes an expression-bodied `ModMeta.Name => ...` example while also documenting the game compiler as C# 3. Record this as `SOURCE_CONFLICT`; Workshop/game-compiled generation follows the compiler profile and emits a C#3-compatible property getter.

While the documented straight-`.cs` enum caveat remains active, treat **enum usage** in game-compiled `.cs` as a blocker rather than narrowing the warning to custom enum declarations. A local DLL profile is evaluated separately.

## ModMeta and ModBehaviour
A Code mod defines `ModMeta` metadata/options behavior and one or more `ModBehaviour` components. Documented lifecycle surfaces include `Awake`, `Start`, `Update`, `OnDestroy`, `OnActive`, and `OnDeactivate`; event subscription cleanup belongs in deactivation/destruction paths. `ModMeta.Name` is persistence-sensitive and should remain stable across releases unless a migration deliberately accounts for the change.

## Compatibility symbols
The game compiler exposes `SWINCTYPE` (`SWINCBETA`/`SWINCRELEASE`), `SWINCTYPEMAJOR` (for example `SWINCBETA1`) and `SWINCTYPEMAJOR_MINOR` (for example `SWINCBETA1_7`, `SWINCBETA1_8`). Use these for documented compile-time compatibility branches instead of inventing runtime version APIs.

## Dependencies and diagnostics
External DLLs in `Software Inc_Data/Managed` are a documented but installation-global mutation: classify as high-impact, collision-prone and require explicit user approval. A mod-local dependency loaded through `AssemblyResolve` belongs to the local DLL/full-access architecture and is not the normal Workshop path.

`-DisableModErrors` is a development diagnostic option for investigating injected mod-error handling, not a production requirement or final verification method.

## Workshop and GiveMeFreedom
`GiveMeFreedom` is a full-access local/DLL path and is incompatible with normal Workshop upload. Do not present a precompiled/full-access architecture as an interchangeable Workshop deliverable.

## Known gaps / evidence limits
Exact Beta 1.8.42 managed assembly/API evidence remains mandatory for generation-grade exact-target Code claims.
