---
document_id: K14
title: Discovery, Brainstorm and Design
knowledge_type: WORKFLOW
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [discover, brainstorm, concept, design]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH_WITH_EXACT_TARGET_GATE
known_version_gaps: []
---

# Discovery, Brainstorm and Design

## Discovery
Infer the user's intent and ask only questions that change feasibility, family routing, distribution, artifact surface, or the meaningful design. Stop interviewing once the MOD WORKING BRIEF is sufficient.

## Brainstorming
When ideating, produce materially distinct concepts and screen each against Software Inc capability evidence before presenting it as buildable. Separate creative desirability from technical feasibility; a compelling idea can still be `RESEARCH_REQUIRED` or `CONSTRAINT_CONFLICT`.

## Concept matrix
Useful dimensions include gameplay impact, novelty, family/capability requirements, Data/SIPL/Code needs, asset needs, implementation complexity, compatibility/collision risk, balancing complexity, maintenance burden, distribution constraints and expansion potential.

## Family architecture
Prefer the minimum-sufficient technology. `DATA_SIPL` is chosen only when a documented entry point/scope can express the behavior; Code is not a default escape hatch. Hybrids are explicit architectures with component ownership and cross-component contracts.

## Constraints
Record user hard constraints separately from preferences and technical constraints. Never quietly violate a hard constraint to make an idea fit. If the requested behavior has no documented public surface, explain the limit and offer the closest supported architecture without pretending equivalence.

## Known gaps / evidence limits
Brainstorm outputs are design hypotheses until routed through evidence/feasibility and, when required, runtime proof.
