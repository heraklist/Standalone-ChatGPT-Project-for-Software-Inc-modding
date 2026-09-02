from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/verify.yml"


def test_verify_workflow_runs_sim_preview_pipeline_and_preserves_project_release() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    required = (
        "python tools/validate_sim_layout.py",
        "python tools/validate_sim_references.py",
        "python tools/validate_sim_evals.py production/evals/sim",
        "python tools/build_sim_release.py --channel preview",
        "python tools/verify_sim_release.py dist/sim-0.2.0-preview.zip dist/sim-0.2.0-preview.release-report.json --expected-version 0.2.0-preview",
        "python tools/build_release.py --generation-grade",
    )
    for command in required:
        assert command in text


def test_sim_preview_steps_follow_exact_target_and_project_release_gates() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    exact_target = text.index("python tools/validate_exact_target.py\n")
    project_release = text.index("python tools/build_release.py --generation-grade")
    sim_layout = text.index("python tools/validate_sim_layout.py")
    sim_build = text.index("python tools/build_sim_release.py --channel preview")
    sim_verify = text.index("python tools/verify_sim_release.py")

    assert exact_target < project_release < sim_layout < sim_build < sim_verify
