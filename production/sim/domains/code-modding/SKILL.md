---
name: code-modding
description: SIM specialist workflow for Software Inc Code mods, compiler/distribution profile selection, runtime persistence/security constraints, and conservative static validation.
---

# Code Modding

Own the Code-mod-specific analysis and implementation proposal. Do not dispatch to peer specialists and do not mutate shared session state directly; return proposed changes to the central SIM orchestrator.

## Profiles

Distinguish the two supported Code authoring profiles before generating or validating source:

- `GAME_COMPILED_CSHARP3`: Workshop/game-compiled `.cs` under the documented Software Inc game compiler profile. Treat the compiler target as C# 3 and avoid post-C#3 syntax. The documented straight-`.cs` enum caveat remains a blocker for this profile.
- `LOCAL_PRECOMPILED`: externally compiled local DLL architecture. Do not apply the game compiler's lexical C#3/enum restrictions as if they were compiler rules for this profile; runtime/API compatibility with the target game still requires separate verification.

C# 3 supports `var`, lambdas/query expressions, and LINQ. Do not reject lambda `=>` merely because expression-bodied members also use that token.

## Official example conflict

The official Code documentation shows an expression-bodied `ModMeta.Name => ...` example while also documenting the game compiler as C# 3. Preserve this as `SOURCE_CONFLICT`. For `GAME_COMPILED_CSHARP3`, generate a C#3-compatible property getter instead of expression-bodied syntax.

## Persistence and target blockers

For Beta 1.8.34 and later, `UnityEngine.PlayerPrefs` is a static blocker because the official patch notes state those mods no longer load. Use documented `ModBehaviour.SaveSetting` / `LoadSetting` for global settings or `Serialize` / `Deserialize` plus `WriteDictionary` for per-save state. Keep `ModMeta.Name` stable unless an explicit migration handles persistence identity changes.

## Distribution and security

`GiveMeFreedom` belongs to a local/full-access DLL architecture and is incompatible with the normal Workshop path. Do not present full-access/precompiled output as an interchangeable Workshop artifact.

Placing external dependencies in `Software Inc_Data/Managed` is an installation-global dependency mutation. Classify it as high-impact and collision-prone; require explicit user approval before any such mutation. Prefer non-destructive analysis and package-local designs when supported.

## Validation boundary

`tools/validate_code_profile.py` is a conservative lexical checker, not a C# compiler. Use it to catch evidence-backed profile hazards such as enum syntax and expression-bodied members for `GAME_COMPILED_CSHARP3`. Compiler success does not establish runtime/API correctness; unavailable runtime checks remain `NOT_EXECUTED`.
