from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jsonschema

EXPECTED_CATEGORIES = {
    "ACTIVATION", "ROUTING", "SESSION", "RESEARCH", "AUTONOMY",
    "ARTIFACT", "REPAIR", "SECURITY", "VERIFICATION", "CROSS_SURFACE",
}


def validate_sim_evals(root: Path, schema_path: Path | None = None) -> list[str]:
    schema_path = schema_path or Path("schemas/sim-eval.schema.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    ids: list[str] = []
    categories: set[str] = set()
    files = sorted(root.glob("*.json"))
    if not files:
        return [f"{root}: no SIM eval suites found"]

    for path in files:
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        try:
            jsonschema.validate(records, schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"{path}: schema error: {exc.message}")
            continue
        for record in records:
            value = record["id"]
            if re.fullmatch(r"S\d{3}", value) is None:
                errors.append(f"{path}: invalid SIM eval id {value}")
            ids.append(value)
            categories.add(record["category"])

    if len(ids) != len(set(ids)):
        errors.append("SIM eval IDs must be globally unique")
    missing = EXPECTED_CATEGORIES - categories
    extra = categories - EXPECTED_CATEGORIES
    if missing:
        errors.append(f"missing SIM eval categories: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected SIM eval categories: {sorted(extra)}")
    return errors


def main(argv=None) -> int:
    args = argv or sys.argv[1:]
    root = Path(args[0]) if args else Path("production/evals/sim")
    errors = validate_sim_evals(root)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
