from __future__ import annotations

from pathlib import Path

REQUIRED_DIRS = (
    "archive",
    "work",
    "production",
    "docs",
    "schemas",
    "tools",
    "tests",
)


def verify(root: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_DIRS:
        if not (root / name).is_dir():
            errors.append(f"missing repository root: {name}")
    ignore = root / ".gitignore"
    if not ignore.exists():
        errors.append("missing .gitignore")
    else:
        text = ignore.read_text(encoding="utf-8")
        for required in (".local-sources/", "dist/"):
            if required not in text:
                errors.append(f".gitignore missing {required}")
    return errors


def main(root: Path | None = None) -> int:
    repo = root or Path(__file__).resolve().parents[1]
    errors = verify(repo)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
