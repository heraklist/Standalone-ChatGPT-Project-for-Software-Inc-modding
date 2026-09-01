from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_ci_runs_generation_grade_and_template_fail_closed_validators():
    text=(ROOT/'.github/workflows/verify.yml').read_text(encoding='utf-8')
    for command in (
        'python -m pytest -v',
        'python tools/verify_repo.py',
        'python tools/validate_registry.py production/knowledge/17_EVIDENCE_REGISTRY.json',
        'python tools/validate_evals.py production/evals',
        'python tools/validate_exact_target.py work/corpus/beta-1.8.42/capture-manifest.template.json --structural',
        'python tools/validate_exact_target.py',
        'python tools/build_release.py --generation-grade',
    ):
        assert command in text
