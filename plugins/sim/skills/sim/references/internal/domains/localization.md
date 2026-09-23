---
name: localization
description: SIM specialist workflow for Software Inc Localization packages, exact optional name-list filenames, reload/comparison helpers, and UI verification.
---

# Localization

Own Localization-specific analysis and proposed changes. Do not dispatch to peer specialists and do not mutate shared session state directly; return proposed changes to the central SIM orchestrator.

## Loader and package surface

Localization uses the documented `Localization/<Language>/` loader root, with mod-bundled localization following documented package paths where applicable. Do not invent a universal `Localization/English/modstrings.tyd` requirement.

## Exact optional name-list filenames

The canonical optional English name-list filenames are exactly lowercase:

- `femalefirstnames.txt`
- `malefirstnames.txt`
- `lastnames.txt`

Each file contains one name per line. Ordering expresses how common a name should be, so do not alphabetically sort these lists.

## Development helpers

`RELOAD_LOCALIZATION` reloads localization data but does not guarantee already rendered UI updates immediately. `COMPARE_LOCALIZATION` and `CONVERT_LOCALIZATION_TYD` are documented development helpers; preserve exact command spelling and arguments.

## Verification boundary

Verify key coverage, intended language/fallback behavior, UI display after reopening affected surfaces, ordered name lists, and UTF-8/text integrity. Static file presence does not prove every UI string is exercised; unavailable runtime checks remain `NOT_EXECUTED`.
