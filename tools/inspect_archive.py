from __future__ import annotations

import argparse
import hashlib
import io
import json
import stat
import zipfile
from pathlib import Path

from tools.safe_artifacts import normalize_archive_member


def _finding(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _ratio(info: zipfile.ZipInfo) -> float:
    if info.file_size == 0:
        return 0.0
    if info.compress_size == 0:
        return float("inf")
    return info.file_size / info.compress_size


def _inspect_zip(
    archive: zipfile.ZipFile,
    *,
    policy: dict,
    depth: int,
    prefix: str,
    state: dict,
) -> None:
    infos = archive.infolist()
    state["entries"] += len(infos)
    if state["entries"] > int(policy["max_entries"]):
        state["findings"].append(
            _finding(
                "ARCHIVE_ENTRY_COUNT",
                prefix or ".",
                f"entry count exceeds {policy['max_entries']}",
            )
        )

    names_seen: set[str] = set()
    folded_seen: set[str] = set()
    total_here = sum(int(info.file_size) for info in infos)
    state["total_uncompressed_bytes"] += total_here
    if state["total_uncompressed_bytes"] > int(
        policy["max_total_uncompressed_bytes"]
    ):
        state["findings"].append(
            _finding(
                "ARCHIVE_TOTAL_UNCOMPRESSED",
                prefix or ".",
                "total uncompressed bytes exceed policy",
            )
        )

    for info in infos:
        raw_name = info.filename
        is_dir = info.is_dir()
        candidate = raw_name[:-1] if is_dir and raw_name.endswith("/") else raw_name
        display = f"{prefix}!/{candidate}" if prefix else candidate

        try:
            normalized = normalize_archive_member(candidate)
        except ValueError as exc:
            state["findings"].append(
                _finding("ARCHIVE_PATH_INVALID", display, str(exc))
            )
            continue

        if normalized in names_seen:
            state["findings"].append(
                _finding(
                    "ARCHIVE_DUPLICATE",
                    display,
                    f"duplicate archive member: {normalized}",
                )
            )
        else:
            names_seen.add(normalized)

        if bool(policy.get("windows_casefold_paths", False)):
            folded = normalized.casefold()
            if folded in folded_seen:
                state["findings"].append(
                    _finding(
                        "ARCHIVE_CASEFOLD_COLLISION",
                        display,
                        f"case-insensitive collision: {normalized}",
                    )
                )
            else:
                folded_seen.add(folded)

        mode = info.external_attr >> 16
        file_type = stat.S_IFMT(mode)
        if file_type == stat.S_IFLNK:
            state["findings"].append(
                _finding("ARCHIVE_SYMLINK", display, "symlink entries are not allowed")
            )
            continue
        if (
            file_type
            and not is_dir
            and file_type not in {stat.S_IFREG, stat.S_IFDIR}
        ):
            state["findings"].append(
                _finding(
                    "ARCHIVE_SPECIAL_FILE",
                    display,
                    "special file entries are not allowed",
                )
            )
            continue

        if is_dir:
            continue

        if info.file_size > int(policy["max_entry_uncompressed_bytes"]):
            state["findings"].append(
                _finding(
                    "ARCHIVE_ENTRY_SIZE",
                    display,
                    "entry uncompressed bytes exceed policy",
                )
            )

        ratio = _ratio(info)
        if ratio > float(policy["max_compression_ratio"]):
            state["findings"].append(
                _finding(
                    "ARCHIVE_COMPRESSION_RATIO",
                    display,
                    "entry compression ratio exceeds policy",
                )
            )
            # Do not read a suspicious high-ratio member.
            continue

        if not normalized.lower().endswith(".zip"):
            continue

        if depth >= int(policy["max_nested_depth"]):
            state["findings"].append(
                _finding(
                    "ARCHIVE_NESTED_DEPTH",
                    display,
                    "nested archive depth exceeds policy",
                )
            )
            continue

        state["max_nested_depth_observed"] = max(
            state["max_nested_depth_observed"], depth + 1
        )
        state["nested_uncompressed_bytes"] += int(info.file_size)
        if state["nested_uncompressed_bytes"] > int(
            policy["max_cumulative_nested_uncompressed_bytes"]
        ):
            state["findings"].append(
                _finding(
                    "ARCHIVE_NESTED_CUMULATIVE_SIZE",
                    display,
                    "cumulative nested uncompressed bytes exceed policy",
                )
            )
            continue

        try:
            nested_bytes = archive.read(info)
            with zipfile.ZipFile(io.BytesIO(nested_bytes), "r") as nested:
                _inspect_zip(
                    nested,
                    policy=policy,
                    depth=depth + 1,
                    prefix=display,
                    state=state,
                )
        except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
            state["findings"].append(
                _finding(
                    "ARCHIVE_NESTED_INVALID",
                    display,
                    f"nested ZIP is invalid: {exc}",
                )
            )


def inspect_archive(path: Path, policy: dict) -> dict:
    archive_path = Path(path)
    data = archive_path.read_bytes()
    findings: list[dict[str, str]] = []

    if len(data) > int(policy["max_archive_bytes"]):
        findings.append(
            _finding(
                "ARCHIVE_SIZE",
                archive_path.name,
                f"archive bytes exceed {policy['max_archive_bytes']}",
            )
        )

    state = {
        "entries": 0,
        "total_uncompressed_bytes": 0,
        "max_nested_depth_observed": 0,
        "nested_uncompressed_bytes": 0,
        "findings": findings,
    }
    try:
        with zipfile.ZipFile(io.BytesIO(data), "r") as archive:
            _inspect_zip(
                archive,
                policy=policy,
                depth=0,
                prefix="",
                state=state,
            )
    except zipfile.BadZipFile as exc:
        findings.append(
            _finding("ARCHIVE_INVALID", archive_path.name, f"invalid ZIP: {exc}")
        )

    ordered_findings = sorted(
        findings,
        key=lambda item: (item["code"], item["path"], item["message"]),
    )
    return {
        "result": "PASS" if not ordered_findings else "REJECT",
        "archive_sha256": hashlib.sha256(data).hexdigest(),
        "entries": state["entries"],
        "total_uncompressed_bytes": state["total_uncompressed_bytes"],
        "max_nested_depth_observed": state["max_nested_depth_observed"],
        "findings": ordered_findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("production/sim/manifests/archive-safety-policy.json"),
    )
    args = parser.parse_args(argv)
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    result = inspect_archive(args.archive, policy)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
