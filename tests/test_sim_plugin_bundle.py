from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def _head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_plugin_bundle_cli_is_deterministic_rooted_and_independently_verified(
    tmp_path: Path,
) -> None:
    from tools.build_sim_plugin import build_candidate

    candidate = tmp_path / "candidate"
    build_candidate(ROOT, _head(), candidate)

    first = tmp_path / "a.zip"
    first_report = tmp_path / "a.report.json"
    second = tmp_path / "b.zip"
    second_report = tmp_path / "b.report.json"

    for output, report in ((first, first_report), (second, second_report)):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/build_sim_plugin_bundle.py"),
                "--candidate",
                str(candidate),
                "--output",
                str(output),
                "--report-out",
                str(report),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    assert first.read_bytes() == second.read_bytes()
    assert _sha256(first) == _sha256(second)

    first_payload = json.loads(first_report.read_text(encoding="utf-8"))
    second_payload = json.loads(second_report.read_text(encoding="utf-8"))
    assert first_payload == second_payload
    assert first_payload["bundle_sha256"] == _sha256(first)

    with ZipFile(first) as archive:
        names = archive.namelist()
        assert "plugin.json" in names
        assert "skills/sim/SKILL.md" in names
        assert not any(name.startswith("sim/") for name in names)
        assert not any(name.startswith("0.2.3-preview.1/") for name in names)
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist())

    verify = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/verify_sim_plugin_bundle.py"),
            "--candidate",
            str(candidate),
            "--zip",
            str(first),
            "--report",
            str(first_report),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert verify.returncode == 0, verify.stdout + verify.stderr
    assert "SIM_PLUGIN_BUNDLE_OK" in verify.stdout
