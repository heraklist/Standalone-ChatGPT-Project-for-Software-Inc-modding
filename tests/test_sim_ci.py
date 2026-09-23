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
        "python tools/verify_sim_release.py dist/sim-0.2.2-preview.zip dist/sim-0.2.2-preview.release-report.json --expected-version 0.2.2-preview",
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


def test_verify_workflow_builds_and_validates_exact_source_sha_sim_plugin_twice() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "SIM_SOURCE_SHA: ${{ github.event.pull_request.head.sha || github.sha }}" in text
    required = (
        'python tools/build_sim_plugin.py build --repo-root . --source-sha "$SIM_SOURCE_SHA" --output dist/sim-plugin-a',
        'python tools/build_sim_plugin.py build --repo-root . --source-sha "$SIM_SOURCE_SHA" --output dist/sim-plugin-b',
        'python tools/validate_sim_plugin.py check --repo-root . --source-sha "$SIM_SOURCE_SHA" --candidate dist/sim-plugin-a',
        'python tools/validate_sim_plugin.py check --repo-root . --source-sha "$SIM_SOURCE_SHA" --candidate dist/sim-plugin-b',
        "SIM_PLUGIN_REPRODUCIBLE",
        "sim-plugin-candidate-${{ env.SIM_SOURCE_SHA }}",
        "actions/upload-artifact@v4",
    )
    for command in required:
        assert command in text

    assert '--source-sha "$GITHUB_SHA"' not in text

def test_verify_workflow_fetches_pull_request_head_git_object() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    checkout = text.index("uses: actions/checkout@v4")
    setup_python = text.index("uses: actions/setup-python@v5")
    checkout_block = text[checkout:setup_python]

    assert "fetch-depth: 2" in checkout_block


def test_sim_plugin_ci_does_not_publish_marketplace_or_materialize_plugins_tree() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert ".agents/plugins/marketplace.json" not in text
    assert "--output plugins/sim" not in text
