from __future__ import annotations

import hashlib
from pathlib import Path

import pytest


def _expected(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for path in sorted(files):
        file_sha = hashlib.sha256(files[path]).hexdigest()
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_sha.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def test_hash_bytes_tree_is_path_and_content_sensitive() -> None:
    from tools.sim_candidate_identity import hash_bytes_tree

    files = {"a.txt": b"A", "b.txt": b"B"}
    first = hash_bytes_tree(files)
    second = hash_bytes_tree({"b.txt": b"B", "a.txt": b"A"})
    changed = hash_bytes_tree({"a.txt": b"A", "b.txt": b"C"})
    renamed = hash_bytes_tree({"a.txt": b"A", "c.txt": b"B"})

    assert first == _expected(files)
    assert first == second
    assert first != changed
    assert first != renamed
    assert len(first) == 64


def test_aggregate_file_hashes_matches_bytes_tree_vector() -> None:
    from tools.sim_candidate_identity import aggregate_file_hashes, hash_bytes_tree

    files = {"a.txt": b"A", "b.txt": b"B"}
    declared = {
        path: hashlib.sha256(data).hexdigest()
        for path, data in files.items()
    }
    assert aggregate_file_hashes(declared) == hash_bytes_tree(files)


def test_hash_tree_includes_finalized_provenance_files(tmp_path: Path) -> None:
    from tools.sim_candidate_identity import hash_tree

    (tmp_path / "skills/sim").mkdir(parents=True)
    (tmp_path / "skills/sim/SKILL.md").write_bytes(b"skill")
    provenance = tmp_path / "provenance"
    provenance.mkdir()
    manifest = provenance / "plugin_manifest.json"
    manifest.write_bytes(b"one")
    first = hash_tree(tmp_path)
    manifest.write_bytes(b"two")
    second = hash_tree(tmp_path)
    assert first != second


def test_hash_tree_rejects_symlinks(tmp_path: Path) -> None:
    from tools.sim_candidate_identity import hash_tree
    import os

    target = tmp_path / "target.txt"
    target.write_text("target", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        os.symlink(target, link)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    with pytest.raises(ValueError):
        hash_tree(tmp_path)
