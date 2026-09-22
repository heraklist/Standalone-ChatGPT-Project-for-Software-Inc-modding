from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "production/sim/SKILL.md"
REFERENCE_MAP = ROOT / "production/sim/manifests/reference-source-map.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_reference_map_declares_package_path_for_every_reference() -> None:
    data = json.loads(REFERENCE_MAP.read_text(encoding="utf-8"))
    assert data["entries"]
    for entry in data["entries"]:
        assert entry["package_path"].startswith("references/")
        assert entry["package_path"] == Path(entry["output_path"]).relative_to("production/sim").as_posix()


def test_root_routing_paths_resolve_to_real_chatgpt_package_entries(tmp_path: Path) -> None:
    from tools.build_sim_chatgpt_upload import build_chatgpt_upload

    zip_path, _ = build_chatgpt_upload(ROOT, out_dir=tmp_path)
    with ZipFile(zip_path) as archive:
        names = set(archive.namelist())

    text = SIM.read_text(encoding="utf-8")
    section = text.split("## Runtime routing and progressive disclosure", 1)[1].split("\n## ", 1)[0]
    routed_paths = set(re.findall(r"`((?:references|manifests)/[^`]+)`", section))
    assert routed_paths
    assert sorted(routed_paths - names) == []


def test_chatgpt_upload_has_complete_runtime_provenance(tmp_path: Path) -> None:
    from tools.build_sim_chatgpt_upload import build_chatgpt_upload

    zip_path, report = build_chatgpt_upload(ROOT, out_dir=tmp_path)
    with ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        provenance_bytes = archive.read("manifests/runtime-provenance.json")
        provenance = json.loads(provenance_bytes)
        entries = provenance["entries"]
        by_package = {entry["package_path"]: entry for entry in entries}

        assert provenance["schema_version"] == 1
        assert provenance["self_entry_excluded"] is True
        assert set(by_package) == names - {"manifests/runtime-provenance.json"}
        assert report["runtime_provenance_sha256"] == sha256(provenance_bytes)

        for package_path, entry in by_package.items():
            packaged = archive.read(package_path)
            assert entry["package_sha256"] == sha256(packaged)
            source = ROOT / entry["source_path"]
            assert source.is_file(), entry
            assert entry["source_sha256"] == sha256(source.read_bytes())
            assert entry["transform_type"] in {"COPY", "REMAP", "AUGMENT"}


def test_runtime_provenance_marks_transformed_surfaces_explicitly(tmp_path: Path) -> None:
    from tools.build_sim_chatgpt_upload import build_chatgpt_upload

    zip_path, _ = build_chatgpt_upload(ROOT, out_dir=tmp_path)
    with ZipFile(zip_path) as archive:
        provenance = json.loads(archive.read("manifests/runtime-provenance.json"))
    by_package = {entry["package_path"]: entry for entry in provenance["entries"]}

    assert by_package["SKILL.md"]["source_path"] == "production/sim/SKILL.md"
    assert by_package["SKILL.md"]["transform_type"] == "AUGMENT"
    assert by_package["references/internal/domains/editor-native.md"]["source_path"] == "production/sim/domains/editor-native/SKILL.md"
    assert by_package["references/internal/domains/editor-native.md"]["transform_type"] == "REMAP"
    assert by_package["tools/validate_code_profile.py"]["source_path"] == "tools/validate_code_profile.py"
    assert by_package["tools/validate_code_profile.py"]["transform_type"] == "COPY"
