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
    payload = {name: b"fixture" for name in entries}
    kp = {
        "pack_version": version,
        "exact_target_generation_grade": True,
        "mandatory_knowledge_files": [Path(p).name for p in knowledge],
        "file_sha256": {
            name: hashlib.sha256(data).hexdigest()
            for name, data in payload.items()
        },
    }

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for name, data in payload.items():
            zf.writestr(name, data)
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


def _rewrite_bundle(
    zip_path: Path,
    report_path: Path,
    *,
    transform,
) -> Path:
    rewritten = zip_path.with_name("rewritten.zip")
    with ZipFile(zip_path) as src, ZipFile(
        rewritten, "w", compression=ZIP_DEFLATED
    ) as dst:
        for info in src.infolist():
            name = info.filename
            data = src.read(name)
            replacement = transform(name, data)
            if replacement is None:
                continue
            out_name, out_data = replacement
            dst.writestr(out_name, out_data)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["bundle_sha256"] = hashlib.sha256(rewritten.read_bytes()).hexdigest()
    report_path.write_text(json.dumps(report), encoding="utf-8")
    return rewritten


def test_verifier_rejects_tampered_packed_file_even_with_updated_outer_hash(
    tmp_path: Path,
) -> None:
    zip_path, report_path = _make_bundle(tmp_path)

    rewritten = _rewrite_bundle(
        zip_path,
        report_path,
        transform=lambda name, data: (
            (name, b"TAMPERED\n")
            if name == "knowledge/00_FILE.md"
            else (name, data)
        ),
    )

    errors = verify_release_artifacts(
        rewritten, report_path, expected_version="0.1.0"
    )
    assert any("packed file SHA-256 mismatch" in error for error in errors)


def test_verifier_rejects_undeclared_knowledge_member(tmp_path: Path) -> None:
    zip_path, report_path = _make_bundle(tmp_path)

    rewritten = zip_path.with_name("rewritten.zip")
    with ZipFile(zip_path) as src, ZipFile(
        rewritten, "w", compression=ZIP_DEFLATED
    ) as dst:
        for info in src.infolist():
            dst.writestr(info.filename, src.read(info.filename))
        dst.writestr("knowledge/rogue.md", b"rogue")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["bundle_sha256"] = hashlib.sha256(rewritten.read_bytes()).hexdigest()
    report_path.write_text(json.dumps(report), encoding="utf-8")

    errors = verify_release_artifacts(
        rewritten, report_path, expected_version="0.1.0"
    )
    assert any("undeclared packed file" in error for error in errors)


def test_verifier_rejects_missing_declared_packed_file(tmp_path: Path) -> None:
    zip_path, report_path = _make_bundle(tmp_path)

    rewritten = _rewrite_bundle(
        zip_path,
        report_path,
        transform=lambda name, data: (
            None if name == "knowledge/00_FILE.md" else (name, data)
        ),
    )

    errors = verify_release_artifacts(
        rewritten, report_path, expected_version="0.1.0"
    )
    assert any("missing packed file" in error for error in errors)



def test_verifier_rejects_duplicate_zip_member_even_when_bytes_match(
    tmp_path: Path,
) -> None:
    zip_path, report_path = _make_bundle(tmp_path)

    rewritten = zip_path.with_name("rewritten-duplicate.zip")
    with ZipFile(zip_path) as src, ZipFile(
        rewritten, "w", compression=ZIP_DEFLATED
    ) as dst:
        for info in src.infolist():
            dst.writestr(info.filename, src.read(info.filename))
        duplicate_name = "knowledge/00_FILE.md"
        dst.writestr(duplicate_name, b"fixture")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["bundle_sha256"] = hashlib.sha256(rewritten.read_bytes()).hexdigest()
    report_path.write_text(json.dumps(report), encoding="utf-8")

    errors = verify_release_artifacts(
        rewritten, report_path, expected_version="0.1.0"
    )
    assert any("duplicate ZIP entry" in error for error in errors)
