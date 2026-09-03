from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "production/evals/sim_editor_native.json"


def _load() -> list[dict]:
    return json.loads(SUITE.read_text(encoding="utf-8"))


def test_editor_native_suite_uses_behavioral_variants_not_one_literal_guard() -> None:
    rows = _load()
    assert len(rows) >= 9
    assert len({row["prompt"] for row in rows}) == len(rows)
    assert {row["surface"] for row in rows} == {"ChatGPT"}
    assert {row["target"] for row in rows} == {"Beta 1.8.42 (implicit default)"}

    joined_prompts = "\n".join(row["prompt"].lower() for row in rows)
    for concept in (
        "building",
        "blueprint",
        "descriptor",
        "release",
        "installer",
        "validator",
        "source tree",
        "zip",
    ):
        assert concept in joined_prompts


def test_every_variant_requires_native_route_blockage_and_no_substitute_artifact() -> None:
    for row in _load():
        required = " ".join(row["required_assertions"]).lower()
        forbidden = " ".join(row["forbidden_assertions"]).lower()

        assert row["title"]
        assert row["category"]
        assert row["severity"] in {"P0", "P1", "P2"}
        assert row["pass_rule"]
        assert "editor-native" in required
        assert "tooling_blocked" in required
        assert "native" in required and ("editor" in required or "workshop" in required)
        assert "substitute artifact" in forbidden
        assert "filesystem" in forbidden or "package" in forbidden
        assert row["verification_ceiling_without_native_open"] == "V0"


def test_suite_rejects_semantic_aliases_of_prior_a06_failures() -> None:
    rows = _load()
    forbidden = "\n".join(
        assertion.lower()
        for row in rows
        for assertion in row["forbidden_assertions"]
    )

    for semantic_alias in (
        "design specification",
        "authoring kit",
        "release kit",
        "storage path",
        "placeholder payload",
        "finalizer",
        "validation helper",
        "generic loader contract",
    ):
        assert semantic_alias in forbidden


def test_suite_does_not_require_user_to_repeat_target_version() -> None:
    for row in _load():
        assert "1.8.42" not in row["prompt"]
        required = " ".join(row["required_assertions"]).lower()
        assert "implicit beta 1.8.42 default" in required


def test_suite_covers_native_extension_storage_escape_regression() -> None:
    rows = _load()
    matching = [
        row
        for row in rows
        if ".build" in row["prompt"].lower() and ".xml" in row["prompt"].lower()
    ]
    assert matching, "missing live A06 regression for .build/.xml storage-to-package escape"

    row = matching[0]
    prompt = row["prompt"].lower()
    required = " ".join(row["required_assertions"]).lower()
    forbidden = " ".join(row["forbidden_assertions"]).lower()

    assert "native" in prompt
    assert "zip" in prompt
    assert "storage" in required
    assert "install" in required or "package" in required
    assert "tooling_blocked" in required
    assert ".build" in forbidden
    assert ".xml" in forbidden
    assert "substitute artifact" in forbidden
    assert "filesystem" in forbidden or "package" in forbidden
    assert row["verification_ceiling_without_native_open"] == "V0"
