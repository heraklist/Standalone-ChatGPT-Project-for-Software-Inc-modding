from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


ALLOWED_RESULTS = {"PASS", "FAIL", "PLATFORM_LIMITATION", "NOT_TESTED"}


@dataclass(frozen=True)
class CertificationContext:
    candidate_tree_sha256: str
    semantic_aggregate_sha256: str
    source_commit: str
    plugin_version: str
    exact_target_manifest_sha256: str
    protocol_version: str
    surface: str
    transport: str | None = None
    plugin_id: str | None = None
    release_id: str | None = None


@dataclass(frozen=True)
class AcceptanceSummary:
    status: str
    case_results: dict[str, str]
    known_gaps: tuple[str, ...]


def load_acceptance_records(evidence_dir: Path) -> list[dict]:
    records: list[dict] = []
    if not evidence_dir.is_dir():
        return records
    for path in sorted(evidence_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid acceptance evidence {path.name}: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"invalid acceptance evidence {path.name}: expected object")
        data = dict(data)
        data["_record_id"] = path.stem
        records.append(data)
    return records


def _matches_context(record: dict, context: CertificationContext) -> bool:
    return (
        record.get("candidate_tree_sha256") == context.candidate_tree_sha256
        and record.get("semantic_aggregate_sha256")
        == context.semantic_aggregate_sha256
        and record.get("candidate_source_commit") == context.source_commit
        and record.get("plugin_version") == context.plugin_version
        and record.get("exact_target_manifest_sha256")
        == context.exact_target_manifest_sha256
        and record.get("certification_protocol_version") == context.protocol_version
        and record.get("surface") == context.surface
        and (
            context.protocol_version != "sim-live-v3"
            or (
                record.get("transport") == context.transport
                and record.get("plugin_id") == context.plugin_id
                and record.get("release_id") == context.release_id
            )
        )
    )


@lru_cache(maxsize=1)
def _acceptance_validator() -> jsonschema.Draft202012Validator:
    schema_path = ROOT / "schemas/sim-acceptance-evidence.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid acceptance evidence schema: {exc}") from exc
    return jsonschema.Draft202012Validator(schema)


def _validate_matched_records(records: list[dict]) -> None:
    validator = _acceptance_validator()
    for record in records:
        payload = {
            key: value
            for key, value in record.items()
            if key != "_record_id"
        }
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        if errors:
            record_id = record.get("_record_id", "<unknown>")
            raise ValueError(
                "acceptance evidence schema violation "
                f"in {record_id}: {errors[0].message}"
            )


def _terminal_result(records: list[dict], case_id: str) -> str:
    if not records:
        return "NOT_TESTED"

    record_ids = {record["_record_id"] for record in records}
    for record in records:
        result = record.get("result")
        if result not in ALLOWED_RESULTS:
            raise ValueError(
                f"invalid acceptance result for {case_id}: {result!r}"
            )
        parent = record.get("retest_of")
        if parent is not None and parent not in record_ids:
            raise ValueError(
                f"orphan retest for {case_id}: {record['_record_id']} -> {parent}"
            )

    superseded = {
        record["retest_of"]
        for record in records
        if isinstance(record.get("retest_of"), str)
    }
    terminals = [
        record for record in records if record["_record_id"] not in superseded
    ]
    if len(terminals) != 1:
        names = ", ".join(sorted(record["_record_id"] for record in terminals))
        raise ValueError(
            f"ambiguous terminal acceptance evidence for {case_id}: {names}"
        )

    terminal = terminals[0]
    seen: set[str] = set()
    current = terminal
    by_id = {record["_record_id"]: record for record in records}
    while True:
        current_id = current["_record_id"]
        if current_id in seen:
            raise ValueError(f"cyclic retest chain for {case_id}")
        seen.add(current_id)
        parent = current.get("retest_of")
        if parent is None:
            break
        current = by_id[parent]

    if seen != record_ids:
        leftover = ", ".join(sorted(record_ids - seen))
        raise ValueError(
            f"disconnected or cyclic retest chain for {case_id}: {leftover}"
        )

    return terminal["result"]


def summarize_acceptance(
    evidence_dir: Path,
    context: CertificationContext,
    required_cases: tuple[str, ...],
) -> AcceptanceSummary:
    records = [
        record
        for record in load_acceptance_records(evidence_dir)
        if _matches_context(record, context)
    ]
    _validate_matched_records(records)

    case_results: dict[str, str] = {}
    for case_id in required_cases:
        case_records = [
            record for record in records if record.get("case_id") == case_id
        ]
        case_results[case_id] = _terminal_result(case_records, case_id)

    if any(result == "FAIL" for result in case_results.values()):
        status = "FAIL"
    elif any(
        result in {"NOT_TESTED", "PLATFORM_LIMITATION"}
        for result in case_results.values()
    ):
        status = "INCOMPLETE"
    else:
        status = "PASS"

    known_gaps = tuple(
        f"{case_id} {context.surface} acceptance {result}"
        for case_id, result in case_results.items()
        if result != "PASS"
    )
    return AcceptanceSummary(
        status=status,
        case_results=case_results,
        known_gaps=known_gaps,
    )
