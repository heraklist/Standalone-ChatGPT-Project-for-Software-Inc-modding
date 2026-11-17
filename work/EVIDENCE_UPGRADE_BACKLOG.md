# Evidence Upgrade Backlog

This is a **work/** artifact, not production authority. It defines the fail-closed path to
raising mod reliability and knowledge coverage **without inventing engine facts**. Each item
is a research task with an acceptance criterion; a claim is only promoted into a production
owner document and the Evidence Registry after it clears `docs/governance/evidence-update-process.md`.

Nothing here changes current generation behavior. Until an item is resolved, the Studio stays
fail-closed (`RESEARCH_REQUIRED` / `RUNTIME_PROOF_REQUIRED` / `NO_DOCUMENTED_SURFACE`).

## Priority board

| # | Area | Current state | Evidence needed | Acceptance criterion |
| --- | --- | --- | --- | --- |
| 1 | Exact-target assembly surface (Code) | `01`/`06`/`07` note exact assemblies pending beyond the committed capture | Assembly-CSharp public API surface for persistence, events, UI, networking at Beta 1.8.42 | Registry claim per API with `currency: EXACT_TARGET` + `verification: ASSEMBLY_OBSERVED`; owner docs cite it |
| 2 | Building / Blueprint public schema | `11` classifies filesystem schema as unverified → `EDITOR_CONTENT` only | Whether any documented public standalone package/loader path exists | Either a corroborated loader claim, or an explicit `NO_DOCUMENTED_SURFACE` record that keeps the ban on invented `Data/BuildingBlueprint.tyd` and `/Mods/Blueprints/` |
| 3 | Mod-level load order / dependencies | `13` records no documented public mechanism | Whether the engine exposes any inter-mod resolution/declaration | A runtime/assembly-backed claim, or a reaffirmed negative record; never emit `Dependencies`/`LoadAfter`/`Priority` until resolved |
| 4 | Localization corpus | `10` notes exact shipped corpus pending | Beta 1.8.42 shipped localization keys/loader-root layout | Hash-bound localization manifest in the exact-target capture; key-coverage claim |
| 5 | Hardware Design internal fields | `11` marks editor-generated fields `UNDOCUMENTED_BUT_OBSERVED` | Which internal TyD fields are public/stable vs editor-internal | Field-level claims scoped as documented-public only where corroborated; others stay observed-only |
| 6 | SIPL member surface | `05` requires documented/shipped/assembly/runtime proof per member | Per-scope member inventory for ProductScope/SaleScope/CopyScope/DevScope at target | `LIST_SCOPE_MEMBERS` runtime capture bound to exact version/environment |
| 7 | Material atlas limits | `09` gives the `256 @ 4096²` figure as an example, not a cap | Actual per-tier capacity behavior at target | Claim scoped to the measured environment, not presented as a universal cap |

## Reliability-focused upgrades (no new engine facts required)

These raise reliability using only already-established doctrine and can proceed independently of
the research board above:

- Author per-family **authoring templates** that emit only evidence-backed structure and embed
  the `## Pre-delivery reliability checklist` gates, so every generated mod is package-complete
  and collision-checked by construction.
- Extend the Evidence Registry to record **every** `hard_generation_rule` currently asserted in an
  owner document (not only the critical conflict set), so coverage is explicit and testable.
- Capture an **exact-target vanilla identifier index** per family wherever a corpus is licensed for
  retention, to make collision preflight real rather than best-effort.

## Process reminder

For any item: new source → registry source record → claim classification → conflict/currency/scope
check → owner document update → affected eval update → CI → release manifest. Exact-target claims
must not be inferred from older vanilla corpora, wiki edit dates, or generic linked-engine docs.
