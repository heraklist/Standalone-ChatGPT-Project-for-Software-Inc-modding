from pathlib import Path
import csv
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.verify_repo import KNOWLEDGE_FILES, META_KEYS, verify
from tools.validate_registry import validate_registry

REQUIRED_DIRS = {"archive", "work", "production", "docs", "schemas", "tools", "tests"}
CANONICAL_SPEC_SHA256 = "7b77f04c522fb48e087e1b1a0be190a27b8614cd598abf7f7ed243e3e52c31f2"


def test_required_repository_roots_exist():
    missing = sorted(name for name in REQUIRED_DIRS if not (ROOT / name).is_dir())
    assert missing == []


def test_local_and_dist_are_ignored():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".local-sources/" in ignore
    assert "dist/" in ignore


def test_canonical_spec_hash_matches_approved_design():
    path = ROOT / "docs/superpowers/specs/2026-08-31-software-inc-mod-studio-design-v1.2.md"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == CANONICAL_SPEC_SHA256


def test_migration_source_map_has_required_columns():
    path = ROOT / "work/migration/source-map.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == ["original_name", "repo_path", "lifecycle", "classification", "sha256", "notes"]
        rows = list(reader)
    assert len(rows) >= 5


def test_exact_knowledge_file_set():
    actual = {p.name for p in (ROOT / "production/knowledge").iterdir() if p.is_file()}
    assert actual == KNOWLEDGE_FILES


def test_markdown_metadata_headers_are_complete():
    for path in (ROOT / "production/knowledge").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        head = text.split("---\n", 2)[1]
        for key in META_KEYS:
            assert f"{key}:" in head, (path.name, key)
        assert "## Known gaps / evidence limits" in text


def test_production_registry_validates():
    assert validate_registry(ROOT / "production/knowledge/17_EVIDENCE_REGISTRY.json") == []


def test_repo_verifier_accepts_current_tree():
    assert verify(ROOT) == []
