from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
K16 = ROOT / "production/knowledge/16_VERIFICATION_AND_QA.md"
VERIFICATION = ROOT / "production/sim/references/verification.md"


def test_report_task2_reference_hashes() -> None:
    source_hash = hashlib.sha256(K16.read_bytes()).hexdigest()
    output_hash = hashlib.sha256(VERIFICATION.read_bytes()).hexdigest()
    assert False, f"K16_SHA256={source_hash} VERIFICATION_SHA256={output_hash}"
