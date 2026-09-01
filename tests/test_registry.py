import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.validate_registry import validate_registry


def test_beta17_manifest_is_older_version_and_has_expected_hash():
    data = json.loads((ROOT / "work/corpus/beta-1.7.15/manifest.json").read_text())
    assert data["game_version"] == "Beta 1.7.15"
    assert data["source_role"] == "OLDER_VANILLA_CORPUS"
    assert data["archive_sha256"] == "29685ddc23cbcf1d3e1488c29aeeb09612d9ddd79c346949361b863fd325b02d"
    assert data["file_count"] == 50
    assert data["uncompressed_bytes"] == 121991


def test_beta17_file_manifest_is_safe_and_deterministic():
    data = json.loads((ROOT / "work/corpus/beta-1.7.15/file-hashes.json").read_text())
    assert data["unsafe_paths"] == []
    paths = [item["path"] for item in data["files"]]
    assert paths == sorted(paths)
    assert len(paths) == data["file_count"] == 50


def test_registry_seed_contract_and_roles():
    registry = json.loads((ROOT / "work/evidence/registry.seed.json").read_text())
    assert set(registry) == {"sources", "claims", "corpora", "media"}
    required = {
        "source_id",
        "source_class",
        "source_role",
        "canonical_url_or_origin",
        "currency",
        "scope",
        "retrieved_at",
        "status",
    }
    for source in registry["sources"].values():
        assert required <= set(source)
    roles = {source["source_role"] for source in registry["sources"].values()}
    assert {
        "DEVELOPER_WIKI",
        "OFFICIAL_PATCH_NOTE",
        "ENGINE_FORK_SOURCE",
        "LINKED_ENGINE_API",
        "OLDER_VANILLA_CORPUS",
    } <= roles


def test_registry_seed_validates_semantically():
    assert validate_registry(ROOT / "work/evidence/registry.seed.json") == []
