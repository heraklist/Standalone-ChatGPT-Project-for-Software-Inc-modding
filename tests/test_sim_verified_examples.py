from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "production" / "sim" / "examples"

EXPECTED = {
    "tyd": "tyd/list-and-comments.tyd",
    "sipl": "sipl/end-of-day.tyd",
    "code": "code/GameCompiledMinimal.cs",
    "furniture": "furniture/transform-parent.tyd",
    "materials": "materials/materials.tyd",
}


def test_verified_examples_corpus_has_exact_minimum_family_set() -> None:
    manifest = json.loads((EXAMPLES / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert set(manifest["examples"]) == set(EXPECTED)
    for family, relative in EXPECTED.items():
        record = manifest["examples"][family]
        assert record["path"] == relative
        assert record["verification"] == "STATICALLY_VERIFIED"
        assert record["runtime_proof"] is False
        assert record["synthetic"] is True
        assert record["canonical_references"]
        assert (EXAMPLES / relative).is_file()


def test_examples_readme_declares_scope_and_no_runtime_overclaim() -> None:
    text = (EXAMPLES / "README.md").read_text(encoding="utf-8")
    for phrase in (
        "synthetic and redistributable",
        "STATICALLY_VERIFIED",
        "not runtime/load proof",
        "Beta 1.8.42",
    ):
        assert phrase in text


def test_tyd_and_sipl_examples_preserve_parser_boundary() -> None:
    tyd = (EXAMPLES / EXPECTED["tyd"]).read_text(encoding="utf-8")
    sipl = (EXAMPLES / EXPECTED["sipl"]).read_text(encoding="utf-8")

    assert "#" in tyd
    assert "[" in tyd and ";" in tyd
    assert "~[" not in tyd
    assert "Script_EndOfDay" in sipl
    assert "~[" in sipl
    assert "//" in sipl
    assert "RunType Everyone" in sipl


def test_game_compiled_code_example_is_conservative_csharp3() -> None:
    text = (EXAMPLES / EXPECTED["code"]).read_text(encoding="utf-8")
    assert "class ModMeta" in text
    assert "class ModBehaviour" in text
    assert "get" in text
    assert "=>" not in text
    assert "PlayerPrefs" not in text
    assert "enum " not in text


def test_furniture_and_material_examples_encode_only_documented_core_rules() -> None:
    furniture = (EXAMPLES / EXPECTED["furniture"]).read_text(encoding="utf-8")
    materials = (EXAMPLES / EXPECTED["materials"]).read_text(encoding="utf-8")

    assert furniture.index('Name "Seat"') < furniture.index('TransformParent "Seat"')
    assert 'Name "SIM_EXAMPLE_FURNITURE"' in furniture
    assert "SIM_EXAMPLE_MATERIAL {" in materials
    for field in ("Base", "Bump", "Extra"):
        assert field in materials


def test_chatgpt_upload_contains_verified_examples(tmp_path: Path) -> None:
    from tools.build_sim_chatgpt_upload import build_chatgpt_upload

    zip_path, _ = build_chatgpt_upload(ROOT, out_dir=tmp_path)
    with ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert "examples/README.md" in names
    assert "examples/manifest.json" in names
    for relative in EXPECTED.values():
        assert f"examples/{relative}" in names
