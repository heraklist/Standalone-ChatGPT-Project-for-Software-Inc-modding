---
name: data-tyd
description: Bounded SIM domain workflow for Software Inc Data modding and TyD authoring, repair, migration, and validation.
---

# Data and TyD

Own Software Inc Data/TyD work for `SoftwareTypes`, `CompanyTypes`, `NameGenerators`, root `Personalities.tyd`, and documented Data definitions nested inside those surfaces.

Documented public Data package structure under `Mods/<ModName>/` includes `SoftwareTypes/`, `CompanyTypes/`, `NameGenerators/`, and optional root `Personalities.tyd`. `Categories`, `Features`, `SubFeatures`, `AddOns`, and Manufacturing definitions are nested concepts, not canonical directories or standalone generic Data files.

SoftwareType definitions own Categories, Features/SubFeatures, AddOns, hardware/manufacturing Data, balancing fields, and documented references. `Override True` is a partial SoftwareType override; when it supplies `Features`, that feature list is replaced as a whole. `Override Delete` is the documented directive for removing the matching SoftwareType definition. Keep these semantics scoped to SoftwareTypes.

For TyD authoring, use quoted strings, numbers, lists such as `[a; b]`, tables, and `#` comments as documented. Canonical generated TyD booleans are `True` and `False`. Preserve these guardrails: no universal field-order law, no lowercase-only boolean law, and no Greek-semicolon law. Do not infer parser behavior beyond verified Software Inc evidence.

Keep the TyD/SIPL boundary explicit. SIPL arrays such as `~[a, b]` and SIPL `//` comments belong to the SIPL parser, not TyD.

Use generated focused references for detailed game truth rather than duplicating the canonical knowledge base. Return structured findings, proposed file or design changes, evidence used, assumptions, unresolved gaps, and validation needs to the SIM orchestrator.

Do not dispatch peer specialists. Do not mutate canonical SIM session state directly. The orchestrator owns cross-domain composition, accepted changes, and final state transitions.
