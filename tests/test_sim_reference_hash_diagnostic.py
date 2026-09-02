import json
from pathlib import Path

import pytest

from tools.build_sim_references import REFERENCE_MAPPINGS, sha256_file


ROOT = Path(__file__).resolve().parents[1]


def test_emit_canonical_reference_hashes_for_task_6() -> None:
    hashes = {
        source_path: sha256_file(ROOT / source_path)
        for _, source_path, _ in REFERENCE_MAPPINGS
    }
    pytest.fail("TASK6_HASHES=" + json.dumps(hashes, sort_keys=True))
