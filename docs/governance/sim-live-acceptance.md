# SIM Live Acceptance Protocol

## Purpose

This protocol governs live acceptance for `SIM — Software Inc Modding` Preview. Repository-green evidence is necessary but is not live ChatGPT deployment acceptance. Every case uses explicit `@Sim` invocation and records only observed behavior.

Beta 1.8.42 is the implicit SIM target unless a test intentionally selects another version. Acceptance prompts may omit Beta 1.8.42 because it is the implicit SIM target; the response must still preserve exact-target evidence discipline.

Allowed case outcomes are `PASS`, `FAIL`, `PLATFORM_LIMITATION`, and `NOT_TESTED`. `PASS` requires direct observation of the required outcomes on the named surface. `PLATFORM_LIMITATION` means the surface was actually exercised far enough to establish that a platform capability blocks the case. `NOT_TESTED` means the case was not executed. Missing execution must never be promoted to `PASS`.

For every case, evidence capture is non-sensitive metadata only. v0.2.2 records bind the observation to the exact behavioral candidate and target evidence using `candidate_tree_sha256`, `semantic_aggregate_sha256`, `candidate_source_commit`, `plugin_version`, `exact_target_manifest_sha256`, `certification_protocol_version`, and `installation_evidence_id`. Required/forbidden outcome observations and the verification ceiling belong inside `host_observation`; supporting non-sensitive references belong in `evidence_refs`. Do not commit private conversation content, account identifiers, secrets, proprietary Software Inc payloads, or raw user artifacts.

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

Each v0.2.2 executed case validates against `schemas/sim-acceptance-evidence.schema.json` and records:

```json
{
  "schema_version": 2,
  "case_id": "A01",
  "surface": "ChatGPT",
  "result": "PASS",
  "candidate_tree_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "semantic_aggregate_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "candidate_source_commit": "cccccccccccccccccccccccccccccccccccccccc",
  "plugin_version": "0.2.2-preview",
  "exact_target_manifest_sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
  "certification_protocol_version": "sim-live-v2",
  "installation_evidence_id": "chatgpt-v022-example",
  "host_observation": {
    "verification_ceiling": "V2",
    "required_outcomes_observed": [],
    "forbidden_outcomes_observed": []
  },
  "evidence_refs": ["obs-a01"],
  "retest_of": null,
  "recorded_at": "2026-09-22T20:00:00+03:00"
}
```

The example digests above are format examples only. Real records must contain the exact observed candidate/target values. Transport-specific identity such as a ZIP hash belongs to installation evidence; it is not the universal behavioral candidate key.

## Fresh same-candidate sequence

For v0.2.2 Preview certification, run **A06 first** as the current blocker/canary.

- If A06 is `FAIL`, `PLATFORM_LIMITATION`, or `NOT_TESTED`, the candidate is not ChatGPT-certified and later cases cannot complete the gate.
- If A06 is `PASS`, run **fresh A01–A05** and fresh A07–A12 on the same exact candidate/context.
- ChatGPT certification requires **A01–A12** all `PASS` with the same `candidate_tree_sha256`, `exact_target_manifest_sha256`, `certification_protocol_version`, and ChatGPT surface.
- Historical v0.2.0/v0.2.1 records remain regression evidence only. They are not reused to fill v0.2.2 required cases.
- Retests may supersede an earlier result only inside the same exact certification context and through an unambiguous `retest_of` chain.

## Cross-surface protocol

### ChatGPT

ChatGPT is release-blocking for v0.2.2 Preview. After exact candidate installation/resolver evidence is recorded, run A01–A12 according to the fresh sequence above.

### Codex

Codex is release-blocking for v0.2.2 Preview. After exact candidate installation/resolver evidence is recorded, run `A01, A03, A09, A10, A12` fresh on Codex. A ChatGPT PASS is never copied to Codex.

### ChatGPT Project

ChatGPT Project is non-blocking for v0.2.2 Preview unless a later versioned certification profile explicitly advertises Project as a required supported surface. Evidence may still be collected, but it cannot substitute for a required ChatGPT or Codex case.

### No-script behavior

On a surface where deterministic script execution is unavailable, require `NOT_EXECUTED` for the unavailable check and a lower verification ceiling. Static review must not be relabeled as load/native-open or behavior verification. When the required case itself proves a platform limitation, record `PLATFORM_LIMITATION`; required-surface limitations block certification rather than becoming PASS.

## Historical execution checkpoint — 2026-09-02

The 2026-09-02 agent checkpoint remains historical evidence of the execution boundary observed at that time. It predates the v0.2.2 candidate-bound record contract and cannot certify v0.2.2. Later live A-case records remain separate observed evidence and must satisfy the fresh same-candidate sequence above to contribute to v0.2.2 certification.
