import json
import shutil
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]

from tools.validate_sim_layout import verify_sim_layout
from tools.verify_repo import verify


SCHEMA_NAMES = (
    "sim-session.schema.json",
    "sim-plan.schema.json",
    "sim-specialist-request.schema.json",
    "sim-specialist-result.schema.json",
    "sim-reference-map.schema.json",
    "sim-release-manifest.schema.json",
    "sim-eval.schema.json",
)

SIM_MANIFEST = {
    "product": "SIM",
    "display_name": "Software Inc Modding",
    "version": "0.2.0-preview",
    "channel": "PREVIEW",
    "canonical_game_target": "Beta 1.8.42",
    "evidence_grade": "GENERATION_GRADE",
}

COMPATIBILITY_CAPABILITIES = {
    "explicit_invocation": "TO_BE_VERIFIED",
    "thread_persistence": "TO_BE_VERIFIED",
    "script_execution": "CAPABILITY_DEPENDENT",
    "artifact_creation": "CAPABILITY_DEPENDENT",
}


def write_sim_contracts(root: Path) -> None:
    schemas = root / "schemas"
    schemas.mkdir(parents=True)
    for name in SCHEMA_NAMES:
        shutil.copy2(ROOT / "schemas" / name, schemas / name)

    manifests = root / "production" / "sim" / "manifests"
    manifests.mkdir(parents=True)
    (manifests / "sim-manifest.json").write_text(
        json.dumps(SIM_MANIFEST), encoding="utf-8"
    )
    (manifests / "reference-source-map.json").write_text(
        json.dumps({"schema_version": 1, "entries": []}), encoding="utf-8"
    )
    (manifests / "compatibility-matrix.json").write_text(
        json.dumps(
            {
                "surfaces": {
                    surface: COMPATIBILITY_CAPABILITIES
                    for surface in ("ChatGPT", "ChatGPT Project", "Codex")
                }
            }
        ),
        encoding="utf-8",
    )


def test_manifest_declares_preview_product_identity() -> None:
    manifest = json.loads(
        (ROOT / "production/sim/manifests/sim-manifest.json").read_text(encoding="utf-8")
    )

    assert manifest == SIM_MANIFEST


def test_empty_reference_source_map_conforms_to_machine_contract() -> None:
    source_map = json.loads(
        (ROOT / "production/sim/manifests/reference-source-map.json").read_text(
            encoding="utf-8"
        )
    )
    schema = json.loads(
        (ROOT / "schemas/sim-reference-map.schema.json").read_text(encoding="utf-8")
    )

    assert source_map == {"schema_version": 1, "entries": []}
    jsonschema.Draft202012Validator(schema).validate(source_map)


def test_compatibility_matrix_makes_no_host_support_claims() -> None:
    matrix = json.loads(
        (ROOT / "production/sim/manifests/compatibility-matrix.json").read_text(
            encoding="utf-8"
        )
    )

    for surface in ("ChatGPT", "ChatGPT Project", "Codex"):
        assert matrix["surfaces"][surface] == COMPATIBILITY_CAPABILITIES


def test_verify_sim_layout_accepts_complete_pr_a_contract(tmp_path: Path) -> None:
    write_sim_contracts(tmp_path)

    assert verify_sim_layout(tmp_path) == []


def test_verify_sim_layout_reports_missing_required_paths(tmp_path: Path) -> None:
    write_sim_contracts(tmp_path)
    (tmp_path / "production/sim/manifests/reference-source-map.json").unlink()

    assert verify_sim_layout(tmp_path) == [
        "missing SIM required path: production/sim/manifests/reference-source-map.json"
    ]


def test_verify_sim_layout_rejects_invalid_manifest_identity(tmp_path: Path) -> None:
    write_sim_contracts(tmp_path)
    manifest_path = tmp_path / "production/sim/manifests/sim-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["product"] = "NOT_SIM"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert verify_sim_layout(tmp_path) == ["SIM manifest identity mismatch: product"]


@pytest.mark.parametrize("manifest_root", ([], None))
def test_verify_sim_layout_reports_non_object_manifest_json(
    tmp_path: Path, manifest_root: object
) -> None:
    write_sim_contracts(tmp_path)
    manifest_path = tmp_path / "production/sim/manifests/sim-manifest.json"
    manifest_path.write_text(json.dumps(manifest_root), encoding="utf-8")

    assert verify_sim_layout(tmp_path) == ["SIM manifest must be a JSON object"]


def test_verify_repo_requires_sim_contract_only_when_sim_exists(tmp_path: Path) -> None:
    repo = tmp_path / "repository"
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    manifest_path = repo / "production/sim/manifests/sim-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["product"] = "NOT_SIM"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert "sim layout: SIM manifest identity mismatch: product" in verify(repo)

    shutil.rmtree(repo / "production/sim")

    assert verify(repo) == []
