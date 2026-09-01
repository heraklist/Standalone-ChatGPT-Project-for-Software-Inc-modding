# Release Process

## Release surfaces

A repository release is not automatically a runtime-verified Software Inc mod. This process packages the **ChatGPT Project knowledge surface**.

Two release statuses exist:

- `STRUCTURAL_PREVIEW` — repository structure, knowledge identities, manifests, evals, and static gates pass, but exact Beta 1.8.42 generation-grade evidence is incomplete.
- `GENERATION_GRADE` — permitted only when `tools/validate_exact_target.py` reports no missing exact-target evidence.

## Canonical flow

```text
approved source/claim changes
→ update production owner document
→ update Evidence Registry
→ update affected deterministic evals
→ run full CI
→ build release bundle
→ inspect generated manifests
→ publish/share the approved bundle
```

## Bundle contract

`tools/build_release.py` creates:

```text
project-instructions/PROJECT_INSTRUCTIONS.md
knowledge/<18 exact canonical files>
manifests/knowledge-pack-manifest.json
manifests/release-manifest.json
```

Repository evals, migration work, historical research, and raw archives are QA/evidence assets and are not part of the ChatGPT Project knowledge upload bundle.

## Structural preview

Run:

```bash
python tools/build_release.py
```

The built manifest resolves all upload-payload SHA-256 values. The release report records the final ZIP SHA-256. Structural preview must retain `exact_target_generation_grade: false`.

## Generation-grade release

Run only after an exact-target capture has replaced UNKNOWN/null values in the Beta 1.8.42 capture manifest:

```bash
python tools/build_release.py --generation-grade
```

The builder must refuse the release if any exact-target requirement is missing. Never bypass this gate by editing release status or hashes manually.

## Merge/release checklist

- CI green on the PR checkout.
- Exactly 18 production knowledge files.
- Resident Project Instructions separate from the 18-file count.
- Evidence Registry validates.
- E01–E74 validates and auxiliary suites remain present.
- Legacy critical claim map contains no `UNMAPPED` item.
- No invented Software Inc filesystem paths introduced.
- `STRUCTURAL_PREVIEW` is used whenever exact-target evidence is incomplete.
