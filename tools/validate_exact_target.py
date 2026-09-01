from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

UNKNOWN = {None, "", "UNKNOWN"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _missing(value: object) -> bool:
    try:
        return value in UNKNOWN
    except TypeError:
        return False


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.fullmatch(value))


def default_manifest_path(root: Path) -> Path:
    actual = root / "work/corpus/beta-1.8.42/capture-manifest.json"
    if actual.exists():
        return actual
    return root / "work/corpus/beta-1.8.42/capture-manifest.template.json"


def generation_grade_errors(manifest: dict[str, object]) -> list[str]:
    errors: list[str] = []

    def miss(label: str, value: object) -> None:
        if _missing(value):
            errors.append(label)

    if manifest.get("game_version") != "Beta 1.8.42":
        errors.append("game_version must equal Beta 1.8.42")

    for key, label in [
        ("release_channel", "missing release_channel"),
        ("platform", "missing platform"),
        ("distribution", "missing distribution"),
        ("capture_timestamp", "missing capture_timestamp"),
        ("capture_method", "missing capture_method"),
        ("vanilla_data_manifest_sha256", "missing vanilla Data manifest hash"),
        ("localization_manifest_sha256", "missing Localization manifest hash"),
        ("loader_root_snapshot_sha256", "missing loader-root snapshot hash"),
        ("identifiers_collision_index_sha256", "missing identifiers/collision index hash"),
    ]:
        miss(label, manifest.get(key))

    miss("missing executable SHA-256", manifest.get("executable_sha256"))

    if manifest.get("distribution") == "Steam":
        miss("missing Steam build ID", manifest.get("steam_build_id_or_equivalent"))

    for key, label in [
        ("executable_sha256", "invalid executable SHA-256"),
        ("vanilla_data_manifest_sha256", "invalid vanilla Data manifest SHA-256"),
        ("localization_manifest_sha256", "invalid Localization manifest SHA-256"),
        ("loader_root_snapshot_sha256", "invalid loader-root snapshot SHA-256"),
        ("identifiers_collision_index_sha256", "invalid identifiers/collision index SHA-256"),
    ]:
        value = manifest.get(key)
        if not _missing(value) and not _valid_sha256(value):
            errors.append(label)

    assemblies = manifest.get("managed_assemblies")
    if not isinstance(assemblies, list) or not assemblies:
        errors.append("missing managed assembly hashes/versions/MVIDs")
    else:
        saw_assembly_csharp = False
        for item in assemblies:
            if (
                not isinstance(item, dict)
                or any(_missing(item.get(k)) for k in ("name", "sha256", "assembly_version", "mvid"))
                or not _valid_sha256(item.get("sha256"))
            ):
                errors.append("incomplete managed assembly evidence")
                break
            if item.get("name") == "Assembly-CSharp.dll":
                saw_assembly_csharp = True
        if not saw_assembly_csharp:
            errors.append("missing Assembly-CSharp.dll exact-target identity")

    code = manifest.get("code_api_surface")
    if (
        not isinstance(code, dict)
        or not code.get("captured")
        or not _valid_sha256(code.get("manifest_sha256"))
        or not code.get("includes_persistence")
        or not code.get("includes_security")
    ):
        errors.append("missing current Code persistence/security API surface")

    hw = manifest.get("hardware_design_observations")
    if (
        not isinstance(hw, dict)
        or not hw.get("captured")
        or not _valid_sha256(hw.get("manifest_sha256"))
    ):
        errors.append("missing current Hardware Design observations")

    vanilla = manifest.get("vanilla_data_evidence")
    if not isinstance(vanilla, dict) or not vanilla.get("captured"):
        errors.append("missing current vanilla Data evidence")
    else:
        if not vanilla.get("scope_isolated"):
            errors.append("vanilla Data evidence not isolated from user/mod content")
        if not vanilla.get("content_resolved"):
            errors.append("vanilla Data content unresolved")
        vhash = vanilla.get("manifest_sha256")
        if not _valid_sha256(vhash):
            errors.append("invalid vanilla Data evidence manifest SHA-256")
        elif manifest.get("vanilla_data_manifest_sha256") != vhash:
            errors.append("vanilla Data manifest hash mismatch")

    collisions = manifest.get("identifiers_collision_index")
    if not isinstance(collisions, dict) or not collisions.get("captured"):
        errors.append("missing current identifiers/collision index evidence")
    else:
        chash = collisions.get("manifest_sha256")
        if not _valid_sha256(chash):
            errors.append("invalid identifiers/collision index evidence SHA-256")
        elif manifest.get("identifiers_collision_index_sha256") != chash:
            errors.append("identifiers/collision index hash mismatch")
        entry_count = collisions.get("entry_count")
        if not isinstance(entry_count, int) or entry_count <= 0:
            errors.append("empty current identifiers/collision index")

    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", nargs="?")
    ap.add_argument("--structural", action="store_true")
    ns = ap.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    path = Path(ns.manifest) if ns.manifest else default_manifest_path(root)
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = generation_grade_errors(data)

    if ns.structural:
        if not errors:
            print("structural gate error: public exact-target evidence unexpectedly qualifies as generation-grade")
            return 1
        print(
            f"STRUCTURAL_OK: exact-target generation-grade remains blocked by "
            f"{len(errors)} evidence requirements from {path.name}"
        )
        return 0

    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
