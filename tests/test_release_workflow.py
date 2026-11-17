from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/release.yml"


def test_release_workflow_publishes_generation_grade_tagged_release():
    text = WORKFLOW.read_text(encoding="utf-8")

    required_fragments = (
        "name: release",
        "tags:",
        "- 'v*'",
        "contents: write",
        "python -m pytest -v",
        "python tools/verify_repo.py",
        "python tools/validate_registry.py production/knowledge/17_EVIDENCE_REGISTRY.json",
        "python tools/validate_evals.py production/evals",
        "python tools/validate_exact_target.py",
        "python tools/build_release.py --generation-grade",
        "software-inc-mod-studio-project-${{ env.VERSION }}.zip",
        "software-inc-mod-studio-project-${{ env.VERSION }}.release-report.json",
        "actions/upload-artifact@v4",
        "softprops/action-gh-release@v2",
    )
    for fragment in required_fragments:
        assert fragment in text


def test_release_workflow_does_not_hardcode_pack_version():
    """The build/upload/publish steps must derive the version from the manifest,
    not pin a specific release number, so a version bump does not silently break
    artifact verification and upload."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "project-0.1.0.zip" not in text
    assert "--expected-version 0.1.0" not in text
    assert "Software Inc Mod Studio v0.1.0" not in text


def test_release_workflow_verifies_bundle_sha_before_publish():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "verify_release_artifacts.py" in text
    assert "release-report.json" in text


def test_release_workflow_supports_controlled_publish_branch_trigger():
    text = WORKFLOW.read_text(encoding="utf-8")
    for fragment in (
        "branches:",
        "- 'publish/v*'",
        'GITHUB_REF_TYPE',
        'publish/v${VERSION}',
        'tag_name: v${{ env.VERSION }}',
        'target_commitish: ${{ github.sha }}',
    ):
        assert fragment in text
