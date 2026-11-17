import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/corpus-manifest.schema.json"
CORPUS_MANIFESTS = sorted((ROOT / "work/corpus").glob("*/manifest.json"))


def _errors(data, schema):
    return sorted(jsonschema.Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))


def test_corpus_manifests_exist():
    # The schema must have inputs to guard; a silently-unused schema is dead weight.
    assert CORPUS_MANIFESTS, "no work/corpus/*/manifest.json found to validate"


def test_corpus_manifests_conform_to_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for path in CORPUS_MANIFESTS:
        data = json.loads(path.read_text(encoding="utf-8"))
        errors = _errors(data, schema)
        assert not errors, f"{path.relative_to(ROOT)}: " + "; ".join(f"{list(e.path)}: {e.message}" for e in errors)


def test_schema_enums_reject_unknown_currency():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    good = json.loads(CORPUS_MANIFESTS[0].read_text(encoding="utf-8"))
    bad = dict(good)
    bad["currency"] = "SOMEDAY_MAYBE"
    assert _errors(bad, schema), "schema should reject an unknown currency value"
