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

import hashlib

CANONICAL_SPEC_SHA256 = "7b77f04c522fb48e087e1b1a0be190a27b8614cd598abf7f7ed243e3e52c31f2"


def test_canonical_spec_hash_matches_approved_design():
    root = Path(__file__).resolve().parents[1]
    path = root / "docs/superpowers/specs/2026-08-31-software-inc-mod-studio-design-v1.2.md"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == CANONICAL_SPEC_SHA256
