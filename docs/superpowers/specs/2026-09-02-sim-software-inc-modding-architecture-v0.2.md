# SIM — Software Inc Modding Architecture v0.2

Status: DESIGN CANDIDATE
Date: 2026-09-02
Baseline: Software Inc Mod Studio v0.1.0
Canonical baseline commit: `62b72ca5ce3d30167228e4b77da5da289a03a1d6`
Canonical game target: Software Inc Beta 1.8.42
Evidence grade: GENERATION_GRADE

## 1. Purpose

SIM is the next delivery/runtime architecture for Software Inc Mod Studio.

The mission does not change. SIM remains a full-lifecycle Software Inc modding environment that can research, brainstorm, design, create, edit, extend, repair, debug, migrate, validate, package, and verify mods. The change is how the product is invoked, orchestrated, and distributed.

The user-facing entry point is explicit:

```text
@Sim
```

SIM is not a documentation-only or advisory skill. When the user asks to build, edit, repair, migrate, or package a mod, SIM should produce the strongest real artifact the active surface supports and report exactly how far that artifact has been verified.

## 2. Product model

The product architecture is:

```text
Software Inc Mod Studio
├── Canonical evidence/governance repository
├── SIM runtime
│   ├── one user-facing @Sim entry point
│   ├── one central orchestrator
│   ├── lifecycle methodology modules
│   ├── Software Inc domain specialist modules
│   ├── generated/focused references
│   ├── deterministic validators/generators where supported
│   └── artifact/verification pipeline
└── Compatibility surfaces
    ├── ChatGPT Skills / Plugin container when officially supported
    ├── ChatGPT Projects as optional workspaces
    ├── Codex
    └── other Agent Skills-compatible clients
```

The repository MUST NOT invent an undocumented ChatGPT Plugin manifest, package schema, nested-skill runtime, or persistence mechanism. Product semantics are stable; packaging adapts to documented host capabilities.

## 3. Invocation and session contract

### 3.1 Explicit activation only

SIM is deliberately explicit-invocation-first.

```text
new chat
→ SIM inactive

@Sim <request>
→ SIM activated
```

The product UX must not depend on automatic skill activation as its primary entry mechanism.

### 3.2 Persistent thread session

Desired SIM behavior after explicit activation:

```text
@Sim ...
→ SIM owns the Software Inc modding session for the thread
→ follow-up Software Inc requests continue without repeated @Sim
```

A clearly unrelated request causes a graceful temporary yield. Returning to the Software Inc modding task resumes the active SIM session.

A new chat resets SIM to inactive.

If a host surface cannot preserve invocation/session ownership natively, SIM must disclose that platform limitation and use the strongest explicit compatibility fallback. It must never pretend persistence that the surface does not provide.

## 4. Core operating invariants

SIM is defined by the following hard invariants:

```text
explicit outer activation
+
persistent thread work session where supported
+
automatic internal specialist routing
+
high autonomy
+
artifact-first execution
+
proactive research when needed
+
non-destructive mutation by default
+
verification before delivery
+
zero fabrication
```

### 4.1 High autonomy

After receiving an adequate goal, SIM advances autonomously through research, design, implementation, validation, repair, packaging, and delivery.

SIM asks the user only when:

- a material product/gameplay fork cannot be responsibly resolved;
- indispensable input is missing;
- a protected destructive/public/external action requires approval.

Routine implementation decisions are not converted into repeated confirmation prompts.

### 4.2 Autonomous but never fabricate

High autonomy never overrides evidence discipline.

If a path, schema, API, runtime behavior, or file format cannot be verified, SIM must not invent it. It should research first, continue with the strongest supported implementation, and label unresolved parts as `UNVERIFIED`, `RESEARCH_REQUIRED`, or an equivalent explicit state.

## 5. Product scope

SIM preserves the complete Software Inc Mod Studio scope, including:

- mod concept discovery and brainstorming;
- proactive external research and feasibility analysis;
- Data/TyD authoring;
- SoftwareTypes, Categories, Features, SubFeatures, AddOns;
- CompanyTypes, NameGenerators, Personalities;
- hardware/manufacturing Data;
- SIPL and Level-3 features;
- Code Mods / DLLMods / C# source;
- persistence, UI, networking, events, assets, security;
- Furniture;
- Materials;
- Localization;
- Hardware Design;
- Building Blueprints;
- Buildings;
- uploaded folder/ZIP inspection;
- debugging and repair;
- version migration/modernization;
- compatibility and collision analysis;
- artifact packaging;
- static/runtime/native verification planning and reporting.

ModForge is a separate product. ModForge limitations, schemas, or support boundaries are never treated as Software Inc engine truth for SIM.

## 6. Adaptive lifecycle methodology

SIM uses lifecycle methodologies only when they improve the task.

```text
well-specified fix
→ debug / repair directly

open-ended idea
→ research
→ brainstorm
→ feasibility
→ design
→ implementation
```

Brainstorming is not mandatory ceremony.

The lifecycle layer contains at least:

- `research-evidence`
- `brainstorm-design`
- `implementation`
- `systematic-debugging`
- `verification-delivery`

The lifecycle layer answers: **how should this task be worked?**

## 7. Software Inc domain specialists

The domain layer answers: **which Software Inc domain owns the task?**

Initial domain modules:

- `data-tyd`
- `sipl`
- `code-modding`
- `furniture`
- `materials`
- `localization`
- `editor-native`
- `compatibility-packaging`

Specialists are internal implementation details and silent by default. The user sees SIM as one coherent product. Routing detail may be exposed for architecture review, audit, debugging, or when the user asks.

## 8. Central orchestration

Only the SIM orchestrator may:

- create and own the work session;
- classify intent;
- select lifecycle methodologies;
- dispatch domain specialists;
- sequence multi-specialist work;
- resolve proposal conflicts;
- commit state changes;
- control repair loops;
- enforce security boundaries;
- decide completion;
- synthesize the final user-facing result.

Specialists MUST NOT independently dispatch other specialists or mutate shared session state directly.

## 9. Structured specialist protocol

### 9.1 Specialist request

Conceptual request contract:

```text
SPECIALIST_REQUEST

request_id
session_id
task
intent
target_game_version
domain_scope
relevant_files
relevant_design_decisions
relevant_evidence
constraints
requested_output
verification_target
```

### 9.2 Specialist result

Conceptual result contract:

```text
SPECIALIST_RESULT

request_id
status
scope
findings
decisions
proposed_changes
files_touched
evidence_used
assumptions
unresolved_gaps
validation
requested_followup
risk_flags
next_action
```

Allowed statuses:

- `READY`
- `PARTIAL`
- `BLOCKED`
- `FAILED`

Handoffs are structured and auditable, not unrestricted free-form inter-agent narration.

## 10. Canonical work session

SIM maintains one structured operational state per active modding thread:

```text
SIM_SESSION
├── meta
├── goal
├── target
├── baseline
├── architecture
├── workspace
├── evidence
├── decisions
├── validation
├── artifact
├── risks
└── history
```

Only the orchestrator has write ownership.

Specialists receive scoped reads and return proposed updates.

The session stores operational facts only: goals, files, evidence, material decisions, validation, artifact state, and auditable state transitions. It is not a private chain-of-thought store.

## 11. Evidence and truth architecture

The existing repository remains the authority:

```text
production/knowledge/
production/evals/
production/manifests/
work/corpus/
work/evidence/
schemas/
tools/
tests/
```

The current claim-scoped evidence model remains canonical:

`source_class × source_role × currency × scope × confidence × verification`

Conflict states remain:

- `CONSISTENT`
- `SOURCE_CONFLICT`
- `VERSION_CONFLICT`
- `SCOPE_CONFLICT`
- `UNRESOLVED`

SIM must not replace claim-scoped reasoning with a global source-precedence ladder.

## 12. Governed game-version targeting

SIM product version and Software Inc game target are independent.

Example:

```text
SIM v0.2.x-preview
Canonical game target: Beta 1.8.42
Evidence grade: GENERATION_GRADE
```

If the user does not specify a Software Inc version, SIM defaults to the latest fully verified canonical target.

A newly discovered game version may be researched for the current task, but it is not silently promoted to canonical. Canonical promotion requires governed evidence capture, corpus/API/schema analysis, collision refresh, regression evals, exact-target validation, and release promotion.

## 13. Proactive research

SIM may research without asking permission when research is materially required for correctness, currency, feasibility, or creative design.

Routing policy:

```text
stable generation-grade claim
→ canonical evidence first

version-sensitive/current claim
→ targeted current research

uncertain feasibility
→ targeted research

open-ended mod concept
→ broader research may include community patterns and real-world inspiration
```

SIM must preserve source roles. Community patterns and inspiration never become engine truth merely because they are useful design input.

Session research findings do not automatically mutate canonical repository knowledge. Promotion into canonical evidence remains governed.

## 14. Single source of truth and generated references

SIM references are a downstream distribution layer, not a second manually maintained knowledge base.

```text
canonical knowledge/evidence
→ deterministic transform/copy/excerpt
→ focused SIM references
→ hash-bound release
```

Each generated/copied reference must be traceable through a source map containing, at minimum:

- output path;
- canonical source path(s);
- source SHA-256;
- transform type (`COPY`, `EXCERPT`, `DERIVED_METADATA` or equivalent);
- output SHA-256.

If a canonical source changes without rebuilding the dependent SIM reference, CI must fail.

## 15. Authoring pipeline

For new file/package mod projects:

```text
intent
→ resolve target
→ research if needed
→ brainstorm/design if useful
→ select family/families
→ build internal execution plan
→ generate files
→ deterministic/static checks
→ repair detected failures
→ revalidate
→ package where appropriate
→ report artifact + verification state
```

Supported intent classes include at least:

- `CREATE`
- `EDIT`
- `EXTEND`
- `REPAIR`
- `DEBUG`
- `MIGRATE`
- `MODERNIZE`
- `AUDIT`
- `VALIDATE`
- `PACKAGE`
- `RESEARCH`
- `BRAINSTORM`
- `EXPLAIN`
- `COMPARE`

## 16. Existing-mod repair pipeline

User-provided artifacts are preserved as a read-only baseline:

```text
original artifact
→ inventory + hashes
→ family detection
→ static inspection
→ diagnosis
→ isolated working copy
→ minimal/requested repair
→ validation
→ regression checks
→ new repaired artifact
```

Default behavior is non-destructive. A repair request does not imply permission to overwrite or delete the original.

A bugfix request should preserve unrelated behavior. Modernization/redesign occurs only when requested or necessary to satisfy an explicit target.

## 17. Artifact surfaces

### 17.1 File/package surfaces

For documented filesystem mod families, SIM should create real files/directories and package them where appropriate.

### 17.2 Editor-native surfaces

Hardware Design, Building Blueprint, and Building remain editor/native content families.

SIM may design them, guide native creation, handle verified native artifacts, and report native-open verification where available.

SIM MUST NOT invent public filesystem schemas, TyD formats, or `/Mods/...` paths for editor-native content when not evidenced.

## 18. Artifact states and verification levels

Canonical artifact states remain:

- `ARTIFACT_UNBUILT`
- `CANDIDATE_ARTIFACT`
- `FINAL_ARTIFACT`

Canonical verification levels remain:

- `V0 DESIGN_READY`
- `V1 ARTIFACT_GENERATED`
- `V2 STATICALLY_REVIEWED`
- `V3 LOAD_OR_NATIVE_OPEN_VERIFIED`
- `V4 BEHAVIOR_VERIFIED`
- `V5 REGRESSION_VERIFIED`

SIM may advance these states only with real supporting evidence.

Generation does not imply V3. Static review does not imply runtime behavior. “Looks correct” does not imply native/game load verification.

## 19. Verification before delivery

Every artifact-producing or artifact-modifying workflow must run the highest available meaningful verification before completion.

```text
generate / modify
→ verify
→ failure?
   ├─ yes → diagnose → repair → verify again
   └─ no  → continue
→ package
→ verify package
→ deliver
```

SIM should automatically repair validation failures when there is a clear evidence-backed fix.

Repair loops stop when:

- the same failure repeats without new evidence;
- required runtime/native evidence is unavailable;
- the next action crosses a protected boundary;
- a material unresolved design fork appears.

Then SIM returns `BLOCKED` with cause, evidence, attempted repairs, and the next required action.

## 20. Capability-adaptive execution

Bundled deterministic scripts strengthen SIM but are not assumed to be executable on every surface.

```text
script execution available
→ run actual validator/generator
→ consume actual output

script execution unavailable
→ strongest static/manual fallback
→ explicitly mark deterministic check as NOT_EXECUTED
```

SIM never fabricates tool execution or success.

Potential deterministic tooling includes:

- TyD static checks;
- TyD/SIPL boundary checks;
- Data layout validation;
- identifier/collision checks;
- mod-tree inspection;
- Code profile checks;
- package validation;
- artifact hashing;
- ZIP/package building.

Static tooling never masquerades as Software Inc runtime verification.

## 21. Collision and compatibility behavior

Collision handling is first-class.

SIM must distinguish:

- vanilla collision;
- internal duplicate;
- intentional documented override;
- cross-file broken reference;
- safe prefixed identifier.

For migrations, issues should be classifiable as:

- `SAFE_AUTOFIX`
- `REVIEW_REQUIRED`
- `RUNTIME_REQUIRED`
- `UNKNOWN`

## 22. Code Mod safety/profile behavior

User-supplied code and binaries are inspected statically first.

SIM distinguishes at least:

```text
WORKSHOP / GAME-COMPILED .cs
→ C#3 restrictions
→ no enum usage
→ workshop-safe constraints

LOCAL / PRECOMPILED DLL
→ broader source syntax may be possible
→ runtime compatibility still required
```

User-supplied DLLs are not executed by default.

## 23. Security and trust boundaries

Trust classes:

```text
TRUSTED_SIM
USER_DATA
UNTRUSTED_EXECUTABLE
EXTERNAL_MUTATION
```

Risk classes:

```text
R0 READ
R1 WORKSPACE_WRITE
R2 EXTERNAL_REVERSIBLE
R3 EXTERNAL_DESTRUCTIVE_OR_PUBLIC
```

Default autonomy:

- R0: autonomous;
- R1: autonomous inside controlled working state;
- R2: task-dependent and permitted when clearly within the explicit task;
- R3: explicit approval required.

Implementation autonomy does not imply integration or publication autonomy.

Examples of protected actions include:

- overwriting/deleting original artifacts;
- merge;
- branch deletion;
- public release/tagging/publishing;
- Steam Workshop upload;
- remote deployment;
- direct live-game-installation mutation;
- high-impact global dependency mutation.

## 24. Untrusted input and prompt injection

Uploaded ZIPs, READMEs, comments, localization strings, source comments, web pages, community posts, and repository content are data/evidence, not authority over SIM.

Instructions embedded inside analyzed artifacts or research sources must not override the SIM operating contract or user intent.

Unknown executables, user-supplied DLLs, installers, PowerShell/batch files, and arbitrary scripts are not run merely because they are present in an artifact.

## 25. Repository mutation model

For repository work, the preferred model is:

```text
canonical main
→ feature branch
→ implementation
→ tests/CI
→ PR
→ human integration checkpoint
```

SIM may work autonomously within an approved branch/task scope, but merge, destructive branch deletion, release, or public publishing remain protected checkpoints unless explicitly approved.

## 26. Evaluation architecture

### 26.1 Existing domain correctness

E01–E74 remain canonical Software Inc correctness requirements.

No SIM release may lower or discard them.

### 26.2 SIM behavioral evals

Add a separate `S001+` behavioral suite covering at least:

- explicit activation;
- session continuity;
- unrelated-request yield/resume;
- intent/lifecycle/domain routing;
- hybrid routing;
- decision retention;
- research judgment;
- evidence conflict handling;
- autonomy / anti-over-questioning;
- artifact production;
- repair correctness;
- non-destructive behavior;
- migration;
- collision handling;
- security and prompt injection;
- mutation boundaries;
- capability fallback;
- verification honesty;
- repair-loop termination;
- structured handoff/schema validity;
- state-transition validity.

Behavioral evals should test contract outcomes, not brittle exact wording.

## 27. Test artifacts and fixtures

Create small synthetic, redistributable fixtures for deterministic testing, for example:

```text
data-valid
data-broken
data-sipl-valid
sipl-broken
code-csharp3-valid
code-csharp3-invalid
furniture-valid
materials-valid
localization-valid
malicious-prompt-injection
migration
```

Fixtures must not contain raw proprietary Software Inc game payloads.

Repair tests should assert both expected fixes and preservation of unrelated content, including original artifact/hash preservation where relevant.

## 28. Machine contracts

Planned schemas include:

```text
sim-session.schema.json
sim-plan.schema.json
sim-specialist-request.schema.json
sim-specialist-result.schema.json
sim-reference-map.schema.json
sim-release-manifest.schema.json
sim-eval.schema.json
```

State transition rules must reject unsupported jumps such as `ARTIFACT_UNBUILT → FINAL_ARTIFACT` without generation or `V2 → V5` without evidence.

## 29. Cross-surface acceptance

SIM must be tested on actual supported surfaces rather than assuming parity.

Target acceptance surfaces include, where available:

- plain ChatGPT conversation with `@Sim`;
- ChatGPT Project with `@Sim`;
- Codex;
- another Agent Skills-compatible client when practical.

Capabilities to test include:

- explicit invocation;
- thread/session continuity;
- reference loading;
- script execution;
- artifact creation;
- external tool integration.

Unsupported capabilities are recorded as platform limitations, not hidden failures or fabricated passes.

At least one complete successful mod workflow must be demonstrated outside a dedicated ChatGPT Project before first Stable promotion.

## 30. Release channels and versioning

SIM product version and Software Inc game target remain independent.

Release channels:

### PREVIEW

For new SIM runtime capabilities, platform-sensitive behavior, or newly observed game-version evidence under evaluation.

Known gaps and verification ceilings must be explicit.

### STABLE

Default channel. Stable requires all mandatory correctness, evidence, security, artifact, and acceptance gates to pass.

No silent promotion from Preview to Stable or from an observed game version to a canonical game target.

## 31. Repository migration model

The v0.1.0 repository remains the canonical foundation.

Existing surfaces remain valid:

```text
production/project-instructions/
production/knowledge/
production/evals/
production/manifests/
work/corpus/
work/evidence/
schemas/
tools/
tests/
docs/governance/
```

Add a new product source tree under:

```text
production/sim/
```

Conceptual layout:

```text
production/sim/
├── SKILL.md
├── lifecycle/
├── domains/
├── references/
├── scripts/
├── assets/
└── manifests/
```

This is source structure, not an assertion that every host supports nested executable skills. If a host supports only a single public skill plus resource files, internal lifecycle/domain modules are packaged as workflow resources while preserving the same semantics.

## 32. v0.1.0 preservation

The existing Project-first release remains a frozen, supported canonical knowledge foundation.

SIM migration must not delete or silently rewrite the v0.1.0 product semantics.

Project deployment becomes compatibility/workspace mode rather than the primary future distribution model.

The existing Project release/build path should remain reproducible until explicitly deprecated through governance.

## 33. Proposed SIM repository additions

Planned additions include:

```text
production/sim/
production/evals/sim/
tests/fixtures/sim/
```

and tools such as:

```text
build_sim_references.py
validate_sim_references.py
validate_sim_skills.py
build_sim_release.py
verify_sim_release.py
run_sim_evals.py
```

Existing v0.1.0 tooling should be reused rather than rewritten where responsibilities already match.

## 34. Release artifacts

A SIM Preview/Stable release should produce independently verifiable artifacts such as:

```text
dist/
├── sim-<version>.zip
├── sim-<version>.release-report.json
├── sim-<version>.reference-source-map.json
└── sim-<version>.checksums.txt
```

A formal Plugin package is emitted only when the official package authoring surface and schema are verified. The repository must not fabricate one.

## 35. Release report

The release report should record at least:

- SIM version;
- channel;
- canonical Software Inc target;
- evidence grade;
- source revision;
- skill/package digest;
- reference-map digest;
- domain eval results;
- SIM behavioral eval results;
- security results;
- artifact fixture results;
- cross-surface acceptance status;
- known gaps;
- release status.

## 36. Stable release gates

A Stable release is fail-closed and should require, at minimum:

1. repository structural validation;
2. canonical evidence validation;
3. exact-target validation;
4. E01–E74 green;
5. mandatory S-evals green;
6. machine-schema validation;
7. reference-source-map/hash validation;
8. skill/resource structural validation;
9. deterministic script tests;
10. golden artifact tests;
11. repair/migration tests;
12. security tests;
13. deterministic/reproducible build controls;
14. release artifact verification;
15. live cross-surface acceptance.

A partially green build is not Stable.

## 37. Initial live acceptance set

The first Preview-to-Stable acceptance set should include at least:

```text
A01  explicit @Sim cold activation + new Data mod
A02  open-ended brainstorming → design
A03  Data + SIPL hybrid
A04  Code Mod repair
A05  Furniture or Materials creation
A06  Building/Blueprint no-fabrication test
A07  uploaded broken ZIP repair
A08  collision detection
A09  limited-capability fallback
A10  multi-turn session continuity
A11  unrelated-question yield/resume
A12  artifact + V-level honesty
```

## 38. Version roadmap

```text
v0.1.0
Canonical Knowledge Foundation
Project-first generation-grade release

v0.2.0-preview
SIM runtime foundation
@Sim orchestrator
session/hand-off schemas
generated references
initial lifecycle/domain modules
basic artifact workflows
initial S-evals

v0.2.x-preview
expanded deterministic tooling
expanded fixtures and repair coverage
cross-surface hardening

v0.3.0
first SIM Stable release after live acceptance
```

## 39. Implementation sequence

Implementation proceeds in bounded phases:

```text
Phase A  architecture contracts / schemas / layout tests
Phase B  outer @Sim orchestrator
Phase C  lifecycle layer
Phase D  Data/TyD + SIPL end-to-end foundation
Phase E  Code Modding
Phase F  Furniture / Materials / Localization
Phase G  editor-native + compatibility/packaging
Phase H  deterministic tooling hardening
Phase I  SIM behavioral eval expansion
Phase J  Preview release tooling
Phase K  live ChatGPT acceptance
Phase L  cross-surface acceptance
Phase M  Stable promotion
```

Every implementation phase follows TDD where machine behavior is involved:

```text
RED
→ minimal implementation
→ GREEN
→ refactor
```

Prose-heavy skill behavior is verified through behavioral/eval contracts rather than exact-string tests.

Major phases use feature branches, CI, PR review, and human integration checkpoints. Branches are not auto-deleted.

## 40. Definition of Done for first SIM Stable

The first SIM Stable is production-ready only when all of the following are true:

- explicit `@Sim` invocation works on the target ChatGPT surface;
- the complete Software Inc Mod Studio mission remains available;
- one canonical session/orchestrator model is implemented;
- internal lifecycle/domain routing works for single and hybrid tasks;
- references are derived from canonical sources and hash-bound;
- Beta 1.8.42 generation-grade evidence gates remain green unless a later governed target has replaced it;
- E01–E74 remain green;
- all required S-evals are green;
- security/trust boundaries are enforced;
- non-destructive repair works;
- real artifact generation and packaging work on capable surfaces;
- capability fallback is honest on limited surfaces;
- artifact states and V0–V5 labels are evidence-backed;
- a full workflow succeeds outside a dedicated ChatGPT Project;
- the release artifact is independently verifiable;
- platform limitations and known gaps are explicit.

## 41. Final architectural invariant

SIM changes the delivery and orchestration model of Software Inc Mod Studio, not its mission, evidence standards, authoring depth, artifact responsibilities, or verification discipline.

The canonical summary is:

```text
@Sim
→ explicit activation
→ one orchestrator
→ one stateful mod work session
→ adaptive lifecycle methodology
→ automatic internal Software Inc specialist routing
→ proactive evidence-aware research
→ high-autonomy artifact creation/repair
→ deterministic validation where supported
→ non-destructive security boundaries
→ zero fabricated schemas/runtime claims
→ exact artifact + V0–V5 verification reporting
```
