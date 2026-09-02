import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "research-evidence",
    "brainstorm-design",
    "implementation",
    "systematic-debugging",
    "verification-delivery",
}

from tools.validate_sim_layout import verify_sim_layout


def lifecycle_text(name: str) -> str:
    return (ROOT / "production/sim/lifecycle" / name / "SKILL.md").read_text(
        encoding="utf-8"
    )


def test_exact_lifecycle_module_set_exists() -> None:
    lifecycle_root = ROOT / "production/sim/lifecycle"
    assert lifecycle_root.is_dir()
    assert {path.name for path in lifecycle_root.iterdir() if path.is_dir()} == EXPECTED
    for name in EXPECTED:
        assert (lifecycle_root / name / "SKILL.md").is_file()


def test_lifecycle_modules_are_bounded_proposal_producers() -> None:
    for name in EXPECTED:
        lowered = lifecycle_text(name).lower()
        assert "do not dispatch" in lowered
        assert "do not mutate" in lowered
        assert "proposed" in lowered
        assert "orchestrator" in lowered


def test_research_evidence_workflow_is_canonical_first_and_conflict_aware() -> None:
    lowered = lifecycle_text("research-evidence").lower()
    assert "canonical" in lowered
    assert "targeted research" in lowered
    assert "conflict" in lowered
    assert "unresolved" in lowered


def test_brainstorm_design_is_adaptive_not_mandatory() -> None:
    lowered = lifecycle_text("brainstorm-design").lower()
    assert "open-ended" in lowered
    assert "material" in lowered
    assert "fork" in lowered
    assert "not mandatory" in lowered


def test_implementation_coordinates_artifact_work_without_domain_ownership() -> None:
    lowered = lifecycle_text("implementation").lower()
    assert "artifact" in lowered
    assert "domain" in lowered
    assert "coordinate" in lowered
    assert "does not own" in lowered


def test_systematic_debugging_is_evidence_backed_and_minimal() -> None:
    lowered = lifecycle_text("systematic-debugging").lower()
    for token in ("observe", "isolate", "hypothesis", "minimal", "verify"):
        assert token in lowered


def test_verification_delivery_enforces_exact_completion_state() -> None:
    text = lifecycle_text("verification-delivery")
    lowered = text.lower()
    assert "verification before delivery" in lowered
    assert "BLOCKED" in text
    assert "NOT_EXECUTED" in text
    assert "V0 DESIGN_READY" in text
    assert "V5 REGRESSION_VERIFIED" in text


def test_layout_verifier_rejects_unexpected_lifecycle_module(tmp_path: Path) -> None:
    repo = tmp_path / "repository"
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    extra = repo / "production/sim/lifecycle/unplanned"
    extra.mkdir(parents=True)
    (extra / "SKILL.md").write_text("---\nname: unplanned\n---\n", encoding="utf-8")

    assert "unexpected SIM lifecycle module: unplanned" in verify_sim_layout(repo)
