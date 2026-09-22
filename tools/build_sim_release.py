from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_evals import validate_dir as validate_domain_evals
from tools.validate_exact_target import default_manifest_path, generation_grade_errors
from tools.validate_sim_evals import validate_sim_evals
from tools.validate_sim_layout import verify_sim_layout
from tools.validate_sim_references import validate_references

FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
ACCEPTANCE_CASE_IDS = tuple(f"A{index:02d}" for index in range(1, 13))
ACCEPTANCE_RESULTS = {"PASS", "FAIL", "PLATFORM_LIMITATION", "NOT_TESTED"}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _gate(label: str, errors: list[str]) -> None:
    if errors:
        raise RuntimeError(f"{label} failed: " + "; ".join(errors))


def _live_acceptance_summary(root: Path) -> tuple[str, list[str]]:
    acceptance_dir = root / "work/evidence/sim-acceptance"
    records: list[tuple[Path, dict]] = []
    if acceptance_dir.is_dir():
        for path in sorted(acceptance_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"invalid SIM acceptance evidence {path.name}: {exc}") from exc
            if not isinstance(data, dict):
                continue
            case_id = data.get("case_id")
            if case_id not in ACCEPTANCE_CASE_IDS or data.get("surface") != "ChatGPT":
                continue
            result = data.get("result")
            if result not in ACCEPTANCE_RESULTS:
                raise RuntimeError(
                    f"invalid SIM acceptance result for {case_id} in {path.name}: {result!r}"
                )
            records.append((path, data))

    if not records:
        return (
            "NOT_TESTED",
            [f"{case_id} ChatGPT acceptance NOT_TESTED" for case_id in ACCEPTANCE_CASE_IDS],
        )

    latest: dict[str, str] = {}
    for case_id in ACCEPTANCE_CASE_IDS:
        case_records = [(path, data) for path, data in records if data["case_id"] == case_id]
        if not case_records:
            latest[case_id] = "NOT_TESTED"
            continue

        superseded = {
            data["retest_of"]
            for _, data in case_records
            if isinstance(data.get("retest_of"), str)
        }
        terminal = [
            (path, data)
            for path, data in case_records
            if path.name not in superseded
        ]
        if len(terminal) != 1:
            names = ", ".join(path.name for path, _ in terminal) or "<none>"
            raise RuntimeError(
                f"ambiguous latest SIM acceptance evidence for {case_id}: {names}"
            )
        latest[case_id] = terminal[0][1]["result"]

    if any(result == "FAIL" for result in latest.values()):
        overall = "FAIL"
    elif all(result == "PASS" for result in latest.values()):
        overall = "PASS"
    elif all(result == "NOT_TESTED" for result in latest.values()):
        overall = "NOT_TESTED"
    else:
        overall = "INCOMPLETE"

    gaps = [
        f"{case_id} ChatGPT acceptance {result}"
        for case_id, result in latest.items()
        if result != "PASS"
    ]
    return overall, gaps


def build_sim_release(
    root: Path,
    channel: str = "preview",
    out_dir: Path | None = None,
) -> tuple[Path, dict]:
    if channel.lower() != "preview":
        raise RuntimeError("SIM v0.2 builder supports preview channel only")

    _gate("SIM layout validation", verify_sim_layout(root))
    _gate("SIM reference validation", validate_references(root))
    _gate(
        "SIM eval validation",
        validate_sim_evals(root / "production/evals/sim", root / "schemas/sim-eval.schema.json"),
    )
    _gate("canonical eval validation", validate_domain_evals(root / "production/evals"))

    exact_path = default_manifest_path(root)
    exact_manifest = json.loads(exact_path.read_text(encoding="utf-8"))
    _gate("exact-target generation-grade validation", generation_grade_errors(exact_manifest))

    sim_manifest = json.loads(
        (root / "production/sim/manifests/sim-manifest.json").read_text(encoding="utf-8")
    )
    version = sim_manifest["version"]
    if version != "0.2.0-preview":
        raise RuntimeError("unexpected SIM Preview version")

    payload_root = root / "production/sim"
    payload: dict[str, bytes] = {}
    for path in sorted(p for p in payload_root.rglob("*") if p.is_file()):
        relative = path.relative_to(root).as_posix()
        payload[relative] = path.read_bytes()

    surface_acceptance, known_gaps = _live_acceptance_summary(root)
    file_hashes = {name: _sha256_bytes(data) for name, data in sorted(payload.items())}
    reference_map_path = root / "production/sim/manifests/reference-source-map.json"
    report = {
        "sim_version": version,
        "channel": "PREVIEW",
        "target": sim_manifest["canonical_game_target"],
        "evidence_grade": sim_manifest["evidence_grade"],
        "canonical_source_revision": "exact-target-manifest-sha256:" + _sha256_file(exact_path),
        "reference_map_sha256": _sha256_file(reference_map_path),
        "eval_results": {
            "domain": ["E01-E74: VALIDATED"],
            "sim": ["S001+: VALIDATED"],
        },
        "security_results": ["NOT_EXECUTED_BY_RELEASE_BUILDER"],
        "artifact_fixture_results": ["NOT_EXECUTED_BY_RELEASE_BUILDER"],
        "surface_acceptance": surface_acceptance,
        "known_gaps": known_gaps,
        "bundle_sha256": "0" * 64,
        "files": file_hashes,
        "release_status": "PREVIEW_CANDIDATE",
    }

    output = out_dir or (root / "dist")
    output.mkdir(parents=True, exist_ok=True)
    zip_path = output / f"sim-{version}.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            info = ZipInfo(name, FIXED_ZIP_TIME)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)

    report["bundle_sha256"] = _sha256_file(zip_path)
    report_path = output / f"sim-{version}.release-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return zip_path, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--channel", default="preview")
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        zip_path, report = build_sim_release(args.root, channel=args.channel, out_dir=args.out_dir)
    except RuntimeError as exc:
        print(exc)
        return 1
    print(zip_path)
    print(report["release_status"])
    print(report["bundle_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
