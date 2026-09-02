from __future__ import annotations

from pathlib import Path

from tools.validate_data_layout import validate_data_layout


def validate_package_tree(root: Path, families: list[str]) -> list[str]:
    errors: list[str] = []
    if "EDITOR_NATIVE" in families:
        errors.append("EDITOR_NATIVE: no verified generic ZIP schema")
    if "DATA_TYD" in families:
        errors.extend(validate_data_layout(root))
    return errors
