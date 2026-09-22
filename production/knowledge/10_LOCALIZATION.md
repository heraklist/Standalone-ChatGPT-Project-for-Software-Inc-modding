---
document_id: K10
title: Localization
knowledge_type: FAMILY
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [Localization, translations, names]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH
known_version_gaps: [Claim-specific localization coverage may require exact-target corpus or runtime UI evidence]
---

# Localization

## Loader and package structure
Localization is a documented top-level loader root `Localization/<Language>/`; mod-bundled localization may also follow documented mod package paths. Preserve the documented surface instead of inventing a generic `Localization/English/modstrings.tyd` law. TyD localization records use the game's localization keys/values.

## Name lists
Canonical optional English name-list filenames are exactly lowercase: `femalefirstnames.txt`, `malefirstnames.txt`, `lastnames.txt`. Each contains one name per line and is ordered by how common the name should be; do **not** alphabetically sort these lists.

## Reload and comparison
`RELOAD_LOCALIZATION` reloads localization data but does not guarantee that already rendered UI updates immediately. `COMPARE_LOCALIZATION` and `CONVERT_LOCALIZATION_TYD` are documented development helpers; preserve exact command spelling and arguments when using them.

## Verification
Check key coverage, intended language/fallback behavior, UI display after reopening affected surfaces, name-list ordering and UTF-8/text integrity. Static presence of a translation file does not prove that every UI string is exercised.

## Known gaps / evidence limits
The canonical Beta 1.8.42 exact-target generation gate is resolved. Language/key coverage questions remain claim-specific and may require shipped localization corpus inspection or runtime UI evidence.
