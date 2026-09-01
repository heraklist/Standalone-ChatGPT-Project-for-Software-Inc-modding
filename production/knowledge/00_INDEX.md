---
document_id: K00
title: Knowledge Index
knowledge_type: INDEX
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [router, aliases, retrieval]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH_WITH_EXACT_TARGET_GATE
known_version_gaps: [Beta 1.8.42 exact environment corpus pending]
---

# Knowledge Index

## Purpose
This is the retrieval router for the standalone Software Inc Mod Studio. Retrieve the smallest owner set that can answer the request; fail closed when an owner document or critical evidence is unavailable.

## Routing aliases
- `won't load`, `console`, `reload` → `12_DEBUGGING_CONSOLE_AND_RUNTIME.md`.
- `HUD`, `custom window`, `WindowManager`, `PlayerPrefs` → `06` + `07`.
- `floor texture`, `wall material` → `09_MATERIALS.md`.
- `chair`, `desk`, `snap point` → `08_FURNITURE.md`.
- `SoftwareType`, `Category`, `Feature`, `AddOn`, `Manufacturing`, `AmountScript` → `04_DATA_MODDING.md`; add `05_SIPL.md` for scripts/expressions.
- `building`, `blueprint`, `hardware design` → `11_EDITOR_CONTENT_HARDWARE_BLUEPRINTS_BUILDINGS.md`; Hardware SoftwareType integration also uses `04`.
- `Workshop`, compiler profile → `06_CODE_MODDING_CORE_AND_DISTRIBUTION.md`.

## Retrieval contract
Retrieve `01` for version/evidence conflicts, `02` for routing ambiguity, then only the owner family documents needed. Do not use archive/work material as production truth.

## Known gaps / evidence limits
Exact Beta 1.8.42 local corpus and assembly surface remain a production-release gate.
