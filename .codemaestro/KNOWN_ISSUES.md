# Known Issues

## Acceptance blocker

A06 live ChatGPT acceptance remains FAIL after four observed attempts/retests.
A07–A12 are NOT_TESTED.

This blocks a claim of accepted Preview/Stable product behavior even though repository CI and packaging are green.

## Open architecture observations

1. Verification-state representation asymmetry:
schemas/sim-session.schema.json uses full labels such as V2 STATICALLY_REVIEWED while tools/sim_contracts.py uses V0–V5 shorthand. This is recorded as architecture debt, not a proven runtime defect.

2. Bundled tool capability scope:
production/sim/manifests/tool-capabilities.json intentionally declares a narrow executable-helper surface. Expansion should be evidence-driven and evaluated against A07–A09.

## Release boundary

PR #16 is draft and unmerged. No merge, Stable promotion, release publication, or branch deletion is included in DL-001 packaging.
