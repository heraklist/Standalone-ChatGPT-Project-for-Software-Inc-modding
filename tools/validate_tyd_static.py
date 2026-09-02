from __future__ import annotations

import argparse
from pathlib import Path

from tools.validate_sipl_boundaries import validate_tyd_sipl_boundaries


def validate_tyd_text(text: str) -> list[str]:
    return validate_tyd_sipl_boundaries(text)


def validate_tyd_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return [f"unable to read TyD file: {path}"]
    return validate_tyd_text(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)

    errors = validate_tyd_file(args.path)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
