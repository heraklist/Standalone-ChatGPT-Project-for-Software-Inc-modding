import json
from pathlib import Path


def test_beta17_manifest_is_older_version_and_has_expected_hash():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "work/corpus/beta-1.7.15/manifest.json").read_text())
    assert data["game_version"] == "Beta 1.7.15"
    assert data["source_role"] == "OLDER_VANILLA_CORPUS"
    assert data["archive_sha256"] == "29685ddc23cbcf1d3e1488c29aeeb09612d9ddd79c346949361b863fd325b02d"
    assert data["file_count"] == 50
    assert data["uncompressed_bytes"] == 121991


def test_beta17_file_manifest_is_safe_and_deterministic():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "work/corpus/beta-1.7.15/file-hashes.json").read_text())
    assert data["unsafe_paths"] == []
    paths = [item["path"] for item in data["files"]]
    assert paths == sorted(paths)
    assert len(paths) == data["file_count"] == 50
