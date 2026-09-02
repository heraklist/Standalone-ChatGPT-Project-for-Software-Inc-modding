from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from tools.build_sim_release import build_sim_release

ROOT = Path(__file__).resolve().parents[1]


def _report_path(root: Path) -> Path:
    return root / "sim-0.2.0-preview.release-report.json"


def _rewrite_zip(source: Path, destination: Path, *, drop: set[str] | None = None, add: dict[str, bytes] | None = None) -> None:
    drop = drop or set()
    add = add or {}
    with ZipFile(source) as original, ZipFile(destination, "w", compression=ZIP_DEFLATED) as rewritten:
        for name in original.namelist():
            if name not in drop:
                rewritten.writestr(name, original.read(name))
        for name, data in add.items():
            rewritten.writestr(name, data)


def test_independent_verifier_accepts_valid_preview_build(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, _ = build_sim_release(ROOT, out_dir=tmp_path)
    assert verify_sim_release(zip_path, _report_path(tmp_path), "0.2.0-preview") == []


def test_verifier_rejects_bundle_digest_mismatch(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, _ = build_sim_release(ROOT, out_dir=tmp_path)
    report_path = _report_path(tmp_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["bundle_sha256"] = "0" * 64
    report_path.write_text(json.dumps(report), encoding="utf-8")
    assert any("bundle SHA-256 mismatch" in error for error in verify_sim_release(zip_path, report_path, "0.2.0-preview"))


def test_verifier_rejects_missing_required_runtime_entries(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, _ = build_sim_release(ROOT, out_dir=tmp_path)
    for missing in ("production/sim/SKILL.md", "production/sim/manifests/reference-source-map.json"):
        altered = tmp_path / (Path(missing).name + ".zip")
        _rewrite_zip(zip_path, altered, drop={missing})
        errors = verify_sim_release(altered, _report_path(tmp_path), "0.2.0-preview")
        assert any("missing required SIM bundle entry" in error for error in errors)


def test_verifier_rejects_forbidden_raw_evidence_path(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, _ = build_sim_release(ROOT, out_dir=tmp_path)
    altered = tmp_path / "forbidden.zip"
    _rewrite_zip(zip_path, altered, add={"work/corpus/private.bin": b"fixture"})
    errors = verify_sim_release(altered, _report_path(tmp_path), "0.2.0-preview")
    assert any("forbidden bundle path" in error for error in errors)


def test_verifier_rejects_reported_file_hash_mismatch(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, _ = build_sim_release(ROOT, out_dir=tmp_path)
    altered = tmp_path / "tampered.zip"
    _rewrite_zip(zip_path, altered, add={"production/sim/SKILL.md": b"tampered"}, drop={"production/sim/SKILL.md"})
    errors = verify_sim_release(altered, _report_path(tmp_path), "0.2.0-preview")
    assert any("file SHA-256 mismatch" in error or "bundle SHA-256 mismatch" in error for error in errors)
