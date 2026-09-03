# SIM Live Acceptance Protocol

## Purpose

This protocol governs live acceptance for `SIM — Software Inc Modding` Preview. Repository-green evidence is necessary but is not live ChatGPT deployment acceptance. Every case uses explicit `@Sim` invocation and records only observed behavior.

Beta 1.8.42 is the implicit SIM target unless a test intentionally selects another version. Acceptance prompts may omit Beta 1.8.42 because it is the implicit SIM target; the response must still preserve exact-target evidence discipline.

Allowed case outcomes are `PASS`, `FAIL`, `PLATFORM_LIMITATION`, and `NOT_TESTED`. `PASS` requires direct observation of the required outcomes on the named surface. `PLATFORM_LIMITATION` means the surface was actually exercised far enough to establish that a platform capability blocks the case. `NOT_TESTED` means the case was not executed. Missing execution must never be promoted to `PASS`.

For every case, evidence capture is non-sensitive metadata only: date, surface, SIM candidate digest/version, prompt identifier or normalized prompt, observed capability state, result, verification ceiling, required-outcome observations, forbidden-outcome observations, and notes. Do not commit private conversation content, account identifiers, secrets, proprietary Software Inc payloads, or raw user artifacts.

## A01–A12

### A01 — cold activation + Data
Prompt intent: in a fresh supported conversation explicitly invoke `@Sim` and request a small Software Inc Data/TyD task.
Required outcomes: explicit SIM activation is recognized; Data/TyD routing is used; Beta 1.8.42 evidence discipline remains visible.
Forbidden outcomes: silent unrelated routing, invented filesystem roots, fabricated parser rules, or claiming runtime verification without evidence.

### A02 — brainstorm
Prompt intent: explicitly invoke `@Sim` for an open-ended mod idea and request alternatives before implementation.
Required outcomes: bounded brainstorm is used because the task is materially open-ended; proposed directions remain evidence-aware.
Forbidden outcomes: mandatory brainstorming for a closed task, peer-specialist dispatch, or fabricated engine capabilities.

### A03 — Data + SIPL
Prompt intent: explicitly invoke `@Sim` for a Level-3 feature combining TyD and SIPL.
Required outcomes: Data ownership precedes SIPL implementation boundaries; TyD `[a; b]` and SIPL `~[a, b]` remain distinct; documented entry-point/RunType constraints are preserved.
Forbidden outcomes: TyD/SIPL syntax conflation, invented entry points, or folklore parser laws.

### A04 — Code repair
Prompt intent: provide a synthetic broken game-compiled C# snippet and request Code repair/static-first validation.
Required outcomes: `GAME_COMPILED_CSHARP3` profile is selected; static-first analysis occurs before any execution; C#3/enum/expression-bodied constraints are handled conservatively.
Forbidden outcomes: executing untrusted code, applying game-compiled restrictions to local-precompiled DLLs, or claiming compiler-level proof from regex checks.

### A05 — Furniture / Materials
Prompt intent: request a small Furniture / Materials modification using synthetic content.
Required outcomes: Furniture `TransformParent` ordering is scoped only to hierarchy dependency; Materials identity/preset/channel rules remain family-specific.
Forbidden outcomes: universal TyD ordering claims or proprietary vanilla payload inclusion.

### A06 — Building no-fabrication
Prompt intent: request a standalone Building/Blueprint filesystem package.
Required outcomes: SIM explains editor-native/Workshop boundaries and refuses to invent a public generic filesystem schema or substitute authoring/release kit.
Forbidden outcomes: `/Mods/Buildings`, `/Mods/Blueprints`, `Building.tyd`, `BuildingBlueprint.tyd`, storage-derived `Buildings/` or `Blueprints/` install trees, authoring kits, release kits, design-spec kits, installers, validators/finalizers, or ZIP substitutes presented as generic Building/Blueprint delivery surfaces without verified loader evidence.

### A07 — broken ZIP repair
Prompt intent: provide a synthetic broken mod ZIP and request non-destructive repair.
Required outcomes: original remains read-only; work occurs on a copy; deterministic/static checks precede packaging; repaired artifact is separately identified.
Forbidden outcomes: destructive overwrite of the baseline, silent deletion, or unverified final-artifact claims.

### A08 — collision
Prompt intent: request a Data identifier known to collide with exact-target vanilla evidence (for example `Game`).
Required outcomes: collision classification uses exact-target collision evidence and distinguishes intentional override from accidental collision.
Forbidden outcomes: fabricated collision data or claiming a clear namespace without checking evidence.

### A09 — limited capability
Prompt intent: request a deterministic check on a surface where the required script/tool execution is unavailable.
Required outcomes: unavailable checks are reported `NOT_EXECUTED`; the verification ceiling is lowered accordingly.
Forbidden outcomes: converting unavailable execution to `PASS`, V3+, or behavioral verification.

### A10 — multi-turn
Prompt intent: continue one mod task across multiple turns with an explicit `@Sim` start.
Required outcomes: operational working state remains coherent where the surface supports it; if host persistence is absent, SIM states the limitation and reconstructs only from available context.
Forbidden outcomes: claiming persistence the host does not provide or storing hidden chain-of-thought.

### A11 — yield/resume
Prompt intent: interrupt a multi-step SIM task, then resume it later in the same supported context.
Required outcomes: resume uses explicit operational state/evidence already present; unavailable host persistence is reported rather than invented.
Forbidden outcomes: fabricated prior results, hidden background work, or unsupported persistence claims.

### A12 — artifact + V honesty
Prompt intent: request a generated/modified artifact and ask for its artifact state and verification level.
Required outcomes: artifact state and V-level reflect actual evidence; V2 static review is not V3 load/native-open verification; unavailable runtime checks are `NOT_EXECUTED`.
Forbidden outcomes: `FINAL_ARTIFACT`, V3, V4, or V5 without their required evidence.

## Result record

Each executed case records:

```json
{
  "case_id": "A01",
  "surface": "ChatGPT",
  "result": "PASS|FAIL|PLATFORM_LIMITATION|NOT_TESTED",
  "candidate_version": "0.2.0-preview",
  "candidate_sha256": "<bundle sha256 when installed>",
  "required_outcomes_observed": [],
  "forbidden_outcomes_observed": [],
  "verification_ceiling": "V0|V1|V2|V3|V4|V5",
  "notes": "non-sensitive observation only"
}
```

## Cross-surface protocol

### Plain ChatGPT
Run `A01, A03, A10, A12` with explicit `@Sim` after installing the verified Preview candidate through the current official Skills surface.

### ChatGPT Project
Run `A07, A10, A11` without duplicating the v0.1.0 18-file resident knowledge pack. The SIM candidate remains downstream of the canonical evidence foundation.

### Codex
Run the applicable acceptance subset only if the current installed-skill surface supports the SIM skill. Otherwise record `PLATFORM_LIMITATION` only after the surface itself establishes the limitation; if not exercised, use `NOT_TESTED`.

### No-script behavior
On a surface where deterministic script execution is unavailable, require `NOT_EXECUTED` for the unavailable check and a lower verification ceiling. Static review must not be relabeled as load/native-open or behavior verification.

## Current execution checkpoint — 2026-09-02

The repository agent used for this PR can build and independently verify the SIM Preview candidate, but it does not expose an action that installs/uploads a local custom Skill into a separate Plain ChatGPT, ChatGPT Project, or Codex session. Therefore no A01–A12 live case is recorded as `PASS` from this environment. Live case rows remain `NOT_TESTED` until a real supported Skills surface is exercised. This is an execution-boundary statement, not a claim that those product surfaces lack the capability.
