from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_ci_runs_same_public_structural_validators():
    text=(ROOT/'.github/workflows/verify.yml').read_text(encoding='utf-8')
    for command in (
        'python -m pytest -v',
        'python tools/verify_repo.py',
        'python tools/validate_registry.py production/knowledge/17_EVIDENCE_REGISTRY.json',
        'python tools/validate_evals.py production/evals',
        'python tools/validate_exact_target.py --structural',
    ):
        assert command in text
