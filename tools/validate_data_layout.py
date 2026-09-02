from __future__ import annotations

from pathlib import Path


DOCUMENTED_DATA_ROOT_DIRS = {"SoftwareTypes", "CompanyTypes", "NameGenerators"}
NESTED_CONCEPT_DIRS = {"Features", "Categories", "SubFeatures", "AddOns", "Manufacturing"}


def validate_data_layout(root: Path) -> list[str]:
    errors: list[str] = []
    for name in sorted(NESTED_CONCEPT_DIRS):
        if (root / name).is_dir():
            errors.append(
                f"nested Data concept must not be treated as a canonical top-level directory: {name}"
            )
    return errors
