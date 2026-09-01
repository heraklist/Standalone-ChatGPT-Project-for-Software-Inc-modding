# Software Inc Mod Studio v1.2 — A–O Canonical Rebuild Verification

**Verified:** 2026-09-01
**Canonical spec:** `2026-08-31-software-inc-mod-studio-design-v1.2.md`
**SHA-256:** `7b77f04c522fb48e087e1b1a0be190a27b8614cd598abf7f7ed243e3e52c31f2`

## Result

```text
PASS | 26 numbered sections | ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26']
PASS | 18 canonical retrieval files | ['00_INDEX.md', '01_EVIDENCE_VERSION_AND_TRUTH.md', '02_MOD_ECOSYSTEM_AND_ROUTER.md', '03_TYD_FOUNDATIONS.md', '04_DATA_MODDING.md', '05_SIPL.md', '06_CODE_MODDING_CORE_AND_DISTRIBUTION.md', '07_CODE_RUNTIME_UI_PERSISTENCE_SECURITY.md', '08_FURNITURE.md', '09_MATERIALS.md', '10_LOCALIZATION.md', '11_EDITOR_CONTENT_HARDWARE_BLUEPRINTS_BUILDINGS.md', '12_DEBUGGING_CONSOLE_AND_RUNTIME.md', '13_COMPATIBILITY_MIGRATION_AND_COLLISIONS.md', '14_DISCOVERY_BRAINSTORM_AND_DESIGN.md', '15_BUILD_EDIT_REPAIR_AND_DELIVERY.md', '16_VERIFICATION_AND_QA.md', '17_EVIDENCE_REGISTRY.json']
PASS | 18 retrieval files unique
PASS | markdown code fences balanced | 286
PASS | no TODO/TBD
PASS | E01-E74 complete in order | count=74 first=['E01', 'E02', 'E03'] last=['E72', 'E73', 'E74']
PASS | Evals unique
PASS | Core 74 heading
PASS | Core 74 release gate
PASS | No Core 50 remnants
PASS | artifact contract contains artifact_surface
PASS | artifact contract contains delivery_mode
PASS | artifact contract contains MOD_PACKAGE
PASS | artifact contract contains EDITOR_CONTENT
PASS | artifact contract contains INSTALLABLE_ZIP
PASS | artifact contract contains NATIVE_EDITOR_ARTIFACT
PASS | artifact contract contains WORKSHOP_READY_CONTENT
PASS | No universal final-ZIP canonical decision
PASS | Surface-aware canonical decision
PASS | Editor content forbids fabricated FS
PASS | Artifact states replace package-only state
PASS | No old package state enum
PASS | LINKED_ENGINE_API source role
PASS | delegated engine metadata
PASS | Media registry namespace
PASS | Exact env reproducible fields
PASS | Beta17 remains older
PASS | Wiki date not exact-target proof
PASS | AmountScript present
PASS | TyD/SIPL list separation
PASS | Override True partial
PASS | Personality replace not mandatory
PASS | No invented Data pseudo-layout in canonical rules
PASS | SIPL builtins complete markers
PASS | TyD comments vs SIPL comments
PASS | PlayerPrefs blocker
PASS | C#3 official-example conflict
PASS | No invented C#3 no-var rule
PASS | Enum usage blocker
PASS | SWINC defines
PASS | DisableModErrors documented diagnostic
PASS | External DLL dependency risk
PASS | GenerateUI documented surface
PASS | UI layout tag horizontallayout
PASS | UI layout tag verticallayout
PASS | UI layout tag gridlayout
PASS | UI layout tag contentfitter
PASS | UI layout tag layoutelement
PASS | Linked Unity comp HorizontalLayoutGroup
PASS | Linked Unity comp VerticalLayoutGroup
PASS | Linked Unity comp GridLayoutGroup
PASS | Linked Unity comp ContentSizeFitter
PASS | Linked Unity comp LayoutElement
PASS | No global Unity 2018.2 claim
PASS | Furniture TransformParent ordering
PASS | Furniture replacements exact root
PASS | Furniture debug visual fixture policy
PASS | Material three atlases
PASS | Material channels
PASS | No universal 256 material cap
PASS | Localization exact names
PASS | No camelcase localization filenames
PASS | Exact RELOAD_FURNITURE command
PASS | Exact data console commands
PASS | Hardware STANDARD
PASS | Blueprint STANDARD
PASS | Building STANDARD
PASS | Hardware verification details
PASS | Blueprint verification details
PASS | Building verification details
PASS | Editor invalidation rows
PASS | No invented layout /Mods/Buildings/ before evals
PASS | No invented layout /Mods/Blueprints/ before evals
PASS | No invented layout Data/Building.tyd before evals
PASS | No invented layout Data/BuildingBlueprint.tyd before evals
PASS | No invented layout Data/HardwareDesigns.tyd before evals
PASS | Implementation plan 74-case
PASS | Canonical decision E01-E74
PASS | Migration gate E01-E74
PASS | Canonical registry includes Media

TOTAL 80/80 PASS
SHA256 7b77f04c522fb48e087e1b1a0be190a27b8614cd598abf7f7ed243e3e52c31f2
```

## Manual integrity pass

- No duplicate Markdown headings detected.
- Critical sections manually inspected: terminal product promise, evidence/source-role model, Evidence Registry, AmountScript/SIPL, Code compiler/UI, Furniture, Materials, artifact delivery, verification profiles, Definition of Done, E65–E74, Canonical Design Decision.
- No changes were made after the final automated verification run.
