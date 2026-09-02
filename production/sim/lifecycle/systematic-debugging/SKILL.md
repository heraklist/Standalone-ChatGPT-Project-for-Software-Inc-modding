---
name: systematic-debugging
description: Bounded SIM lifecycle workflow for evidence-backed diagnosis and minimal repair of Software Inc mods.
---

# Systematic Debugging

Use this lifecycle workflow for crashes, parser/load failures, validation failures, migration regressions, or unexpected mod behavior.

Observe the actual reported or captured failure first. Isolate the smallest relevant scope, form an evidence-backed hypothesis, apply the minimal repair or diagnostic test that can distinguish the hypothesis, and verify the result before expanding the change surface.

Avoid shotgun editing. Preserve unrelated behavior and the read-only original baseline. If a repair fails, use the new evidence to refine the hypothesis; if the same failure repeats without new evidence, report the blocker instead of looping indefinitely.

Return structured findings, the working hypothesis, proposed minimal changes, validation evidence, unresolved gaps, and the next debugging action to the SIM orchestrator.

This workflow does not dispatch peer specialists and does not mutate canonical SIM session state directly. The orchestrator owns accepted repairs, cross-domain coordination, and final state transitions.
