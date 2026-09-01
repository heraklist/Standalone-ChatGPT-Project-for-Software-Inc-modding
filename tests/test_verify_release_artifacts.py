import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.verify_release_artifacts import verify_release_artifacts


def _make_bundle(tmp_path: Path, *, version: str = "0.1.0") -> tuple[Path, Path]:
    zip_path = tmp_path / f"software-inc-mod-studio-project-{version}.zip"
    report_path = tmp_path / f"software-inc-mod-studio-project-{version}.release-report.json"

    knowledge = [f"knowledge/{i:02d}_FILE.md" for i in range(17)] + ["knowledge/17_EVIDENCE_REGISTRY.json"]
    entries = ["project-instructions/PROJECT_INSTRUCTIONS.md", *knowledge]
    kp = {
        "pack_version": version,
        "exact_target_generation_grade": True,
        "mandatory_knowledge_files": [Path(p).name for p in knowledge],
    }

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for name in entries:
            zf.writestr(name, b"fixture")
        zf.writestr("manifests/knowledge-pack-manifest.json", json.dumps(kp))
        zf.writestr("manifests/release-manifest.json", json.dumps({"generation_grade": True}))

    report = {
        "release_status": "GENERATION_GRADE",
        "generation_grade": True,
        "exact_target_gate_errors": [],
        "bundle_sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
    }
    report_path.write_text(json.dumps(report), encoding="utf-8")
    return zip_path, report_path


def test_verifier_accepts_generation_grade_v010_bundle(tmp_path):
    zip_path, report_path = _make_bundle(tmp_path)
    assert verify_release_artifacts(zip_path, report_path, expected_version="0.1.0") == []


def test_verifier_rejects_bundle_hash_mismatch(tmp_path):
    zip_path, report_path = _make_bundle(tmp_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["bundle_sha256"] = "0" * 64
    report_path.write_text(json.dumps(report), encoding="utf-8")

    errors = verify_release_artifacts(zip_path, report_path, expected_version="0.1.0")
    assert "bundle SHA-256 mismatch" in errors


def test_verifier_rejects_wrong_release_status_or_version(tmp_path):
    zip_path, report_path = _make_bundle(tmp_path, version="0.1.0")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["release_status"] = "STRUCTURAL_PREVIEW"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    errors = verify_release_artifacts(zip_path, report_path, expected_version="9.9.9")
    assert "release status is not GENERATION_GRADE" in errors
    assert "knowledge-pack version does not match expected version 9.9.9" in errors
