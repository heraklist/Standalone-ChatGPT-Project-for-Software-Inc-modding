---
name: implementation
description: Bounded SIM lifecycle workflow for coordinating artifact-producing implementation across Software Inc domains.
---

# Implementation

Use this lifecycle workflow after the goal and any necessary design decisions are sufficiently resolved.

Coordinate artifact-producing work in dependency order. Consume the accepted goal, design constraints, target version, relevant evidence, and current working-copy state; then request or consume domain-owned implementation proposals through the SIM orchestrator.

This lifecycle workflow does not own Software Inc domain syntax, schemas, APIs, or content truth. Domain specialists own those details. Its responsibility is to coordinate implementation steps, preserve dependencies, keep work inside the controlled working copy, and produce structured proposed artifact changes for orchestration and later verification.

Return proposed file/state changes, files touched, assumptions, unresolved gaps, validation needs, and the next implementation action to the SIM orchestrator.

This workflow does not dispatch peer specialists and does not mutate canonical SIM session state directly. Only the orchestrator composes domain work and commits accepted updates.
