from __future__ import annotations

from pathlib import Path


DATA_ROOTS = {"SoftwareTypes", "CompanyTypes", "NameGenerators"}
UNTRUSTED_EXECUTABLE_SUFFIXES = {".dll", ".exe", ".ps1", ".bat", ".cmd", ".sh"}


def inspect_tree(root: Path) -> dict:
    paths = sorted(path for path in root.rglob("*") if path.is_file())
    files = [path.relative_to(root).as_posix() for path in paths]

    families: list[str] = []
    if any(path.startswith("SoftwareTypes/") and path.endswith(".tyd") for path in files):
        families.append("DATA_TYD")
    elif any(path == "Personalities.tyd" for path in files):
        families.append("DATA_TYD")
    elif any(path.split("/", 1)[0] in DATA_ROOTS for path in files if "/" in path):
        families.append("DATA_TYD")

    executables = sorted(
        path.relative_to(root).as_posix()
        for path in paths
        if path.suffix.lower() in UNTRUSTED_EXECUTABLE_SUFFIXES
    )
    warnings = [
        f"untrusted executable/script content: {relative}" for relative in executables
    ]

    return {
        "files": files,
        "families": sorted(families),
        "executables": executables,
        "warnings": warnings,
    }
