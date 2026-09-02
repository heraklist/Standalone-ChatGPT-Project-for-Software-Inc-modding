from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REFERENCE_MAPPINGS = (
    ("evidence-truth", "production/knowledge/01_EVIDENCE_VERSION_AND_TRUTH.md", "production/sim/references/evidence-truth.md"),
    ("ecosystem-router", "production/knowledge/02_MOD_ECOSYSTEM_AND_ROUTER.md", "production/sim/references/ecosystem-router.md"),
    ("tyd", "production/knowledge/03_TYD_FOUNDATIONS.md", "production/sim/references/tyd.md"),
    ("data", "production/knowledge/04_DATA_MODDING.md", "production/sim/references/data.md"),
    ("sipl", "production/knowledge/05_SIPL.md", "production/sim/references/sipl.md"),
    ("code-core", "production/knowledge/06_CODE_MODDING_CORE_AND_DISTRIBUTION.md", "production/sim/references/code-core.md"),
    ("code-runtime", "production/knowledge/07_CODE_RUNTIME_UI_PERSISTENCE_SECURITY.md", "production/sim/references/code-runtime.md"),
    ("furniture", "production/knowledge/08_FURNITURE.md", "production/sim/references/furniture.md"),
    ("materials", "production/knowledge/09_MATERIALS.md", "production/sim/references/materials.md"),
    ("localization", "production/knowledge/10_LOCALIZATION.md", "production/sim/references/localization.md"),
    ("editor-content", "production/knowledge/11_EDITOR_CONTENT_HARDWARE_BLUEPRINTS_BUILDINGS.md", "production/sim/references/editor-content.md"),
    ("debugging", "production/knowledge/12_DEBUGGING_CONSOLE_AND_RUNTIME.md", "production/sim/references/debugging.md"),
    ("compatibility", "production/knowledge/13_COMPATIBILITY_MIGRATION_AND_COLLISIONS.md", "production/sim/references/compatibility.md"),
    ("delivery", "production/knowledge/15_BUILD_EDIT_REPAIR_AND_DELIVERY.md", "production/sim/references/delivery.md"),
    ("verification", "production/knowledge/16_VERIFICATION_AND_QA.md", "production/sim/references/verification.md"),
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"path must be inside repository root: {path}") from exc


def build_reference(
    *,
    root: Path,
    source_paths: list[Path],
    output_path: Path,
    transform: str,
    reference_id: str,
    source_id: str,
) -> dict:
    if transform != "COPY":
        raise ValueError(f"unsupported SIM reference transform: {transform}")
    if len(source_paths) != 1:
        raise ValueError("COPY references require exactly one source")

    source = source_paths[0]
    if not source.is_file():
        raise FileNotFoundError(source)

    source_relative = _relative(root, source)
    output_relative = _relative(root, output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(source.read_bytes())

    return {
        "reference_id": reference_id,
        "source_id": source_id,
        "output_path": output_relative,
        "canonical_source_paths": [source_relative],
        "source_sha256": {source_relative: sha256_file(source)},
        "transform_type": "COPY",
        "output_sha256": sha256_file(output_path),
    }


def build_references(root: Path) -> dict:
    entries: list[dict] = []
    for reference_id, source_path, output_path in REFERENCE_MAPPINGS:
        entries.append(
            build_reference(
                root=root,
                source_paths=[root / source_path],
                output_path=root / output_path,
                transform="COPY",
                reference_id=reference_id,
                source_id=source_path,
            )
        )

    manifest = {"schema_version": 1, "entries": entries}
    manifest_path = root / "production/sim/manifests/reference-source-map.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    manifest = build_references(args.root)
    print(f"built {len(manifest['entries'])} SIM references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
