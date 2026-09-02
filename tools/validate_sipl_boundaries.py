from __future__ import annotations


def _mask_quoted_strings_and_tyd_comments(text: str) -> str:
    masked: list[str] = []
    in_string = False
    escaped = False
    in_comment = False

    for char in text:
        if char == "\n":
            masked.append(char)
            in_comment = False
            escaped = False
            continue

        if in_comment:
            masked.append(" ")
            continue

        if in_string:
            masked.append(" ")
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == "#":
            masked.append(" ")
            in_comment = True
            continue

        if char == '"':
            masked.append(" ")
            in_string = True
            escaped = False
            continue

        masked.append(char)

    return "".join(masked)


def validate_tyd_sipl_boundaries(text: str) -> list[str]:
    errors: list[str] = []
    masked = _mask_quoted_strings_and_tyd_comments(text)

    for line_number, line in enumerate(masked.splitlines(), start=1):
        if "~[" in line:
            errors.append(
                f"line {line_number}: SIPL array marker '~[' is not valid in TyD context"
            )
        if "//" in line:
            errors.append(
                f"line {line_number}: SIPL comment marker '//' is not valid in TyD context"
            )

    return errors
