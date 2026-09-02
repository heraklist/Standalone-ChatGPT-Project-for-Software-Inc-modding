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
        return "UNKNOWN_NAMESPACE"

    if name not in identifiers:
        return "CLEAR"
    if intentional_override:
        return "INTENTIONAL_OVERRIDE"
    return "VANILLA_COLLISION"
