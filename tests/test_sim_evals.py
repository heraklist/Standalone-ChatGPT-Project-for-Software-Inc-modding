from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM_EVAL_DIR = ROOT / "production/evals/sim"
EXPECTED_CATEGORIES = {
    "ACTIVATION",
    "ROUTING",
    "SESSION",
    "RESEARCH",
    "AUTONOMY",
    "ARTIFACT",
    "REPAIR",
    "SECURITY",
    "VERIFICATION",
    "CROSS_SURFACE",
}


def test_sim_eval_validator_exists_and_validates_directory() -> None:
    from tools.validate_sim_evals import validate_sim_evals

    assert validate_sim_evals(SIM_EVAL_DIR) == []


def test_sim_eval_layer_has_unique_s_ids_and_exact_categories() -> None:
    records = []
    for path in sorted(SIM_EVAL_DIR.glob("*.json")):
        records.extend(json.loads(path.read_text(encoding="utf-8")))

    ids = [record["id"] for record in records]
    assert len(ids) >= 16
    assert len(ids) == len(set(ids))
    assert all(re.fullmatch(r"S\d{3}", value) for value in ids)
    assert {record["category"] for record in records} == EXPECTED_CATEGORIES


def test_seed_contract_s001_through_s016_is_present() -> None:
    records = {}
    for path in sorted(SIM_EVAL_DIR.glob("*.json")):
        for record in json.loads(path.read_text(encoding="utf-8")):
            records[record["id"]] = record

    for index in range(1, 17):
        assert f"S{index:03d}" in records

    assert "explicit" in records["S001"]["prompt"].lower()
    assert "NOT_EXECUTED" in " ".join(records["S013"]["required_outcomes"])
    assert "V2" in " ".join(records["S014"]["required_outcomes"])
    assert "BLOCKED" in " ".join(records["S016"]["required_outcomes"])


def test_legacy_core_eval_ids_remain_exactly_e01_e74() -> None:
    core = json.loads((ROOT / "production/evals/core.json").read_text(encoding="utf-8"))
    assert [record["id"] for record in core] == [f"E{i:02d}" for i in range(1, 75)]
