from __future__ import annotations

import re


GAME_COMPILED_CSHARP3 = "GAME_COMPILED_CSHARP3"
LOCAL_PRECOMPILED = "LOCAL_PRECOMPILED"
PROFILES = {GAME_COMPILED_CSHARP3, LOCAL_PRECOMPILED}

_ENUM_RE = re.compile(r"\benum\b")
_EXPRESSION_BODIED_MEMBER_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|virtual|override|sealed|abstract|new|extern|unsafe|readonly|partial)\s+)+"
    r"[A-Za-z_][\w<>,\.\[\]\?]*\s+"
    r"[A-Za-z_]\w*\s*(?:\([^;{}]*\))?\s*=>"
)


def _mask_comments_and_strings(text: str) -> str:
    out: list[str] = []
    i = 0
    in_string = False
    in_char = False
    in_line_comment = False
    in_block_comment = False
    escaped = False

    while i < len(text):
        char = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if char == "\n":
            out.append(char)
            in_line_comment = False
            escaped = False
            i += 1
            continue

        if in_line_comment:
            out.append(" ")
            i += 1
            continue

        if in_block_comment:
            if char == "*" and nxt == "/":
                out.extend((" ", " "))
                in_block_comment = False
                i += 2
            else:
                out.append(" ")
                i += 1
            continue

        if in_string or in_char:
            out.append(" ")
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif in_string and char == '"':
                in_string = False
            elif in_char and char == "'":
                in_char = False
            i += 1
            continue

        if char == "/" and nxt == "/":
            out.extend((" ", " "))
            in_line_comment = True
            i += 2
            continue
        if char == "/" and nxt == "*":
            out.extend((" ", " "))
            in_block_comment = True
            i += 2
            continue
        if char == '"':
            out.append(" ")
            in_string = True
            i += 1
            continue
        if char == "'":
            out.append(" ")
            in_char = True
            i += 1
            continue

        out.append(char)
        i += 1

    return "".join(out)


def validate_code_source(text: str, profile: str) -> list[str]:
    if profile not in PROFILES:
        raise ValueError(f"unknown SIM Code profile: {profile}")
    if profile == LOCAL_PRECOMPILED:
        return []

    errors: list[str] = []
    masked = _mask_comments_and_strings(text)
    for line_number, line in enumerate(masked.splitlines(), start=1):
        if _ENUM_RE.search(line):
            errors.append(
                f"line {line_number}: enum usage is blocked for GAME_COMPILED_CSHARP3"
            )
        if _EXPRESSION_BODIED_MEMBER_RE.search(line):
            errors.append(
                f"line {line_number}: expression-bodied member is not valid C# 3 game-compiled syntax"
            )
    return errors
