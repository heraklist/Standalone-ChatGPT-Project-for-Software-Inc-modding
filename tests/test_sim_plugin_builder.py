from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def make_git_source_fixture(tmp_path: Path):
    from tools.sim_git_source import GitSource

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "sim@example.invalid")
    _git(repo, "config", "user.name", "SIM Test")
    skill = repo / "production/sim/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_bytes(b"committed\n")
    _git(repo, "add", "production/sim/SKILL.md")
    _git(repo, "commit", "-m", "fixture")
    source = GitSource(repo, "HEAD")
    skill.write_bytes(b"dirty\n")
    return source


def test_git_source_reads_committed_bytes_not_dirty_worktree(tmp_path: Path) -> None:
    source = make_git_source_fixture(tmp_path)
    assert source.read_bytes("production/sim/SKILL.md") == b"committed\n"


def test_git_source_lists_committed_files_in_sorted_order(tmp_path: Path) -> None:
    from tools.sim_git_source import GitSource

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "sim@example.invalid")
    _git(repo, "config", "user.name", "SIM Test")
    for relative, data in (
        ("production/sim/z.txt", b"z"),
        ("production/sim/a.txt", b"a"),
        ("outside.txt", b"x"),
    ):
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fixture")

    source = GitSource(repo, "HEAD")
    assert source.list_files("production/sim") == (
        "production/sim/a.txt",
        "production/sim/z.txt",
    )


def test_git_source_rejects_invalid_source_sha(tmp_path: Path) -> None:
    from tools.sim_git_source import GitSource

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    with pytest.raises(ValueError, match="commit"):
        GitSource(repo, "definitely-not-a-commit")


@pytest.mark.parametrize(
    "path",
    ("/absolute.txt", "../secret.txt", "production/../secret.txt", r"production\sim\SKILL.md"),
)
def test_git_source_rejects_unsafe_repository_paths(tmp_path: Path, path: str) -> None:
    source = make_git_source_fixture(tmp_path)
    with pytest.raises(ValueError, match="path"):
        source.read_bytes(path)
