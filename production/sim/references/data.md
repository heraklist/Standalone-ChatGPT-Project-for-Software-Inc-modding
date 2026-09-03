---
document_id: K04
title: Data Modding
knowledge_type: FAMILY
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [Data, SoftwareType, CompanyType, AddOn, Hardware]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH
known_version_gaps: []
---

# Data Modding

## Public Data package structure
Documented public Data package structure is `Mods/<ModName>/SoftwareTypes/`, `CompanyTypes/`, `NameGenerators/`, with optional root `Personalities.tyd`. `Categories`, `Features`, `AddOns`, and `Manufacturing` are nested concepts in SoftwareType definitions, not canonical `Data/Features.tyd`, `Data/AddOns.tyd`, or `Data/Manufacturing.tyd` files.

## SoftwareTypes
SoftwareType TyD owns Categories, Features/SubFeatures/SpecFeatures, AddOns, hardware/manufacturing data, balancing values, and references such as Hardware `Design`/`FeatureBinding` where documented.

## CompanyTypes
CompanyTypes are separate Data files. `CompanyTypes/delete.txt` is the documented deletion mechanism.

## NameGenerators
Same-name generators merge by default; `[REPLACE]` on the first line requests replacement. Preserve file/content semantics and do not alphabetically normalize ordered data unless documented.

## Personalities
`Personalities.tyd` normally merges with the base set. `Replace True` requests replacement; it is not a generic mandatory rule merely because a mod contains more than two personalities.

## Features, AddOns and Manufacturing
Features can be nested at several levels. Level 3 custom behavior uses the documented SIPL entry points. AddOn features may define `MaxFactor`, `AmountScript`, and `DependsOn`. `AmountScript` is valid in its documented AddOn/`MaxFactor` context, uses the SIPL interpreter, binds `x` to the selected factor, and produces a formatted display value. Manufacturing definitions use `Components`, `Processes`, `FinalTime` and related documented nodes inside the relevant Data definition.

## Hardware integration
Hardware gameplay/manufacturing is Data. Hardware visual authoring is the Hardware Design capability domain. Older vanilla `HardwareDesign/` presence is `VANILLA_OBSERVED`; it does not alone prove a public current loader path. Do not present editor-generated internal HardwareDesign fields as documented public schema without stronger evidence.

## Overrides and merge semantics
`Override True` is a partial SoftwareType override: unspecified fields remain inherited. If an override supplies `Features`, the feature list is replaced as a whole. `Override Delete` deletes the SoftwareType. These semantics are domain-specific; do not generalize to every TyD table. Materials have their own table-name replacement semantics.

## Known gaps / evidence limits
Beta 1.7.15 is an older vanilla fixture, not exact-target authority.
