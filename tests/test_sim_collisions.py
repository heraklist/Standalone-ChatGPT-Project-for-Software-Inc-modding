from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def synthetic_index() -> dict:
    return {
        "namespaces": {
            "software_type": {
                "identifier_count": 2,
                "identifiers": [
                    {"identifier": "Game", "occurrences": []},
                    {"identifier": "Office Software", "occurrences": []},
                ],
            },
            "company_type": {
                "identifier_count": 1,
                "identifiers": [
                    {"identifier": "Games", "occurrences": []},
                ],
            },
        }
    }


def test_collision_classifier_distinguishes_collision_override_and_clear() -> None:
    from tools.check_sim_collisions import classify_identifier

    index = synthetic_index()
    assert classify_identifier("Game", "software_type", index) == "VANILLA_COLLISION"
    assert (
        classify_identifier("Game", "software_type", index, intentional_override=True)
        == "INTENTIONAL_OVERRIDE"
    )
    assert classify_identifier("SIM_NewType", "software_type", index) == "CLEAR"


def test_collision_classifier_fails_closed_on_unknown_namespace() -> None:
    from tools.check_sim_collisions import classify_identifier

    assert classify_identifier("Anything", "not_real", synthetic_index()) == "UNKNOWN_NAMESPACE"


def test_exact_target_collision_index_smoke_uses_observed_identifier() -> None:
    from tools.check_sim_collisions import classify_identifier

    path = ROOT / "work/corpus/beta-1.8.42/identifiers-collision-index.json"
    index = json.loads(path.read_text(encoding="utf-8"))
    identifiers = index["namespaces"]["software_type"]["identifiers"]
    assert "Game" in {entry["identifier"] for entry in identifiers}
    assert classify_identifier("Game", "software_type", index) == "VANILLA_COLLISION"


def test_collision_classifier_fails_closed_on_legacy_string_list() -> None:
    from tools.check_sim_collisions import classify_identifier

    legacy = {
        "namespaces": {
            "software_type": {
                "identifier_count": 1,
                "identifiers": ["Game"],
            }
        }
    }
    assert (
        classify_identifier("Game", "software_type", legacy)
        == "MALFORMED_COLLISION_EVIDENCE"
    )
