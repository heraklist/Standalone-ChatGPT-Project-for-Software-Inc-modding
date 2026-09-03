from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_chatgpt_upload_exposes_only_one_public_skill(tmp_path: Path) -> None:
    from tools.build_sim_chatgpt_upload import build_chatgpt_upload

    zip_path, report = build_chatgpt_upload(ROOT, out_dir=tmp_path)

    assert zip_path.name == "sim-0.2.0-preview-chatgpt-upload.zip"
    assert report["public_skill_entries"] == ["SKILL.md"]

    with ZipFile(zip_path) as archive:
        names = archive.namelist()

    assert [name for name in names if name.endswith("SKILL.md")] == ["SKILL.md"]
    assert not any(name.startswith("production/sim/") for name in names)


def test_chatgpt_upload_preserves_internal_specialists_as_references(tmp_path: Path) -> None:
    from tools.build_sim_chatgpt_upload import build_chatgpt_upload

    zip_path, _ = build_chatgpt_upload(ROOT, out_dir=tmp_path)
    with ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        root_skill = archive.read("SKILL.md").decode("utf-8")

    expected_domains = {
        "code-modding",
        "compatibility-packaging",
        "data-tyd",
        "editor-native",
        "furniture",
        "localization",
        "materials",
        "sipl",
    }
    expected_lifecycle = {
        "brainstorm-design",
        "implementation",
        "research-evidence",
        "systematic-debugging",
        "verification-delivery",
    }

    for name in expected_domains:
        path = f"references/internal/domains/{name}.md"
        assert path in names
        assert path in root_skill
    for name in expected_lifecycle:
        path = f"references/internal/lifecycle/{name}.md"
        assert path in names
        assert path in root_skill


def test_chatgpt_upload_is_deterministic(tmp_path: Path) -> None:
    from tools.build_sim_chatgpt_upload import build_chatgpt_upload

    first, first_report = build_chatgpt_upload(ROOT, out_dir=tmp_path / "first")
    second, second_report = build_chatgpt_upload(ROOT, out_dir=tmp_path / "second")

    assert _sha256(first) == _sha256(second)
    assert first_report["bundle_sha256"] == second_report["bundle_sha256"]
    assert first_report["files"] == second_report["files"]
