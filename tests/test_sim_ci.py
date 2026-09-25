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
        'python tools/verify_sim_release.py "dist/sim-$SIM_VERSION.zip" "dist/sim-$SIM_VERSION.release-report.json" --expected-version "$SIM_VERSION"',
        "python tools/build_release.py --generation-grade",
    )
    for command in required:
        assert command in text

    assert "Resolve SIM version" in text
    assert "SIM_VERSION=" in text


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


def test_sim_ci_names_head_reproducibility_without_implying_certification() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "- name: Verify SIM HEAD reproducibility" in text
    assert "- name: Validate SIM HEAD portable manifest" in text
    assert "- name: Build deterministic SIM personal-plugin bundle" in text
    assert "- name: Verify deterministic SIM personal-plugin bundle" in text
    assert "HEAD certified" not in text
    assert "Certify SIM HEAD" not in text


def test_compatibility_matrix_is_observational_per_surface_and_transport() -> None:
    import json

    matrix = json.loads(
        (ROOT / "production/sim/manifests/compatibility-matrix.json").read_text(
            encoding="utf-8"
        )
    )
    assert matrix["schema_version"] == 2
    records = matrix["records"]
    web_personal = next(
        record
        for record in records
        if record["surface"] == "CHATGPT_WEB_NORMAL_CHAT"
        and record["transport"] == "OPENAI_PERSONAL_PLUGIN"
    )
    assert web_personal["resolver_activation"] == "NOT_TESTED"
    assert web_personal["last_verified_release_id"] is None
    assert web_personal["status"] == "NOT_VERIFIED"

    web_local = next(
        record
        for record in records
        if record["surface"] == "CHATGPT_WEB_NORMAL_CHAT"
        and record["transport"] == "MARKETPLACE_GIT_SUBDIR"
    )
    assert web_local["discovery"] == "PASS"
    assert web_local["resolver_activation"] == "BLOCKED"
