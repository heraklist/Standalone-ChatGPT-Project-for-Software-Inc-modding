from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas/vendor/agent-plugins/1.0.0/plugin.schema.json"
DEFAULT_CHECKSUM = ROOT / "schemas/vendor/agent-plugins/1.0.0/SHA256SUM"


def _declared_checksum(checksum_path: Path, schema_path: Path) -> str | None:
    if not checksum_path.is_file():
        return None
    for raw_line in checksum_path.read_text(encoding="utf-8").splitlines():
        parts = raw_line.strip().split()
        if len(parts) >= 2 and parts[-1].lstrip("*") == schema_path.name:
            return parts[0]
    return None


def validate_plugin_manifest(
    manifest_path: Path,
    schema_path: Path = DEFAULT_SCHEMA,
    checksum_path: Path = DEFAULT_CHECKSUM,
) -> list[str]:
    manifest_path = Path(manifest_path)
    schema_path = Path(schema_path)
    checksum_path = Path(checksum_path)

    if not schema_path.is_file():
        return ["AGENT_PLUGIN_SCHEMA_MISSING"]
    expected = _declared_checksum(checksum_path, schema_path)
    if expected is None:
        return ["AGENT_PLUGIN_SCHEMA_CHECKSUM_MISSING"]
    actual = hashlib.sha256(schema_path.read_bytes()).hexdigest()
    if actual != expected:
        return ["AGENT_PLUGIN_SCHEMA_CHECKSUM_MISMATCH"]
    if not manifest_path.is_file():
        return ["AGENT_PLUGIN_MANIFEST_MISSING"]

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        return [f"AGENT_PLUGIN_SCHEMA_INVALID_JSON: {exc}"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        return [f"AGENT_PLUGIN_MANIFEST_INVALID_JSON: {exc}"]

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        return [f"AGENT_PLUGIN_SCHEMA_INVALID: {exc.message}"]

    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(manifest),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            error.message,
        ),
    )
    return [error.message for error in errors]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--checksum", type=Path, default=DEFAULT_CHECKSUM)
    args = parser.parse_args(argv)

    errors = validate_plugin_manifest(args.manifest, args.schema, args.checksum)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("AGENT_PLUGIN_SCHEMA_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
