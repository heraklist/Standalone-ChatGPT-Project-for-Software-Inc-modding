from __future__ import annotations

from pathlib import Path

from tools.validate_data_layout import validate_data_layout

FULL_STATIC = "FULL_STATIC"
PARTIAL_STATIC = "PARTIAL_STATIC"
UNSUPPORTED = "UNSUPPORTED"
EDITOR_NATIVE_REQUIRED = "EDITOR_NATIVE_REQUIRED"

_EDITOR_NATIVE_FAMILIES = {
    "EDITOR_NATIVE",
    "BUILDING",
    "BUILDING_BLUEPRINT",
    "HARDWARE_DESIGN",
}

_COVERAGE = {
    "DATA_TYD": FULL_STATIC,
    "SIPL": UNSUPPORTED,
    "CODE": UNSUPPORTED,
    "FURNITURE": UNSUPPORTED,
    "MATERIALS": UNSUPPORTED,
    "LOCALIZATION": UNSUPPORTED,
    **{family: EDITOR_NATIVE_REQUIRED for family in _EDITOR_NATIVE_FAMILIES},
}


def validation_coverage(family: str) -> str:
    return _COVERAGE.get(family, UNSUPPORTED)


def validate_package_tree_report(root: Path, families: list[str]) -> dict:
    ordered_families = list(dict.fromkeys(families))
    coverage = {
        family: validation_coverage(family)
        for family in ordered_families
    }
    checks: list[dict[str, object]] = []
    errors: list[str] = []

    for family in ordered_families:
        level = coverage[family]
        if family == "DATA_TYD":
            family_errors = validate_data_layout(root)
            errors.extend(family_errors)
            checks.append(
                {
                    "id": "DATA_LAYOUT",
                    "family": family,
                    "result": "FAIL" if family_errors else "PASS",
                    "errors": family_errors,
                }
            )
        elif level == EDITOR_NATIVE_REQUIRED:
            checks.append(
                {
                    "id": "EDITOR_NATIVE_REQUIRED",
                    "family": family,
                    "result": "NOT_EXECUTED",
                    "errors": [],
                }
            )
        else:
            checks.append(
                {
                    "id": "PACKAGE_COMPLETENESS",
                    "family": family,
                    "result": "NOT_EXECUTED",
                    "errors": [],
                }
            )

    if any(level == EDITOR_NATIVE_REQUIRED for level in coverage.values()):
        result = "TOOLING_BLOCKED"
    elif errors:
        result = "FAIL"
    elif any(level == UNSUPPORTED for level in coverage.values()):
        result = "UNSUPPORTED"
    elif any(level == PARTIAL_STATIC for level in coverage.values()):
        result = "PARTIAL_STATIC"
    else:
        result = "PASS"

    return {
        "families": ordered_families,
        "coverage": coverage,
        "result": result,
        "checks": checks,
    }


def validate_package_tree(root: Path, families: list[str]) -> list[str]:
    report = validate_package_tree_report(root, families)
    errors: list[str] = []
    for check in report["checks"]:
        check_errors = check.get("errors", [])
        if isinstance(check_errors, list):
            errors.extend(str(error) for error in check_errors)

    for family in report["families"]:
        if report["coverage"][family] == EDITOR_NATIVE_REQUIRED:
            errors.append(f"{family}: no verified generic ZIP schema")
    return errors
