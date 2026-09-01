# Software Inc ChatGPT Project — Knowledge Pack Audit

## Audit basis

This audit reviews the supplied `knowledge.zip` as source material for an **independent ChatGPT Project that directly designs, creates, edits, repairs and packages Software Inc mods**. It does not treat ModForge implementation limits as ChatGPT limits.

This is an internal-content audit of the supplied pack. It does not independently re-verify every factual claim against current external documentation.

## Architectural decision

The ChatGPT Project and ModForge must be independent consumers of Software Inc knowledge.

```text
                    Software Inc evidence
                           |
             +-------------+-------------+
             |                           |
             v                           v
   ChatGPT Project knowledge       ModForge knowledge
   + authoring workflows           + schemas/validators/UI
   + direct mod files              + ModSpec/compiler pipeline
```

The ChatGPT Project must never be constrained by ModForge `support_matrix.json`, ModSpec schemas, writer status, validator status or UI implementation.

## Classification

### KEEP — useful as Software Inc factual/reference knowledge

Keep after normal editorial review:

- `source_registry.json` — retain Software Inc official/community/runtime sources; remove ModForge-only sources/target metadata.
- `observations/in_game_findings.json` — valuable runtime evidence if observations remain accurately version-scoped.
- `reference/01_tyd.md`
- `reference/03_software_types.md`
- `reference/04_features.md`
- `reference/05_categories.md`
- `reference/06_name_generators.md`
- `reference/07_company_types.md`
- `reference/08_personalities.md`
- `reference/09_addons.md`
- `reference/10_hardware.md`
- `reference/11_sipl.md`
- `reference/12_code_mods.md`
- `reference/13_code_mod_patterns_1_8_41.md`
- `reference/14_furniture_materials_localization.md`
- `reference/15_debugging_validation.md`
- `reference/16_compatibility_collisions.md`
- `reference/17_vanilla_data_gap.md`
- `reference/18_balancing_authoring.md`
- `reference/19_versioning_update_policy.md`
- `reference/21_loader_taxonomy_and_unsupported_surfaces.md`
- `reference/22_runtime_regression_matrix.md`
- `reference/23_family_golden_paths.md`
- `reference/24_code_mod_operational_constraints.md`
- `community/code_mod_patterns.md`
- `community/data_mod_patterns.md`
- `community/examples_registry.json`
- actual TyD/text/C# examples that describe real Software Inc formats rather than ModSpec.

### CLEAN / SPLIT — strong engine knowledge mixed with ModForge policy

These should be retained but rewritten so engine facts and product policy are no longer mixed:

- `README.md`
- `provenance_model.md`
- `reference/00_mod_taxonomy.md`
- `reference/01_tyd.md` (`ModForge writer policy` section)
- `reference/02_data_mod_structure.md`
- `reference/03_software_types.md`
- `reference/04_features.md`
- `reference/06_name_generators.md`
- `reference/07_company_types.md`
- `reference/08_personalities.md`
- `reference/11_sipl.md`
- `reference/12_code_mods.md`
- `reference/14_furniture_materials_localization.md`
- `reference/15_debugging_validation.md`
- `reference/16_compatibility_collisions.md`
- `reference/18_balancing_authoring.md`
- `reference/19_versioning_update_policy.md`
- `reference/20_repair_validation_strategy.md`
- `reference/21_loader_taxonomy_and_unsupported_surfaces.md`
- `reference/23_family_golden_paths.md`
- `reference/24_code_mod_operational_constraints.md`

Editorial rule: replace “Current ModForge status/policy/profile” with either a pure Software Inc fact, a general authoring safety policy, or remove it.

### EXCLUDE — ModForge-specific and should not constrain the ChatGPT Project

- `support_matrix.json`
- `chatgpt/MODSPEC_OUTPUT_CONTRACT.md`
- current `chatgpt/PROJECT_INSTRUCTIONS.md`
- current `chatgpt/AUTHORING_CHECKLIST.md`
- `chatgpt/REPAIR_RESPONSE_SCHEMA.json` as currently ModForge-shaped
- `rules/active_static_execution_map.json`
- `rules/diagnostic_enrichment_schema.json`
- `rules/validator_code_map.json`
- ModSpec-specific rule/schema entries
- ModSpec JSON examples under `examples/valid/` and `examples/invalid/`
- ModForge-specific repair examples
- ModForge-specific authoring/validation eval cases

They may remain in the ModForge repository, but should not be loaded as authoritative instructions for the independent ChatGPT Project.

### ADAPT — potentially reusable machine-readable knowledge

- `rules/field_catalog.json`
- `rules/rule_catalog.json`
- `rules/console_command_catalog.json`
- `rules/repair_catalog.json`
- `rules/rule_schema.json`

Do not import them wholesale. Extract only rules whose provenance establishes **Software Inc semantics**, and remove `PROFILE_RESTRICTION` / `MODFORGE_POLICY` rules or recast them as optional authoring policy where appropriate.

## Major gaps for the independent ChatGPT Project

The supplied pack is validation/research oriented. The new Project additionally needs first-class authoring workflows.

### 1. Discovery and mini-interview

Need a workflow that can start from an incomplete idea and determine:

- player goal / gameplay purpose;
- content vs mechanic vs overhaul;
- historical / fictional / hybrid direction;
- era and progression;
- expected scope;
- preferred complexity;
- standalone vs integrated behavior;
- correct Software Inc mod family or hybrid family architecture.

The interview must stop once enough information exists.

### 2. Brainstorming

Need a creative workflow that produces materially different concepts, not cosmetic variants.

Each concept should be screened for Software Inc technical feasibility before being promoted to an implementation plan.

### 3. Concept matrix

Need reusable matrix dimensions such as:

- novelty;
- gameplay impact;
- engine fit;
- required mod family/families;
- Data/SIPL/Code requirements;
- asset requirements;
- implementation complexity;
- compatibility risk;
- balancing complexity;
- maintenance burden;
- expansion potential.

### 4. Direct artifact generation

The Project needs explicit rules for producing real Software Inc files rather than ModSpec:

- `.tyd`
- SIPL-bearing TyD / script text where valid
- name-generator `.txt`
- localization files
- furniture/material definitions and asset manifests
- C# source/project scaffolding for code mods
- metadata and directory structure
- ZIP/package output when requested.

### 5. Existing-mod edit/repair workflow

Need an input-driven workflow:

```text
uploaded folder/ZIP
  -> classify family
  -> inventory files
  -> parse/review
  -> identify defects
  -> preserve intent
  -> apply minimal repair
  -> cross-reference check
  -> output repaired files/package
  -> list runtime checks still required
```

### 6. Family-specific complete templates

The pack contains knowledge, but not enough complete canonical, user-ready templates for every family. Build verified templates/golden examples for:

- Data mod base package
- SoftwareType
- CompanyType
- Personalities
- AddOns
- Hardware/manufacturing
- SIPL Level 3 usage
- Localization
- Furniture
- Materials
- Code mod (Workshop source and local DLL development path)

### 7. Hybrid-mod architecture guidance

Need explicit guidance for ideas that span multiple families, e.g. Data + SIPL, Data + Localization, Code + Localization, Furniture + Materials, etc.

### 8. Artifact quality gate

Before declaring a mod “ready”, the Project should distinguish:

- `STATICALLY_VALIDATED`
- `SOURCE_CONSISTENT`
- `RUNTIME_TEST_REQUIRED`
- `RUNTIME_VERIFIED` only when evidence was actually supplied/run.

The Project must never claim in-game success from static inspection alone.

## Proposed independent Project knowledge structure

```text
software-inc-chatgpt/
├── PROJECT_INSTRUCTIONS.md
├── 00_core/
│   ├── mission_scope.md
│   ├── provenance_policy.md
│   ├── version_policy.md
│   ├── mod_family_taxonomy.md
│   └── artifact_quality_gate.md
├── 01_workflows/
│   ├── discover_interview.md
│   ├── brainstorming.md
│   ├── concept_matrix.md
│   ├── design_to_build.md
│   ├── edit_existing_mod.md
│   ├── debug_repair.md
│   └── hybrid_mods.md
├── 02_data_modding/
├── 03_sipl/
├── 04_localization/
├── 05_furniture/
├── 06_materials/
├── 07_code_mods/
├── 08_debugging_validation/
├── 09_vanilla_runtime_reference/
└── 10_examples_templates/
```

## Key behavioral rule

The ChatGPT Project should infer the appropriate workflow from the user's intent. The user should not need to select “Discover”, “Brainstorm”, “Build”, “Edit”, “Debug”, “Repair” or “Audit” manually.

## Migration principle

Do **not** fork ModForge implementation constraints into the ChatGPT Project.

Instead:

1. extract Software Inc factual knowledge from the existing pack;
2. preserve source/provenance/version metadata;
3. remove ModForge-specific restrictions;
4. add independent creative/authoring/repair workflows;
5. add complete family-specific real-file templates;
6. keep runtime verification honest and version-scoped.
