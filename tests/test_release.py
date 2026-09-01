import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.build_release import build_release
from tools.verify_repo import KNOWLEDGE_FILES


def test_structural_preview_bundle_has_exact_upload_layout_and_hashes(tmp_path):
    zip_path, kp, release = build_release(ROOT, out_dir=tmp_path)
    assert release["release_status"] == "STRUCTURAL_PREVIEW"
    assert release["generation_grade"] is False
    assert release["exact_target_manifest"] == "work/corpus/beta-1.8.42/capture-manifest.json"
    assert "vanilla Data content unresolved" in release["exact_target_gate_errors"]
    assert "missing current identifiers/collision index evidence" in release["exact_target_gate_errors"]
    assert "missing current Hardware Design observations" not in release["exact_target_gate_errors"]
    assert "missing current Code persistence/security API surface" not in release["exact_target_gate_errors"]
    assert len(kp["mandatory_knowledge_files"]) == 18
    assert set(kp["mandatory_knowledge_files"]) == KNOWLEDGE_FILES
    assert len(kp["project_instructions_sha256"]) == 64
    assert len(kp["registry_sha256"]) == 64
    assert len(kp["file_sha256"]) == 19

    with ZipFile(zip_path) as zf:
        names=set(zf.namelist())
        expected={"project-instructions/PROJECT_INSTRUCTIONS.md","manifests/knowledge-pack-manifest.json","manifests/release-manifest.json"}
        expected |= {f"knowledge/{name}" for name in KNOWLEDGE_FILES}
        assert names == expected
        assert len(names) == 21
        assert not any(name.startswith("evals/") or name.startswith("archive/") for name in names)
        packed_kp=json.loads(zf.read("manifests/knowledge-pack-manifest.json"))
        for path,digest in packed_kp["file_sha256"].items():
            assert hashlib.sha256(zf.read(path)).hexdigest() == digest

    assert len(release["bundle_sha256"]) == 64
    assert hashlib.sha256(zip_path.read_bytes()).hexdigest() == release["bundle_sha256"]


def test_generation_grade_release_is_blocked_by_unresolved_exact_target_data(tmp_path):
    with pytest.raises(RuntimeError, match="vanilla Data content unresolved"):
        build_release(ROOT, generation_grade=True, out_dir=tmp_path)
