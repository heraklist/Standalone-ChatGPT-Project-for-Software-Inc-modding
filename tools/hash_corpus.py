from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile, is_zipfile

from tools.safe_artifacts import validate_archive_names

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "production/sim/manifests/archive-safety-policy.json"
BLOCK_PREFIX = "BLOCKED_UNTRUSTED_ARCHIVE:"

_REQUIRED_LIMITS = (
    "max_archive_bytes",
    "max_entries",
    "max_total_uncompressed_bytes",
    "max_entry_uncompressed_bytes",
    "max_compression_ratio",
    "max_nested_depth",
    "max_cumulative_nested_uncompressed_bytes",
)


def _blocked(reason: str) -> ValueError:
    return ValueError(f"{BLOCK_PREFIX} {reason}")


def _load_policy(overrides: dict | None) -> dict:
    try:
        policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _blocked(f"invalid archive safety policy: {exc}") from exc
    if not isinstance(policy, dict) or policy.get("schema_version") != 1:
        raise _blocked("archive safety policy schema_version must be 1")
    if overrides is not None:
        if not isinstance(overrides, dict):
            raise _blocked("archive safety policy override must be an object")
        policy.update(overrides)
    for key in _REQUIRED_LIMITS:
        value = policy.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            raise _blocked(f"invalid archive safety limit: {key}")
    if not isinstance(policy.get("windows_casefold_paths"), bool):
        raise _blocked("windows_casefold_paths must be boolean")
    return policy


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _metadata_gate(
    zf: ZipFile,
    *,
    policy: dict,
    depth: int,
    state: dict[str, int],
) -> list:
    infos = [info for info in zf.infolist() if not info.is_dir()]
    state["entry_count"] += len(infos)
    if state["entry_count"] > int(policy["max_entries"]):
        raise _blocked(
            f"entry count {state['entry_count']} exceeds {policy['max_entries']}"
        )

    try:
        validate_archive_names(
            [info.filename for info in infos],
            windows_casefold=bool(policy["windows_casefold_paths"]),
        )
    except ValueError as exc:
        raise _blocked(str(exc)) from exc

    total_uncompressed = sum(info.file_size for info in infos)
    if total_uncompressed > int(policy["max_total_uncompressed_bytes"]):
        raise _blocked(
            "total uncompressed bytes "
            f"{total_uncompressed} exceeds {policy['max_total_uncompressed_bytes']}"
        )

    if depth > 0:
        state["nested_uncompressed"] += total_uncompressed
        if (
            state["nested_uncompressed"]
            > int(policy["max_cumulative_nested_uncompressed_bytes"])
        ):
            raise _blocked(
                "cumulative nested uncompressed bytes "
                f"{state['nested_uncompressed']} exceeds "
                f"{policy['max_cumulative_nested_uncompressed_bytes']}"
            )

    for info in infos:
        if info.file_size > int(policy["max_entry_uncompressed_bytes"]):
            raise _blocked(
                f"entry {info.filename!r} uncompressed bytes {info.file_size} "
                f"exceeds {policy['max_entry_uncompressed_bytes']}"
            )
        ratio = info.file_size / max(info.compress_size, 1)
        if ratio > float(policy["max_compression_ratio"]):
            raise _blocked(
                f"entry {info.filename!r} compression ratio {ratio:.2f} "
                f"exceeds {policy['max_compression_ratio']}"
            )

    return sorted(infos, key=lambda info: info.filename)


def _inspect_open_zip(
    zf: ZipFile,
    *,
    policy: dict,
    depth: int,
    state: dict[str, int],
) -> dict[str, object]:
    infos = _metadata_gate(zf, policy=policy, depth=depth, state=state)
    files: list[dict[str, object]] = []
    compressed_total = 0
    uncompressed_total = 0

    for info in infos:
        try:
            data = zf.read(info)
        except (BadZipFile, RuntimeError, OSError) as exc:
            raise _blocked(f"cannot read {info.filename!r}: {exc}") from exc

        compressed_total += info.compress_size
        uncompressed_total += info.file_size
        files.append(
            {
                "path": info.filename,
                "compressed_bytes": info.compress_size,
                "uncompressed_bytes": info.file_size,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )

        nested_stream = io.BytesIO(data)
        if is_zipfile(nested_stream):
            if depth >= int(policy["max_nested_depth"]):
                raise _blocked(
                    f"nested archive depth {depth + 1} exceeds "
                    f"{policy['max_nested_depth']}"
                )
            if len(data) > int(policy["max_archive_bytes"]):
                raise _blocked(
                    f"nested archive {info.filename!r} bytes {len(data)} exceeds "
                    f"{policy['max_archive_bytes']}"
                )
            nested_stream.seek(0)
            try:
                with ZipFile(nested_stream) as nested:
                    _inspect_open_zip(
                        nested,
                        policy=policy,
                        depth=depth + 1,
                        state=state,
                    )
            except BadZipFile as exc:
                raise _blocked(
                    f"invalid nested ZIP {info.filename!r}: {exc}"
                ) from exc

    return {
        "file_count": len(files),
        "compressed_bytes": compressed_total,
        "uncompressed_bytes": uncompressed_total,
        "unsafe_paths": [],
        "files": files,
    }


def inspect_zip(path: Path, policy: dict | None = None) -> dict[str, object]:
    path = Path(path)
    effective = _load_policy(policy)
    try:
        archive_size = path.stat().st_size
    except OSError as exc:
        raise _blocked(f"cannot stat archive: {exc}") from exc
    if archive_size > int(effective["max_archive_bytes"]):
        raise _blocked(
            f"archive bytes {archive_size} exceeds {effective['max_archive_bytes']}"
        )

    archive_sha256 = _sha256_path(path)
    state = {"entry_count": 0, "nested_uncompressed": 0}
    try:
        with ZipFile(path) as zf:
            result = _inspect_open_zip(
                zf,
                policy=effective,
                depth=0,
                state=state,
            )
    except BadZipFile as exc:
        raise _blocked(f"invalid ZIP: {exc}") from exc

    result["archive_sha256"] = archive_sha256
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    try:
        result = inspect_zip(args.zip_path)
    except ValueError as exc:
        print(exc)
        return 1
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
