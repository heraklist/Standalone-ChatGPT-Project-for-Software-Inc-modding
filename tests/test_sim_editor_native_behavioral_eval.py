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


def test_suite_covers_concrete_tree_before_refusal_regression() -> None:
    rows = _load()
    matching = [
        row
        for row in rows
        if "exact folder structure" in row["prompt"].lower()
        and "zip" in row["prompt"].lower()
        and "building" in row["prompt"].lower()
        and "blueprint" in row["prompt"].lower()
    ]
    assert matching, "missing A06 regression for concrete install tree before refusal"

    row = matching[0]
    required = " ".join(row["required_assertions"]).lower()
    forbidden = " ".join(row["forbidden_assertions"]).lower()

    assert "tooling_blocked" in required
    assert "do not enumerate" in required
    assert "storage/export observation" in required
    assert "software inc\\buildings" in forbidden
    assert "software inc\\blueprints" in forbidden
    assert "later refusal" in forbidden
    assert row["verification_ceiling_without_native_open"] == "V0"


def test_runtime_contains_explicit_building_blueprint_package_hard_stop() -> None:
    public_skill = (ROOT / "production/sim/SKILL.md").read_text(encoding="utf-8").lower()
    owner_skill = (
        ROOT / "production/sim/domains/editor-native/SKILL.md"
    ).read_text(encoding="utf-8").lower()
    knowledge = (
        ROOT / "production/knowledge/11_EDITOR_CONTENT_HARDWARE_BLUEPRINTS_BUILDINGS.md"
    ).read_text(encoding="utf-8").lower()

    for text in (public_skill, owner_skill, knowledge):
        assert "building/blueprint package hard stop" in text
        assert "do not enumerate" in text
        assert "concrete install tree" in text
        assert "tooling_blocked" in text


def test_runtime_hard_stop_uses_canonical_single_windows_path_separator() -> None:
    paths = (
        ROOT / "production/sim/SKILL.md",
        ROOT / "production/sim/domains/editor-native/SKILL.md",
        ROOT / "production/knowledge/11_EDITOR_CONTENT_HARDWARE_BLUEPRINTS_BUILDINGS.md",
    )
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        assert "software inc\\\\buildings" not in text
        assert "software inc\\\\blueprints" not in text
        assert "software inc\\buildings" in text
        assert "software inc\\blueprints" in text


def test_runtime_has_p0_preflight_before_research_for_building_blueprint_packages() -> None:
    public_skill = (ROOT / "production/sim/SKILL.md").read_text(encoding="utf-8").lower()
    owner_skill = (
        ROOT / "production/sim/domains/editor-native/SKILL.md"
    ).read_text(encoding="utf-8").lower()
    knowledge = (
        ROOT / "production/knowledge/11_EDITOR_CONTENT_HARDWARE_BLUEPRINTS_BUILDINGS.md"
    ).read_text(encoding="utf-8").lower()

    public_preflight = public_skill.index("p0 building/blueprint preflight")
    assert public_preflight < public_skill.index("## operating mode")
    assert public_preflight < public_skill.index("## evidence and research")

    for text in (public_skill, owner_skill, knowledge):
        assert "p0 building/blueprint preflight" in text
        assert "before any web search" in text
        assert "do not search for or repeat filesystem paths" in text
        assert "do not show a negative example tree" in text
        assert "tooling_blocked" in text


def test_suite_covers_loader_claim_and_negative_example_tree_regression() -> None:
    rows = _load()
    matching = [row for row in rows if row["id"] == "A06-BHV-11"]
    assert matching, "missing A06 regression for loader claim plus negative example tree"

    row = matching[0]
    required = " ".join(row["required_assertions"]).lower()
    forbidden = " ".join(row["forbidden_assertions"]).lower()

    assert "before web search" in required
    assert "tooling_blocked" in required
    assert "do not repeat literal filesystem paths" in required
    assert "load as" in forbidden
    assert "negative example tree" in forbidden
    assert "mods/mybuilding" in forbidden
    assert row["verification_ceiling_without_native_open"] == "V0"
