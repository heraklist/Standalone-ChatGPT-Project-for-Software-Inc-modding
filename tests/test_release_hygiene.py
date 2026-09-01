import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_templates_are_v010_and_status_neutral():
    kp = json.loads((ROOT / "production/manifests/knowledge-pack-manifest.json").read_text(encoding="utf-8"))
    release = json.loads((ROOT / "production/manifests/release-manifest.json").read_text(encoding="utf-8"))

    assert kp["pack_version"] == "0.1.0"
    assert kp["exact_target_generation_grade"] == "AUTO"
    assert kp["known_gaps"] == []

    assert release["release_status"] == "AUTO"
    assert release["generation_grade"] == "AUTO"


def test_readme_declares_generation_grade_ready():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "GENERATION_GRADE` is ready" in text
    assert "python tools/build_release.py --generation-grade" in text
    assert "intentionally blocked until" not in text
    assert "Generation-grade attempts fail closed until" not in text


def test_release_governance_declares_v010_generation_grade_flow():
    text = (ROOT / "docs/governance/release-process.md").read_text(encoding="utf-8")
    assert "v0.1.0" in text
    assert "Beta 1.8.42 exact-target evidence is resolved" in text
    assert "python tools/build_release.py --generation-grade" in text
    assert "Generation-grade build succeeds in CI" in text
