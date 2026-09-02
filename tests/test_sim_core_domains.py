import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

from tools.validate_sim_layout import verify_sim_layout


def domain_text(name: str) -> str:
    return (ROOT / "production/sim/domains" / name / "SKILL.md").read_text(
        encoding="utf-8"
    )


def test_data_and_sipl_core_domains_exist() -> None:
    for name in ("data-tyd", "sipl"):
        assert (ROOT / "production/sim/domains" / name / "SKILL.md").is_file()


def test_data_tyd_domain_owns_documented_data_surfaces() -> None:
    text = domain_text("data-tyd")
    for token in (
        "SoftwareTypes",
        "CompanyTypes",
        "NameGenerators",
        "Personalities.tyd",
        "Categories",
        "Features",
        "SubFeatures",
        "AddOns",
        "Override True",
        "Override Delete",
    ):
        assert token in text


def test_data_tyd_domain_preserves_canonical_tyd_anti_folklore_rules() -> None:
    lowered = domain_text("data-tyd").lower()
    assert "no universal field-order law" in lowered
    assert "no lowercase-only boolean law" in lowered
    assert "no greek-semicolon law" in lowered
    assert "canonical generated tyd booleans" in lowered
    assert "true" in lowered and "false" in lowered


def test_data_tyd_domain_keeps_nested_concepts_out_of_fake_directories() -> None:
    lowered = domain_text("data-tyd").lower()
    assert "nested" in lowered
    assert "not canonical directories" in lowered
    assert "manufacturing" in lowered


def test_sipl_domain_declares_language_and_tyd_boundary() -> None:
    text = domain_text("sipl")
    for token in (
        "~[",
        "TyD",
        "RunType",
        "Level-3",
        "Script_EndOfDay",
        "Script_AfterSales",
        "Script_OnRelease",
        "Script_NewCopies",
        "Script_WorkItemChange",
        "AmountScript",
    ):
        assert token in text
    assert "[a; b]" in text
    assert "//" in text
    assert "#" in text


def test_sipl_domain_preserves_runtype_scope_constraints() -> None:
    text = domain_text("sipl")
    lowered = text.lower()
    assert "afterSales".lower() in lowered
    assert "host-only" in lowered
    assert "workitemchange" in lowered
    assert "local-player-only" in lowered
    assert "endofday" in lowered
    assert "onrelease" in lowered
    assert "newcopies" in lowered


def test_core_domain_modules_are_bounded_and_orchestrator_owned() -> None:
    for name in ("data-tyd", "sipl"):
        lowered = domain_text(name).lower()
        assert "do not dispatch" in lowered
        assert "do not mutate" in lowered
        assert "orchestrator" in lowered
        assert "proposed" in lowered


def test_layout_verifier_requires_data_tyd_domain(tmp_path: Path) -> None:
    repo = tmp_path / "repository"
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    shutil.rmtree(repo / "production/sim/domains/data-tyd")

    assert (
        "missing SIM required path: production/sim/domains/data-tyd/SKILL.md"
        in verify_sim_layout(repo)
    )


def test_layout_verifier_requires_sipl_domain(tmp_path: Path) -> None:
    repo = tmp_path / "repository"
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    shutil.rmtree(repo / "production/sim/domains/sipl")

    assert (
        "missing SIM required path: production/sim/domains/sipl/SKILL.md"
        in verify_sim_layout(repo)
    )
