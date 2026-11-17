"""Emit a Claude Skill (and Claude Code plugin wrapper) from the single source of truth.

The repository already packages the knowledge surface as a ChatGPT Project bundle
(`build_release.py`). This target projects the *same* authored content onto Claude's
Agent Skill format so the Mod Studio can run on both platforms without a second,
hand-maintained copy of the knowledge.

Mapping (nothing is invented; everything is read from `production/`):

- `PROJECT_INSTRUCTIONS.md`            -> body of `SKILL.md`
- `00_INDEX.md` .. `17_...json` (18)  -> `references/` (progressive disclosure)
- a generated reference index          -> appended to `SKILL.md` so Claude knows
                                          which reference to open for a request

ChatGPT loads every knowledge file as resident context; a Claude Skill keeps only
`SKILL.md` resident and opens references on demand. The router document
(`00_INDEX.md`) is therefore the entry point the skill body points at first.

Output goes to `dist/` (git-ignored): the base stays clean and single-sourced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.verify_repo import KNOWLEDGE_FILES, verify

SKILL_NAME = "software-inc-mod-studio"
SKILL_DESCRIPTION = (
    "Design, author, edit, repair, migrate, debug, verify and package Software Inc mods "
    "(TyD Data, SIPL, C# Code/DLLMods, Furniture, Materials, Localization, Hardware Design, "
    "Buildings/Blueprints). Use for any Software Inc modding request: choosing the minimum-"
    "sufficient authoring surface, writing evidence-scoped version-aware mods for the canonical "
    "target, producing install-ready packages, and runtime verification. Fail-closed: never "
    "invents engine APIs, loader paths or file formats."
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_frontmatter(text: str) -> dict[str, str]:
    """Minimal parser for the simple `key: value` / `key: [a, b]` knowledge headers."""
    meta: dict[str, str] = {}
    if not text.startswith("---\n"):
        return meta
    head = text.split("---\n", 2)[1]
    for line in head.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta


def _reference_index(root: Path) -> str:
    lines = [
        "## Bundled knowledge (open as needed)",
        "",
        "Route with `references/00_INDEX.md` first, then open only the owner document(s) you need.",
        "",
    ]
    for name in sorted(KNOWLEDGE_FILES):
        if name.endswith(".json"):
            lines.append(f"- `references/{name}` — evidence registry (Source/Claim/Corpus/Media records).")
            continue
        meta = parse_frontmatter((root / "production/knowledge" / name).read_text(encoding="utf-8"))
        title = meta.get("title", name)
        aliases = meta.get("aliases", "").strip("[]")
        suffix = f" — aliases: {aliases}" if aliases else ""
        lines.append(f"- `references/{name}` — {title}{suffix}")
    lines.append("")
    return "\n".join(lines)


def build_skill(root: Path, out_dir: Path | None = None) -> tuple[Path, dict]:
    errors = verify(root)
    if errors:
        raise RuntimeError("repository verification failed: " + "; ".join(errors))

    instructions = (root / "production/project-instructions/PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")

    skill_md = (
        f"---\n"
        f"name: {SKILL_NAME}\n"
        f"description: {SKILL_DESCRIPTION}\n"
        f"---\n\n"
        f"{instructions.rstrip()}\n\n"
        f"{_reference_index(root)}"
    )

    out = out_dir or (root / "dist/claude")
    skill_dir = out / "skills" / SKILL_NAME
    refs_dir = skill_dir / "references"
    if out.exists():
        shutil.rmtree(out)
    refs_dir.mkdir(parents=True, exist_ok=True)

    files: dict[str, bytes] = {}
    skill_bytes = skill_md.encode("utf-8")
    (skill_dir / "SKILL.md").write_bytes(skill_bytes)
    files[f"skills/{SKILL_NAME}/SKILL.md"] = skill_bytes

    for name in sorted(KNOWLEDGE_FILES):
        data = (root / "production/knowledge" / name).read_bytes()
        (refs_dir / name).write_bytes(data)
        files[f"skills/{SKILL_NAME}/references/{name}"] = data

    # Claude Code plugin wrapper so the same skill is installable as a plugin.
    plugin_manifest = {
        "name": SKILL_NAME,
        "description": "Software Inc Mod Studio — evidence-scoped, fail-closed Software Inc modding.",
        "version": json.loads((root / "production/manifests/knowledge-pack-manifest.json").read_text(encoding="utf-8"))[
            "pack_version"
        ],
    }
    plugin_dir = out / ".claude-plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    plugin_bytes = (json.dumps(plugin_manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (plugin_dir / "plugin.json").write_bytes(plugin_bytes)
    files[".claude-plugin/plugin.json"] = plugin_bytes

    manifest = {
        "skill_name": SKILL_NAME,
        "source": "production/ (ChatGPT Project single source of truth)",
        "pack_version": plugin_manifest["version"],
        "reference_count": sum(1 for k in files if "/references/" in k),
        "file_sha256": {path: sha256_bytes(data) for path, data in sorted(files.items())},
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (out / "claude-skill-manifest.json").write_bytes(manifest_bytes)

    return out, manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Claude Skill/plugin from production/.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        out, manifest = build_skill(args.root, args.out)
    except RuntimeError as exc:
        print(exc)
        return 1
    print(out / "skills" / SKILL_NAME / "SKILL.md")
    print(f"references: {manifest['reference_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
