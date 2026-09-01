# Contributing

This repository is the governed source for the standalone Software Inc Mod Studio ChatGPT Project.

## Lifecycle rules

- Put immutable historical material in `archive/`.
- Put active research, migration work, claim mapping, and evidence capture in `work/`.
- Put only approved live/release artifacts in `production/`.
- Put canonical design, plans, and governance in `docs/`.
- Do not commit raw proprietary game binaries, managed assemblies, full vanilla archives, or copied full wiki pages unless redistribution rights are confirmed. Historical user-supplied knowledge packs may be retained under `archive/raw/` when they are project-owned research artifacts rather than game binaries.

Never edit an archived historical source merely to make it agree with current knowledge. Preserve it, record the superseding source/claim, and update the current owner document.

## Evidence changes

For a new or changed technical claim:

```text
new source
→ registry source record
→ claim classification
→ conflict/currency/scope check
→ owner knowledge update
→ affected eval update
→ CI
→ release manifest
```

Exact-target claims must not be inferred from older vanilla corpora, wiki edit dates, or generic linked-engine documentation.

## Production changes

- Project Instructions changes require the full core eval suite.
- Family knowledge changes require the relevant domain tests plus retrieval/version/verification coverage; release CI still runs the complete structural suite.
- The 18-file production knowledge identity is fixed unless the canonical design is explicitly revised.
- Do not introduce ModForge implementation constraints as Software Inc engine facts.

## Verification

Before review, run:

```bash
python -m pytest -v
python tools/verify_repo.py
python tools/validate_registry.py production/knowledge/17_EVIDENCE_REGISTRY.json
python tools/validate_evals.py production/evals
python tools/validate_exact_target.py --structural
```

A structural preview release may be built with `python tools/build_release.py`. `--generation-grade` must remain blocked until the exact Beta 1.8.42 evidence gate passes.

## Integration policy

Use pull requests for production changes. Prefer squash merge for focused repository changes unless a future repository policy explicitly chooses another strategy. Do not merge with failing required CI or unresolved release-blocking claims.
