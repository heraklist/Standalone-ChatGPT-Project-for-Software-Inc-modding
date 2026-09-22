from __future__ import annotations

import os
from pathlib import Path

import pytest


def test_archive_member_rejects_parent_traversal() -> None:
    from tools.safe_artifacts import normalize_archive_member

    with pytest.raises(ValueError):
        normalize_archive_member("../secret.txt")


@pytest.mark.parametrize(
    "name",
    (
        "/absolute.txt",
        "C:/drive.txt",
        r"Data\Game.tyd",
        "Data//Game.tyd",
        "Data/./Game.tyd",
        "",
    ),
)
def test_archive_member_rejects_ambiguous_or_nonrelative_names(name: str) -> None:
    from tools.safe_artifacts import normalize_archive_member

    with pytest.raises(ValueError):
        normalize_archive_member(name)


def test_archive_member_normalizes_safe_posix_name() -> None:
    from tools.safe_artifacts import normalize_archive_member

    assert normalize_archive_member("Data/Game.tyd") == "Data/Game.tyd"


def test_archive_names_reject_windows_casefold_collision() -> None:
    from tools.safe_artifacts import validate_archive_names

    with pytest.raises(ValueError):
        validate_archive_names(
            ["Data/Game.tyd", "data/game.tyd"],
            windows_casefold=True,
        )


def test_archive_names_reject_exact_duplicate() -> None:
    from tools.safe_artifacts import validate_archive_names

    with pytest.raises(ValueError):
        validate_archive_names(
            ["Data/Game.tyd", "Data/Game.tyd"],
            windows_casefold=False,
        )


def test_safe_source_files_rejects_symlink(tmp_path: Path) -> None:
    from tools.safe_artifacts import safe_source_files

    root = tmp_path / "mod"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    try:
        os.symlink(outside, root / "inside-link.txt")
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    with pytest.raises(ValueError):
        safe_source_files(root)


def test_safe_source_files_rejects_symlink_directory(tmp_path: Path) -> None:
    from tools.safe_artifacts import safe_source_files

    root = tmp_path / "mod"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        os.symlink(outside, root / "inside-link", target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink creation unavailable: {exc}")

    with pytest.raises(ValueError):
        safe_source_files(root)


def test_safe_source_files_returns_sorted_regular_files(tmp_path: Path) -> None:
    from tools.safe_artifacts import safe_source_files

    root = tmp_path / "mod"
    (root / "z").mkdir(parents=True)
    (root / "z" / "b.txt").write_text("b", encoding="utf-8")
    (root / "a.txt").write_text("a", encoding="utf-8")

    assert [path.relative_to(root).as_posix() for path in safe_source_files(root)] == [
        "a.txt",
        "z/b.txt",
    ]


def test_safe_source_files_rejects_fifo_when_supported(tmp_path: Path) -> None:
    from tools.safe_artifacts import safe_source_files

    if not hasattr(os, "mkfifo"):
        pytest.skip("FIFO creation unavailable")
    root = tmp_path / "mod"
    root.mkdir()
    fifo = root / "pipe"
    try:
        os.mkfifo(fifo)
    except OSError as exc:
        pytest.skip(f"FIFO creation unavailable: {exc}")

    with pytest.raises(ValueError):
        safe_source_files(root)
