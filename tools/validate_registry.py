from __future__ import annotations

import json
from pathlib import Path
import jsonschema


def validate_registry(path: Path, schema_path: Path | None = None) -> list[str]:
    root = Path(__file__).resolve().parents[1]
    schema_file = schema_path or root / "schemas/evidence-registry.schema.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    errors: list[str] = []

    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        errors.append(f"schema:{'/'.join(map(str, err.path))}: {err.message}")

    source_ids = set(data.get("sources", {}))
    claim_ids = set(data.get("claims", {}))

    for cid, claim in data.get("claims", {}).items():
        if claim.get("claim_id") != cid:
            errors.append(f"claim {cid}: claim_id mismatch")
        for ref in claim.get("evidence_refs", []):
            if ref not in source_ids and ref not in data.get("corpora", {}):
                errors.append(f"claim {cid}: missing evidence ref {ref}")

    for sid, source in data.get("sources", {}).items():
        if source.get("source_id") != sid:
            errors.append(f"source {sid}: source_id mismatch")
        if source.get("source_role") == "LINKED_ENGINE_API":
            if not source.get("delegated_by") or not source.get("linked_from"):
                errors.append(f"source {sid}: LINKED_ENGINE_API requires delegated_by and linked_from")
        if source.get("source_role") == "OLDER_VANILLA_CORPUS" and source.get("currency") == "EXACT_TARGET":
            errors.append(f"source {sid}: older vanilla corpus cannot be EXACT_TARGET")

    for mid, media in data.get("media", {}).items():
        if media.get("parent_source") not in source_ids:
            errors.append(f"media {mid}: missing parent_source")
        for cid in media.get("supported_claims", []):
            if cid not in claim_ids:
                errors.append(f"media {mid}: missing supported claim {cid}")

    return errors


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    errors = validate_registry(args.path)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
