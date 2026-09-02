---
name: verification-delivery
description: Bounded SIM lifecycle workflow for mandatory verification-before-delivery and exact artifact state reporting.
---

# Verification and Delivery

Verification before delivery is mandatory for every generated or modified artifact.

Aggregate only checks that actually ran. Distinguish static review from Software Inc runtime or native-open evidence. When a deterministic check is unavailable on the active surface, record it as `NOT_EXECUTED` rather than implying success.

Assign artifact and verification state only from real evidence:

- `ARTIFACT_UNBUILT`
- `CANDIDATE_ARTIFACT`
- `FINAL_ARTIFACT`
- `V0 DESIGN_READY`
- `V1 ARTIFACT_GENERATED`
- `V2 STATICALLY_REVIEWED`
- `V3 LOAD_OR_NATIVE_OPEN_VERIFIED`
- `V4 BEHAVIOR_VERIFIED`
- `V5 REGRESSION_VERIFIED`

If required evidence cannot be obtained, validation keeps failing without new evidence, or completion would cross a protected boundary, return `BLOCKED` with the reason and next required action instead of overstating completion.

Return structured validation findings, proposed verification updates, known gaps, package/delivery readiness, and exact completion state to the SIM orchestrator.

This workflow does not dispatch peer specialists and does not mutate canonical SIM session state directly. The orchestrator accepts or rejects proposed state transitions and produces the final user-facing delivery.
