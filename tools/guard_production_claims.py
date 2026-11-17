"""Production legacy-claim regression guard.

`scan_legacy_claims.py` is a research scanner: its regexes match myth *strings*
regardless of surrounding context, so they also fire on the production documents
that deliberately *negate* those myths (for example `04_DATA_MODDING.md` stating
that `Data/Features.tyd` is **not** a canonical file). That makes the raw scanner
unusable as a pass/fail gate.

This guard turns the scanner into a deterministic, fail-closed regression gate
without trying to parse natural-language negation. It snapshots the exact set of
known, reviewed matches in `production/` into an allowlist and fails CI when a new
match appears (a myth reintroduced affirmatively) or a recorded match disappears
(the snapshot drifted). Either way a human must consciously run `--update` and the
diff is reviewed in the pull request.

The allowlist stores pattern *codes* (e.g. `INVENTED_BUILDINGS`), never the myth
strings themselves, so the allowlist file never self-triggers; it is also excluded
from the scan explicitly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.scan_legacy_claims import scan_tree

PRODUCTION_DIR = ROOT / "production"
ALLOWLIST_PATH = PRODUCTION_DIR / ".legacy-claim-allowlist.json"
ALLOWLIST_REL = ALLOWLIST_PATH.name


def current_hits(production_dir: Path = PRODUCTION_DIR) -> dict[str, list[str]]:
    """Map each production file (relative path) to its sorted set of pattern codes."""
    hits: dict[str, list[str]] = {}
    for finding in scan_tree(production_dir):
        path = finding["path"]
        if Path(path).name == ALLOWLIST_REL:
            continue
        hits[path] = sorted(set(finding["hits"]))
    return hits


def load_allowlist(path: Path = ALLOWLIST_PATH) -> dict[str, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    allowed = data.get("allowed", {})
    return {k: sorted(set(v)) for k, v in allowed.items()}


def diff(current: dict[str, list[str]], allowed: dict[str, list[str]]) -> list[str]:
    """Return human-readable drift messages. Empty means the snapshot is exact."""
    errors: list[str] = []
    for path in sorted(set(current) | set(allowed)):
        cur = set(current.get(path, []))
        allow = set(allowed.get(path, []))
        for code in sorted(cur - allow):
            errors.append(f"UNEXPECTED legacy-claim match {path}: {code} (reintroduced myth or new file)")
        for code in sorted(allow - cur):
            errors.append(f"STALE allowlist entry {path}: {code} (match removed; run --update)")
    return errors


def write_allowlist(current: dict[str, list[str]], path: Path = ALLOWLIST_PATH) -> None:
    payload = {
        "_comment": (
            "Golden snapshot of reviewed legacy-claim matches in production/. "
            "Entries are pattern CODES from tools/scan_legacy_claims.py, not myth text. "
            "Regenerate with: python tools/guard_production_claims.py --update"
        ),
        "allowed": {k: current[k] for k in sorted(current)},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true", help="rewrite the allowlist snapshot from the current tree")
    parser.add_argument("--production-dir", type=Path, default=PRODUCTION_DIR)
    args = parser.parse_args(argv)

    current = current_hits(args.production_dir)

    if args.update:
        write_allowlist(current)
        print(f"updated {ALLOWLIST_PATH.relative_to(ROOT)} with {sum(len(v) for v in current.values())} match(es)")
        return 0

    if not ALLOWLIST_PATH.is_file():
        print(f"missing allowlist snapshot: {ALLOWLIST_PATH.relative_to(ROOT)}; run --update")
        return 1

    errors = diff(current, load_allowlist())
    for error in errors:
        print(error)
    if errors:
        print("Production legacy-claim guard FAILED. If a change is intentional, run --update and review the diff.")
        return 1
    print("PRODUCTION_CLAIM_GUARD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
