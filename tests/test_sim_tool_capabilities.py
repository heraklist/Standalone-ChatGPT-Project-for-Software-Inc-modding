from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES = ROOT / "production/sim/manifests/tool-capabilities.json"
CODE = ROOT / "production/sim/domains/code-modding/SKILL.md"
SIM = ROOT / "production/sim/SKILL.md"


def test_tool_capability_manifest_distinguishes_bundle_from_execution() -> None:
    data = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    tool = data["tools"]["validate_code_profile"]

    assert tool["repository_source"] == "tools/validate_code_profile.py"
    assert tool["package_path"] == "tools/validate_code_profile.py"
    assert tool["surfaces"]["CHATGPT_WEB_NORMAL_CHAT"]["bundled"] is True
    assert (
        tool["surfaces"]["CHATGPT_WEB_NORMAL_CHAT"]["execution"]
        == "CAPABILITY_DEPENDENT"
    )
    assert tool["unavailable_result"] == "NOT_EXECUTED"


def test_chatgpt_upload_bundles_real_code_profile_validator(tmp_path: Path) -> None:
    from tools.build_sim_chatgpt_upload import build_chatgpt_upload

    zip_path, report = build_chatgpt_upload(ROOT, out_dir=tmp_path)
    with ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        bundled = archive.read("tools/validate_code_profile.py")

    assert "tools/validate_code_profile.py" in names
    assert bundled == (ROOT / "tools/validate_code_profile.py").read_bytes()
    assert report["tool_capabilities"]["validate_code_profile"]["bundled"] is True
    assert report["tool_capabilities"]["validate_code_profile"]["execution"] == "CAPABILITY_DEPENDENT"


def test_runtime_contract_never_equates_bundled_tool_with_execution() -> None:
    code = CODE.read_text(encoding="utf-8")
    sim = SIM.read_text(encoding="utf-8")

    assert "manifests/tool-capabilities.json" in code
    assert "bundled does not mean executable" in code
    assert "record the check as `NOT_EXECUTED`" in code
    assert "Bundled tool presence is not execution evidence" in sim


def test_tool_capabilities_are_surface_complete_and_include_archive_inspector() -> None:
    data = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    expected_surfaces = {
        "CHATGPT_WEB_NORMAL_CHAT",
        "CHATGPT_DESKTOP_NORMAL_CHAT",
        "CHATGPT_WORK",
        "CODEX",
        "REPOSITORY_CI",
    }

    for tool in data["tools"].values():
        assert set(tool["surfaces"]) == expected_surfaces

    inspector = data["tools"]["inspect_archive"]
    assert inspector["repository_source"] == "tools/inspect_archive.py"
    assert inspector["package_path"] == "tools/inspect_archive.py"
    assert inspector["surfaces"]["CHATGPT_WEB_NORMAL_CHAT"]["bundled"] is True
    assert (
        inspector["surfaces"]["CHATGPT_WEB_NORMAL_CHAT"]["execution"]
        == "CAPABILITY_DEPENDENT"
    )
    assert inspector["surfaces"]["REPOSITORY_CI"]["bundled"] is False
    assert inspector["surfaces"]["REPOSITORY_CI"]["execution"] == "SUPPORTED"
    assert inspector["unavailable_result"] == "NOT_EXECUTED"
