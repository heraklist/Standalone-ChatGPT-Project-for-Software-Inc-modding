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

`GENERATION_GRADE` is ready for the canonical Beta 1.8.42 target. The exact-target evidence gate is resolved and the current repository can produce the first release pack as version `0.1.0`.

The unresolved capture template remains deliberately fail-closed. Generation-grade status is granted only from the resolved `work/corpus/beta-1.8.42/capture-manifest.json` and its hash-bound sanitized evidence.

Build a structural preview with:

```bash
python tools/build_release.py
```

Build the canonical generation-grade release with:

```bash
python tools/build_release.py --generation-grade
```

The release bundle contains Project Instructions, the exact 18 knowledge files, and generated manifests. Repository evals, migration work, research archives, and raw/private evidence are not part of the ChatGPT Project upload bundle.

## Verification

Pull requests run the same release gates used locally:

```bash
python -m pytest -v
python tools/verify_repo.py
python tools/validate_registry.py production/knowledge/17_EVIDENCE_REGISTRY.json
python tools/validate_evals.py production/evals
python tools/validate_exact_target.py work/corpus/beta-1.8.42/capture-manifest.template.json --structural
python tools/validate_exact_target.py
python tools/build_release.py --generation-grade
```

See `docs/governance/release-process.md` and `docs/governance/evidence-update-process.md` for maintenance rules.
