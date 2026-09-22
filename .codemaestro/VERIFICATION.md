# Verification

## Required local/CI verification commands

python -m pytest -v
python tools/verify_repo.py
python tools/validate_registry.py production/knowledge/17_EVIDENCE_REGISTRY.json
python tools/validate_evals.py production/evals
python tools/validate_exact_target.py work/corpus/beta-1.8.42/capture-manifest.template.json --structural
python tools/validate_exact_target.py
python tools/build_release.py --generation-grade
python tools/validate_sim_layout.py
python tools/validate_sim_references.py
python tools/validate_sim_evals.py production/evals/sim
python tools/build_sim_release.py --channel preview
python tools/verify_sim_release.py dist/sim-0.2.0-preview.zip dist/sim-0.2.0-preview.release-report.json --expected-version 0.2.0-preview

## Existing evidence before packaging

Source commit:
9c8ac46bf7cb821436dd935fda6e7c51a5ca2568

GitHub Actions:
verify run #213 — SUCCESS.

Prior audited repository evidence records 253 passing pytest tests together with successful generation-grade canonical build, SIM Preview build, and SIM_RELEASE_OK independent verification.

## External verification still required

Live ChatGPT surface acceptance is not reproducible inside repository CI.
Current recorded state:
A01–A05 PASS; A06 FAIL; A07–A12 NOT_TESTED.

A fresh supported-surface A06 retest is mandatory before further acceptance progression.
