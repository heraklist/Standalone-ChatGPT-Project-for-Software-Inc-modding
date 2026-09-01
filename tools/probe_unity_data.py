from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path

EXPECTED_EXE_SHA256 = "89b36700316d8b3ba554550f1d47f5eac68c38a9110b4a5509278ca243aef46f"
TARGET_ASSETS = {
    "Software Inc_Data/globalgamemanagers.assets": "3326fa323740137c7154b9e1be91a7aa3c5004b565fc68a7e8833b3bb8d055bf",
    "Software Inc_Data/resources.assets": "7652d7f1ac99b63a5bf8badb8dd7ecf43c434e43888067ae72a2c4c8548f5740",
    "Software Inc_Data/sharedassets2.assets": "9aa220436585fefb2534acf4e55aaf21d531b36db7946ddb1dd167a4d225bb2d",
}
RELEVANT_TOKENS = [
    "SoftwareType",
    "SoftwareTypes",
    "CompanyType",
    "CompanyTypes",
    "NameGenerator",
    "NameGenerators",
    "Personalities",
    "HardwareDesign",
    "HardwareDesigns",
    "TydCollection",
    "ModPackage",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_relevant_tokens(payload: bytes) -> list[str]:
    lowered = payload.lower()
    result: list[str] = []
    for token in RELEVANT_TOKENS:
        if token.encode("ascii").lower() in lowered:
            if token.endswith("s") and token[:-1] in result:
                continue
            result.append(token)
    return result


def safe_component(value: str) -> str:
    value = re.sub(r'[<>:"/\\|*?]', "_", value)
    value = re.sub(r"[\x00-\x1f]", "_", value)
    return value.strip().strip(".") or "unnamed"


def build_textasset_record(*, source_asset: str, path_id: int, object_name: str, payload: bytes) -> dict[str, object]:
    return {
        "source_asset": source_asset,
        "path_id": int(path_id),
        "object_name": object_name,
        "payload_size": len(payload),
        "payload_sha256": sha256_bytes(payload),
        "tokens": find_relevant_tokens(payload),
    }


def _get_textasset_payload(data: object) -> bytes:
    for attr in ("m_Script", "script"):
        if hasattr(data, attr):
            value = getattr(data, attr)
            if isinstance(value, bytes):
                return value
            if isinstance(value, bytearray):
                return bytes(value)
            if isinstance(value, str):
                return value.encode("utf-8")
    raise ValueError("TextAsset payload property not found")


def _get_object_name(data: object, fallback: str) -> str:
    for attr in ("m_Name", "name"):
        if hasattr(data, attr):
            value = getattr(data, attr)
            if value:
                return str(value)
    return fallback


def _find_game_root(explicit: str | None) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
        if (root / "Software Inc.exe").is_file():
            return root
        raise FileNotFoundError(f"Software Inc.exe not found under {root}")

    candidates: list[Path] = []
    for env_name in ("ProgramFiles(x86)", "ProgramFiles"):
        import os
        base = os.environ.get(env_name)
        if base:
            candidates.append(Path(base) / "Steam" / "steamapps" / "common" / "Software Inc")
    for root in candidates:
        if (root / "Software Inc.exe").is_file():
            return root.resolve()
    raise FileNotFoundError("Could not auto-detect Software Inc; pass --game-root")


def run_probe(game_root: Path, output_dir: Path) -> Path:
    try:
        import UnityPy  # type: ignore
    except ImportError as exc:
        raise RuntimeError("UnityPy is required. Install it with: python -m pip install UnityPy") from exc

    exe = game_root / "Software Inc.exe"
    exe_hash = sha256_file(exe)
    if exe_hash != EXPECTED_EXE_SHA256:
        raise RuntimeError(
            "Exact-target executable hash mismatch. "
            f"Expected {EXPECTED_EXE_SHA256}, got {exe_hash}. Refusing to mix versions."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    staging = output_dir / "Beta1842-unity-data-probe"
    if staging.exists():
        shutil.rmtree(staging)
    private_dir = staging / "PRIVATE-EVIDENCE" / "textassets"
    private_dir.mkdir(parents=True, exist_ok=True)

    asset_reports: list[dict[str, object]] = []
    all_records: list[dict[str, object]] = []
    all_errors: list[dict[str, object]] = []

    for rel, expected_hash in TARGET_ASSETS.items():
        asset_path = game_root / Path(rel)
        actual_hash = sha256_file(asset_path)
        if actual_hash != expected_hash:
            raise RuntimeError(f"Asset hash mismatch for {rel}; refusing mixed-version extraction")

        env = UnityPy.load(str(asset_path))
        type_counts: Counter[str] = Counter()
        text_count = 0
        relevant_count = 0

        for obj in env.objects:
            type_name = getattr(getattr(obj, "type", None), "name", str(getattr(obj, "type", "UNKNOWN")))
            type_counts[type_name] += 1
            if type_name != "TextAsset":
                continue

            text_count += 1
            path_id = int(getattr(obj, "path_id", -1))
            try:
                data = obj.read()
                payload = _get_textasset_payload(data)
                name = _get_object_name(data, f"TextAsset_{path_id}")
                record = build_textasset_record(
                    source_asset=rel,
                    path_id=path_id,
                    object_name=name,
                    payload=payload,
                )

                if record["tokens"]:
                    relevant_count += 1
                    asset_component = safe_component(Path(rel).name)
                    filename = f"{path_id}__{safe_component(name)}.bin"
                    private_path = Path("PRIVATE-EVIDENCE") / "textassets" / asset_component / filename
                    target = staging / private_path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(payload)
                    record["private_path"] = private_path.as_posix()
                else:
                    record["private_path"] = None
                all_records.append(record)
            except Exception as exc:
                all_errors.append({
                    "source_asset": rel,
                    "path_id": path_id,
                    "error": f"{type(exc).__name__}: {exc}",
                })

        asset_reports.append({
            "source_asset": rel,
            "source_asset_sha256": actual_hash,
            "object_type_counts": dict(sorted(type_counts.items())),
            "textasset_count": text_count,
            "relevant_textasset_count": relevant_count,
        })

    summary = {
        "game_version": "Beta 1.8.42",
        "executable_sha256": exe_hash,
        "unitypy_version": getattr(UnityPy, "__version__", "UNKNOWN"),
        "target_assets": TARGET_ASSETS,
        "assets": asset_reports,
        "textasset_count": len(all_records),
        "relevant_textasset_count": sum(1 for r in all_records if r["tokens"]),
        "errors": len(all_errors),
        "raw_game_binaries_copied": False,
        "private_textassets_only": True,
    }

    (staging / "probe-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (staging / "textasset-manifest.json").write_text(json.dumps(all_records, indent=2) + "\n", encoding="utf-8")
    (staging / "errors.json").write_text(json.dumps(all_errors, indent=2) + "\n", encoding="utf-8")

    zip_path = output_dir / "Beta1842-unity-data-probe.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(staging.rglob("*")):
            if file.is_file():
                zf.write(file, file.relative_to(staging).as_posix())
    digest = sha256_file(zip_path)
    (output_dir / "Beta1842-unity-data-probe.zip.sha256.txt").write_text(
        f"{digest}  {zip_path.name}\n", encoding="utf-8"
    )
    shutil.rmtree(staging)
    return zip_path


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-root")
    parser.add_argument("--output-dir", default=str(Path.home() / "Desktop"))
    args = parser.parse_args(argv)
    try:
        root = _find_game_root(args.game_root)
        path = run_probe(root, Path(args.output_dir).expanduser().resolve())
    except Exception as exc:
        print(f"PROBE_ERROR: {type(exc).__name__}: {exc}")
        return 1
    print(f"PROBE_COMPLETE: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
