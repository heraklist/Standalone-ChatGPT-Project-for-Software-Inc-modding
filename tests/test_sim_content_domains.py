from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def domain_text(name: str) -> str:
    return (ROOT / "production/sim/domains" / name / "SKILL.md").read_text(
        encoding="utf-8"
    )


def test_content_pack_domains_exist_and_are_required_by_layout() -> None:
    from tools.validate_sim_layout import REQUIRED_DOMAIN_MODULES

    expected = {"furniture", "materials", "localization"}
    assert expected <= REQUIRED_DOMAIN_MODULES
    for name in expected:
        assert (ROOT / "production/sim/domains" / name / "SKILL.md").is_file()


def test_furniture_domain_limits_ordering_rule_to_transform_dependencies() -> None:
    lowered = domain_text("furniture").lower()
    assert "transformparent" in lowered
    assert "already been created" in lowered
    assert "definition order matters" in lowered
    assert "not a universal tyd field-order rule" in lowered
    assert "reload_furniture" in lowered
    assert "fresh placement" in lowered
    assert "export_furniture_bounds" in lowered


def test_materials_domain_preserves_identity_presets_and_channels() -> None:
    lowered = domain_text("materials").lower()
    for token in (
        "material_table_name",
        "up to eight",
        "base",
        "bump",
        "extra",
        "occlusion",
        "smoothness",
        "metallic",
        "rain/snow",
        "256×256",
    ):
        assert token in lowered
    assert "not a universal hard cap" in lowered
    assert "base.png" in lowered
    assert "not mandatory" in lowered


def test_localization_domain_locks_exact_lowercase_name_list_filenames() -> None:
    text = domain_text("localization")
    for filename in (
        "femalefirstnames.txt",
        "malefirstnames.txt",
        "lastnames.txt",
    ):
        assert filename in text
    assert "exactly lowercase" in text.lower()
    assert "one name per line" in text.lower()
    assert "do not alphabetically sort" in text.lower()
    assert "RELOAD_LOCALIZATION" in text


def test_content_domains_are_bounded_orchestrator_owned_proposal_producers() -> None:
    for name in ("furniture", "materials", "localization"):
        lowered = domain_text(name).lower()
        assert "do not dispatch" in lowered
        assert "do not mutate" in lowered
        assert "orchestrator" in lowered
        assert "proposed" in lowered


def test_synthetic_content_fixtures_are_redistributable_and_non_proprietary() -> None:
    fixtures = ROOT / "tests/fixtures/sim/content"
    furniture = (fixtures / "synthetic-furniture.tyd").read_text(encoding="utf-8")
    materials = (fixtures / "synthetic-materials.tyd").read_text(encoding="utf-8")
    names = (fixtures / "femalefirstnames.txt").read_text(encoding="utf-8")

    assert "SIM_TEST_CHAIR" in furniture
    assert "TransformParent" in furniture
    assert "SIM_TEST_MATERIAL" in materials
    assert "Base" in materials and "Bump" in materials and "Extra" in materials
    assert names.splitlines() == ["Ada", "Bea", "Cyra"]
