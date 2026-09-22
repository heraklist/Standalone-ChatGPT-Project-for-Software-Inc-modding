from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "production/knowledge"

ALLOWED_CURRENCY = {
    "EXACT_TARGET",
    "TARGET_BRANCH",
    "OLDER_VERSION",
    "FUTURE_DEV",
    "UNKNOWN_VERSION",
    "NOT_VERSION_SENSITIVE",
}
STALE_PENDING_PHRASES = (
    "Beta 1.8.42 exact environment corpus pending",
    "Exact target assemblies pending",
    "Exact Beta 1.8.42 managed assembly/API evidence remains mandatory",
    "exact-target assembly evidence remains mandatory",
    "Exact Beta 1.8.42 local corpus and assembly surface remain a production-release gate",
)


def frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+)$", text)
    return match.group(1).strip() if match else None


def test_all_knowledge_currency_summaries_use_canonical_enum() -> None:
    invalid: dict[str, str | None] = {}
    for path in sorted(KNOWLEDGE.glob("*.md")):
        value = frontmatter_value(path.read_text(encoding="utf-8"), "currency_summary")
        if value not in ALLOWED_CURRENCY:
            invalid[path.name] = value
    assert invalid == {}


def test_resolved_exact_target_capture_is_not_still_marked_pending() -> None:
    stale: dict[str, list[str]] = {}
    for path in sorted(KNOWLEDGE.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        hits = [phrase for phrase in STALE_PENDING_PHRASES if phrase in text]
        if hits:
            stale[path.name] = hits
    assert stale == {}


def test_code_metadata_acknowledges_exact_target_assembly_surface() -> None:
    for name in (
        "06_CODE_MODDING_CORE_AND_DISTRIBUTION.md",
        "07_CODE_RUNTIME_UI_PERSISTENCE_SECURITY.md",
    ):
        text = (KNOWLEDGE / name).read_text(encoding="utf-8")
        assert frontmatter_value(text, "currency_summary") == "EXACT_TARGET"
        assert "code API surface" in text.lower() or "assembly surface" in text.lower()
        assert "claim-specific" in text.lower()
