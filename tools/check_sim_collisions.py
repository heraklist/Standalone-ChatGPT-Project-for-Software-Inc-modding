from __future__ import annotations


def classify_identifier(
    name: str,
    namespace: str,
    index: dict,
    intentional_override: bool = False,
) -> str:
    namespaces = index.get("namespaces")
    if not isinstance(namespaces, dict) or namespace not in namespaces:
        return "UNKNOWN_NAMESPACE"

    record = namespaces.get(namespace)
    if not isinstance(record, dict):
        return "UNKNOWN_NAMESPACE"

    identifiers = record.get("identifiers")
    if not isinstance(identifiers, list):
        return "MALFORMED_COLLISION_EVIDENCE"

    known: set[str] = set()
    for entry in identifiers:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("identifier"), str)
            or not isinstance(entry.get("occurrences"), list)
        ):
            return "MALFORMED_COLLISION_EVIDENCE"
        known.add(entry["identifier"])

    if name not in known:
        return "CLEAR"
    if intentional_override:
        return "INTENTIONAL_OVERRIDE"
    return "VANILLA_COLLISION"
