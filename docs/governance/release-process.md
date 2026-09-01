# Release Process

## Release surfaces

A repository release is not automatically a runtime-verified Software Inc mod. This process packages the **ChatGPT Project knowledge surface**.

Two release statuses exist:

- `STRUCTURAL_PREVIEW` — repository structure, knowledge identities, manifests, evals, and static gates pass, but the build is not being asserted as the canonical exact-target release.
- `GENERATION_GRADE` — permitted only when `tools/validate_exact_target.py` reports no missing exact-target evidence.

For **v0.1.0**, Beta 1.8.42 exact-target evidence is resolved and the canonical release path is generation-grade.

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

Repository evals, migration work, historical research, raw/private evidence, and corpus extraction payloads are QA/evidence assets and are not part of the ChatGPT Project knowledge upload bundle.

## Structural preview

Run:

```bash
python tools/build_release.py
```

The built manifest resolves all upload-payload SHA-256 values. The release report records the final ZIP SHA-256. Structural preview retains `exact_target_generation_grade: false` even when the underlying exact-target evidence is complete, because the caller did not request a generation-grade release.

## Generation-grade release

For the canonical Beta 1.8.42 release, run:

```bash
python tools/build_release.py --generation-grade
```

The builder must refuse the release if any exact-target requirement is missing. Never bypass this gate by editing release status or hashes manually.

The unresolved capture template remains fail-closed and is validated independently from the resolved capture manifest.

## v0.1.0 release checkpoint

The first production-ready ChatGPT Project knowledge release is `v0.1.0`.

A v0.1.0 release is eligible only when all of the following are true:

- Beta 1.8.42 exact-target evidence is resolved.
- `python tools/validate_exact_target.py` succeeds against the resolved capture manifest.
- The unresolved capture template still fails closed under `--structural`.
- Repository verification, evidence registry validation, and eval validation succeed.
- Generation-grade build succeeds in CI via `python tools/build_release.py --generation-grade`.
- Generated manifests contain resolved file hashes and no gate errors.
- The upload bundle contains only Project Instructions, the exact 18 knowledge files, and generated manifests.

## Merge/release checklist

- CI green on the PR checkout.
- Exactly 18 production knowledge files.
- Resident Project Instructions separate from the 18-file count.
- Evidence Registry validates.
- E01–E74 validates and auxiliary suites remain present.
- Legacy critical claim map contains no `UNMAPPED` item.
- No invented Software Inc filesystem paths introduced.
- The unresolved template remains fail-closed.
- The resolved exact-target capture passes generation-grade validation.
- Generation-grade build succeeds in CI.
- Generated release version matches the intended tag/version.
