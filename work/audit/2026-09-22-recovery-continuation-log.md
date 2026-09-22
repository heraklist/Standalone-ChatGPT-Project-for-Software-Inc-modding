# Software Inc Mod Studio — Recovery & Continuation Audit Log

Date: 2026-09-22  
Repository: `heraklist/Standalone-ChatGPT-Project-for-Software-Inc-modding`  
Working branch: `sim/v0.2.1-remediation`  
Canonical game target: Software Inc Beta 1.8.42

## 1. Canonical anchors recovered

- `main` is the released v0.1.0 knowledge foundation at commit `62b72ca5ce3d30167228e4b77da5da289a03a1d6`.
- GitHub Release `v0.1.0` exists and is generation-grade for the governed Beta 1.8.42 target.
- The exact-target evidence gate is resolved for the canonical target. The unresolved capture template remains intentionally fail-closed and must not be confused with the resolved capture manifest.
- The canonical design specification is preserved at `docs/superpowers/specs/2026-08-31-software-inc-mod-studio-design-v1.2.md`.
- The SIM v0.2 architecture and implementation plan are preserved under `docs/superpowers/specs/` and `docs/superpowers/plans/`.

## 2. Recovery corrections

Earlier conversation-only recovery produced two stale conclusions that repository evidence corrects:

1. The exact Beta 1.8.42 corpus/assembly gate is **not missing** in the released v0.1.0 baseline. The governed exact-target evidence is present and generation-grade.
2. A SIM `SKILL.md` is **not lost**. It exists on the v0.2 stack at `production/sim/SKILL.md`, with bounded lifecycle/domain modules and package-time internal references.

Repository evidence is authoritative over those earlier recovery assumptions.

## 3. Branch / PR topology

The v0.2 work is a linear stacked series from `main` through:

- architecture
- implementation plan
- PR A machine contracts
- PR B orchestrator/lifecycle
- PR C Data/TyD/SIPL/references
- PR D Code Modding
- PR E content/editor compatibility
- PR F artifact/security tooling
- PR G behavioral evals/state machine
- PR H Preview build/CI
- PR I live/cross-surface acceptance
- v0.2.1 remediation

As of this audit, `sim/v0.2.1-remediation` is 165 commits ahead of `main` and 0 behind. No merge/release action was taken.

## 4. Current runtime implementation

The latest branch contains:

- 241 repository files
- 41 `production/sim/` files
- 14 `SKILL.md` files
- 54 Python test files
- 26 Python tooling scripts
- 17 S-series SIM behavioral evals (`S001`–`S017`)
- 9 additional A06 editor-native behavioral regression variants

The ChatGPT upload transform exposes one public `SKILL.md` and remaps lifecycle/domain skills to `references/internal/...` package resources. Those internal paths are package-time generated intentionally; they are not missing source files.

## 5. Live acceptance state

Recorded ChatGPT acceptance evidence currently resolves to:

- A01: PASS after retest
- A02: PASS
- A03: PASS
- A04: PASS
- A05: PASS
- A06: FAIL after four observed attempts/retests
- A07–A12: NOT_TESTED

A06 failures consistently involved editor-native Building/Blueprint fabrication through one of these escape paths:

- invented `Building.tyd` filesystem scaffold
- storage paths promoted to install contracts
- authoring/release kits around unverified loader semantics
- `.build` / `.xml` extension observations promoted to generic package/install semantics

The latest v0.2.1 remediation now encodes fail-closed rules for all of those observed escape paths. A06 remains FAIL until a fresh observed live ChatGPT retest passes.

## 6. Repository verification before this audit change

At pre-audit head `4770f579f84f845692d6ace4653cce97b283d0c4`:

- GitHub Actions `verify` run #210: SUCCESS
- pytest: 252 passed
- exact-target generation-grade validation: PASS
- legacy v0.1 generation-grade build: PASS
- SIM layout/reference/eval gates: PASS
- SIM Preview build: PASS
- independent SIM release verification: PASS

Repository-green is a Preview build candidate only; it is not live deployment acceptance.

## 7. Audit defect found and repaired

### Finding

`tools/build_sim_release.py` still reported:

- `surface_acceptance: "NOT_RUN"`
- a known gap claiming A01–A12 had not been executed
- empty `security_results`
- empty `artifact_fixture_results`

This was stale after Phase K/L evidence had recorded A01–A06. The root cause was a data-flow break: Phase J created the release report before live acceptance evidence existed, while later acceptance commits added evidence files without wiring them into the builder.

### TDD evidence

RED commit:

`f8b312440406b74d5e8270334fe468d5e58348f4`  
`test: require truthful SIM release evidence summary`

GitHub Actions run #211 failed at the new regression assertion:

`assert report["surface_acceptance"] == "FAIL"`

Observed old value:

`NOT_RUN`

GREEN implementation commit:

`23bee37d60bc599d247d12bebb108b7927c2f35e`  
`fix: report actual SIM acceptance evidence`

The builder now:

- reads recorded ChatGPT A01–A12 evidence
- follows retest supersession chains and selects one terminal result per case
- fails closed on malformed/ambiguous acceptance evidence
- derives aggregate acceptance honestly
- records non-PASS cases in `known_gaps`
- reports security/artifact fixture checks as `NOT_EXECUTED_BY_RELEASE_BUILDER` rather than silently empty arrays

Fresh GREEN evidence:

- GitHub Actions `verify` run #212: SUCCESS
- pytest: 253 passed
- exact-target generation-grade build: PASS
- SIM Preview build: PASS
- independent verifier: `SIM_RELEASE_OK`

## 8. Open audit observations

These are not yet classified as defects:

### State-transition representation

`schemas/sim-session.schema.json` stores full verification labels such as `V2 STATICALLY_REVIEWED`, while `tools/sim_contracts.py` uses shorthand `V0`–`V5`.

The helper appears repository-only and is currently exercised directly by tests; it is not a declared ChatGPT bundled tool. This is architecture debt / representation asymmetry, not yet proven runtime breakage.

### Bundled tool capability coverage

`production/sim/manifests/tool-capabilities.json` currently declares only `validate_code_profile` as a ChatGPT-bundled deterministic helper. Other repository tools exist but are not automatically treated as host-executable capabilities.

This may be intentional capability minimization. It should be evaluated against A07–A09 before expansion; tool presence must never be confused with execution evidence.

## 9. Remaining gates before Preview acceptance

1. Build/identify the fresh verified ChatGPT upload candidate from the current remediation head.
2. Execute fresh A06 on the real supported ChatGPT Skill surface.
3. If A06 passes, execute A07–A12.
4. Update compatibility/surface evidence only from observed behavior.
5. Rebuild and independently verify the Preview report from the updated evidence.
6. Complete cross-surface acceptance where supported.
7. Only after those gates, proceed to Phase M / PR J:
   - protected Preview publication workflow
   - v0.3.0 Stable promotion gate
8. Merge/release/publication remain explicit protected checkpoints.

## 10. Current continuation baseline

Current development baseline:

`sim/v0.2.1-remediation@23bee37d60bc599d247d12bebb108b7927c2f35e`

Status:

- repository CI: GREEN
- canonical Beta 1.8.42 evidence: GENERATION_GRADE
- Preview build: verified repository-side
- live ChatGPT acceptance: FAIL overall because A06 latest result is FAIL
- A07–A12: NOT_TESTED
- merge/release: NOT PERFORMED

Next mandatory product gate: **fresh live A06 retest on the actual SIM ChatGPT Skill surface**.
