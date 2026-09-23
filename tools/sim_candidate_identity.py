from __future__ import annotations

import hashlib
from pathlib import Path

from tools.safe_artifacts import normalize_archive_member, safe_source_files


def aggregate_file_hashes(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    normalized: dict[str, str] = {}
    for path, file_sha in files.items():
        safe_path = normalize_archive_member(path)
        if safe_path in normalized:
            raise ValueError(f"duplicate candidate identity path: {safe_path}")
        if (
            not isinstance(file_sha, str)
            or len(file_sha) != 64
            or any(ch not in "0123456789abcdefABCDEF" for ch in file_sha)
        ):
            raise ValueError(f"invalid SHA-256 for candidate path: {safe_path}")
        normalized[safe_path] = file_sha.lower()

    for path in sorted(normalized):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(normalized[path].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def hash_bytes_tree(files: dict[str, bytes]) -> str:
    hashes: dict[str, str] = {}
    for path, data in files.items():
        if not isinstance(data, bytes):
            raise ValueError(f"candidate bytes required for path: {path}")
        safe_path = normalize_archive_member(path)
        if safe_path in hashes:
            raise ValueError(f"duplicate candidate path: {safe_path}")
        hashes[safe_path] = hashlib.sha256(data).hexdigest()
    return aggregate_file_hashes(hashes)


def hash_tree(root: Path) -> str:
    root = Path(root)
    files: dict[str, bytes] = {}
    for path in safe_source_files(root):
        relative = path.relative_to(root).as_posix()
        files[relative] = path.read_bytes()
    return hash_bytes_tree(files)
