from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from tools.analyze_unity_data_probe import analyze_records
from tools.check_sim_collisions import classify_identifier

ROOT = Path(__file__).resolve().parents[1]


def _schema() -> dict:
    return json.loads(
        (ROOT / "schemas/sim-collision-index.schema.json").read_text(
            encoding="utf-8"
        )
    )


def test_analyzer_output_classifies_game_as_vanilla_collision() -> None:
    payload = b'SoftwareType { Name "Game" Categories [ ] }'
    records = [{
        "path_id": 1,
        "object_name": "Game",
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "payload_size": len(payload),
        "private_path": "synthetic/softwaretype/Game.tyd",
    }]
    result = analyze_records(
        records, {"synthetic/softwaretype/Game.tyd": payload}
    )
    collision_index = result["collision_index"]

    jsonschema.Draft202012Validator(_schema()).validate(collision_index)

    assert (
        classify_identifier(
            "Game",
            "software_type",
            collision_index,
            intentional_override=False,
        )
        == "VANILLA_COLLISION"
    )


def test_exact_target_collision_index_conforms_to_object_schema() -> None:
    collision_index = json.loads(
        (
            ROOT
            / "work/corpus/beta-1.8.42/identifiers-collision-index.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(_schema()).validate(collision_index)
    for namespace in collision_index["namespaces"].values():
        assert all(isinstance(entry, dict) for entry in namespace["identifiers"])
