from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "production/sim/SKILL.md"


def test_root_skill_declares_packaged_progressive_disclosure_paths() -> None:
    text = SIM.read_text(encoding="utf-8")

    required_paths = {
        "references/evidence-truth.md",
        "references/data.md",
        "references/sipl.md",
        "references/code-core.md",
        "references/code-runtime.md",
        "references/furniture.md",
        "references/materials.md",
        "references/localization.md",
        "references/editor-content.md",
        "references/debugging.md",
        "references/compatibility.md",
        "references/delivery.md",
        "references/state-vocabulary.md",
        "references/verification.md",
        "references/internal/domains/data-tyd.md",
        "references/internal/domains/sipl.md",
        "references/internal/domains/code-modding.md",
        "references/internal/domains/furniture.md",
        "references/internal/domains/materials.md",
        "references/internal/domains/localization.md",
        "references/internal/domains/editor-native.md",
        "references/internal/domains/compatibility-packaging.md",
    }

    missing = sorted(path for path in required_paths if path not in text)
    assert missing == []


def test_root_skill_routes_building_requests_to_editor_native_before_artifact_work() -> None:
    text = SIM.read_text(encoding="utf-8")

    assert "Building / Building Blueprint" in text
    assert "references/internal/domains/editor-native.md" in text
    assert "references/editor-content.md" in text
    assert "Route before artifact generation" in text


def test_root_skill_keeps_domain_detail_out_of_routing_table() -> None:
    text = SIM.read_text(encoding="utf-8")

    marker = "## Runtime routing and progressive disclosure"
    assert marker in text
    section = text.split(marker, 1)[1].split("\n## ", 1)[0]

    # Routing should point to owner material, not reproduce detailed family schemas.
    assert "InteractionPoints" not in section
    assert "Base R" not in section
    assert "Script_EndOfDay" not in section
    assert "SaveSetting" not in section
