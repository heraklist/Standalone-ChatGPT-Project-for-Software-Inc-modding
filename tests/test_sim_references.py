import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_copy_reference_is_hash_bound_and_repository_relative(tmp_path: Path) -> None:
    from tools.build_sim_references import build_reference

    source = tmp_path / "production/knowledge/source.md"
    source.parent.mkdir(parents=True)
    source.write_text("alpha\n", encoding="utf-8")
    output = tmp_path / "production/sim/references/out.md"

    record = build_reference(
        root=tmp_path,
        source_paths=[source],
        output_path=output,
        transform="COPY",
        reference_id="test-reference",
        source_id="test-source",
    )

    assert output.read_text(encoding="utf-8") == "alpha\n"
    assert record["canonical_source_paths"] == ["production/knowledge/source.md"]
    assert set(record["source_sha256"]) == {"production/knowledge/source.md"}
    assert len(record["source_sha256"]["production/knowledge/source.md"]) == 64
    assert record["output_path"] == "production/sim/references/out.md"
    assert len(record["output_sha256"]) == 64
    assert record["transform_type"] == "COPY"


def test_copy_reference_rejects_multiple_sources_until_a_real_transform_needs_them(
    tmp_path: Path,
) -> None:
    from tools.build_sim_references import build_reference

    first = tmp_path / "a.md"
    second = tmp_path / "b.md"
    first.write_text("a", encoding="utf-8")
    second.write_text("b", encoding="utf-8")

    try:
        build_reference(
            root=tmp_path,
            source_paths=[first, second],
            output_path=tmp_path / "out.md",
            transform="COPY",
            reference_id="multi",
            source_id="multi",
        )
    except ValueError as exc:
        assert "exactly one source" in str(exc)
    else:
        raise AssertionError("COPY with multiple sources must fail")


def test_validate_references_detects_stale_source(tmp_path: Path) -> None:
    from tools.build_sim_references import build_reference
    from tools.validate_sim_references import validate_references

    source = tmp_path / "production/knowledge/source.md"
    source.parent.mkdir(parents=True)
    source.write_text("alpha\n", encoding="utf-8")
    output = tmp_path / "production/sim/references/out.md"
    record = build_reference(
        root=tmp_path,
        source_paths=[source],
        output_path=output,
        transform="COPY",
        reference_id="test-reference",
        source_id="test-source",
    )
    manifest = tmp_path / "production/sim/manifests/reference-source-map.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps({"schema_version": 1, "entries": [record]}), encoding="utf-8"
    )

    source.write_text("changed\n", encoding="utf-8")

    errors = validate_references(tmp_path)
    assert any("source hash mismatch" in error for error in errors)


def test_validate_references_detects_missing_output(tmp_path: Path) -> None:
    from tools.build_sim_references import build_reference
    from tools.validate_sim_references import validate_references

    source = tmp_path / "production/knowledge/source.md"
    source.parent.mkdir(parents=True)
    source.write_text("alpha\n", encoding="utf-8")
    output = tmp_path / "production/sim/references/out.md"
    record = build_reference(
        root=tmp_path,
        source_paths=[source],
        output_path=output,
        transform="COPY",
        reference_id="test-reference",
        source_id="test-source",
    )
    manifest = tmp_path / "production/sim/manifests/reference-source-map.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps({"schema_version": 1, "entries": [record]}), encoding="utf-8"
    )
    output.unlink()

    errors = validate_references(tmp_path)
    assert any("missing reference output" in error for error in errors)


def test_production_reference_map_has_exact_planned_copy_targets() -> None:
    data = json.loads(
        (ROOT / "production/sim/manifests/reference-source-map.json").read_text(
            encoding="utf-8"
        )
    )
    targets = {entry["output_path"] for entry in data["entries"]}
    assert targets == {
        "production/sim/references/evidence-truth.md",
        "production/sim/references/ecosystem-router.md",
        "production/sim/references/tyd.md",
        "production/sim/references/data.md",
        "production/sim/references/sipl.md",
        "production/sim/references/code-core.md",
        "production/sim/references/code-runtime.md",
        "production/sim/references/furniture.md",
        "production/sim/references/materials.md",
        "production/sim/references/localization.md",
        "production/sim/references/editor-content.md",
        "production/sim/references/debugging.md",
        "production/sim/references/compatibility.md",
        "production/sim/references/delivery.md",
        "production/sim/references/verification.md",
    }
    assert all(entry["transform_type"] == "COPY" for entry in data["entries"])


def test_production_references_validate_cleanly() -> None:
    from tools.validate_sim_references import validate_references

    assert validate_references(ROOT) == []
