from __future__ import annotations

import io
import stat
import zipfile
from pathlib import Path


def _policy(**overrides: object) -> dict:
    policy = {
        "max_archive_bytes": 1024 * 1024,
        "max_entries": 100,
        "max_total_uncompressed_bytes": 1024 * 1024,
        "max_entry_uncompressed_bytes": 1024 * 1024,
        "max_compression_ratio": 50.0,
        "max_nested_depth": 2,
        "max_cumulative_nested_uncompressed_bytes": 2 * 1024 * 1024,
        "windows_casefold_paths": True,
    }
    policy.update(overrides)
    return policy


def _write_zip(path: Path, entries: list[tuple[str, bytes]]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in entries:
            archive.writestr(name, payload)


def _zip_bytes(entries: list[tuple[str, bytes]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in entries:
            archive.writestr(name, payload)
    return buffer.getvalue()


def test_inspect_archive_returns_structured_pass_for_safe_zip(tmp_path: Path) -> None:
    from tools.inspect_archive import inspect_archive

    archive = tmp_path / "safe.zip"
    _write_zip(archive, [("Data/Test.tyd", b"Name = Test\n")])

    result = inspect_archive(archive, _policy())

    assert result["result"] == "PASS"
    assert result["entries"] == 1
    assert result["total_uncompressed_bytes"] > 0
    assert result["max_nested_depth_observed"] == 0
    assert result["findings"] == []
    assert len(result["archive_sha256"]) == 64


def test_inspect_archive_rejects_traversal_and_backslash_paths(tmp_path: Path) -> None:
    from tools.inspect_archive import inspect_archive

    archive = tmp_path / "unsafe.zip"
    _write_zip(
        archive,
        [
            ("../escape.txt", b"x"),
            ("Data\\Game.tyd", b"y"),
        ],
    )

    result = inspect_archive(archive, _policy())

    assert result["result"] == "REJECT"
    assert [item["code"] for item in result["findings"]] == [
        "ARCHIVE_PATH_INVALID",
        "ARCHIVE_PATH_INVALID",
    ]


def test_inspect_archive_rejects_casefold_collision(tmp_path: Path) -> None:
    from tools.inspect_archive import inspect_archive

    archive = tmp_path / "casefold.zip"
    _write_zip(
        archive,
        [
            ("Data/Game.tyd", b"a"),
            ("data/game.tyd", b"b"),
        ],
    )

    result = inspect_archive(archive, _policy())

    assert result["result"] == "REJECT"
    assert any(item["code"] == "ARCHIVE_CASEFOLD_COLLISION" for item in result["findings"])


def test_inspect_archive_rejects_symlink_member(tmp_path: Path) -> None:
    from tools.inspect_archive import inspect_archive

    archive = tmp_path / "symlink.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        zf.writestr(info, "target")

    result = inspect_archive(archive, _policy())

    assert result["result"] == "REJECT"
    assert any(item["code"] == "ARCHIVE_SYMLINK" for item in result["findings"])


def test_inspect_archive_rejects_compression_ratio_before_payload_read(
    tmp_path: Path,
) -> None:
    from tools.inspect_archive import inspect_archive

    archive = tmp_path / "ratio.zip"
    _write_zip(archive, [("payload.bin", b"A" * 200_000)])

    result = inspect_archive(archive, _policy(max_compression_ratio=5.0))

    assert result["result"] == "REJECT"
    assert any(item["code"] == "ARCHIVE_COMPRESSION_RATIO" for item in result["findings"])


def test_inspect_archive_bounds_nested_depth(tmp_path: Path) -> None:
    from tools.inspect_archive import inspect_archive

    deep = _zip_bytes([("payload.txt", b"safe")])
    middle = _zip_bytes([("deep.zip", deep)])
    archive = tmp_path / "outer.zip"
    _write_zip(archive, [("middle.zip", middle)])

    result = inspect_archive(archive, _policy(max_nested_depth=1))

    assert result["result"] == "REJECT"
    assert any(item["code"] == "ARCHIVE_NESTED_DEPTH" for item in result["findings"])
