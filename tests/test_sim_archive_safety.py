from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "production/sim/manifests/archive-safety-policy.json"


def _policy() -> dict:
    return json.loads(POLICY.read_text(encoding="utf-8"))


def test_archive_safety_policy_has_concrete_positive_limits() -> None:
    policy = _policy()
    assert policy["schema_version"] == 1
    for key in (
        "max_archive_bytes",
        "max_entries",
        "max_total_uncompressed_bytes",
        "max_entry_uncompressed_bytes",
        "max_compression_ratio",
        "max_nested_depth",
        "max_cumulative_nested_uncompressed_bytes",
    ):
        assert isinstance(policy[key], (int, float))
        assert policy[key] > 0
    assert policy["windows_casefold_paths"] is True


def test_repository_owned_zip_fixtures_fit_archive_byte_budget() -> None:
    policy = _policy()
    fixtures = [ROOT / "archive/raw/knowledge.zip"]
    for fixture in fixtures:
        assert fixture.is_file()
        assert fixture.stat().st_size <= policy["max_archive_bytes"]


def _test_policy(**overrides: object) -> dict:
    policy = {
        "max_archive_bytes": 16 * 1024 * 1024,
        "max_entries": 100,
        "max_total_uncompressed_bytes": 16 * 1024 * 1024,
        "max_entry_uncompressed_bytes": 16 * 1024 * 1024,
        "max_compression_ratio": 200.0,
        "max_nested_depth": 2,
        "max_cumulative_nested_uncompressed_bytes": 32 * 1024 * 1024,
        "windows_casefold_paths": True,
    }
    policy.update(overrides)
    return policy


def test_inspect_zip_blocks_compression_ratio_before_entry_read(tmp_path: Path) -> None:
    import zipfile
    import pytest
    from tools.hash_corpus import inspect_zip

    archive = tmp_path / "bomb.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("payload.txt", b"A" * (8 * 1024 * 1024))

    with pytest.raises(ValueError, match="BLOCKED_UNTRUSTED_ARCHIVE"):
        inspect_zip(archive, policy=_test_policy(max_compression_ratio=10.0))


def test_inspect_zip_blocks_archive_byte_limit(tmp_path: Path) -> None:
    import zipfile
    import pytest
    from tools.hash_corpus import inspect_zip

    archive = tmp_path / "large.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("payload.bin", b"X" * 256)

    assert archive.stat().st_size > 128
    with pytest.raises(ValueError, match="BLOCKED_UNTRUSTED_ARCHIVE"):
        inspect_zip(archive, policy=_test_policy(max_archive_bytes=128))


def test_inspect_zip_blocks_entry_count_limit(tmp_path: Path) -> None:
    import zipfile
    import pytest
    from tools.hash_corpus import inspect_zip

    archive = tmp_path / "entries.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("a.txt", b"a")
        zf.writestr("b.txt", b"b")

    with pytest.raises(ValueError, match="BLOCKED_UNTRUSTED_ARCHIVE"):
        inspect_zip(archive, policy=_test_policy(max_entries=1))


def test_inspect_zip_blocks_total_and_single_entry_limits(tmp_path: Path) -> None:
    import zipfile
    import pytest
    from tools.hash_corpus import inspect_zip

    archive = tmp_path / "sizes.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("a.bin", b"A" * 100)
        zf.writestr("b.bin", b"B" * 100)

    with pytest.raises(ValueError, match="BLOCKED_UNTRUSTED_ARCHIVE"):
        inspect_zip(
            archive,
            policy=_test_policy(max_total_uncompressed_bytes=150),
        )
    with pytest.raises(ValueError, match="BLOCKED_UNTRUSTED_ARCHIVE"):
        inspect_zip(
            archive,
            policy=_test_policy(max_entry_uncompressed_bytes=50),
        )


def test_inspect_zip_blocks_windows_casefold_collision(tmp_path: Path) -> None:
    import zipfile
    import pytest
    from tools.hash_corpus import inspect_zip

    archive = tmp_path / "casefold.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("Data/Game.tyd", b"a")
        zf.writestr("data/game.tyd", b"b")

    with pytest.raises(ValueError, match="BLOCKED_UNTRUSTED_ARCHIVE"):
        inspect_zip(archive, policy=_test_policy())


def _zip_bytes(entries: dict[str, bytes]) -> bytes:
    import io
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buffer.getvalue()


def test_inspect_zip_blocks_nested_depth_limit(tmp_path: Path) -> None:
    import zipfile
    import pytest
    from tools.hash_corpus import inspect_zip

    deepest = _zip_bytes({"payload.txt": b"safe"})
    middle = _zip_bytes({"deep.zip": deepest})
    archive = tmp_path / "outer.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("middle.zip", middle)

    with pytest.raises(ValueError, match="BLOCKED_UNTRUSTED_ARCHIVE"):
        inspect_zip(archive, policy=_test_policy(max_nested_depth=1))


def test_inspect_zip_blocks_cumulative_nested_expansion(tmp_path: Path) -> None:
    import zipfile
    import pytest
    from tools.hash_corpus import inspect_zip

    inner = _zip_bytes({"payload.bin": b"A" * 1024})
    archive = tmp_path / "outer.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("one.zip", inner)
        zf.writestr("two.zip", inner)

    with pytest.raises(ValueError, match="BLOCKED_UNTRUSTED_ARCHIVE"):
        inspect_zip(
            archive,
            policy=_test_policy(max_cumulative_nested_uncompressed_bytes=1500),
        )
