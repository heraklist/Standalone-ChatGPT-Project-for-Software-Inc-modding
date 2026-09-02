from __future__ import annotations

from pathlib import Path


DATA_ROOTS = {"SoftwareTypes", "CompanyTypes", "NameGenerators"}


def inspect_tree(root: Path) -> dict:
    files = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    )

    families: list[str] = []
    if any(path.startswith("SoftwareTypes/") and path.endswith(".tyd") for path in files):
        families.append("DATA_TYD")
    elif any(path == "Personalities.tyd" for path in files):
        families.append("DATA_TYD")
    elif any(path.split("/", 1)[0] in DATA_ROOTS for path in files if "/" in path):
        families.append("DATA_TYD")

    return {
        "files": files,
        "families": sorted(families),
        "executables": [],
        "warnings": [],
    }
