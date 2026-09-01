# Standalone ChatGPT Project for Software Inc Modding

Governed source repository for **Software Inc Mod Studio**, an independent ChatGPT Project for designing, authoring, editing, repairing, researching, and verifying Software Inc mods.

This project is independent from ModForge. ModForge schemas, validators, writers, support matrices, and UI capabilities do not define Software Inc engine truth for this repository.

## Repository lifecycle

| Question | Canonical location |
| --- | --- |
| Where do old/superseded files go? | `archive/` |
| Where does current research and migration work go? | `work/` |
| What is actually used by the ChatGPT Project? | `production/` |
| Where are design, implementation plans, and governance? | `docs/` |

- `archive/` is immutable historical evidence. Do not edit old research to make it look current; add a corrected successor and record supersession.
- `work/` contains active evidence capture, corpora manifests, migration maps, and drafts that are not production authority.
- `production/` contains the resident Project Instructions, the exact 18-file canonical knowledge pack, deterministic evals, and release manifests.
- `schemas/`, `tools/`, and `tests/` implement repository contracts and release gates.

## Production knowledge contract

`production/knowledge/` contains exactly 18 upload knowledge files. `production/project-instructions/PROJECT_INSTRUCTIONS.md` is separate and does not count toward that 18-file budget.

The evidence registry is `production/knowledge/17_EVIDENCE_REGISTRY.json` and uses Source/Claim/Corpus/Media records. Community material, older vanilla data, generic TyD material, and linked Unity documentation are never promoted beyond their explicit provenance, currency, and scope.

## Release status

The repository can build a `STRUCTURAL_PREVIEW` ChatGPT Project bundle now. A `GENERATION_GRADE` Beta 1.8.42 release is intentionally blocked until a sanitized exact-target installation/corpus capture supplies every required item in `work/corpus/beta-1.8.42/capture-manifest.template.json`.

Build locally with:

```bash
python tools/build_release.py
```

Generation-grade attempts fail closed until exact-target evidence is complete:

```bash
python tools/build_release.py --generation-grade
```

## Verification

Pull requests run the same public structural gates used locally:

```bash
python -m pytest -v
python tools/verify_repo.py
python tools/validate_registry.py production/knowledge/17_EVIDENCE_REGISTRY.json
python tools/validate_evals.py production/evals
python tools/validate_exact_target.py --structural
```

See `docs/governance/release-process.md` and `docs/governance/evidence-update-process.md` for maintenance rules.
