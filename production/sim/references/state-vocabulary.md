# SIM State Vocabulary

This file is the authoritative runtime normalization for SIM completion, artifact, verification, readiness, and blocked-state terminology. It follows the canonical design contract and prevents family-specific delivery wording from becoming parallel state machines.

## Generic artifact state

The canonical artifact-state axis is:

`ARTIFACT_UNBUILT` → `CANDIDATE_ARTIFACT` → `FINAL_ARTIFACT`

These states describe the maturity of the exact artifact being produced. A transition requires evidence for that exact artifact revision or payload identity.

## Verification level

The canonical verification axis is:

- `V0 DESIGN_READY` — the design/repair approach is evidence-bounded, but no artifact generation is proven.
- `V1 ARTIFACT_GENERATED` — the exact candidate artifact exists.
- `V2 STATICALLY_REVIEWED` — applicable deterministic/static checks that actually ran are recorded; unavailable checks remain `NOT_EXECUTED`.
- `V3 LOAD_OR_NATIVE_OPEN_VERIFIED` — the exact artifact was actually loaded by Software Inc or opened/recognized by the authoritative native editor surface.
- `V4 BEHAVIOR_VERIFIED` — required behavior was exercised on the exact loaded/native-open artifact.
- `V5 REGRESSION_VERIFIED` — the required regression profile passed on the exact artifact/environment.

Verification levels describe evidence, not optimism. Static inspection cannot establish V3, generation cannot establish V2+, and a user-facing label cannot advance a verification level without matching proof.

## Surface-specific delivery labels

Terms such as `FINAL_VERIFIED_ZIP`, `CANDIDATE_NATIVE_ARTIFACT`, and `FINAL_VERIFIED_NATIVE_ARTIFACT` are surface-specific delivery labels, not additional artifact-state enums.

- a candidate ZIP or `CANDIDATE_NATIVE_ARTIFACT` maps to `CANDIDATE_ARTIFACT`;
- `FINAL_VERIFIED_ZIP` and `FINAL_VERIFIED_NATIVE_ARTIFACT` may map to `FINAL_ARTIFACT` only after the required verification profile for that surface has actually passed;
- the delivery label never overrides the generic artifact or verification axes.

## Readiness and blocked dispositions

`READY_FOR_GAME_TESTING`, `TOOLING_BLOCKED`, and `PARTIAL_BUILD` are workflow/readiness dispositions. They do not by themselves advance artifact state or verification level.

- `READY_FOR_GAME_TESTING` means the candidate is ready for the next required game/runtime check, not that the check passed.
- `TOOLING_BLOCKED` means the required supported authoring/verification capability is unavailable on the active surface.
- `PARTIAL_BUILD` means the requested terminal artifact is incomplete and must not be presented as a complete candidate or final deliverable.

Blocked/readiness dispositions may coexist with the strongest honestly supported generic artifact and verification state.

## Transition rule

State progression is monotonic and evidence-bound. Never skip a verification level, never infer runtime/native-open proof from static checks, and never convert missing execution into PASS. `NOT_EXECUTED` is a check result, not evidence of success.