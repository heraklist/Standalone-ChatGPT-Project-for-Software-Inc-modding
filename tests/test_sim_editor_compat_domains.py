from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def domain_text(name: str) -> str:
    return (ROOT / "production/sim/domains" / name / "SKILL.md").read_text(
        encoding="utf-8"
    )


def test_final_domain_set_is_exactly_eight_modules() -> None:
    from tools.validate_sim_layout import REQUIRED_DOMAIN_MODULES

    assert REQUIRED_DOMAIN_MODULES == {
        "data-tyd",
        "sipl",
        "code-modding",
        "furniture",
        "materials",
        "localization",
        "editor-native",
        "compatibility-packaging",
    }


def test_editor_native_domain_rejects_invented_public_filesystem_schemas() -> None:
    text = domain_text("editor-native")
    lowered = text.lower()
    for invented in (
        "/Mods/Buildings",
        "/Mods/Blueprints",
        "Building.tyd",
        "BuildingBlueprint.tyd",
    ):
        assert invented.lower() in lowered
    assert "do not invent" in lowered
    assert "hardware design" in lowered
    assert "data" in lowered
    assert "native" in lowered
    assert "editor" in lowered
    assert "native-open" in lowered
    assert "tooling_blocked" in lowered


def test_compatibility_packaging_domain_uses_explicit_decision_states() -> None:
    text = domain_text("compatibility-packaging")
    for state in (
        "SAFE_AUTOFIX",
        "REVIEW_REQUIRED",
        "RUNTIME_REQUIRED",
        "UNKNOWN",
    ):
        assert state in text
    lowered = text.lower()
    assert "collision" in lowered
    assert "prefix" in lowered
    assert "manifest" in lowered
    assert "hash" in lowered
    assert "package" in lowered
    assert "dependencies" in lowered
    assert "loadafter" in lowered
    assert "priority" in lowered
    assert "do not invent" in lowered


def test_final_domains_are_bounded_orchestrator_owned_proposal_producers() -> None:
    for name in ("editor-native", "compatibility-packaging"):
        lowered = domain_text(name).lower()
        assert "do not dispatch" in lowered
        assert "do not mutate" in lowered
        assert "orchestrator" in lowered
        assert "proposed" in lowered


def test_layout_verifier_rejects_unexpected_domain_module(tmp_path: Path) -> None:
    from tools.validate_sim_layout import verify_sim_layout

    repo = tmp_path / "repository"
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    extra = repo / "production/sim/domains/invented-domain"
    extra.mkdir(parents=True)
    (extra / "SKILL.md").write_text("---\nname: invented-domain\n---\n", encoding="utf-8")

    assert "unexpected SIM domain module: invented-domain" in verify_sim_layout(repo)
