from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME_PROFILE = "GAME_COMPILED_CSHARP3"
LOCAL_PROFILE = "LOCAL_PRECOMPILED"


def fixture_text(name: str) -> str:
    return (ROOT / "tests/fixtures/sim/code" / name).read_text(encoding="utf-8")


def load_validator():
    spec = importlib.util.find_spec("tools.validate_code_profile")
    assert spec is not None, "Task 8 validator module must exist"
    module = importlib.import_module("tools.validate_code_profile")
    return module.validate_code_source


def test_code_domain_exists_and_is_required_by_layout() -> None:
    skill = ROOT / "production/sim/domains/code-modding/SKILL.md"
    assert skill.is_file()

    from tools.validate_sim_layout import REQUIRED_DOMAIN_MODULES

    assert "code-modding" in REQUIRED_DOMAIN_MODULES


def test_game_compiled_profile_rejects_enum_usage() -> None:
    validate_code_source = load_validator()
    errors = validate_code_source(fixture_text("invalid-enum.cs"), GAME_PROFILE)
    assert any("enum" in error.lower() for error in errors)


def test_game_compiled_profile_rejects_expression_bodied_member() -> None:
    validate_code_source = load_validator()
    errors = validate_code_source(
        fixture_text("invalid-expression-bodied.cs"), GAME_PROFILE
    )
    assert any("expression-bodied" in error.lower() for error in errors)


def test_game_compiled_profile_keeps_csharp3_lambda_valid() -> None:
    validate_code_source = load_validator()
    assert validate_code_source(fixture_text("valid-csharp3.cs"), GAME_PROFILE) == []


def test_local_precompiled_profile_does_not_apply_game_compiler_lexical_rules() -> None:
    validate_code_source = load_validator()
    text = fixture_text("invalid-enum.cs") + "\n" + fixture_text(
        "invalid-expression-bodied.cs"
    )
    assert validate_code_source(text, LOCAL_PROFILE) == []


def test_code_domain_documents_distribution_runtime_and_security_constraints() -> None:
    text = (ROOT / "production/sim/domains/code-modding/SKILL.md").read_text(
        encoding="utf-8"
    )
    lowered = text.lower()
    for token in (
        "GAME_COMPILED_CSHARP3",
        "LOCAL_PRECOMPILED",
        "C# 3",
        "SOURCE_CONFLICT",
        "expression-bodied",
        "PlayerPrefs",
        "Beta 1.8.34",
        "SaveSetting",
        "LoadSetting",
        "Serialize",
        "Deserialize",
        "WriteDictionary",
        "GiveMeFreedom",
        "Managed",
    ):
        assert token.lower() in lowered
    assert "workshop" in lowered
    assert "high-impact" in lowered
    assert "do not dispatch" in lowered
    assert "do not mutate" in lowered
    assert "orchestrator" in lowered
    assert "proposed" in lowered
