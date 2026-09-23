from __future__ import annotations

import os
import stat
from pathlib import Path, PurePosixPath


def normalize_archive_member(name: str) -> str:
    if not isinstance(name, str) or not name or "\x00" in name:
        raise ValueError("unsafe archive member name")
    if "\\" in name:
        raise ValueError(f"backslash archive path is ambiguous: {name!r}")
    if name.startswith("/") or (
        len(name) >= 2 and name[0].isalpha() and name[1] == ":"
    ):
        raise ValueError(f"archive member must be relative: {name!r}")

    raw_parts = name.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise ValueError(f"unsafe archive path segment: {name!r}")

    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise ValueError(f"unsafe archive member: {name!r}")
    normalized = path.as_posix()
    if normalized in {"", "."}:
        raise ValueError("empty archive member")
    return normalized


def validate_archive_names(
    names: list[str],
    *,
    windows_casefold: bool,
) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    seen_casefold: set[str] = set()
    for name in names:
        safe_name = normalize_archive_member(name)
        if safe_name in seen:
            raise ValueError(f"duplicate archive member: {safe_name}")
        seen.add(safe_name)
        if windows_casefold:
            folded = safe_name.casefold()
            if folded in seen_casefold:
                raise ValueError(
                    f"case-insensitive archive member collision: {safe_name}"
                )
            seen_casefold.add(folded)
        normalized.append(safe_name)
    return normalized


def _is_reparse_point(metadata: os.stat_result) -> bool:
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    attributes = getattr(metadata, "st_file_attributes", 0)
    return bool(flag and attributes & flag)


def _resolved_within(root_resolved: Path, path: Path) -> Path:
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"path escapes declared root: {path}") from exc
    return resolved


def assert_regular_file_within(root: Path, path: Path) -> None:
    root = Path(root)
    path = Path(path)
    root_resolved = root.resolve(strict=True)
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode) or _is_reparse_point(metadata):
        raise ValueError(f"symlink/reparse point is not allowed: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"special file is not allowed: {path}")
    _resolved_within(root_resolved, path)


def safe_source_files(root: Path) -> list[Path]:
    root = Path(root)
    if not root.exists():
        raise ValueError(f"source root does not exist: {root}")

    root_metadata = root.lstat()
    if (
        stat.S_ISLNK(root_metadata.st_mode)
        or _is_reparse_point(root_metadata)
        or not stat.S_ISDIR(root_metadata.st_mode)
    ):
        raise ValueError(f"source root must be a real directory: {root}")

    root_resolved = root.resolve(strict=True)
    files: list[Path] = []
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)

        for dirname in sorted(dirnames):
            directory = current_path / dirname
            metadata = directory.lstat()
            if stat.S_ISLNK(metadata.st_mode) or _is_reparse_point(metadata):
                raise ValueError(
                    f"symlink/reparse directory is not allowed: {directory}"
                )
            if not stat.S_ISDIR(metadata.st_mode):
                raise ValueError(f"non-directory traversal entry: {directory}")
            _resolved_within(root_resolved, directory)

        for filename in sorted(filenames):
            path = current_path / filename
            assert_regular_file_within(root, path)
            files.append(path)

    return sorted(files, key=lambda path: path.relative_to(root).as_posix())
