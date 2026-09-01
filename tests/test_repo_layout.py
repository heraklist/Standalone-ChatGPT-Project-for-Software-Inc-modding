from pathlib import Path

REQUIRED_DIRS = {
    "archive",
    "work",
    "production",
    "docs",
    "schemas",
    "tools",
    "tests",
}


def test_required_repository_roots_exist():
    root = Path(__file__).resolve().parents[1]
    missing = sorted(name for name in REQUIRED_DIRS if not (root / name).is_dir())
    assert missing == []


def test_local_and_dist_are_ignored():
    root = Path(__file__).resolve().parents[1]
    ignore = (root / ".gitignore").read_text(encoding="utf-8")
    assert ".local-sources/" in ignore
    assert "dist/" in ignore
